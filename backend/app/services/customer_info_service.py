from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

class CustomerInfoService:
    """Service for querying customer information including credit history and existing loans"""
    
    def __init__(self):
        # Mock database - in production, this would connect to a real database
        self.customer_data = self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> Dict[str, Any]:
        """Initialize mock customer data"""
        return {
            "test123": {
                "customer_id": "test123",
                "customer_name": "Test Company",
                "business_type": "Technology",
                "annual_revenue": 1000000,
                "credit_history_years": 5,
                "credit_score": 750,
                "existing_loans": [
                    {
                        "loan_id": "L-001",
                        "loan_type": "Business Line of Credit",
                        "amount": 200000,
                        "outstanding_balance": 150000,
                        "interest_rate": 6.5,
                        "start_date": "2023-01-15",
                        "end_date": "2025-01-15",
                        "payment_history": "Excellent",
                        "days_past_due": 0
                    },
                    {
                        "loan_id": "L-002",
                        "loan_type": "Equipment Loan",
                        "amount": 100000,
                        "outstanding_balance": 75000,
                        "interest_rate": 7.2,
                        "start_date": "2023-06-01",
                        "end_date": "2026-06-01",
                        "payment_history": "Good",
                        "days_past_due": 0
                    }
                ],
                "credit_history": {
                    "total_credit_lines": 8,
                    "active_credit_lines": 6,
                    "credit_utilization": 0.35,
                    "payment_history": {
                        "on_time_payments": 48,
                        "late_payments_30_days": 2,
                        "late_payments_60_days": 0,
                        "late_payments_90_days": 0
                    },
                    "credit_inquiries": {
                        "last_6_months": 2,
                        "last_12_months": 4
                    }
                },
                "banking_relationship": {
                    "primary_bank": "First National Bank",
                    "account_types": ["Business Checking", "Savings", "CD"],
                    "average_balance": 50000,
                    "relationship_years": 3
                },
                "business_financials": {
                    "cash_flow": "Positive",
                    "debt_to_income_ratio": 0.25,
                    "profit_margin": 0.15,
                    "liquidity_ratio": 2.5
                }
            },
            "cust456": {
                "customer_id": "cust456",
                "customer_name": "Manufacturing Corp",
                "business_type": "Manufacturing",
                "annual_revenue": 2500000,
                "credit_history_years": 3,
                "credit_score": 680,
                "existing_loans": [
                    {
                        "loan_id": "L-003",
                        "loan_type": "Term Loan",
                        "amount": 500000,
                        "outstanding_balance": 400000,
                        "interest_rate": 8.0,
                        "start_date": "2022-03-01",
                        "end_date": "2027-03-01",
                        "payment_history": "Fair",
                        "days_past_due": 15
                    }
                ],
                "credit_history": {
                    "total_credit_lines": 5,
                    "active_credit_lines": 4,
                    "credit_utilization": 0.65,
                    "payment_history": {
                        "on_time_payments": 36,
                        "late_payments_30_days": 5,
                        "late_payments_60_days": 1,
                        "late_payments_90_days": 0
                    },
                    "credit_inquiries": {
                        "last_6_months": 3,
                        "last_12_months": 6
                    }
                },
                "banking_relationship": {
                    "primary_bank": "Regional Bank",
                    "account_types": ["Business Checking", "Savings"],
                    "average_balance": 25000,
                    "relationship_years": 2
                },
                "business_financials": {
                    "cash_flow": "Variable",
                    "debt_to_income_ratio": 0.45,
                    "profit_margin": 0.08,
                    "liquidity_ratio": 1.2
                }
            }
        }
    
    async def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive customer information"""
        if customer_id in self.customer_data:
            return {
                "status": "success",
                "data": self.customer_data[customer_id],
                "retrieved_at": datetime.now().isoformat()
            }
        else:
            return {
                "status": "not_found",
                "message": f"No customer found with ID {customer_id}",
                "data": None,
                "retrieved_at": datetime.now().isoformat()
            }
    
    async def get_credit_history(self, customer_id: str) -> Dict[str, Any]:
        """Get customer credit history"""
        customer_info = await self.get_customer_info(customer_id)
        if customer_info["status"] == "success":
            return customer_info["data"]["credit_history"]
        return {}
    
    async def get_existing_loans(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get customer's existing loans"""
        customer_info = await self.get_customer_info(customer_id)
        if customer_info["status"] == "success":
            return customer_info["data"]["existing_loans"]
        return []
    
    async def get_credit_score(self, customer_id: str) -> int:
        """Get customer's credit score"""
        customer_info = await self.get_customer_info(customer_id)
        if customer_info["status"] == "success":
            return customer_info["data"]["credit_score"]
        return 0
    
    async def get_total_debt(self, customer_id: str) -> float:
        """Get customer's total outstanding debt"""
        existing_loans = await self.get_existing_loans(customer_id)
        return sum(loan["outstanding_balance"] for loan in existing_loans)
    
    async def get_payment_history_summary(self, customer_id: str) -> Dict[str, Any]:
        """Get summary of payment history"""
        credit_history = await self.get_credit_history(customer_id)
        if credit_history:
            payment_history = credit_history["payment_history"]
            total_payments = sum(payment_history.values())
            on_time_rate = payment_history["on_time_payments"] / total_payments if total_payments > 0 else 0
            
            return {
                "total_payments": total_payments,
                "on_time_rate": on_time_rate,
                "late_payments_30_days": payment_history["late_payments_30_days"],
                "late_payments_60_days": payment_history["late_payments_60_days"],
                "late_payments_90_days": payment_history["late_payments_90_days"]
            }
        return {}
    
    async def get_banking_relationship(self, customer_id: str) -> Dict[str, Any]:
        """Get banking relationship information"""
        customer_info = await self.get_customer_info(customer_id)
        if customer_info["status"] == "success":
            return customer_info["data"]["banking_relationship"]
        return {}
    
    async def get_business_financials(self, customer_id: str) -> Dict[str, Any]:
        """Get business financial metrics"""
        customer_info = await self.get_customer_info(customer_id)
        if customer_info["status"] == "success":
            return customer_info["data"]["business_financials"]
        return {}
    
    async def get_credit_utilization(self, customer_id: str) -> float:
        """Get credit utilization ratio"""
        credit_history = await self.get_credit_history(customer_id)
        if credit_history:
            return credit_history["credit_utilization"]
        return 0.0
    
    async def get_debt_to_income_ratio(self, customer_id: str) -> float:
        """Get debt-to-income ratio"""
        business_financials = await self.get_business_financials(customer_id)
        if business_financials:
            return business_financials["debt_to_income_ratio"]
        return 0.0
