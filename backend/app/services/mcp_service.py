import httpx
import json
from typing import Dict, Any, Optional, List
from app.core.config import settings
import asyncio
from .loan_application_service import LoanApplicationService
from .customer_info_service import CustomerInfoService
from .compliance_service import ComplianceService

class MCPService:
    def __init__(self):
        self.base_url = settings.mcp_server_url
        self.client = httpx.AsyncClient(timeout=30.0)
        # Initialize the new services
        self.loan_application_service = LoanApplicationService()
        self.customer_info_service = CustomerInfoService()
        self.compliance_service = ComplianceService()
    
    async def get_market_data(self, business_type: str) -> Dict[str, Any]:
        """Retrieve market data for a specific business type"""
        try:
            payload = {
                "method": "get_market_data",
                "params": {
                    "business_type": business_type,
                    "data_type": "market_trends"
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp/market",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._get_mock_market_data(business_type)
                
        except Exception as e:
            # Fallback to mock data
            return self._get_mock_market_data(business_type)
    
    async def get_industry_analysis(self, business_type: str) -> Dict[str, Any]:
        """Retrieve industry analysis for a specific business type"""
        try:
            payload = {
                "method": "get_industry_analysis",
                "params": {
                    "business_type": business_type,
                    "analysis_type": "comprehensive"
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp/industry",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._get_mock_industry_data(business_type)
                
        except Exception as e:
            # Fallback to mock data
            return self._get_mock_industry_data(business_type)
    
    async def get_financial_ratios(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial ratios for credit risk assessment"""
        try:
            payload = {
                "method": "calculate_financial_ratios",
                "params": {
                    "annual_revenue": request_data.get("annual_revenue", 0),
                    "requested_amount": request_data.get("requested_amount", 0),
                    "credit_history_years": request_data.get("credit_history_years", 0)
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp/financial",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._calculate_mock_financial_ratios(request_data)
                
        except Exception as e:
            # Fallback to mock calculations
            return self._calculate_mock_financial_ratios(request_data)
    
    # Loan Application Information Query Tool
    async def get_loan_application_info(self, customer_id: str) -> Dict[str, Any]:
        """Query loan application information for a customer"""
        return await self.loan_application_service.get_loan_application_info(customer_id)
    
    async def get_loan_amount(self, customer_id: str) -> float:
        """Get loan amount for a customer"""
        return await self.loan_application_service.get_loan_amount(customer_id)
    
    async def get_application_date(self, customer_id: str) -> str:
        """Get loan application date for a customer"""
        return await self.loan_application_service.get_application_date(customer_id)
    
    async def get_loan_purpose(self, customer_id: str) -> str:
        """Get loan purpose for a customer"""
        return await self.loan_application_service.get_loan_purpose(customer_id)
    
    async def get_collateral_info(self, customer_id: str) -> Dict[str, Any]:
        """Get collateral information for a customer"""
        return await self.loan_application_service.get_collateral_info(customer_id)
    
    # Customer Information Query Tool
    async def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """Query customer information including credit history and existing loans"""
        return await self.customer_info_service.get_customer_info(customer_id)
    
    async def get_credit_history(self, customer_id: str) -> Dict[str, Any]:
        """Get customer credit history"""
        return await self.customer_info_service.get_credit_history(customer_id)
    
    async def get_existing_loans(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get customer's existing loans"""
        return await self.customer_info_service.get_existing_loans(customer_id)
    
    async def get_credit_score(self, customer_id: str) -> int:
        """Get customer's credit score"""
        return await self.customer_info_service.get_credit_score(customer_id)
    
    async def get_total_debt(self, customer_id: str) -> float:
        """Get customer's total outstanding debt"""
        return await self.customer_info_service.get_total_debt(customer_id)
    
    async def get_payment_history_summary(self, customer_id: str) -> Dict[str, Any]:
        """Get summary of payment history"""
        return await self.customer_info_service.get_payment_history_summary(customer_id)
    
    # Compliance Requirements Retriever
    async def get_compliance_requirements(self, business_type: str = None, loan_amount: float = None) -> Dict[str, Any]:
        """Query compliance requirements for loan applications"""
        return await self.compliance_service.get_compliance_requirements(business_type, loan_amount)
    
    async def check_kyc_compliance(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check KYC compliance requirements"""
        return await self.compliance_service.check_kyc_compliance(customer_data)
    
    async def check_aml_compliance(self, customer_data: Dict[str, Any], loan_amount: float) -> Dict[str, Any]:
        """Check AML compliance requirements"""
        return await self.compliance_service.check_aml_compliance(customer_data, loan_amount)
    
    async def check_regulatory_compliance(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check regulatory compliance requirements"""
        return await self.compliance_service.check_regulatory_compliance(customer_data)
    
    async def check_financial_requirements(self, customer_data: Dict[str, Any], loan_amount: float) -> Dict[str, Any]:
        """Check financial requirements compliance"""
        return await self.compliance_service.check_financial_requirements(customer_data, loan_amount)
    
    async def get_overall_compliance_status(self, customer_data: Dict[str, Any], loan_amount: float) -> Dict[str, Any]:
        """Get overall compliance status for the application"""
        return await self.compliance_service.get_overall_compliance_status(customer_data, loan_amount)
    
    async def get_required_documents(self, business_type: str = None, loan_amount: float = None) -> List[str]:
        """Get list of required documents based on business type and loan amount"""
        return await self.compliance_service.get_required_documents(business_type, loan_amount)
    
    # Additional loan application methods
    async def get_submitted_applications(self) -> List[Dict[str, Any]]:
        """Get all loan applications with 'submitted' status"""
        return await self.loan_application_service.get_submitted_applications()
    
    async def get_application_status(self, customer_id: str) -> str:
        """Get application status for a customer"""
        return await self.loan_application_service.get_application_status(customer_id)
    
    async def is_application_submitted(self, customer_id: str) -> bool:
        """Check if the application is in submitted status"""
        return await self.loan_application_service.is_application_submitted(customer_id)
    
    async def get_credit_history_data(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve credit history data for a customer"""
        try:
            payload = {
                "method": "get_credit_history",
                "params": {
                    "customer_id": customer_id,
                    "data_type": "comprehensive"
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp/credit",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._get_mock_credit_history(customer_id)
                
        except Exception as e:
            # Fallback to mock data
            return self._get_mock_credit_history(customer_id)
    
    async def get_regulatory_data(self, business_type: str) -> Dict[str, Any]:
        """Retrieve regulatory and compliance data"""
        try:
            payload = {
                "method": "get_regulatory_data",
                "params": {
                    "business_type": business_type,
                    "jurisdiction": "US"
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp/regulatory",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._get_mock_regulatory_data(business_type)
                
        except Exception as e:
            # Fallback to mock data
            return self._get_mock_regulatory_data(business_type)
    
    def _get_mock_market_data(self, business_type: str) -> Dict[str, Any]:
        """Mock market data for development/testing"""
        return {
            "market_trends": {
                "growth_rate": 0.05,
                "market_size": "2.5T USD",
                "key_drivers": ["Digital transformation", "E-commerce growth", "Supply chain optimization"],
                "risks": ["Economic uncertainty", "Supply chain disruptions", "Regulatory changes"]
            },
            "competitive_landscape": {
                "major_players": ["Company A", "Company B", "Company C"],
                "market_concentration": "Moderate",
                "entry_barriers": "Medium"
            },
            "business_type": business_type,
            "data_source": "mock_data"
        }
    
    def _get_mock_industry_data(self, business_type: str) -> Dict[str, Any]:
        """Mock industry analysis data"""
        return {
            "industry_overview": {
                "sector": "Technology",
                "subsector": business_type,
                "maturity": "Growth",
                "cyclicality": "Low"
            },
            "financial_metrics": {
                "average_roi": 0.15,
                "profit_margins": 0.25,
                "debt_to_equity": 0.4
            },
            "risk_factors": {
                "operational_risks": ["Technology obsolescence", "Cybersecurity threats"],
                "financial_risks": ["Cash flow volatility", "High R&D costs"],
                "regulatory_risks": ["Data privacy regulations", "Antitrust concerns"]
            },
            "business_type": business_type,
            "data_source": "mock_data"
        }
    
    def _calculate_mock_financial_ratios(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate mock financial ratios"""
        annual_revenue = request_data.get("annual_revenue", 0)
        requested_amount = request_data.get("requested_amount", 0)
        credit_history_years = request_data.get("credit_history_years", 0)
        
        # Mock calculations
        debt_service_coverage = annual_revenue / (requested_amount * 0.1) if requested_amount > 0 else 0
        debt_to_income = requested_amount / annual_revenue if annual_revenue > 0 else 0
        credit_utilization = min(requested_amount / (annual_revenue * 0.3), 1.0) if annual_revenue > 0 else 0
        
        return {
            "debt_service_coverage_ratio": round(debt_service_coverage, 2),
            "debt_to_income_ratio": round(debt_to_income, 2),
            "credit_utilization_ratio": round(credit_utilization, 2),
            "credit_history_score": min(credit_history_years / 10, 1.0),
            "financial_strength_score": 0.7,
            "risk_assessment": {
                "low_risk": debt_service_coverage > 2.0 and debt_to_income < 0.4,
                "medium_risk": 1.5 <= debt_service_coverage <= 2.0 or 0.4 <= debt_to_income <= 0.6,
                "high_risk": debt_service_coverage < 1.5 or debt_to_income > 0.6
            },
            "data_source": "mock_calculations"
        }
    
    def _get_mock_credit_history(self, customer_id: str) -> Dict[str, Any]:
        """Mock credit history data"""
        return {
            "customer_id": customer_id,
            "credit_score": 750,
            "payment_history": {
                "on_time_payments": 0.95,
                "late_payments_30_days": 2,
                "late_payments_60_days": 0,
                "late_payments_90_days": 0
            },
            "credit_utilization": 0.35,
            "length_of_credit": 8,
            "credit_mix": ["Credit cards", "Business loans", "Trade credit"],
            "new_credit": 1,
            "risk_factors": [],
            "data_source": "mock_data"
        }
    
    def _get_mock_regulatory_data(self, business_type: str) -> Dict[str, Any]:
        """Mock regulatory data"""
        return {
            "regulatory_environment": {
                "compliance_requirements": ["GDPR", "SOX", "Industry-specific regulations"],
                "licensing_requirements": ["Business license", "Industry certifications"],
                "reporting_obligations": ["Quarterly financial reports", "Annual compliance reports"]
            },
            "regulatory_risks": {
                "compliance_risk": "Low",
                "regulatory_changes": "Moderate",
                "enforcement_actions": "None"
            },
            "business_type": business_type,
            "data_source": "mock_data"
        }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
