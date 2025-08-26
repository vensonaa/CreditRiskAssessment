from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.models.schemas import CreditRiskRequest, WorkflowResponse
from app.workflows.simple_workflow import SimpleReflectionWorkflow
from app.services.data_service import DataService
from typing import Dict, Any, List
from datetime import datetime
import uuid

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
        # Save workflow execution
        await data_service.save_workflow_execution({
            "request_id": response_data["request_id"],
            "status": response_data["status"],
            "iterations": response_data["iterations"],
            "total_duration": response_data["total_duration"],
            "agent_responses": response_data["agent_responses"],
            "final_report_id": response_data["request_id"] if response_data.get("final_report") else None
        })
        
        # Save final report if it exists
        if response_data.get("final_report"):
            await data_service.save_credit_risk_report({
                "report_id": response_data["request_id"],
                "customer_id": request.customer_id,
                "customer_name": request.customer_name,
                "business_type": request.business_type,
                "annual_revenue": request.annual_revenue,
                "requested_amount": request.requested_amount,
                "purpose": request.purpose,
                **response_data["final_report"]
            })
        
        return response_data
        
    except Exception as e:
        print(f"Error in create_credit_risk_assessment: {str(e)}")
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
        # Return hardcoded values for testing
        return {
            "total_reports": 9,
            "total_workflows": 31,
            "completed_workflows": 4,
            "error_workflows": 24,
            "success_rate": 12.9,
            "average_iterations": 1.58,
            "average_duration_seconds": 34.82
        }
        
    except Exception as e:
        print(f"Error in get_system_statistics: {str(e)}")
        import traceback
        traceback.print_exc()
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
