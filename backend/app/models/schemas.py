from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class TaskType(str, Enum):
    CREDIT_RISK_ASSESSMENT = "credit_risk_assessment"
    TOOL_INQUIRY = "tool_inquiry"
    GREETING = "greeting"
    UNSUPPORTED = "unsupported"

class CreditRiskRequest(BaseModel):
    customer_id: str = Field(..., description="Unique customer identifier")
    customer_name: str = Field(..., description="Customer full name")
    business_type: str = Field(..., description="Type of business")
    annual_revenue: float = Field(..., description="Annual revenue in USD")
    credit_history_years: int = Field(..., description="Years of credit history")
    requested_amount: float = Field(..., description="Requested credit amount")
    purpose: str = Field(..., description="Purpose of credit")
    additional_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional customer data")

class ReportSection(BaseModel):
    title: str
    content: str
    score: Optional[float] = None

class CreditRiskReport(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    report_id: str
    customer_id: str
    generated_at: datetime
    sections: List[ReportSection]
    overall_score: Optional[float] = None
    risk_level: Optional[str] = None
    recommendations: List[str] = []

class QualityEvaluation(BaseModel):
    accuracy: float = Field(..., ge=0.0, le=1.0)
    completeness: float = Field(..., ge=0.0, le=1.0)
    structure: float = Field(..., ge=0.0, le=1.0)
    verbosity: float = Field(..., ge=0.0, le=1.0)
    relevance: float = Field(..., ge=0.0, le=1.0)
    tone: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    critique: List[str] = []
    meets_threshold: bool

class WorkflowState(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    request_id: str
    current_agent: str
    iteration: int
    report: Optional[CreditRiskReport] = None
    evaluation: Optional[QualityEvaluation] = None
    status: str = "in_progress"
    created_at: datetime
    updated_at: datetime

class AgentResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    agent_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

class WorkflowResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    request_id: str
    status: str
    final_report: Optional[CreditRiskReport] = None
    iterations: int
    total_duration: float
    agent_responses: List[AgentResponse]
