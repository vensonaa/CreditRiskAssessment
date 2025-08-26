from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent
from app.models.schemas import CreditRiskRequest, CreditRiskReport, ReportSection, TaskType
from app.services.mcp_service import MCPService
from app.services.data_service import DataService
import json
from datetime import datetime
import uuid

class GeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Generator")
        self.mcp_service = MCPService()
        self.data_service = DataService()
    
    def get_system_prompt(self) -> str:
        return """You are a Generator Agent specialized in credit risk assessment. Your responsibilities include:

1. Understanding user intent and creating execution plans
2. Querying and retrieving relevant data using available tools
3. Generating comprehensive credit risk assessment reports
4. Supporting credit risk assessment, tool inquiries, greetings, and unsupported task detection

When generating credit risk assessment reports, include the following sections:
- Executive Summary
- Customer Profile Analysis
- Financial Analysis
- Credit History Assessment
- Risk Factors Analysis
- Industry and Market Analysis
- Collateral Assessment (if applicable)
- Risk Rating and Recommendations
- Terms and Conditions

Be thorough, professional, and ensure all sections are well-structured and informative."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Determine task type
            task_type = self._determine_task_type(input_data)
            
            if task_type == TaskType.CREDIT_RISK_ASSESSMENT:
                return await self._generate_credit_risk_report(input_data)
            elif task_type == TaskType.TOOL_INQUIRY:
                return await self._handle_tool_inquiry(input_data)
            elif task_type == TaskType.GREETING:
                return await self._handle_greeting(input_data)
            else:
                return await self._handle_unsupported_task(input_data)
                
        except Exception as e:
            return {
                "agent_type": "Generator",
                "status": "error",
                "error": str(e),
                "content": f"Error processing request: {str(e)}"
            }

    def _determine_task_type(self, input_data: Dict[str, Any]) -> TaskType:
        """Determine the type of task from input data"""
        if "customer_id" in input_data and "customer_name" in input_data:
            return TaskType.CREDIT_RISK_ASSESSMENT
        elif "tool" in input_data.get("message", "").lower():
            return TaskType.TOOL_INQUIRY
        elif any(word in input_data.get("message", "").lower() for word in ["hello", "hi", "greetings"]):
            return TaskType.GREETING
        else:
            return TaskType.UNSUPPORTED

    async def _generate_credit_risk_report(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive credit risk assessment report"""
        
        # Check if the loan application is in submitted status
        customer_id = input_data["customer_id"]
        is_submitted = await self.mcp_service.is_application_submitted(customer_id)
        
        if not is_submitted:
            return {
                "agent_type": "Generator",
                "status": "error",
                "error": f"Loan application for customer {customer_id} is not in submitted status. Cannot proceed with credit risk assessment.",
                "content": f"Application status check failed: Application must be in 'submitted' status to proceed with credit risk assessment."
            }
        
        # Create execution plan
        execution_plan = await self._create_execution_plan(input_data)
        
        # Retrieve additional data using MCP tools
        additional_data = await self._retrieve_additional_data(input_data)
        
        # Generate report sections
        sections = await self._generate_report_sections(input_data, additional_data)
        
        # Create final report
        report = CreditRiskReport(
            report_id=str(uuid.uuid4()),
            customer_id=input_data["customer_id"],
            generated_at=datetime.now(),
            sections=sections,
            risk_level=self._determine_risk_level(sections),
            recommendations=self._generate_recommendations(sections)
        )
        
        # Convert report to dict and ensure sections are also converted
        report_dict = report.dict()
        report_dict['sections'] = [section.dict() if hasattr(section, 'dict') else section for section in report_dict['sections']]
        
        return {
            "agent_type": "Generator",
            "status": "success",
            "task_type": TaskType.CREDIT_RISK_ASSESSMENT,
            "report": report_dict,
            "execution_plan": execution_plan,
            "content": "Credit risk assessment report generated successfully"
        }

    async def _create_execution_plan(self, input_data: Dict[str, Any]) -> str:
        """Create execution plan for credit risk assessment"""
        plan_prompt = f"""
        Create a detailed execution plan for credit risk assessment for customer {input_data['customer_name']}.
        Business type: {input_data['business_type']}
        Annual revenue: ${input_data['annual_revenue']:,.2f}
        Credit history: {input_data['credit_history_years']} years
        Requested amount: ${input_data['requested_amount']:,.2f}
        Purpose: {input_data['purpose']}
        
        Plan should include:
        1. Data collection strategy
        2. Analysis approach
        3. Risk assessment methodology
        4. Report structure
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=plan_prompt)
        ]
        
        return await self.generate_response(messages)

    async def _retrieve_additional_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve additional data using MCP tools"""
        try:
            customer_id = input_data["customer_id"]
            
            # Use MCP service to get comprehensive data
            market_data = await self.mcp_service.get_market_data(input_data["business_type"])
            industry_data = await self.mcp_service.get_industry_analysis(input_data["business_type"])
            
            # Loan Application Information
            loan_app_info = await self.mcp_service.get_loan_application_info(customer_id)
            loan_amount = await self.mcp_service.get_loan_amount(customer_id)
            application_date = await self.mcp_service.get_application_date(customer_id)
            loan_purpose = await self.mcp_service.get_loan_purpose(customer_id)
            collateral_info = await self.mcp_service.get_collateral_info(customer_id)
            
            # Customer Information
            customer_info = await self.mcp_service.get_customer_info(customer_id)
            credit_history = await self.mcp_service.get_credit_history(customer_id)
            existing_loans = await self.mcp_service.get_existing_loans(customer_id)
            credit_score = await self.mcp_service.get_credit_score(customer_id)
            total_debt = await self.mcp_service.get_total_debt(customer_id)
            payment_history = await self.mcp_service.get_payment_history_summary(customer_id)
            
            # Compliance Information
            compliance_requirements = await self.mcp_service.get_compliance_requirements(
                input_data["business_type"], 
                input_data["requested_amount"]
            )
            compliance_status = await self.mcp_service.get_overall_compliance_status(
                input_data, 
                input_data["requested_amount"]
            )
            required_documents = await self.mcp_service.get_required_documents(
                input_data["business_type"], 
                input_data["requested_amount"]
            )
            
            return {
                "market_data": market_data,
                "industry_data": industry_data,
                "loan_application": {
                    "info": loan_app_info,
                    "amount": loan_amount,
                    "date": application_date,
                    "purpose": loan_purpose,
                    "collateral": collateral_info
                },
                "customer_information": {
                    "info": customer_info,
                    "credit_history": credit_history,
                    "existing_loans": existing_loans,
                    "credit_score": credit_score,
                    "total_debt": total_debt,
                    "payment_history": payment_history
                },
                "compliance": {
                    "requirements": compliance_requirements,
                    "status": compliance_status,
                    "required_documents": required_documents
                },
                "retrieved_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Failed to retrieve additional data: {str(e)}"}

    async def _generate_report_sections(self, input_data: Dict[str, Any], additional_data: Dict[str, Any]) -> List[ReportSection]:
        """Generate all report sections"""
        sections = []
        
        # Executive Summary
        executive_summary = await self._generate_executive_summary(input_data, additional_data)
        sections.append(ReportSection(title="Executive Summary", content=executive_summary))
        
        # Customer Profile Analysis
        customer_profile = await self._generate_customer_profile(input_data)
        sections.append(ReportSection(title="Customer Profile Analysis", content=customer_profile))
        
        # Financial Analysis
        financial_analysis = await self._generate_financial_analysis(input_data)
        sections.append(ReportSection(title="Financial Analysis", content=financial_analysis))
        
        # Credit History Assessment
        credit_history = await self._generate_credit_history(input_data)
        sections.append(ReportSection(title="Credit History Assessment", content=credit_history))
        
        # Risk Factors Analysis
        risk_factors = await self._generate_risk_factors(input_data, additional_data)
        sections.append(ReportSection(title="Risk Factors Analysis", content=risk_factors))
        
        # Industry and Market Analysis
        industry_analysis = await self._generate_industry_analysis(input_data, additional_data)
        sections.append(ReportSection(title="Industry and Market Analysis", content=industry_analysis))
        
        # Recommendations
        recommendations = await self._generate_recommendations_section(input_data, additional_data)
        sections.append(ReportSection(title="Recommendations", content=recommendations))
        
        return sections

    async def _generate_executive_summary(self, input_data: Dict[str, Any], additional_data: Dict[str, Any]) -> str:
        """Generate executive summary section"""
        prompt = f"""
        Generate an executive summary for a credit risk assessment report.
        
        Customer: {input_data['customer_name']}
        Business: {input_data['business_type']}
        Revenue: ${input_data['annual_revenue']:,.2f}
        Requested Amount: ${input_data['requested_amount']:,.2f}
        Purpose: {input_data['purpose']}
        
        Provide a concise overview of the assessment, key findings, and initial risk assessment.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_customer_profile(self, input_data: Dict[str, Any]) -> str:
        """Generate customer profile analysis"""
        prompt = f"""
        Analyze the customer profile for credit risk assessment.
        
        Customer: {input_data['customer_name']}
        Business Type: {input_data['business_type']}
        Annual Revenue: ${input_data['annual_revenue']:,.2f}
        Credit History: {input_data['credit_history_years']} years
        
        Provide detailed analysis of the customer's business profile, market position, and stability.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_financial_analysis(self, input_data: Dict[str, Any]) -> str:
        """Generate financial analysis section"""
        prompt = f"""
        Conduct financial analysis for credit risk assessment.
        
        Annual Revenue: ${input_data['annual_revenue']:,.2f}
        Requested Amount: ${input_data['requested_amount']:,.2f}
        Credit History: {input_data['credit_history_years']} years
        
        Analyze financial ratios, cash flow considerations, debt capacity, and financial stability.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_credit_history(self, input_data: Dict[str, Any]) -> str:
        """Generate credit history assessment"""
        prompt = f"""
        Assess credit history for risk evaluation.
        
        Credit History Years: {input_data['credit_history_years']}
        Customer: {input_data['customer_name']}
        
        Evaluate credit history length, payment patterns, and creditworthiness indicators.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_risk_factors(self, input_data: Dict[str, Any], additional_data: Dict[str, Any]) -> str:
        """Generate risk factors analysis"""
        prompt = f"""
        Identify and analyze risk factors for this credit application.
        
        Business Type: {input_data['business_type']}
        Requested Amount: ${input_data['requested_amount']:,.2f}
        Purpose: {input_data['purpose']}
        
        Consider industry risks, market risks, financial risks, and operational risks.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_industry_analysis(self, input_data: Dict[str, Any], additional_data: Dict[str, Any]) -> str:
        """Generate industry and market analysis"""
        prompt = f"""
        Provide industry and market analysis for credit risk assessment.
        
        Business Type: {input_data['business_type']}
        
        Analyze industry trends, market conditions, competitive landscape, and regulatory environment.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_recommendations_section(self, input_data: Dict[str, Any], additional_data: Dict[str, Any]) -> str:
        """Generate recommendations section"""
        prompt = f"""
        Provide comprehensive recommendations for this credit application.
        
        Customer: {input_data['customer_name']}
        Requested Amount: ${input_data['requested_amount']:,.2f}
        Purpose: {input_data['purpose']}
        
        Include credit terms, conditions, monitoring requirements, and risk mitigation strategies.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    def _determine_risk_level(self, sections: List[ReportSection]) -> str:
        """Determine overall risk level based on analysis"""
        # This would be a more sophisticated algorithm in practice
        return "Medium Risk"

    def _generate_recommendations(self, sections: List[ReportSection]) -> List[str]:
        """Generate list of recommendations"""
        return [
            "Regular financial monitoring required",
            "Quarterly review of credit terms",
            "Maintain adequate collateral coverage",
            "Monitor industry trends and market conditions"
        ]

    async def _handle_tool_inquiry(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool inquiry requests"""
        return {
            "agent_type": "Generator",
            "status": "success",
            "task_type": TaskType.TOOL_INQUIRY,
            "content": "Available tools: Market data retrieval, Industry analysis, Financial calculations, Credit history lookup"
        }

    async def _handle_greeting(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greeting messages"""
        return {
            "agent_type": "Generator",
            "status": "success",
            "task_type": TaskType.GREETING,
            "content": "Hello! I'm the Generator Agent. I can help you with credit risk assessments, data retrieval, and report generation. How can I assist you today?"
        }

    async def _handle_unsupported_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unsupported task types"""
        return {
            "agent_type": "Generator",
            "status": "error",
            "task_type": TaskType.UNSUPPORTED,
            "content": "I'm sorry, but I cannot process this type of request. I specialize in credit risk assessments, tool inquiries, and related financial analysis tasks."
        }
