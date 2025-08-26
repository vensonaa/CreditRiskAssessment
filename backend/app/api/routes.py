from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.models.schemas import CreditRiskRequest, WorkflowResponse
from app.workflows.simple_workflow import SimpleReflectionWorkflow
from app.services.data_service import DataService
from typing import Dict, Any, List
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
workflow = SimpleReflectionWorkflow()
data_service = DataService()

@router.post("/credit-risk-assessment")
async def create_credit_risk_assessment(request: CreditRiskRequest):
    """Create a credit risk assessment using the reflection workflow"""
    try:
        # Execute the workflow
        workflow = SimpleReflectionWorkflow()
        response_data = await workflow.execute(request.model_dump())
        
        # The workflow now returns a dictionary, so we don't need to convert it
        # IMPORTANT: Save report first (if it exists), then workflow execution to avoid race conditions
        report_id = None
        if response_data.get("final_report"):
            # Use the report's own ID, not the request_id
            report_id = response_data["final_report"].get("report_id") or response_data["request_id"]
            await data_service.save_credit_risk_report({
                "report_id": report_id,
                "customer_id": request.customer_id,
                "customer_name": request.customer_name,
                "business_type": request.business_type,
                "annual_revenue": request.annual_revenue,
                "requested_amount": request.requested_amount,
                "purpose": request.purpose,
                **response_data["final_report"]
            })
        
        # Save workflow execution AFTER report is persisted (so final_report_id implies report exists)
        await data_service.save_workflow_execution({
            "request_id": response_data["request_id"],
            "status": response_data["status"],
            "iterations": response_data["iterations"],
            "total_duration": response_data["total_duration"],
            "agent_responses": response_data["agent_responses"],
            "final_report_id": report_id if response_data.get("final_report") else None
        })
        
        return response_data
        
    except Exception as e:
        logger.exception("Error in create_credit_risk_assessment")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/{request_id}", response_model=Dict[str, Any])
async def get_workflow_status(request_id: str):
    """
    Get the status and details of a specific workflow execution
    """
    try:
        # Get workflow status from database
        workflow_data = await data_service.get_workflow_execution(request_id)
        
        if not workflow_data:
            # Fallback: if a report exists with this ID, synthesize a minimal completed workflow response
            try:
                report = await data_service.get_credit_risk_report(request_id)
            except Exception:
                report = None
            
            if report:
                logger.debug("Workflow not found; returning synthesized completed workflow for existing report %s", request_id)
                return {
                    "request_id": request_id,
                    "status": "completed",
                    "iterations": 0,
                    "total_duration": 0.0,
                    "agent_responses": [],
                    "final_report_id": request_id,
                    "created_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                }
            
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return workflow_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve workflow status: {str(e)}")

@router.get("/reports/{report_id}", response_model=Dict[str, Any])
async def get_credit_risk_report(report_id: str):
    """
    Get a specific credit risk assessment report
    """
    try:
        report = await data_service.get_credit_risk_report(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report: {str(e)}")

@router.delete("/reports/{report_id}")
async def delete_credit_risk_report(report_id: str):
    """
    Delete a specific credit risk assessment report
    """
    try:
        # First check if the report exists
        report = await data_service.get_credit_risk_report(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Delete the report
        success = await data_service.delete_credit_risk_report(report_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete report")
        
        return {
            "message": "Report deleted successfully",
            "report_id": report_id,
            "deleted_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

@router.get("/reports/customer/{customer_id}", response_model=List[Dict[str, Any]])
async def get_customer_reports(customer_id: str):
    """
    Get all credit risk assessment reports for a specific customer
    """
    try:
        reports = await data_service.get_reports_by_customer(customer_id)
        return reports
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve customer reports: {str(e)}")

@router.get("/reports", response_model=List[Dict[str, Any]])
async def get_all_reports(limit: int = 50):
    """
    Get all credit risk assessment reports
    """
    try:
        reports = await data_service.get_all_reports(limit)
        return reports
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reports: {str(e)}")

@router.get("/workflows/recent", response_model=List[Dict[str, Any]])
async def get_recent_workflows(limit: int = 10):
    """
    Get recent workflow executions
    """
    try:
        workflows = await data_service.get_recent_workflows(limit)
        return workflows
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve recent workflows: {str(e)}")

@router.get("/statistics", response_model=Dict[str, Any])
async def get_system_statistics():
    """
    Get system statistics and metrics
    """
    try:
        # Calculate real statistics from database
        total_reports = await data_service.get_total_reports()
        total_workflows = await data_service.get_total_workflows()
        completed_workflows = await data_service.get_completed_workflows()
        error_workflows = await data_service.get_error_workflows()
        avg_iterations = await data_service.get_average_iterations()
        avg_duration = await data_service.get_average_duration()
        
        # Calculate success rate
        success_rate = 0.0
        if total_workflows > 0:
            success_rate = (completed_workflows / total_workflows) * 100
        
        result = {
            "total_reports": total_reports,
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "error_workflows": error_workflows,
            "success_rate": round(success_rate, 1),
            "average_iterations": round(avg_iterations, 1),
            "average_duration_seconds": round(avg_duration, 2)
        }
        return result
        
    except Exception as e:
        logger.exception("Error in get_system_statistics")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@router.get("/submitted-applications", response_model=List[Dict[str, Any]])
async def get_submitted_applications():
    """
    Get all loan applications with 'submitted' status
    """
    try:
        # Create a fresh instance to ensure latest data
        from app.services.loan_application_service import LoanApplicationService
        loan_service = LoanApplicationService()
        submitted_apps = await loan_service.get_submitted_applications()
        return submitted_apps
        
    except Exception as e:
        print(f"Error in get_submitted_applications: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to retrieve submitted applications: {str(e)}")

@router.get("/application-status/{customer_id}", response_model=Dict[str, Any])
async def get_application_status(customer_id: str):
    """
    Get application status for a specific customer
    """
    try:
        from app.services.mcp_service import MCPService
        mcp_service = MCPService()
        status = await mcp_service.get_application_status(customer_id)
        return {
            "customer_id": customer_id,
            "application_status": status,
            "is_submitted": status.lower() == "submitted"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve application status: {str(e)}")

@router.post("/workflow/{request_id}/cancel")
async def cancel_workflow(request_id: str):
    """
    Cancel a running workflow execution
    """
    try:
        # Update workflow status to cancelled
        success = await data_service.update_workflow_status(request_id, "cancelled")
        
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {"message": "Workflow cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel workflow: {str(e)}")

@router.delete("/workflow/{request_id}")
async def delete_workflow(request_id: str):
    """
    Delete a workflow execution and its associated report
    """
    try:
        success = await data_service.delete_workflow_execution(request_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "message": "Workflow and associated report deleted successfully",
            "request_id": request_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "credit-risk-assessment-api",
        "timestamp": "2024-01-01T00:00:00Z"
    }
