from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

class ComplianceService:
    """Service for querying compliance requirements and checking compliance adherence"""
    
    def __init__(self):
        # Mock database - in production, this would connect to a real database
        self.compliance_requirements = self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> Dict[str, Any]:
        """Initialize mock compliance requirements data"""
        return {
            "general_requirements": {
                "kYC_requirements": {
                    "customer_identification": True,
                    "beneficial_ownership": True,
                    "risk_assessment": True,
                    "ongoing_monitoring": True
                },
                "aml_requirements": {
                    "suspicious_activity_reporting": True,
                    "currency_transaction_reporting": True,
                    "customer_due_diligence": True,
                    "enhanced_due_diligence": False
                },
                "regulatory_requirements": {
                    "fair_lending_compliance": True,
                    "truth_in_lending": True,
                    "equal_credit_opportunity": True,
                    "community_reinvestment": True
                }
            },
            "business_loan_requirements": {
                "documentation_requirements": [
                    "Business license",
                    "Articles of incorporation",
                    "Financial statements (3 years)",
                    "Tax returns (3 years)",
                    "Business plan",
                    "Personal financial statements",
                    "Collateral documentation"
                ],
                "financial_requirements": {
                    "minimum_credit_score": 650,
                    "minimum_annual_revenue": 100000,
                    "maximum_debt_to_income_ratio": 0.5,
                    "minimum_cash_flow_coverage": 1.25
                },
                "collateral_requirements": {
                    "minimum_collateral_coverage": 1.2,
                    "acceptable_collateral_types": [
                        "Real estate",
                        "Equipment",
                        "Inventory",
                        "Accounts receivable",
                        "Securities"
                    ]
                }
            },
            "industry_specific_requirements": {
                "technology": {
                    "intellectual_property_valuation": True,
                    "patent_documentation": True,
                    "rd_tax_credits": True
                },
                "manufacturing": {
                    "environmental_compliance": True,
                    "safety_certifications": True,
                    "equipment_valuation": True
                },
                "healthcare": {
                    "licensing_requirements": True,
                    "medicare_medicaid_compliance": True,
                    "hipaa_compliance": True
                },
                "real_estate": {
                    "property_valuation": True,
                    "zoning_compliance": True,
                    "environmental_assessment": True
                }
            },
            "risk_based_requirements": {
                "low_risk": {
                    "documentation_level": "Standard",
                    "monitoring_frequency": "Annual",
                    "collateral_requirements": "Standard"
                },
                "medium_risk": {
                    "documentation_level": "Enhanced",
                    "monitoring_frequency": "Quarterly",
                    "collateral_requirements": "Enhanced"
                },
                "high_risk": {
                    "documentation_level": "Comprehensive",
                    "monitoring_frequency": "Monthly",
                    "collateral_requirements": "Comprehensive"
                }
            }
        }
    
    async def get_compliance_requirements(self, business_type: str = None, loan_amount: float = None) -> Dict[str, Any]:
        """Get comprehensive compliance requirements"""
        requirements = {
            "general_requirements": self.compliance_requirements["general_requirements"],
            "business_loan_requirements": self.compliance_requirements["business_loan_requirements"],
            "retrieved_at": datetime.now().isoformat()
        }
        
        # Add industry-specific requirements if business type is provided
        if business_type and business_type.lower() in self.compliance_requirements["industry_specific_requirements"]:
            requirements["industry_specific"] = self.compliance_requirements["industry_specific_requirements"][business_type.lower()]
        
        # Add risk-based requirements based on loan amount
        if loan_amount:
            if loan_amount < 100000:
                risk_level = "low_risk"
            elif loan_amount < 1000000:
                risk_level = "medium_risk"
            else:
                risk_level = "high_risk"
            requirements["risk_based"] = self.compliance_requirements["risk_based_requirements"][risk_level]
        
        return requirements
    
    async def check_kyc_compliance(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check KYC compliance requirements"""
        kyc_requirements = self.compliance_requirements["general_requirements"]["kYC_requirements"]
        compliance_status = {}
        
        # Check customer identification
        compliance_status["customer_identification"] = {
            "required": kyc_requirements["customer_identification"],
            "status": "compliant" if customer_data.get("customer_id") and customer_data.get("customer_name") else "non_compliant",
            "details": "Customer ID and name provided" if customer_data.get("customer_id") and customer_data.get("customer_name") else "Missing customer identification"
        }
        
        # Check beneficial ownership (simplified check)
        compliance_status["beneficial_ownership"] = {
            "required": kyc_requirements["beneficial_ownership"],
            "status": "compliant",  # Simplified for demo
            "details": "Beneficial ownership verified"
        }
        
        # Check risk assessment
        compliance_status["risk_assessment"] = {
            "required": kyc_requirements["risk_assessment"],
            "status": "compliant",  # Simplified for demo
            "details": "Risk assessment completed"
        }
        
        return compliance_status
    
    async def check_aml_compliance(self, customer_data: Dict[str, Any], loan_amount: float) -> Dict[str, Any]:
        """Check AML compliance requirements"""
        aml_requirements = self.compliance_requirements["general_requirements"]["aml_requirements"]
        compliance_status = {}
        
        # Check suspicious activity reporting
        compliance_status["suspicious_activity_reporting"] = {
            "required": aml_requirements["suspicious_activity_reporting"],
            "status": "compliant",  # Simplified for demo
            "details": "No suspicious activity detected"
        }
        
        # Check currency transaction reporting
        compliance_status["currency_transaction_reporting"] = {
            "required": aml_requirements["currency_transaction_reporting"],
            "status": "compliant" if loan_amount < 10000 else "requires_reporting",
            "details": "Transaction amount below reporting threshold" if loan_amount < 10000 else "Transaction requires CTR filing"
        }
        
        # Check customer due diligence
        compliance_status["customer_due_diligence"] = {
            "required": aml_requirements["customer_due_diligence"],
            "status": "compliant",  # Simplified for demo
            "details": "Customer due diligence completed"
        }
        
        # Check enhanced due diligence
        enhanced_dd_required = loan_amount > 500000 or customer_data.get("business_type") in ["high_risk_industries"]
        compliance_status["enhanced_due_diligence"] = {
            "required": enhanced_dd_required,
            "status": "compliant" if not enhanced_dd_required else "requires_enhanced_dd",
            "details": "Enhanced due diligence not required" if not enhanced_dd_required else "Enhanced due diligence required due to loan amount or business type"
        }
        
        return compliance_status
    
    async def check_regulatory_compliance(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check regulatory compliance requirements"""
        regulatory_requirements = self.compliance_requirements["general_requirements"]["regulatory_requirements"]
        compliance_status = {}
        
        # Check fair lending compliance
        compliance_status["fair_lending_compliance"] = {
            "required": regulatory_requirements["fair_lending_compliance"],
            "status": "compliant",  # Simplified for demo
            "details": "Fair lending requirements met"
        }
        
        # Check truth in lending
        compliance_status["truth_in_lending"] = {
            "required": regulatory_requirements["truth_in_lending"],
            "status": "compliant",  # Simplified for demo
            "details": "Truth in lending disclosures provided"
        }
        
        # Check equal credit opportunity
        compliance_status["equal_credit_opportunity"] = {
            "required": regulatory_requirements["equal_credit_opportunity"],
            "status": "compliant",  # Simplified for demo
            "details": "Equal credit opportunity requirements met"
        }
        
        return compliance_status
    
    async def check_financial_requirements(self, customer_data: Dict[str, Any], loan_amount: float) -> Dict[str, Any]:
        """Check financial requirements compliance"""
        financial_reqs = self.compliance_requirements["business_loan_requirements"]["financial_requirements"]
        compliance_status = {}
        
        # Check credit score requirement
        credit_score = customer_data.get("credit_score", 0)
        compliance_status["credit_score"] = {
            "required": financial_reqs["minimum_credit_score"],
            "actual": credit_score,
            "status": "compliant" if credit_score >= financial_reqs["minimum_credit_score"] else "non_compliant",
            "details": f"Credit score {credit_score} meets minimum requirement" if credit_score >= financial_reqs["minimum_credit_score"] else f"Credit score {credit_score} below minimum requirement of {financial_reqs['minimum_credit_score']}"
        }
        
        # Check annual revenue requirement
        annual_revenue = customer_data.get("annual_revenue", 0)
        compliance_status["annual_revenue"] = {
            "required": financial_reqs["minimum_annual_revenue"],
            "actual": annual_revenue,
            "status": "compliant" if annual_revenue >= financial_reqs["minimum_annual_revenue"] else "non_compliant",
            "details": f"Annual revenue ${annual_revenue:,.2f} meets minimum requirement" if annual_revenue >= financial_reqs["minimum_annual_revenue"] else f"Annual revenue ${annual_revenue:,.2f} below minimum requirement of ${financial_reqs['minimum_annual_revenue']:,.2f}"
        }
        
        # Check debt-to-income ratio
        dti_ratio = customer_data.get("debt_to_income_ratio", 0)
        compliance_status["debt_to_income_ratio"] = {
            "required": financial_reqs["maximum_debt_to_income_ratio"],
            "actual": dti_ratio,
            "status": "compliant" if dti_ratio <= financial_reqs["maximum_debt_to_income_ratio"] else "non_compliant",
            "details": f"DTI ratio {dti_ratio:.2f} within acceptable range" if dti_ratio <= financial_reqs["maximum_debt_to_income_ratio"] else f"DTI ratio {dti_ratio:.2f} exceeds maximum of {financial_reqs['maximum_debt_to_income_ratio']:.2f}"
        }
        
        return compliance_status
    
    async def get_required_documents(self, business_type: str = None, loan_amount: float = None) -> List[str]:
        """Get list of required documents based on business type and loan amount"""
        base_documents = self.compliance_requirements["business_loan_requirements"]["documentation_requirements"]
        required_documents = base_documents.copy()
        
        # Add industry-specific documents
        if business_type and business_type.lower() in self.compliance_requirements["industry_specific_requirements"]:
            industry_reqs = self.compliance_requirements["industry_specific_requirements"][business_type.lower()]
            if industry_reqs.get("intellectual_property_valuation"):
                required_documents.append("Intellectual property valuation report")
            if industry_reqs.get("environmental_compliance"):
                required_documents.append("Environmental compliance certificate")
            if industry_reqs.get("licensing_requirements"):
                required_documents.append("Business license and certifications")
        
        # Add risk-based documents
        if loan_amount:
            if loan_amount >= 1000000:
                required_documents.extend([
                    "Comprehensive business plan",
                    "Detailed financial projections",
                    "Market analysis report",
                    "Management team resumes"
                ])
            elif loan_amount >= 500000:
                required_documents.extend([
                    "Business plan",
                    "Financial projections"
                ])
        
        return required_documents
    
    async def get_overall_compliance_status(self, customer_data: Dict[str, Any], loan_amount: float) -> Dict[str, Any]:
        """Get overall compliance status for the application"""
        kyc_status = await self.check_kyc_compliance(customer_data)
        aml_status = await self.check_aml_compliance(customer_data, loan_amount)
        regulatory_status = await self.check_regulatory_compliance(customer_data)
        financial_status = await self.check_financial_requirements(customer_data, loan_amount)
        
        # Calculate overall compliance
        all_checks = {**kyc_status, **aml_status, **regulatory_status, **financial_status}
        compliant_checks = sum(1 for check in all_checks.values() if check["status"] == "compliant")
        total_checks = len(all_checks)
        compliance_rate = compliant_checks / total_checks if total_checks > 0 else 0
        
        return {
            "overall_status": "compliant" if compliance_rate >= 0.9 else "requires_review",
            "compliance_rate": compliance_rate,
            "compliant_checks": compliant_checks,
            "total_checks": total_checks,
            "kyc_compliance": kyc_status,
            "aml_compliance": aml_status,
            "regulatory_compliance": regulatory_status,
            "financial_compliance": financial_status,
            "required_documents": await self.get_required_documents(customer_data.get("business_type"), loan_amount),
            "assessment_date": datetime.now().isoformat()
        }
