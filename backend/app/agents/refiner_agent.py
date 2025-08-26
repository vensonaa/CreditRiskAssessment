from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent
from app.models.schemas import CreditRiskReport, QualityEvaluation, ReportSection
from app.services.mcp_service import MCPService
from app.services.data_service import DataService
import json
from datetime import datetime
import uuid

class RefinerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Refiner")
        self.mcp_service = MCPService()
        self.data_service = DataService()
    
    def get_system_prompt(self) -> str:
        return """You are a Refiner Agent specialized in improving credit risk assessment reports based on critique. Your responsibilities include:

1. Accepting critique from the Reflection agent
2. Planning corrections based on feedback
3. Using tools to retrieve missing data when needed
4. Regenerating complete reports with improvements
5. Ensuring all identified issues are addressed

When refining reports, focus on:
- Addressing all critique points systematically
- Improving accuracy and completeness
- Enhancing structure and flow
- Adjusting verbosity to appropriate levels
- Ensuring relevance to credit risk assessment
- Maintaining professional tone throughout

Be thorough in addressing feedback and ensure the refined report meets quality standards."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            original_report = input_data.get("report")
            evaluation = input_data.get("evaluation")
            original_request = input_data.get("original_request")
            
            # Convert Pydantic models to dict if needed
            if hasattr(original_report, 'dict'):
                original_report = original_report.dict()
            if hasattr(evaluation, 'dict'):
                evaluation = evaluation.dict()
            
            if not original_report or not evaluation:
                return {
                    "agent_type": "Refiner",
                    "status": "error",
                    "error": "Missing original report or evaluation data"
                }
            
            # Plan corrections based on critique
            correction_plan = await self._plan_corrections(evaluation)
            
            # Retrieve additional data if needed
            additional_data = await self._retrieve_missing_data(original_request, evaluation)
            
            # Regenerate report with corrections
            refined_report = await self._regenerate_report_with_corrections(
                original_report, evaluation, correction_plan, additional_data, original_request
            )
            
            return {
                "agent_type": "Refiner",
                "status": "success",
                "refined_report": refined_report.dict(),
                "correction_plan": correction_plan,
                "content": f"Report refined successfully. Addressed {len(evaluation.get('critique', []))} critique points."
            }
            
        except Exception as e:
            return {
                "agent_type": "Refiner",
                "status": "error",
                "error": str(e),
                "content": f"Error refining report: {str(e)}"
            }

    async def _plan_corrections(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Plan corrections based on evaluation feedback"""
        plan = {
            "accuracy_improvements": [],
            "completeness_improvements": [],
            "structure_improvements": [],
            "verbosity_improvements": [],
            "relevance_improvements": [],
            "tone_improvements": [],
            "section_specific_improvements": []
        }
        
        # Plan based on individual scores
        if evaluation.get("accuracy", 0.0) < 0.8:
            plan["accuracy_improvements"].append("Verify all factual information and ensure data consistency")
            plan["accuracy_improvements"].append("Cross-reference data across sections for consistency")
        
        if evaluation.get("completeness", 0.0) < 0.8:
            plan["completeness_improvements"].append("Add missing required sections")
            plan["completeness_improvements"].append("Expand analysis depth in existing sections")
        
        if evaluation.get("structure", 0.0) < 0.8:
            plan["structure_improvements"].append("Reorganize sections for better logical flow")
            plan["structure_improvements"].append("Improve transitions between sections")
        
        if evaluation.get("verbosity", 0.0) < 0.8:
            plan["verbosity_improvements"].append("Adjust detail level based on section importance")
            plan["verbosity_improvements"].append("Balance comprehensiveness with conciseness")
        
        if evaluation.get("relevance", 0.0) < 0.8:
            plan["relevance_improvements"].append("Focus analysis on credit risk factors")
            plan["relevance_improvements"].append("Remove irrelevant information")
        
        if evaluation.get("tone", 0.0) < 0.8:
            plan["tone_improvements"].append("Ensure consistent professional tone throughout")
            plan["tone_improvements"].append("Maintain objectivity and impartiality")
        
        # Add specific critique-based improvements
        for critique_point in evaluation.get("critique", []):
            plan["section_specific_improvements"].append(critique_point)
        
        return plan

    async def _retrieve_missing_data(self, original_request: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve additional data if needed based on evaluation"""
        additional_data = {}
        
        # If completeness score is low, retrieve more data
        if evaluation.get("completeness", 0.0) < 0.8:
            try:
                # Get additional market and industry data
                if original_request:
                    business_type = original_request.get("business_type", "")
                    additional_data["enhanced_market_data"] = await self.mcp_service.get_market_data(business_type)
                    additional_data["enhanced_industry_data"] = await self.mcp_service.get_industry_analysis(business_type)
                    additional_data["financial_ratios"] = await self.mcp_service.get_financial_ratios(original_request)
            except Exception as e:
                additional_data["error"] = f"Failed to retrieve additional data: {str(e)}"
        
        return additional_data

    async def _regenerate_report_with_corrections(
        self, 
        original_report: Dict[str, Any], 
        evaluation: Dict[str, Any], 
        correction_plan: Dict[str, Any],
        additional_data: Dict[str, Any],
        original_request: Dict[str, Any]
    ) -> CreditRiskReport:
        """Regenerate the complete report with all corrections applied"""
        
        # Generate improved sections based on correction plan
        improved_sections = await self._generate_improved_sections(
            original_report, evaluation, correction_plan, additional_data, original_request
        )
        
        # Create refined report
        refined_report = CreditRiskReport(
            report_id=str(uuid.uuid4()),
            customer_id=original_report.get("customer_id"),
            generated_at=datetime.now(),
            sections=improved_sections,
            risk_level=self._determine_risk_level(improved_sections),
            recommendations=self._generate_recommendations(improved_sections)
        )
        
        return refined_report

    async def _generate_improved_sections(
        self,
        original_report: Dict[str, Any],
        evaluation: Dict[str, Any],
        correction_plan: Dict[str, Any],
        additional_data: Dict[str, Any],
        original_request: Dict[str, Any]
    ) -> List[ReportSection]:
        """Generate improved sections based on correction plan"""
        
        improved_sections = []
        original_sections = original_report.get("sections", [])
        
        # Define required sections
        required_sections = [
            "Executive Summary", "Customer Profile Analysis", "Financial Analysis",
            "Credit History Assessment", "Risk Factors Analysis", "Industry and Market Analysis",
            "Recommendations"
        ]
        
        # Process each required section
        for section_title in required_sections:
            # Find original section if it exists
            original_section = next(
                (s for s in original_sections if s.get("title") == section_title), 
                None
            )
            
            # Generate improved section
            improved_section = await self._generate_improved_section(
                section_title, original_section, evaluation, correction_plan, 
                additional_data, original_request
            )
            
            improved_sections.append(improved_section)
        
        return improved_sections

    async def _generate_improved_section(
        self,
        section_title: str,
        original_section: Dict[str, Any],
        evaluation: QualityEvaluation,
        correction_plan: Dict[str, Any],
        additional_data: Dict[str, Any],
        original_request: Dict[str, Any]
    ) -> ReportSection:
        """Generate an improved version of a specific section"""
        
        # Create improvement prompt based on correction plan
        improvement_prompt = self._create_improvement_prompt(
            section_title, original_section, evaluation, correction_plan, 
            additional_data, original_request
        )
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=improvement_prompt)
        ]
        
        improved_content = await self.generate_response(messages)
        
        return ReportSection(
            title=section_title,
            content=improved_content
        )

    def _create_improvement_prompt(
        self,
        section_title: str,
        original_section: Dict[str, Any],
        evaluation: Dict[str, Any],
        correction_plan: Dict[str, Any],
        additional_data: Dict[str, Any],
        original_request: Dict[str, Any]
    ) -> str:
        """Create a detailed prompt for improving a specific section"""
        
        original_content = original_section.get("content", "") if original_section else ""
        
        prompt = f"""
        Improve the '{section_title}' section of a credit risk assessment report.
        
        Original content:
        {original_content}
        
        Quality evaluation scores:
        - Accuracy: {evaluation.get('accuracy', 0.0)}
- Completeness: {evaluation.get('completeness', 0.0)}
- Structure: {evaluation.get('structure', 0.0)}
- Verbosity: {evaluation.get('verbosity', 0.0)}
- Relevance: {evaluation.get('relevance', 0.0)}
- Tone: {evaluation.get('tone', 0.0)}
- Overall: {evaluation.get('overall_score', 0.0)}
        
        Correction plan for this section:
        {self._get_section_specific_corrections(section_title, correction_plan)}
        
        Customer information:
        - Name: {original_request.get('customer_name', 'N/A')}
        - Business Type: {original_request.get('business_type', 'N/A')}
        - Annual Revenue: ${original_request.get('annual_revenue', 0):,.2f}
        - Credit History: {original_request.get('credit_history_years', 0)} years
        - Requested Amount: ${original_request.get('requested_amount', 0):,.2f}
        - Purpose: {original_request.get('purpose', 'N/A')}
        
        Additional data available:
        {json.dumps(additional_data, indent=2) if additional_data else 'None'}
        
        Generate an improved version of this section that addresses all identified issues.
        Focus on:
        1. Improving accuracy and factual correctness
        2. Enhancing completeness and depth of analysis
        3. Better structure and organization
        4. Appropriate level of detail
        5. Relevance to credit risk assessment
        6. Professional and objective tone
        
        Provide a comprehensive, well-structured section that meets high-quality standards.
        """
        
        return prompt

    def _get_section_specific_corrections(self, section_title: str, correction_plan: Dict[str, Any]) -> str:
        """Get section-specific corrections from the correction plan"""
        corrections = []
        
        # Add general improvements
        for improvement_type, improvements in correction_plan.items():
            if improvements and improvement_type != "section_specific_improvements":
                corrections.extend(improvements)
        
        # Add section-specific improvements
        section_specific = [
            improvement for improvement in correction_plan.get("section_specific_improvements", [])
            if section_title.lower() in improvement.lower()
        ]
        corrections.extend(section_specific)
        
        return "\n".join([f"- {correction}" for correction in corrections]) if corrections else "No specific corrections identified for this section."

    def _determine_risk_level(self, sections: List[ReportSection]) -> str:
        """Determine overall risk level based on improved analysis"""
        # This would be a more sophisticated algorithm in practice
        # For now, return a default risk level
        return "Medium Risk"

    def _generate_recommendations(self, sections: List[ReportSection]) -> List[str]:
        """Generate list of recommendations based on improved analysis"""
        return [
            "Regular financial monitoring required",
            "Quarterly review of credit terms",
            "Maintain adequate collateral coverage",
            "Monitor industry trends and market conditions",
            "Enhanced due diligence recommended"
        ]
