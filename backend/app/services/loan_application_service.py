from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import uuid

class LoanApplicationService:
    """Service for querying loan application information"""
    
    def __init__(self):
        # Mock database - in production, this would connect to a real database
        self.loan_applications = self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> Dict[str, Any]:
        """Initialize mock loan application data"""
        return {
            "test123": {
                "application_id": "LA-2024-001",
                "customer_id": "test123",
                "customer_name": "Test Company",
                "application_date": "2024-08-25",
                "loan_amount": 500000,
                "loan_purpose": "Business expansion",
                "business_type": "Technology",
                "annual_revenue": 1000000,
                "credit_history_years": 5,
                "requested_amount": 500000,
                "purpose": "Business expansion",
                "loan_term": 60,  # months
                "interest_rate": 7.5,
                "collateral_type": "Commercial property",
                "collateral_value": 750000,
                "application_status": "submitted",
                "submitted_documents": [
                    "Business plan",
                    "Financial statements",
                    "Tax returns",
                    "Bank statements"
                ],
                "risk_factors": [
                    "New business line",
                    "Seasonal revenue patterns"
                ],
                "strengths": [
                    "Strong credit history",
                    "Adequate collateral",
                    "Clear business plan"
                ]
            },
            "cust456": {
                "application_id": "LA-2024-002",
                "customer_id": "cust456",
                "customer_name": "Manufacturing Corp",
                "application_date": "2024-08-20",
                "loan_amount": 250000,
                "loan_purpose": "Equipment purchase",
                "business_type": "Manufacturing",
                "annual_revenue": 2500000,
                "credit_history_years": 3,
                "requested_amount": 250000,
                "purpose": "Equipment purchase",
                "loan_term": 36,
                "interest_rate": 6.8,
                "collateral_type": "Equipment",
                "collateral_value": 300000,
                "application_status": "submitted",
                "submitted_documents": [
                    "Equipment quotes",
                    "Financial projections",
                    "Personal guarantee"
                ],
                "risk_factors": [
                    "Limited operating history",
                    "Equipment depreciation risk"
                ],
                "strengths": [
                    "High-value collateral",
                    "Personal guarantee",
                    "Clear equipment need"
                ]
            },
            "retail789": {
                "application_id": "LA-2024-003",
                "customer_id": "retail789",
                "customer_name": "Green Grocers Market",
                "application_date": "2024-08-22",
                "loan_amount": 150000,
                "loan_purpose": "Working capital",
                "business_type": "Retail",
                "annual_revenue": 800000,
                "credit_history_years": 8,
                "requested_amount": 150000,
                "purpose": "Working capital",
                "loan_term": 24,
                "interest_rate": 8.2,
                "collateral_type": "Inventory",
                "collateral_value": 200000,
                "application_status": "submitted",
                "submitted_documents": [
                    "Inventory valuation",
                    "Cash flow projections",
                    "Business license",
                    "Insurance certificates"
                ],
                "risk_factors": [
                    "Seasonal business",
                    "Low profit margins",
                    "Inventory obsolescence risk"
                ],
                "strengths": [
                    "Established business",
                    "Good location",
                    "Steady customer base"
                ]
            },
            "tech101": {
                "application_id": "LA-2024-004",
                "customer_id": "tech101",
                "customer_name": "Innovate Solutions LLC",
                "application_date": "2024-08-18",
                "loan_amount": 750000,
                "loan_purpose": "Product development",
                "business_type": "Software Development",
                "annual_revenue": 1500000,
                "credit_history_years": 2,
                "requested_amount": 750000,
                "purpose": "Product development",
                "loan_term": 48,
                "interest_rate": 9.5,
                "collateral_type": "Intellectual property",
                "collateral_value": 500000,
                "application_status": "submitted",
                "submitted_documents": [
                    "Patent documentation",
                    "Market analysis",
                    "Development timeline",
                    "Team resumes"
                ],
                "risk_factors": [
                    "Early-stage company",
                    "Unproven technology",
                    "High development costs"
                ],
                "strengths": [
                    "Innovative product",
                    "Strong team",
                    "Market opportunity"
                ]
            },
            "restaurant202": {
                "application_id": "LA-2024-005",
                "customer_id": "restaurant202",
                "customer_name": "Bella Vista Restaurant",
                "application_date": "2024-08-24",
                "loan_amount": 300000,
                "loan_purpose": "Renovation and expansion",
                "business_type": "Food & Beverage",
                "annual_revenue": 1200000,
                "credit_history_years": 6,
                "requested_amount": 300000,
                "purpose": "Renovation and expansion",
                "loan_term": 60,
                "interest_rate": 7.8,
                "collateral_type": "Real estate",
                "collateral_value": 800000,
                "application_status": "submitted",
                "submitted_documents": [
                    "Renovation plans",
                    "Building permits",
                    "Financial statements",
                    "Market analysis"
                ],
                "risk_factors": [
                    "Construction delays",
                    "Seasonal business",
                    "Competition in area"
                ],
                "strengths": [
                    "Prime location",
                    "Established reputation",
                    "Strong collateral"
                ]
            },
            "construction303": {
                "application_id": "LA-2024-006",
                "customer_id": "construction303",
                "customer_name": "Metro Construction Co",
                "application_date": "2024-08-21",
                "loan_amount": 1000000,
                "loan_purpose": "Project financing",
                "business_type": "Construction",
                "annual_revenue": 5000000,
                "credit_history_years": 12,
                "requested_amount": 1000000,
                "purpose": "Project financing",
                "loan_term": 72,
                "interest_rate": 6.5,
                "collateral_type": "Equipment and receivables",
                "collateral_value": 1500000,
                "application_status": "submitted",
                "submitted_documents": [
                    "Project contracts",
                    "Equipment inventory",
                    "Performance bonds",
                    "Insurance policies"
                ],
                "risk_factors": [
                    "Project completion risk",
                    "Economic sensitivity",
                    "Weather delays"
                ],
                "strengths": [
                    "Long track record",
                    "Diversified projects",
                    "Strong equipment base"
                ]
            },
            "healthcare404": {
                "application_id": "LA-2024-007",
                "customer_id": "healthcare404",
                "customer_name": "Wellness Medical Center",
                "application_date": "2024-08-23",
                "loan_amount": 400000,
                "loan_purpose": "Medical equipment",
                "business_type": "Healthcare",
                "annual_revenue": 3000000,
                "credit_history_years": 10,
                "requested_amount": 400000,
                "purpose": "Medical equipment",
                "loan_term": 48,
                "interest_rate": 6.2,
                "collateral_type": "Medical equipment",
                "collateral_value": 600000,
                "application_status": "submitted",
                "submitted_documents": [
                    "Equipment specifications",
                    "Medical licenses",
                    "Insurance certificates",
                    "Financial statements"
                ],
                "risk_factors": [
                    "Regulatory changes",
                    "Insurance reimbursement delays",
                    "Equipment obsolescence"
                ],
                "strengths": [
                    "Stable industry",
                    "Recurring revenue",
                    "Professional staff"
                ]
            },
            "transport505": {
                "application_id": "LA-2024-008",
                "customer_id": "transport505",
                "customer_name": "Express Logistics Inc",
                "application_date": "2024-08-19",
                "loan_amount": 600000,
                "loan_purpose": "Fleet expansion",
                "business_type": "Transportation",
                "annual_revenue": 4000000,
                "credit_history_years": 7,
                "requested_amount": 600000,
                "purpose": "Fleet expansion",
                "loan_term": 60,
                "interest_rate": 7.0,
                "collateral_type": "Commercial vehicles",
                "collateral_value": 800000,
                "application_status": "submitted",
                "submitted_documents": [
                    "Vehicle quotes",
                    "Route analysis",
                    "Fuel cost projections",
                    "Driver contracts"
                ],
                "risk_factors": [
                    "Fuel price volatility",
                    "Driver shortage",
                    "Maintenance costs"
                ],
                "strengths": [
                    "Established routes",
                    "Long-term contracts",
                    "Experienced team"
                ]
            }
        }
    
    async def get_loan_application_info(self, customer_id: str) -> Dict[str, Any]:
        """Get loan application information for a customer"""
        if customer_id in self.loan_applications:
            return {
                "status": "success",
                "data": self.loan_applications[customer_id],
                "retrieved_at": datetime.now().isoformat()
            }
        else:
            return {
                "status": "not_found",
                "message": f"No loan application found for customer {customer_id}",
                "data": None,
                "retrieved_at": datetime.now().isoformat()
            }
    
    async def get_loan_amount(self, customer_id: str) -> float:
        """Get loan amount for a customer"""
        app_info = await self.get_loan_application_info(customer_id)
        if app_info["status"] == "success":
            return app_info["data"]["loan_amount"]
        return 0.0
    
    async def get_application_date(self, customer_id: str) -> str:
        """Get loan application date for a customer"""
        app_info = await self.get_loan_application_info(customer_id)
        if app_info["status"] == "success":
            return app_info["data"]["application_date"]
        return ""
    
    async def get_loan_purpose(self, customer_id: str) -> str:
        """Get loan purpose for a customer"""
        app_info = await self.get_loan_application_info(customer_id)
        if app_info["status"] == "success":
            return app_info["data"]["loan_purpose"]
        return ""
    
    async def get_collateral_info(self, customer_id: str) -> Dict[str, Any]:
        """Get collateral information for a customer"""
        app_info = await self.get_loan_application_info(customer_id)
        if app_info["status"] == "success":
            data = app_info["data"]
            return {
                "type": data["collateral_type"],
                "value": data["collateral_value"],
                "coverage_ratio": data["collateral_value"] / data["loan_amount"]
            }
        return {"type": "", "value": 0, "coverage_ratio": 0}
    
    async def get_risk_factors(self, customer_id: str) -> List[str]:
        """Get risk factors identified in the loan application"""
        app_info = await self.get_loan_application_info(customer_id)
        if app_info["status"] == "success":
            return app_info["data"]["risk_factors"]
        return []
    
    async def get_application_strengths(self, customer_id: str) -> List[str]:
        """Get strengths identified in the loan application"""
        app_info = await self.get_loan_application_info(customer_id)
        if app_info["status"] == "success":
            return app_info["data"]["strengths"]
        return []
    
    async def get_submitted_documents(self, customer_id: str) -> List[str]:
        """Get list of submitted documents"""
        app_info = await self.get_loan_application_info(customer_id)
        if app_info["status"] == "success":
            return app_info["data"]["submitted_documents"]
        return []
    
    async def get_submitted_applications(self) -> List[Dict[str, Any]]:
        """Get all loan applications with 'submitted' status"""
        submitted_apps = []
        for customer_id, app_data in self.loan_applications.items():
            if app_data["application_status"].lower() == "submitted":
                submitted_apps.append({
                    "customer_id": customer_id,
                    "application_data": app_data
                })
        return submitted_apps
    
    async def get_application_status(self, customer_id: str) -> str:
        """Get application status for a customer"""
        app_info = await self.get_loan_application_info(customer_id)
        if app_info["status"] == "success":
            return app_info["data"]["application_status"]
        return ""
    
    async def is_application_submitted(self, customer_id: str) -> bool:
        """Check if the application is in submitted status"""
        status = await self.get_application_status(customer_id)
        return status.lower() == "submitted"
