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
        return """You are a Generator Agent specialized in credit risk assessment. Produce executive-ready, user-friendly content that is:

STYLE GUIDELINES
- Concise, clear, and free of repetition
- Actionable and decision-oriented for credit committees
- Skimmable: use short paragraphs, bullets, and ordered lists where helpful
- Quantify statements with concrete figures where possible
- Avoid generic filler text and excessive hedging

REQUIRED SECTIONS (when generating a full report)
- Executive Summary
- Customer Profile Analysis
- Financial Analysis
- Credit History Assessment
- Risk Factors Analysis
- Industry and Market Analysis
- Collateral Assessment (if applicable)
- Risk Rating and Recommendations

OUTPUT RULES
- Start each section with a one-sentence takeaway
- Use compact bullet points for details (no more than 5 per list)
- Avoid repeating the same facts across sections
- Prefer simple language over jargon
- Do not include boilerplate like "this report provides"; focus on the substance
"""

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
        Write an executive-ready summary for a credit committee.

        Context
        - Customer: {input_data['customer_name']}
        - Business type: {input_data['business_type']}
        - Annual revenue: ${input_data['annual_revenue']:,.2f}
        - Requested amount: ${input_data['requested_amount']:,.2f}
        - Purpose: {input_data['purpose']}

        Output format (strict):
        1) One-sentence takeaway capturing the overall risk and outlook.
        2) Key metrics (3-5 bullets): revenue, leverage/coverage if applicable, credit score or history signal, cash flow capacity vs request.
        3) Strengths (2-4 bullets) avoiding generic statements; be specific.
        4) Risks/Mitigants (2-4 bullets) with crisp, non-redundant phrasing.
        5) Preliminary decision guidance (1-2 sentences) referencing risk rating and any conditions (e.g., covenants, collateral, monitoring).

        Rules: avoid boilerplate and repetition; keep it concise and skimmable.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_customer_profile(self, input_data: Dict[str, Any]) -> str:
        """Generate customer profile analysis"""
        prompt = f"""
        Customer Profile Analysis (concise, skimmable):
        - Customer: {input_data['customer_name']}
        - Business type: {input_data['business_type']}
        - Annual revenue: ${input_data['annual_revenue']:,.2f}
        - Credit history: {input_data['credit_history_years']} years

        Provide:
        - Business model and revenue drivers (1-2 sentences)
        - Customer concentration or diversification (bullets)
        - Management/operating track record highlights (bullets)
        - Any notable recent changes/events (bullets)
        Avoid repeating executive summary content.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_financial_analysis(self, input_data: Dict[str, Any]) -> str:
        """Generate financial analysis section"""
        prompt = f"""
        Financial Analysis (crisp, quantitative when possible):
        - Annual revenue: ${input_data['annual_revenue']:,.2f}
        - Requested amount: ${input_data['requested_amount']:,.2f}

        Include:
        - Profitability and margin signal (1-2 sentences)
        - Cash flow coverage of requested debt (bullets with simple math if feasible)
        - Leverage/solvency indicators (bullets; keep to top 2-3)
        - Working capital/liquidity notes (bullets)
        Keep it short; avoid boilerplate.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_credit_history(self, input_data: Dict[str, Any]) -> str:
        """Generate credit history assessment"""
        prompt = f"""
        Credit History Assessment (brief):
        - Customer: {input_data['customer_name']}
        - Credit history: {input_data['credit_history_years']} years

        Provide:
        - Payment behavior summary (bullets)
        - Any delinquencies/defaults/derogatories (bullets or "none")
        - Trend/trajectory if known (1 sentence)
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_risk_factors(self, input_data: Dict[str, Any], additional_data: Dict[str, Any]) -> str:
        """Generate risk factors analysis"""
        prompt = f"""
        Risk Factors Analysis (prioritized, avoid redundancy):
        - Business type: {input_data['business_type']}
        - Requested amount: ${input_data['requested_amount']:,.2f}
        - Purpose: {input_data['purpose']}

        Provide 3-6 bullets covering the most material risks across industry, market, financial, and operational categories. Keep each bullet to a single, clear sentence. Where relevant, add one-word mitigants in parentheses.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_industry_analysis(self, input_data: Dict[str, Any], additional_data: Dict[str, Any]) -> str:
        """Generate industry and market analysis"""
        prompt = f"""
        Industry and Market Analysis (short, decision-useful):
        - Business type: {input_data['business_type']}

        Include:
        - Demand/trend snapshot (1-2 sentences)
        - Competitive intensity and positioning (bullets)
        - Regulatory/technology shifts if material (bullets)
        Keep it focused on what affects credit risk.
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        return await self.generate_response(messages)

    async def _generate_recommendations_section(self, input_data: Dict[str, Any], additional_data: Dict[str, Any]) -> str:
        """Generate recommendations section"""
        prompt = f"""
        Risk Rating and Recommendations (concise):
        - Customer: {input_data['customer_name']}
        - Requested amount: ${input_data['requested_amount']:,.2f}
        - Purpose: {input_data['purpose']}

        Output:
        - Risk rating with one-sentence rationale
        - 3-5 specific recommendations (covenants/conditions, collateral, monitoring cadence)
        - Closing note (one sentence) indicating next steps or approval conditions
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
