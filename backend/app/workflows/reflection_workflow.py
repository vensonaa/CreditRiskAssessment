from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.generator_agent import GeneratorAgent
from app.agents.reflection_agent import ReflectionAgent
from app.agents.refiner_agent import RefinerAgent
from app.models.schemas import WorkflowState, WorkflowResponse, AgentResponse
from app.core.config import settings
from datetime import datetime
import uuid

# Define the state structure for the workflow
class WorkflowState(TypedDict):
    request_id: str
    current_agent: str
    iteration: int
    original_request: Dict[str, Any]
    report: Dict[str, Any]
    evaluation: Dict[str, Any]
    refined_report: Dict[str, Any]
    status: str
    agent_responses: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class ReflectionWorkflow:
    def __init__(self):
        self.generator_agent = GeneratorAgent()
        self.reflection_agent = ReflectionAgent()
        self.refiner_agent = RefinerAgent()
        self.memory = MemorySaver()
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow with Generator → Reflection → Refiner loop"""
        
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each agent
        workflow.add_node("generator", self._generator_node)
        workflow.add_node("reflection", self._reflection_node)
        workflow.add_node("refiner", self._refiner_node)
        
        # Define the workflow edges
        workflow.set_entry_point("generator")
        
        # Generator → Reflection
        workflow.add_edge("generator", "reflection")
        
        # Reflection → Refiner (if quality threshold not met)
        workflow.add_conditional_edges(
            "reflection",
            self._should_refine,
            {
                "refine": "refiner",
                "complete": END
            }
        )
        
        # Refiner → Reflection (continue loop)
        workflow.add_edge("refiner", "reflection")
        
        # Compile the workflow
        return workflow.compile(checkpointer=self.memory)
    
    async def _generator_node(self, state: WorkflowState) -> WorkflowState:
        """Generator agent node - creates initial credit risk assessment report"""
        try:
            # Update state
            state["current_agent"] = "generator"
            state["updated_at"] = datetime.now()
            
            # Process with generator agent
            result = await self.generator_agent.process(state["original_request"])
            
            # Add agent response to history
            agent_response = {
                "agent_type": "generator",
                "content": result.get("content", ""),
                "metadata": {
                    "task_type": result.get("task_type"),
                    "execution_plan": result.get("execution_plan"),
                    "status": result.get("status")
                },
                "timestamp": datetime.now()
            }
            state["agent_responses"].append(agent_response)
            
            # Store the generated report
            if result.get("status") == "success" and result.get("report"):
                state["report"] = result["report"]
                state["status"] = "report_generated"
            else:
                state["status"] = "generator_error"
            
            return state
            
        except Exception as e:
            state["status"] = "generator_error"
            state["agent_responses"].append({
                "agent_type": "generator",
                "content": f"Error: {str(e)}",
                "metadata": {"error": str(e)},
                "timestamp": datetime.now()
            })
            return state
    
    async def _reflection_node(self, state: WorkflowState) -> WorkflowState:
        """Reflection agent node - evaluates report quality"""
        try:
            # Update state
            state["current_agent"] = "reflection"
            state["updated_at"] = datetime.now()
            
            # Prepare input for reflection agent
            reflection_input = {
                "report": state.get("report") or state.get("refined_report")
            }
            
            # Process with reflection agent
            result = await self.reflection_agent.process(reflection_input)
            
            # Add agent response to history
            agent_response = {
                "agent_type": "reflection",
                "content": result.get("content", ""),
                "metadata": {
                    "evaluation": result.get("evaluation"),
                    "meets_threshold": result.get("meets_threshold"),
                    "status": result.get("status")
                },
                "timestamp": datetime.now()
            }
            state["agent_responses"].append(agent_response)
            
            # Store the evaluation
            if result.get("status") == "success" and result.get("evaluation"):
                state["evaluation"] = result["evaluation"]
                state["status"] = "evaluation_completed"
            else:
                state["status"] = "reflection_error"
            
            return state
            
        except Exception as e:
            state["status"] = "reflection_error"
            state["agent_responses"].append({
                "agent_type": "reflection",
                "content": f"Error: {str(e)}",
                "metadata": {"error": str(e)},
                "timestamp": datetime.now()
            })
            return state
    
    async def _refiner_node(self, state: WorkflowState) -> WorkflowState:
        """Refiner agent node - improves report based on critique"""
        try:
            # Update state
            state["current_agent"] = "refiner"
            state["iteration"] += 1
            state["updated_at"] = datetime.now()
            
            # Check iteration limit
            if state["iteration"] > settings.max_iterations:
                state["status"] = "max_iterations_reached"
                return state
            
            # Prepare input for refiner agent
            refiner_input = {
                "report": state.get("report") or state.get("refined_report"),
                "evaluation": state.get("evaluation"),
                "original_request": state.get("original_request")
            }
            
            # Process with refiner agent
            result = await self.refiner_agent.process(refiner_input)
            
            # Add agent response to history
            agent_response = {
                "agent_type": "refiner",
                "content": result.get("content", ""),
                "metadata": {
                    "correction_plan": result.get("correction_plan"),
                    "iteration": state["iteration"],
                    "status": result.get("status")
                },
                "timestamp": datetime.now()
            }
            state["agent_responses"].append(agent_response)
            
            # Store the refined report
            if result.get("status") == "success" and result.get("refined_report"):
                state["refined_report"] = result["refined_report"]
                state["status"] = "report_refined"
            else:
                state["status"] = "refiner_error"
            
            return state
            
        except Exception as e:
            state["status"] = "refiner_error"
            state["agent_responses"].append({
                "agent_type": "refiner",
                "content": f"Error: {str(e)}",
                "metadata": {"error": str(e)},
                "timestamp": datetime.now()
            })
            return state
    
    def _should_refine(self, state: WorkflowState) -> str:
        """Determine if the workflow should continue to refinement or complete"""
        evaluation = state.get("evaluation")
        
        if not evaluation:
            return "refine"  # Continue to refiner if no evaluation
        
        # Check if quality threshold is met
        meets_threshold = evaluation.get("meets_threshold", False)
        
        if meets_threshold:
            return "complete"  # Exit workflow
        else:
            return "refine"  # Continue to refiner
    
    async def execute(self, request_data: Dict[str, Any]) -> WorkflowResponse:
        """Execute the complete reflection workflow"""
        start_time = datetime.now()
        
        # Initialize workflow state
        initial_state = {
            "request_id": str(uuid.uuid4()),
            "current_agent": "",
            "iteration": 0,
            "original_request": request_data,
            "report": {},
            "evaluation": {},
            "refined_report": {},
            "status": "started",
            "agent_responses": [],
            "created_at": start_time,
            "updated_at": start_time
        }
        
        try:
            # Execute the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Calculate total duration
            total_duration = (datetime.now() - start_time).total_seconds()
            
            # Determine final report
            final_report = final_state.get("refined_report") or final_state.get("report")
            
            # Create workflow response
            response = WorkflowResponse(
                request_id=final_state["request_id"],
                status=final_state["status"],
                final_report=final_report,
                iterations=final_state["iteration"],
                total_duration=total_duration,
                agent_responses=final_state["agent_responses"]
            )
            
            return response
            
        except Exception as e:
            # Handle workflow execution errors
            error_response = WorkflowResponse(
                request_id=initial_state["request_id"],
                status="workflow_error",
                final_report=None,
                iterations=0,
                total_duration=(datetime.now() - start_time).total_seconds(),
                agent_responses=[{
                    "agent_type": "workflow",
                    "content": f"Workflow execution error: {str(e)}",
                    "metadata": {"error": str(e)},
                    "timestamp": datetime.now()
                }]
            )
            return error_response
    
    async def get_workflow_status(self, request_id: str) -> Dict[str, Any]:
        """Get the status of a specific workflow execution"""
        try:
            # Retrieve workflow state from memory
            state = await self.memory.get({"request_id": request_id})
            return state if state else {"error": "Workflow not found"}
        except Exception as e:
            return {"error": f"Failed to retrieve workflow status: {str(e)}"}
