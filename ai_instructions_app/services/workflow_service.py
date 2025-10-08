"""Workflow orchestration service preserving the LangGraph workflow structure."""
from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from ai_instructions_app.utils.validation import WorkflowConfigSchema
from ai_instructions_app.workflow.state import WebWorkflowState, WorkflowState

LOGGER = logging.getLogger(__name__)


class WebWorkflowService:
    """Service responsible for executing the AI instructions workflow."""

    def __init__(self) -> None:
        self.memory_saver = MemorySaver()
        self.workflow_graph = self._build_web_workflow()
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start_workflow(self, config: WorkflowConfigSchema) -> str:
        workflow_id = str(uuid.uuid4())
        initial_state: WebWorkflowState = WebWorkflowState(
            workflow_id=workflow_id,
            ocg_term_details=config.ocg_term_details,
            document_text=config.document_text,
            human_labeled_answer=config.human_labeled_answer,
            referenced_page_texts=config.referenced_page_texts,
            document_name=config.document_name,
            project_name=config.project_name,
            refinement_attempts=0,
            max_refinement_attempts=3,
            workflow_messages=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            progress_percentage=0.0,
            current_stage="initialized",
            can_pause=False,
            can_edit=False,
            intermediate_results={},
        )

        thread_config = {"configurable": {"thread_id": workflow_id}}
        self.active_workflows[workflow_id] = {
            "status": "running",
            "thread_config": thread_config,
            "current_state": initial_state,
            "progress": 0.0,
            "created_at": initial_state["created_at"],
            "updated_at": initial_state["updated_at"],
        }

        thread = threading.Thread(
            target=self._run_async_workflow,
            args=(workflow_id, initial_state, thread_config),
            daemon=True,
        )
        thread.start()

        return workflow_id

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.active_workflows.get(workflow_id)

    # ------------------------------------------------------------------
    # Workflow construction
    # ------------------------------------------------------------------
    def _build_web_workflow(self) -> StateGraph:
        workflow = StateGraph(WorkflowState)

        workflow.add_node("document_processor", self.document_processor_node)
        workflow.add_node("ai_instructions_generator", self.ai_instructions_generator_node)
        workflow.add_node("extractor", self.extractor_node)
        workflow.add_node("evaluator", self.evaluator_node)
        workflow.add_node("success_handler_node", self.success_handler_node)
        workflow.add_node("refine_ai_instructions_node", self.refine_ai_instructions_node)
        workflow.add_node("ai_instructions_verifier", self.ai_instructions_verifier_node)
        workflow.add_node("validation_extractor", self.validation_extractor_node)
        workflow.add_node("validation_evaluator", self.validation_evaluator_node)

        workflow.add_edge(START, "document_processor")
        workflow.add_conditional_edges(
            "document_processor",
            self.route_from_document_processor,
            {
                "ai_instructions_generator": "ai_instructions_generator",
                "END": END,
            },
        )

        workflow.add_edge("ai_instructions_generator", "extractor")
        workflow.add_edge("extractor", "evaluator")
        workflow.add_conditional_edges(
            "evaluator",
            self.route_after_evaluation,
            {
                "success_handler_node": "success_handler_node",
                "refine_ai_instructions_node": "refine_ai_instructions_node",
                "ai_instructions_verifier": "ai_instructions_verifier",
            },
        )
        workflow.add_edge("success_handler_node", "ai_instructions_verifier")
        workflow.add_edge("refine_ai_instructions_node", "extractor")
        workflow.add_conditional_edges(
            "ai_instructions_verifier",
            self.route_after_verification,
            {
                "validation_extractor": "validation_extractor",
                "END": END,
            },
        )
        workflow.add_edge("validation_extractor", "validation_evaluator")
        workflow.add_edge("validation_evaluator", END)

        return workflow.compile(checkpointer=self.memory_saver)

    # ------------------------------------------------------------------
    # Execution helpers
    # ------------------------------------------------------------------
    def _run_async_workflow(
        self,
        workflow_id: str,
        initial_state: WebWorkflowState,
        thread_config: Dict[str, Any],
    ) -> None:
        asyncio.run(self._execute_workflow(workflow_id, initial_state, thread_config))

    async def _execute_workflow(
        self,
        workflow_id: str,
        initial_state: WebWorkflowState,
        thread_config: Dict[str, Any],
    ) -> None:
        try:
            async for event in self.workflow_graph.astream(
                initial_state,
                thread_config,
                stream_mode="values",
            ):
                await self._update_workflow_progress(workflow_id, event)

            self.active_workflows[workflow_id]["status"] = "completed"
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.exception("Workflow %s failed: %s", workflow_id, exc)
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(exc)

    async def _update_workflow_progress(self, workflow_id: str, event: Dict[str, Any]) -> None:
        workflow_state = self.active_workflows.get(workflow_id)
        if not workflow_state:
            return
        workflow_state["current_state"] = event
        workflow_state["updated_at"] = datetime.utcnow()
        workflow_state["progress"] = event.get("progress", workflow_state.get("progress", 0.0))

    # ------------------------------------------------------------------
    # Routing logic - mirrors original implementation
    # ------------------------------------------------------------------
    def route_from_document_processor(self, state: WorkflowState) -> str:
        if not state.get("document_text"):
            return "END"
        return "ai_instructions_generator"

    def route_after_evaluation(self, state: WorkflowState) -> str:
        judgement_list = state.get("judgement", [])
        current_judgement = judgement_list[-1] if judgement_list else "NO"
        refinement_attempts = state.get("refinement_attempts", 0)
        max_attempts = state.get("max_refinement_attempts", 3)

        if current_judgement in ["YES", "PARTIAL"]:
            return "success_handler_node"
        if current_judgement == "NO" and refinement_attempts < max_attempts:
            return "refine_ai_instructions_node"
        return "ai_instructions_verifier"

    def route_after_verification(self, state: WorkflowState) -> str:
        is_success = state.get("is_success", False)
        return "validation_extractor" if is_success else "END"

    # ------------------------------------------------------------------
    # Node implementations - placeholders preserving structure
    # ------------------------------------------------------------------
    def document_processor_node(self, state: WorkflowState) -> Dict[str, Any]:
        LOGGER.debug("Processing document for workflow")
        return {
            "workflow_messages": ["Document processed"],
            "progress": 10.0,
        }

    def ai_instructions_generator_node(self, state: WorkflowState) -> Dict[str, Any]:
        LOGGER.debug("Generating AI instructions")
        return {
            "initial_ai_instructions": "",
            "reasoning_explanation": "",
            "workflow_messages": ["Initial AI instructions generated"],
            "progress": 25.0,
        }

    def extractor_node(self, state: WorkflowState) -> Dict[str, Any]:
        LOGGER.debug("Running extractor node")
        return {
            "extracted_answer": state.get("extracted_answer", []) + [""],
            "extraction_reasoning": state.get("extraction_reasoning", []) + [""],
            "workflow_messages": ["Extractor executed"],
            "progress": 40.0,
        }

    def evaluator_node(self, state: WorkflowState) -> Dict[str, Any]:
        LOGGER.debug("Evaluating extraction results")
        judgement_list = state.get("judgement", []) + ["NO"]
        return {
            "judgement": judgement_list,
            "match_type": judgement_list[-1],
            "evaluation_reasoning": "",
            "workflow_messages": ["Evaluation complete"],
            "progress": 55.0,
        }

    def success_handler_node(self, state: WorkflowState) -> Dict[str, Any]:
        LOGGER.debug("Handling success path")
        return {
            "is_success": True,
            "final_ai_instructions": state.get("initial_ai_instructions", ""),
            "workflow_messages": ["Success handler executed"],
            "progress": 65.0,
        }

    def refine_ai_instructions_node(self, state: WorkflowState) -> Dict[str, Any]:
        LOGGER.debug("Refining AI instructions")
        attempts = state.get("refinement_attempts", 0) + 1
        return {
            "refinement_attempts": attempts,
            "refined_instructions": state.get("refined_instructions", []) + [""],
            "refinement_reasoning": state.get("refinement_reasoning", []) + [""],
            "workflow_messages": [f"Refinement attempt {attempts}"],
            "progress": 50.0,
        }

    def ai_instructions_verifier_node(self, state: WorkflowState) -> Dict[str, Any]:
        LOGGER.debug("Verifying AI instructions")
        return {
            "verified_instructions": state.get("final_ai_instructions", ""),
            "verification_report": "",
            "workflow_messages": ["Verification complete"],
            "progress": 75.0,
        }

    def validation_extractor_node(self, state: WorkflowState) -> Dict[str, Any]:
        LOGGER.debug("Running validation extractor")
        return {
            "validation_extracted_answer": "",
            "validation_extraction_reasoning": "",
            "workflow_messages": ["Validation extraction complete"],
            "progress": 85.0,
        }

    def validation_evaluator_node(self, state: WorkflowState) -> Dict[str, Any]:
        LOGGER.debug("Running validation evaluator")
        return {
            "validation_match_type": "NO",
            "validation_judgement": "NO",
            "validation_evaluation_reasoning": "",
            "accuracy_maintained": False,
            "workflow_messages": ["Validation evaluation complete"],
            "progress": 100.0,
        }

    # ------------------------------------------------------------------
    # LLM helper - placeholder preserving signature
    # ------------------------------------------------------------------
    def create_llm(self, model: str, project_name: Optional[str] = None) -> ChatOpenAI:
        base_kwargs: Dict[str, Any] = {
            "model": model,
            "temperature": 1 if model in {"o1", "o3"} else 0.2,
            "timeout": 300,
            "max_retries": 3,
        }
        if model in {"o1", "o3"}:
            base_kwargs["reasoning_effort"] = "high"
        return ChatOpenAI(**base_kwargs)
