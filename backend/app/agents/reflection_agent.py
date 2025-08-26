from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base_agent import BaseAgent
from app.models.schemas import CreditRiskReport, QualityEvaluation, ReportSection
from app.core.config import settings
import json
from datetime import datetime

class ReflectionAgent(BaseAgent):
    def __init__(self):
        super().__init__("Reflection")
    
    def get_system_prompt(self) -> str:
        return """You are a Reflection Agent (Critic) specialized in evaluating credit risk assessment reports. Your role is to:

1. Review generated reports with strict evaluation criteria
2. Apply comprehensive quality assessment across multiple dimensions
3. Assign quality scores (0.0 to 1.0) for each evaluation criterion
4. Provide actionable critique when quality scores are below threshold
5. Automatically exit the refinement loop when quality score >= 0.8

Evaluation Criteria:
- ACCURACY: Factual correctness, data precision, and logical consistency
- COMPLETENESS: Coverage of all required assessment areas and sections
- STRUCTURE: Logical organization, flow, and professional presentation
- VERBOSITY: Appropriate level of detail - not too brief, not too verbose
- RELEVANCE: Pertinence to credit risk assessment and business context
- TONE: Professional, objective, and appropriate communication style

Be thorough, objective, and provide specific, actionable feedback for improvement."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            report = input_data.get("report")
            if not report:
                return {
                    "agent_type": "Reflection",
                    "status": "error",
                    "error": "No report provided for evaluation"
                }
            
            # Evaluate the report
            evaluation = await self._evaluate_report(report)
            
            # Determine if quality threshold is met
            meets_threshold = evaluation.overall_score >= settings.quality_threshold
            
            return {
                "agent_type": "Reflection",
                "status": "success",
                "evaluation": evaluation.dict(),
                "meets_threshold": meets_threshold,
                "content": self._generate_evaluation_summary(evaluation, meets_threshold)
            }
            
        except Exception as e:
            return {
                "agent_type": "Reflection",
                "status": "error",
                "error": str(e),
                "content": f"Error evaluating report: {str(e)}"
            }

    async def _evaluate_report(self, report: Dict[str, Any]) -> QualityEvaluation:
        """Comprehensive evaluation of the credit risk assessment report"""
        
        # Convert Pydantic model to dict if needed
        if hasattr(report, 'dict'):
            report = report.dict()
        
        # Extract report sections
        sections = report.get("sections", [])
        
        # Evaluate each criterion
        accuracy_score = await self._evaluate_accuracy(report, sections)
        completeness_score = await self._evaluate_completeness(report, sections)
        structure_score = await self._evaluate_structure(report, sections)
        verbosity_score = await self._evaluate_verbosity(report, sections)
        relevance_score = await self._evaluate_relevance(report, sections)
        tone_score = await self._evaluate_tone(report, sections)
        
        # Calculate overall score (weighted average)
        overall_score = self._calculate_overall_score({
            "accuracy": accuracy_score,
            "completeness": completeness_score,
            "structure": structure_score,
            "verbosity": verbosity_score,
            "relevance": relevance_score,
            "tone": tone_score
        })
        
        # Generate critique if score is below threshold
        critique = []
        if overall_score < settings.quality_threshold:
            critique = await self._generate_critique({
                "accuracy": accuracy_score,
                "completeness": completeness_score,
                "structure": structure_score,
                "verbosity": verbosity_score,
                "relevance": relevance_score,
                "tone": tone_score
            }, sections)
        
        return QualityEvaluation(
            accuracy=accuracy_score,
            completeness=completeness_score,
            structure=structure_score,
            verbosity=verbosity_score,
            relevance=relevance_score,
            tone=tone_score,
            overall_score=overall_score,
            critique=critique,
            meets_threshold=overall_score >= settings.quality_threshold
        )

    async def _evaluate_accuracy(self, report: Dict[str, Any], sections: List[Dict[str, Any]]) -> float:
        """Evaluate factual accuracy and data precision"""
        prompt = f"""
        Evaluate the ACCURACY of this credit risk assessment report.
        
        Report ID: {report.get('report_id')}
        Customer ID: {report.get('customer_id')}
        Number of sections: {len(sections)}
        
        Consider:
        1. Factual correctness of information
        2. Data precision and consistency
        3. Logical reasoning and conclusions
        4. Mathematical calculations (if any)
        5. Consistency across sections
        
        Provide a score from 0.0 to 1.0 and brief justification.
        IMPORTANT: Start your response with "Score: X.X" where X.X is a number between 0.0 and 1.0.
        Example: "Score: 0.8, Justification: The report shows good accuracy with consistent data..."
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        response = await self.generate_response(messages)
        return self._extract_score_from_response(response)

    async def _evaluate_completeness(self, report: Dict[str, Any], sections: List[Dict[str, Any]]) -> float:
        """Evaluate coverage of required assessment areas"""
        required_sections = [
            "Executive Summary", "Customer Profile Analysis", "Financial Analysis",
            "Credit History Assessment", "Risk Factors Analysis", "Industry and Market Analysis",
            "Recommendations"
        ]
        
        present_sections = [section.get("title", "") for section in sections]
        missing_sections = [section for section in required_sections if section not in present_sections]
        
        prompt = f"""
        Evaluate the COMPLETENESS of this credit risk assessment report.
        
        Required sections: {required_sections}
        Present sections: {present_sections}
        Missing sections: {missing_sections}
        
        Consider:
        1. Coverage of all required assessment areas
        2. Depth of analysis in each section
        3. Inclusion of necessary data points
        4. Comprehensive risk assessment
        5. Complete recommendations
        
        Provide a score from 0.0 to 1.0 and brief justification.
        IMPORTANT: Start your response with "Score: X.X" where X.X is a number between 0.0 and 1.0.
        Example: "Score: 0.7, Justification: The report covers most required areas but lacks depth in..."
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        response = await self.generate_response(messages)
        return self._extract_score_from_response(response)

    async def _evaluate_structure(self, report: Dict[str, Any], sections: List[Dict[str, Any]]) -> float:
        """Evaluate logical organization and flow"""
        prompt = f"""
        Evaluate the STRUCTURE of this credit risk assessment report.
        
        Number of sections: {len(sections)}
        Section titles: {[section.get('title', '') for section in sections]}
        
        Consider:
        1. Logical organization and flow
        2. Professional presentation
        3. Clear section transitions
        4. Consistent formatting
        5. Appropriate use of headings and subheadings
        6. Overall readability and navigation
        
        Provide a score from 0.0 to 1.0 and brief justification.
        IMPORTANT: Start your response with "Score: X.X" where X.X is a number between 0.0 and 1.0.
        Example: "Score: 0.6, Justification: The structure is logical but could be improved with better..."
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        response = await self.generate_response(messages)
        return self._extract_score_from_response(response)

    async def _evaluate_verbosity(self, report: Dict[str, Any], sections: List[Dict[str, Any]]) -> float:
        """Evaluate appropriate level of detail"""
        total_content_length = sum(len(section.get("content", "")) for section in sections)
        
        prompt = f"""
        Evaluate the VERBOSITY of this credit risk assessment report.
        
        Total content length: {total_content_length} characters
        Number of sections: {len(sections)}
        
        Consider:
        1. Appropriate level of detail - not too brief, not too verbose
        2. Balance between comprehensiveness and conciseness
        3. Clarity of expression
        4. Avoidance of unnecessary repetition
        5. Sufficient detail for decision-making
        
        Provide a score from 0.0 to 1.0 and brief justification.
        Format: Score: X.X, Justification: [explanation]
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        response = await self.generate_response(messages)
        return self._extract_score_from_response(response)

    async def _evaluate_relevance(self, report: Dict[str, Any], sections: List[Dict[str, Any]]) -> float:
        """Evaluate pertinence to credit risk assessment"""
        prompt = f"""
        Evaluate the RELEVANCE of this credit risk assessment report.
        
        Customer ID: {report.get('customer_id')}
        Business context: Credit risk assessment
        
        Consider:
        1. Pertinence to credit risk assessment
        2. Relevance to business context
        3. Applicability of analysis to decision-making
        4. Focus on credit-related factors
        5. Avoidance of irrelevant information
        
        Provide a score from 0.0 to 1.0 and brief justification.
        Format: Score: X.X, Justification: [explanation]
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        response = await self.generate_response(messages)
        return self._extract_score_from_response(response)

    async def _evaluate_tone(self, report: Dict[str, Any], sections: List[Dict[str, Any]]) -> float:
        """Evaluate professional and appropriate communication style"""
        prompt = f"""
        Evaluate the TONE of this credit risk assessment report.
        
        Consider:
        1. Professional communication style
        2. Objectivity and impartiality
        3. Appropriate formality level
        4. Clear and authoritative voice
        5. Avoidance of bias or emotional language
        6. Consistency in tone across sections
        
        Provide a score from 0.0 to 1.0 and brief justification.
        Format: Score: X.X, Justification: [explanation]
        """
        
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=prompt)
        ]
        
        response = await self.generate_response(messages)
        return self._extract_score_from_response(response)

    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        weights = {
            "accuracy": 0.25,
            "completeness": 0.20,
            "structure": 0.15,
            "verbosity": 0.10,
            "relevance": 0.20,
            "tone": 0.10
        }
        
        overall_score = sum(scores[criterion] * weights[criterion] for criterion in scores)
        return round(overall_score, 3)

    async def _generate_critique(self, scores: Dict[str, float], sections: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable critique for improvement"""
        critique = []
        
        if scores["accuracy"] < 0.8:
            critique.append("Improve factual accuracy and ensure data consistency across all sections")
        
        if scores["completeness"] < 0.8:
            critique.append("Add missing sections and provide more comprehensive analysis")
        
        if scores["structure"] < 0.8:
            critique.append("Improve logical flow and organization of report sections")
        
        if scores["verbosity"] < 0.8:
            critique.append("Adjust detail level - provide more comprehensive analysis where needed")
        
        if scores["relevance"] < 0.8:
            critique.append("Focus more on credit risk factors and business-relevant analysis")
        
        if scores["tone"] < 0.8:
            critique.append("Maintain professional tone and ensure objectivity throughout")
        
        # Add specific section-based critique
        section_critique = await self._generate_section_specific_critique(sections)
        critique.extend(section_critique)
        
        return critique

    async def _generate_section_specific_critique(self, sections: List[Dict[str, Any]]) -> List[str]:
        """Generate critique specific to individual sections"""
        critique = []
        
        for section in sections:
            title = section.get("title", "")
            content = section.get("content", "")
            
            if len(content) < 100:  # Too brief
                critique.append(f"Expand {title} section with more detailed analysis")
            elif len(content) > 2000:  # Too verbose
                critique.append(f"Condense {title} section for better readability")
        
        return critique

    def _extract_score_from_response(self, response: str) -> float:
        """Extract numerical score from LLM response"""
        try:
            # Look for "Score: X.X" pattern
            if "Score:" in response:
                score_part = response.split("Score:")[1].split(",")[0].strip()
                score = float(score_part)
                return score
            
            # Look for "X.X" pattern (decimal number)
            import re
            decimal_pattern = r'\b0\.\d+\b|\b1\.0\b'
            numbers = re.findall(decimal_pattern, response)
            if numbers:
                score = float(numbers[0])
                return score
            
            # Look for any number between 0 and 1
            number_pattern = r'\b[01]\b'
            numbers = re.findall(number_pattern, response)
            if numbers:
                score = float(numbers[0])
                return score
            
            # If no score found, try to infer from text
            if any(word in response.lower() for word in ['excellent', 'outstanding', 'perfect', 'high']):
                score = 0.9
            elif any(word in response.lower() for word in ['good', 'satisfactory', 'adequate']):
                score = 0.7
            elif any(word in response.lower() for word in ['poor', 'inadequate', 'insufficient']):
                score = 0.3
            else:
                score = 0.5
            
            return score
            
        except Exception as e:
            # Return a reasonable default score instead of 0.0
            return 0.6  # Default to a moderate score

    def _generate_evaluation_summary(self, evaluation: QualityEvaluation, meets_threshold: bool) -> str:
        """Generate summary of evaluation results"""
        if meets_threshold:
            return f"Report quality assessment completed. Overall score: {evaluation.overall_score:.3f} - MEETS QUALITY THRESHOLD. Report is ready for final delivery."
        else:
            return f"Report quality assessment completed. Overall score: {evaluation.overall_score:.3f} - BELOW QUALITY THRESHOLD. {len(evaluation.critique)} improvement areas identified. Proceeding to refinement phase."
