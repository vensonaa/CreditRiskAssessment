from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from datetime import datetime
import json

Base = declarative_base()

class CreditRiskReport(Base):
    __tablename__ = "credit_risk_reports"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    business_type = Column(String, nullable=False)
    annual_revenue = Column(Float, nullable=False)
    requested_amount = Column(Float, nullable=False)
    purpose = Column(String, nullable=False)
    report_data = Column(JSON, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(String, primary_key=True)
    request_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    iterations = Column(Integer, default=0)
    total_duration = Column(Float, default=0.0)
    agent_responses = Column(JSON, nullable=False)
    final_report_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)

class DataService:
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def _serialize_agent_responses(self, agent_responses):
        """Convert agent responses to JSON-serializable format"""
        def serialize_value(value):
            if isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, dict):
                return {k: serialize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [serialize_value(item) for item in value]
            else:
                return value
        
        serialized = []
        for response in agent_responses:
            if isinstance(response, dict):
                serialized_response = serialize_value(response)
                serialized.append(serialized_response)
            else:
                # Handle Pydantic models - convert to dict first, then serialize
                try:
                    if hasattr(response, 'dict'):
                        response_dict = response.dict()
                        serialized_response = serialize_value(response_dict)
                        serialized.append(serialized_response)
                    else:
                        serialized.append(response)
                except Exception as e:
                    # Fallback: convert to string if serialization fails
                    serialized.append(str(response))
        return serialized
    
    async def save_credit_risk_report(self, report_data: Dict[str, Any]) -> str:
        """Save credit risk report to database"""
        session = self.get_session()
        try:
            report = CreditRiskReport(
                id=report_data["report_id"],
                customer_id=report_data["customer_id"],
                customer_name=report_data.get("customer_name", ""),
                business_type=report_data.get("business_type", ""),
                annual_revenue=report_data.get("annual_revenue", 0.0),
                requested_amount=report_data.get("requested_amount", 0.0),
                purpose=report_data.get("purpose", ""),
                report_data=json.dumps(report_data),
                status="completed"
            )
            
            session.add(report)
            session.commit()
            return report.id
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    async def save_workflow_execution(self, workflow_data: Dict[str, Any]) -> str:
        """Save workflow execution to database"""
        session = self.get_session()
        try:
            execution = WorkflowExecution(
                id=workflow_data["request_id"],
                request_id=workflow_data["request_id"],
                status=workflow_data["status"],
                iterations=workflow_data.get("iterations", 0),
                total_duration=workflow_data.get("total_duration", 0.0),
                agent_responses=json.dumps(self._serialize_agent_responses(workflow_data.get("agent_responses", []))),
                final_report_id=workflow_data.get("final_report_id"),
                completed_at=datetime.now() if workflow_data["status"] in ["completed", "error"] else None
            )
            
            session.add(execution)
            session.commit()
            return execution.id
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    async def get_credit_risk_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve credit risk report by ID"""
        session = self.get_session()
        try:
            report = session.query(CreditRiskReport).filter(CreditRiskReport.id == report_id).first()
            return json.loads(report.report_data) if report else None
        finally:
            session.close()
    
    async def delete_credit_risk_report(self, report_id: str) -> bool:
        """Delete credit risk report by ID"""
        session = self.get_session()
        try:
            report = session.query(CreditRiskReport).filter(CreditRiskReport.id == report_id).first()
            
            if not report:
                return False
            
            # Also update any workflow executions that reference this report
            workflows = session.query(WorkflowExecution).filter(
                WorkflowExecution.final_report_id == report_id
            ).all()
            
            for workflow in workflows:
                workflow.final_report_id = None
            
            # Delete the report
            session.delete(report)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error deleting report {report_id}: {str(e)}")
            return False
        finally:
            session.close()
    
    async def get_workflow_execution(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow execution by request ID"""
        session = self.get_session()
        try:
            execution = session.query(WorkflowExecution).filter(WorkflowExecution.request_id == request_id).first()
            if execution:
                return {
                    "request_id": execution.request_id,
                    "status": execution.status,
                    "iterations": execution.iterations,
                    "total_duration": execution.total_duration,
                    "agent_responses": json.loads(execution.agent_responses) if execution.agent_responses else [],
                    "final_report_id": execution.final_report_id,
                    "created_at": execution.created_at.isoformat() if execution.created_at else None,
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
                }
            return None
        finally:
            session.close()
    
    async def get_reports_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all reports for a specific customer"""
        session = self.get_session()
        try:
            reports = session.query(CreditRiskReport).filter(
                CreditRiskReport.customer_id == customer_id
            ).order_by(CreditRiskReport.created_at.desc()).all()
            
            return [json.loads(report.report_data) for report in reports]
        finally:
            session.close()
    
    async def get_all_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all credit risk reports"""
        session = self.get_session()
        try:
            reports = session.query(CreditRiskReport).order_by(
                CreditRiskReport.created_at.desc()
            ).limit(limit).all()
            
            return [{
                "report_id": report.id,
                "customer_id": report.customer_id,
                "customer_name": report.customer_name,
                "business_type": report.business_type,
                "annual_revenue": report.annual_revenue,
                "requested_amount": report.requested_amount,
                "purpose": report.purpose,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "report_data": json.loads(report.report_data) if report.report_data else {}
            } for report in reports]
        finally:
            session.close()
    
    async def get_recent_workflows(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow executions"""
        session = self.get_session()
        try:
            executions = session.query(WorkflowExecution).order_by(
                WorkflowExecution.created_at.desc()
            ).limit(limit).all()
            
            return [{
                "request_id": execution.request_id,
                "status": execution.status,
                "iterations": execution.iterations,
                "total_duration": execution.total_duration,
                "created_at": execution.created_at.isoformat() if execution.created_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
            } for execution in executions]
        finally:
            session.close()
    
    async def update_workflow_status(self, request_id: str, status: str, **kwargs) -> bool:
        """Update workflow execution status"""
        session = self.get_session()
        try:
            execution = session.query(WorkflowExecution).filter(
                WorkflowExecution.request_id == request_id
            ).first()
            
            if execution:
                execution.status = status
                if "iterations" in kwargs:
                    execution.iterations = kwargs["iterations"]
                if "total_duration" in kwargs:
                    execution.total_duration = kwargs["total_duration"]
                if "agent_responses" in kwargs:
                    execution.agent_responses = kwargs["agent_responses"]
                if "final_report_id" in kwargs:
                    execution.final_report_id = kwargs["final_report_id"]
                if status in ["completed", "error"]:
                    execution.completed_at = datetime.now()
                
                session.commit()
                return True
            return False
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        session = self.get_session()
        try:
            print("Starting statistics calculation...")
            
            # Get basic counts
            total_reports = session.query(CreditRiskReport).count()
            print(f"Total reports: {total_reports}")
            
            total_workflows = session.query(WorkflowExecution).count()
            print(f"Total workflows: {total_workflows}")
            
            # Get completed workflows count
            completed_workflows = session.query(WorkflowExecution).filter(
                WorkflowExecution.status.in_(["completed", "completed_with_fallback"])
            ).count()
            print(f"Completed workflows: {completed_workflows}")
            
            # Get error workflows count
            error_workflows = session.query(WorkflowExecution).filter(
                WorkflowExecution.status.in_(["workflow_error", "generator_error", "reflection_error", "refiner_error"])
            ).count()
            print(f"Error workflows: {error_workflows}")
            
            # Calculate averages manually to avoid SQLAlchemy issues
            print("Fetching all workflows for average calculation...")
            all_workflows = session.query(WorkflowExecution).all()
            print(f"Fetched {len(all_workflows)} workflows")
            
            total_iterations = sum(w.iterations for w in all_workflows)
            total_duration = sum(w.total_duration for w in all_workflows)
            
            avg_iterations = total_iterations / len(all_workflows) if all_workflows else 0.0
            avg_duration = total_duration / len(all_workflows) if all_workflows else 0.0
            
            success_rate = (completed_workflows / total_workflows * 100) if total_workflows > 0 else 0
            
            result = {
                "total_reports": total_reports,
                "total_workflows": total_workflows,
                "completed_workflows": completed_workflows,
                "error_workflows": error_workflows,
                "success_rate": round(success_rate, 2),
                "average_iterations": round(avg_iterations, 2),
                "average_duration_seconds": round(avg_duration, 2)
            }
            
            print(f"Statistics calculation completed: {result}")
            return result
            
        except Exception as e:
            print(f"Error in get_statistics: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return default values if there's an error
            return {
                "total_reports": 0,
                "total_workflows": 0,
                "completed_workflows": 0,
                "error_workflows": 0,
                "success_rate": 0.0,
                "average_iterations": 0.0,
                "average_duration_seconds": 0.0
            }
        finally:
            session.close()
