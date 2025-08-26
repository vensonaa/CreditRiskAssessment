from typing import Dict, Any, List
from app.agents.generator_agent import GeneratorAgent
from app.agents.reflection_agent import ReflectionAgent
from app.agents.refiner_agent import RefinerAgent
from app.models.schemas import WorkflowResponse, AgentResponse
from app.core.config import settings
from datetime import datetime
import uuid
import asyncio

class SimpleReflectionWorkflow:
    def __init__(self):
        self.generator_agent = GeneratorAgent()
        self.reflection_agent = ReflectionAgent()
        self.refiner_agent = RefinerAgent()
    
    def _serialize_workflow_response(self, response: WorkflowResponse) -> Dict[str, Any]:
        """Convert WorkflowResponse to a JSON-serializable dictionary"""
        try:
            # Use model_dump with json mode to handle datetime serialization
            return response.model_dump(mode='json')
        except Exception as e:
            print(f"Error serializing WorkflowResponse: {str(e)}")
            # Fallback: manually convert to dict and serialize datetimes
            response_dict = response.dict()
            
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: serialize_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [serialize_datetime(item) for item in obj]
                else:
                    return obj
            
            return serialize_datetime(response_dict)
    
    async def execute(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete reflection workflow and return JSON-serializable dict"""
        start_time = datetime.now()
        request_id = str(uuid.uuid4())
        agent_responses = []
        # Align thresholds with configuration
        quality_threshold = settings.quality_threshold
        # A softer threshold for early stopping if score is stable but slightly below target
        stable_threshold = max(0.0, quality_threshold - 0.2)
        
        try:
            # Step 1: Generator Agent
            generator_result = await self.generator_agent.process(request_data)
            print(f"Generator result status: {generator_result.get('status')}")
            print(f"Generator result report type: {type(generator_result.get('report'))}")
            if generator_result.get('status') == 'error':
                print(f"Generator error: {generator_result.get('error')}")
            if generator_result.get('report'):
                print(f"Generator result report sections type: {type(generator_result.get('report').get('sections', []))}")
                if generator_result.get('report').get('sections'):
                    print(f"First section type: {type(generator_result.get('report').get('sections')[0])}")
            # Convert datetime objects in metadata to strings
            metadata = generator_result.copy()
            def convert_datetime_in_dict(d):
                if isinstance(d, dict):
                    for key, value in d.items():
                        if isinstance(value, datetime):
                            d[key] = value.isoformat()
                        elif isinstance(value, dict):
                            convert_datetime_in_dict(value)
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    convert_datetime_in_dict(item)
                return d
            metadata = convert_datetime_in_dict(metadata)
            
            # Also handle any nested datetime objects in the metadata
            def deep_convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: deep_convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [deep_convert_datetime(item) for item in obj]
                else:
                    return obj
            
            metadata = deep_convert_datetime(metadata)
            
            agent_responses.append(AgentResponse(
                agent_type="generator",
                content=generator_result.get("content", ""),
                metadata=metadata,
                timestamp=datetime.now()
            ))
            
            if generator_result.get("status") != "success":
                response = WorkflowResponse(
                    request_id=request_id,
                    status="generator_error",
                    final_report=None,
                    iterations=0,
                    total_duration=(datetime.now() - start_time).total_seconds(),
                    agent_responses=agent_responses
                )
                return self._serialize_workflow_response(response)
            
            current_report = generator_result.get("report")
            # Ensure current_report is a dictionary
            if hasattr(current_report, 'dict'):
                current_report = current_report.dict()
                # Also convert sections to dictionaries
                if 'sections' in current_report:
                    current_report['sections'] = [section.dict() if hasattr(section, 'dict') else section for section in current_report['sections']]
            
            # Convert datetime objects in current_report
            if isinstance(current_report, dict):
                current_report = convert_datetime_in_dict(current_report)
            elif hasattr(current_report, 'model_dump'):
                # If it's a Pydantic model, convert to dict with datetime serialization
                current_report = current_report.model_dump(mode='json')
            elif hasattr(current_report, 'dict'):
                # Fallback to dict() method
                current_report = current_report.dict()
                current_report = convert_datetime_in_dict(current_report)
            iteration = 0
            max_iterations = settings.max_iterations
            
            # Reflection loop
            while iteration < max_iterations:
                iteration += 1
                print(f"Starting iteration {iteration}")
                
                # Reflection Agent
                reflection_result = await self.reflection_agent.process({
                    "report": current_report,
                    "original_request": request_data
                })
                
                # Convert datetime objects in metadata to strings
                reflection_metadata = reflection_result.copy()
                reflection_metadata = convert_datetime_in_dict(reflection_metadata)
                reflection_metadata = deep_convert_datetime(reflection_metadata)
                
                agent_responses.append(AgentResponse(
                    agent_type="reflection",
                    content=reflection_result.get("content", ""),
                    metadata=reflection_metadata,
                    timestamp=datetime.now()
                ))
                
                if reflection_result.get("status") != "success":
                    # Ensure final_report is a dictionary
                    final_report = current_report
                    if hasattr(final_report, 'model_dump'):
                        final_report = final_report.model_dump(mode='json')
                    elif hasattr(final_report, 'dict'):
                        final_report = final_report.dict()
                        final_report = convert_datetime_in_dict(final_report)
                    
                    response = WorkflowResponse(
                        request_id=request_id,
                        status="reflection_error",
                        final_report=final_report,
                        iterations=iteration,
                        total_duration=(datetime.now() - start_time).total_seconds(),
                        agent_responses=agent_responses
                    )
                    return self._serialize_workflow_response(response)
                
                evaluation = reflection_result.get("evaluation", {})
                quality_score = evaluation.get("overall_score", 0.0)
                
                print(f"Iteration {iteration} - Quality Score: {quality_score}")
                
                # Check if quality is acceptable
                if quality_score >= quality_threshold:
                    # Ensure final_report is a dictionary
                    final_report = current_report
                    if hasattr(final_report, 'model_dump'):
                        final_report = final_report.model_dump(mode='json')
                    elif hasattr(final_report, 'dict'):
                        final_report = final_report.dict()
                        final_report = convert_datetime_in_dict(final_report)
                    
                    response = WorkflowResponse(
                        request_id=request_id,
                        status="completed",
                        final_report=final_report,
                        iterations=iteration,
                        total_duration=(datetime.now() - start_time).total_seconds(),
                        agent_responses=agent_responses
                    )
                    return self._serialize_workflow_response(response)
                
                # Exit if we've reached max iterations or if score is stable and reasonable
                if iteration >= max_iterations or (iteration >= 3 and quality_score >= stable_threshold):
                    print(f"Workflow completed: {'Max iterations reached' if iteration >= max_iterations else 'Quality score stable and acceptable'}")
                    final_report = current_report
                    if hasattr(final_report, 'model_dump'):
                        final_report = final_report.model_dump(mode='json')
                    elif hasattr(final_report, 'dict'):
                        final_report = final_report.dict()
                        final_report = convert_datetime_in_dict(final_report)
                    
                    response = WorkflowResponse(
                        request_id=request_id,
                        status="completed" if quality_score >= stable_threshold else "max_iterations_reached",
                        final_report=final_report,
                        iterations=iteration,
                        total_duration=(datetime.now() - start_time).total_seconds(),
                        agent_responses=agent_responses
                    )
                    return self._serialize_workflow_response(response)
                
                # Refiner Agent
                refiner_result = await self.refiner_agent.process({
                    "report": current_report,
                    "evaluation": evaluation,
                    "original_request": request_data
                })
                
                # Convert datetime objects in metadata to strings
                refiner_metadata = refiner_result.copy()
                refiner_metadata = convert_datetime_in_dict(refiner_metadata)
                refiner_metadata = deep_convert_datetime(refiner_metadata)
                
                agent_responses.append(AgentResponse(
                    agent_type="refiner",
                    content=refiner_result.get("content", ""),
                    metadata=refiner_metadata,
                    timestamp=datetime.now()
                ))
                
                if refiner_result.get("status") != "success":
                    # Ensure final_report is a dictionary
                    final_report = current_report
                    if hasattr(final_report, 'model_dump'):
                        final_report = final_report.model_dump(mode='json')
                    elif hasattr(final_report, 'dict'):
                        final_report = final_report.dict()
                        final_report = convert_datetime_in_dict(final_report)
                    
                    response = WorkflowResponse(
                        request_id=request_id,
                        status="refiner_error",
                        final_report=final_report,
                        iterations=iteration,
                        total_duration=(datetime.now() - start_time).total_seconds(),
                        agent_responses=agent_responses
                    )
                    return self._serialize_workflow_response(response)
                
                # Update current report with refined version
                refined_report = refiner_result.get("refined_report", current_report)
                # Ensure refined_report is a dictionary
                if hasattr(refined_report, 'dict'):
                    refined_report = refined_report.dict()
                    # Also convert sections to dictionaries
                    if 'sections' in refined_report:
                        refined_report['sections'] = [section.dict() if hasattr(section, 'dict') else section for section in refined_report['sections']]
                
                # Convert datetime objects in refined_report
                if isinstance(refined_report, dict):
                    refined_report = convert_datetime_in_dict(refined_report)
                current_report = refined_report
            
            # Max iterations reached
            # Ensure final_report is a dictionary
            final_report = current_report
            if hasattr(final_report, 'model_dump'):
                final_report = final_report.model_dump(mode='json')
            elif hasattr(final_report, 'dict'):
                final_report = final_report.dict()
                final_report = convert_datetime_in_dict(final_report)
            
            response = WorkflowResponse(
                request_id=request_id,
                status="max_iterations_reached",
                final_report=final_report,
                iterations=iteration,
                total_duration=(datetime.now() - start_time).total_seconds(),
                agent_responses=agent_responses
            )
            return self._serialize_workflow_response(response)
            
        except Exception as e:
            response = WorkflowResponse(
                request_id=request_id,
                status="workflow_error",
                final_report=None,
                iterations=0,
                total_duration=(datetime.now() - start_time).total_seconds(),
                agent_responses=agent_responses + [AgentResponse(
                    agent_type="workflow",
                    content=f"Workflow execution error: {str(e)}",
                    metadata={"error": str(e)},
                    timestamp=datetime.now()
                )]
            )
            return self._serialize_workflow_response(response)
