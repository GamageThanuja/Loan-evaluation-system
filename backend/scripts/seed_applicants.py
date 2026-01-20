"""
Seed Applicants Script
Generates realistic applicant data with complete financial profiles for testing and demonstration
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random
from decimal import Decimal
import re

# Add parent directories to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

from database.client import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

CLEAR_EXISTING_DATA = False  # Set to True to clear existing seed data before seeding

# Applicant distribution
NUM_EXCELLENT_CREDIT = 8  # 800-850
NUM_VERY_GOOD_CREDIT = 7  # 740-799
NUM_GOOD_CREDIT = 5  # 670-739
NUM_FAIR_CREDIT = 4  # 580-669
NUM_HIGH_DTI = 3  # Good credit but high debt
NUM_INSUFFICIENT_INCOME = 3  # Fair credit but low income
NUM_SHORT_EMPLOYMENT = 2  # Good credit but short employment

# Sample data pools
FIRST_NAMES_M = ["James", "Michael", "Robert", "John", "David", "William", "Richard", "Joseph", "Thomas", "Christopher"]
FIRST_NAMES_F = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
              "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

CITIES = ["Colombo", "Kandy", "Galle", "Jaffna", "Negombo", "Anuradhapura", "Trincomalee", "Batticaloa", "Kurunegala", "Matara"]

EMPLOYERS = ["ABC Corporation", "Tech Solutions Ltd", "Global Enterprises", "National Bank", "Healthcare Plus", 
             "Education Services", "Manufacturing Co", "Retail Group", "Construction Ltd", "Transport Services"]

OCCUPATIONS = ["Software Engineer", "Accountant", "Manager", "Teacher", "Nurse", "Sales Executive", 
               "Marketing Specialist", "Engineer", "Analyst", "Administrator"]

LOAN_PURPOSES = ["purchase", "refinance", "home_improvement", "debt_consolidation", "business", "education", "medical", "other"]

LENDERS = ["Commercial Bank", "People's Bank", "Bank of Ceylon", "Sampath Bank", "HNB", "NDB", "DFCC", "Seylan Bank"]

# ============================================
# UTILITY FUNCTIONS
# ============================================

def random_date(start_days_ago: int, end_days_ago: int = 0) -> str:
    """Generate random date between start_days_ago and end_days_ago"""
    days_ago = random.randint(end_days_ago, start_days_ago)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")

def random_phone() -> str:
    """Generate random Sri Lankan phone number"""
    return f"+94{random.randint(700000000, 799999999)}"

NIC_PATTERN = re.compile(r"^\d{9}[VX]$")

def normalize_gender(gender: str) -> str:
    """Normalize gender values to M/F"""
    if not gender:
        return "M"
    value = str(gender).strip().lower()
    if value.startswith("f"):
        return "F"
    if value.startswith("m"):
        return "M"
    return "M"

def is_valid_nic(nic: str) -> bool:
    """Check NIC format (old Sri Lankan NIC format)"""
    if not nic:
        return False
    return bool(NIC_PATTERN.match(str(nic).strip().upper()))

def generate_nic_from_dob(dob: str, gender: str) -> str:
    """Generate Sri Lankan NIC from date of birth and gender (YYDDDXXXXV)"""
    birth_date = None
    if dob:
        try:
            birth_date = datetime.fromisoformat(str(dob).replace("Z", "+00:00"))
        except Exception:
            try:
                birth_date = datetime.strptime(str(dob), "%Y-%m-%d")
            except Exception:
                birth_date = None
    
    if not birth_date:
        year = random.randint(70, 99)
        days = random.randint(1, 366)
        suffix = random.randint(1000, 9999)
        return f"{year:02d}{days:03d}{suffix:04d}V"
    
    year = birth_date.year % 100
    day_of_year = birth_date.timetuple().tm_yday
    if normalize_gender(gender) == "F":
        day_of_year += 500
    suffix = random.randint(1000, 9999)
    return f"{year:02d}{day_of_year:03d}{suffix:04d}V"

def normalize_nic_value(nic: str) -> str:
    """Normalize NIC to uppercase format or return empty string"""
    if not nic:
        return ""
    normalized = str(nic).strip().upper()
    return normalized if is_valid_nic(normalized) else ""

def random_email(first_name: str, last_name: str) -> str:
    """Generate email address"""
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(domains)}"

def calculate_age_from_dob(dob: str) -> int:
    """Calculate age from date of birth"""
    birth_date = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.now()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# ============================================
# APPLICANT GENERATORS
# ============================================

def generate_base_applicant(gender: str = None) -> Dict[str, Any]:
    """Generate base applicant data"""
    if gender is None:
        gender = random.choice(["M", "F"])
    
    first_name = random.choice(FIRST_NAMES_M if gender == "M" else FIRST_NAMES_F)
    last_name = random.choice(LAST_NAMES)
    
    dob = random_date(365 * 60, 365 * 25)  # 25-60 years old
    nic = generate_nic_from_dob(dob, gender)
    
    return {
        "name": f"{first_name} {last_name}",
        "email": random_email(first_name, last_name),
        "phone": random_phone(),
        "nic": nic,
        "date_of_birth": dob,
        "gender": gender,
        "marital_status": random.choice(["Single", "Married", "Divorced", "Widowed"]),
        "education_level": random.choice(["High School", "Bachelor's Degree", "Master's Degree", "Doctorate", "Diploma"]),
        "address_line1": f"{random.randint(1, 999)} {random.choice(['Main', 'Park', 'Lake', 'Hill', 'Garden'])} Street",
        "city": random.choice(CITIES),
        "state": random.choice(["Western", "Central", "Southern", "Northern", "Eastern"]),
        "postal_code": f"{random.randint(10000, 99999)}",
        "country": "Sri Lanka",
        "employment_status": "Employed",
        "occupation": random.choice(OCCUPATIONS),
        "employer_name": random.choice(EMPLOYERS),
        "loan_purpose": random.choice(LOAN_PURPOSES),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

def generate_excellent_credit_applicant(created_by: str) -> Dict[str, Any]:
    """Generate applicant with excellent credit (800-850)"""
    applicant = generate_base_applicant()
    applicant.update({
        "credit_score": random.randint(800, 850),
        "monthly_income": round(random.uniform(250000, 500000), 2),
        "years_employed": round(random.uniform(5, 20), 1),
        "existing_loans_count": random.randint(0, 2),
        "existing_debt_amount": round(random.uniform(0, 500000), 2),
        "assets_value": round(random.uniform(2000000, 10000000), 2),
        "loan_amount": round(random.uniform(500000, 3000000), 2),
        "loan_term_months": random.choice([12, 24, 36, 48, 60]),
        "created_by": created_by
    })
    return applicant

def generate_good_credit_applicant(created_by: str) -> Dict[str, Any]:
    """Generate applicant with very good credit (740-799)"""
    applicant = generate_base_applicant()
    applicant.update({
        "credit_score": random.randint(740, 799),
        "monthly_income": round(random.uniform(150000, 300000), 2),
        "years_employed": round(random.uniform(3, 15), 1),
        "existing_loans_count": random.randint(1, 3),
        "existing_debt_amount": round(random.uniform(100000, 800000), 2),
        "assets_value": round(random.uniform(1000000, 5000000), 2),
        "loan_amount": round(random.uniform(300000, 2000000), 2),
        "loan_term_months": random.choice([12, 24, 36, 48, 60]),
        "created_by": created_by
    })
    return applicant

def generate_marginal_applicant(created_by: str) -> Dict[str, Any]:
    """Generate applicant with good credit (670-739)"""
    applicant = generate_base_applicant()
    applicant.update({
        "credit_score": random.randint(670, 739),
        "monthly_income": round(random.uniform(100000, 200000), 2),
        "years_employed": round(random.uniform(2, 10), 1),
        "existing_loans_count": random.randint(2, 4),
        "existing_debt_amount": round(random.uniform(200000, 1000000), 2),
        "assets_value": round(random.uniform(500000, 3000000), 2),
        "loan_amount": round(random.uniform(200000, 1000000), 2),
        "loan_term_months": random.choice([12, 24, 36, 48]),
        "created_by": created_by
    })
    return applicant

def generate_poor_credit_applicant(created_by: str) -> Dict[str, Any]:
    """Generate applicant with fair credit (580-669)"""
    applicant = generate_base_applicant()
    applicant.update({
        "credit_score": random.randint(580, 669),
        "monthly_income": round(random.uniform(80000, 150000), 2),
        "years_employed": round(random.uniform(1, 8), 1),
        "existing_loans_count": random.randint(3, 6),
        "existing_debt_amount": round(random.uniform(500000, 1500000), 2),
        "assets_value": round(random.uniform(200000, 1000000), 2),
        "loan_amount": round(random.uniform(150000, 800000), 2),
        "loan_term_months": random.choice([12, 24, 36]),
        "created_by": created_by
    })
    return applicant

def generate_high_dti_applicant(created_by: str) -> Dict[str, Any]:
    """Generate applicant with high debt-to-income ratio"""
    applicant = generate_base_applicant()
    monthly_income = round(random.uniform(150000, 250000), 2)
    applicant.update({
        "credit_score": random.randint(670, 739),
        "monthly_income": monthly_income,
        "years_employed": round(random.uniform(4, 12), 1),
        "existing_loans_count": random.randint(4, 7),
        "existing_debt_amount": round(monthly_income * random.uniform(8, 15), 2),  # High debt
        "assets_value": round(random.uniform(1000000, 4000000), 2),
        "loan_amount": round(random.uniform(500000, 1500000), 2),
        "loan_term_months": random.choice([24, 36, 48]),
        "created_by": created_by
    })
    return applicant

def generate_insufficient_income_applicant(created_by: str) -> Dict[str, Any]:
    """Generate applicant with insufficient income"""
    applicant = generate_base_applicant()
    monthly_income = round(random.uniform(50000, 100000), 2)
    applicant.update({
        "credit_score": random.randint(580, 669),
        "monthly_income": monthly_income,
        "years_employed": round(random.uniform(2, 8), 1),
        "existing_loans_count": random.randint(1, 3),
        "existing_debt_amount": round(random.uniform(100000, 500000), 2),
        "assets_value": round(random.uniform(300000, 1500000), 2),
        "loan_amount": round(random.uniform(800000, 2000000), 2),  # High loan amount relative to income
        "loan_term_months": random.choice([36, 48, 60]),
        "created_by": created_by
    })
    return applicant

def generate_short_employment_applicant(created_by: str) -> Dict[str, Any]:
    """Generate applicant with short employment history"""
    applicant = generate_base_applicant()
    applicant.update({
        "credit_score": random.randint(670, 739),
        "monthly_income": round(random.uniform(120000, 220000), 2),
        "years_employed": round(random.uniform(0.3, 1.5), 1),  # Less than 2 years
        "existing_loans_count": random.randint(1, 2),
        "existing_debt_amount": round(random.uniform(50000, 400000), 2),
        "assets_value": round(random.uniform(500000, 2000000), 2),
        "loan_amount": round(random.uniform(300000, 1000000), 2),
        "loan_term_months": random.choice([12, 24, 36]),
        "created_by": created_by
    })
    return applicant

# ============================================
# CREDIT HISTORY GENERATORS
# ============================================

def generate_credit_accounts(profile_type: str, applicant_id: str, credit_score: int) -> List[Dict[str, Any]]:
    """Generate credit account history based on profile type"""
    num_accounts = random.randint(2, 5)
    accounts = []
    
    for i in range(num_accounts):
        account_type = random.choice(["credit_card", "personal_loan", "auto_loan", "mortgage"])
        
        # Determine account status based on profile
        if profile_type in ["excellent", "good"]:
            account_status = random.choices(["open", "closed"], weights=[0.7, 0.3])[0]
        elif profile_type == "marginal":
            account_status = random.choices(["open", "closed"], weights=[0.6, 0.4])[0]
        else:  # poor credit
            account_status = random.choices(["open", "closed", "charged_off"], weights=[0.5, 0.3, 0.2])[0]
        
        opened_date = random_date(365 * 15, 365 * 1)  # 1-15 years ago
        closed_date = random_date(365 * 5, 0) if account_status == "closed" else None
        
        # Generate balances based on account type
        if account_type == "credit_card":
            credit_limit = round(random.uniform(100000, 1000000), 2)
            if profile_type in ["excellent", "good"]:
                balance = round(credit_limit * random.uniform(0.1, 0.4), 2)
            elif profile_type == "marginal":
                balance = round(credit_limit * random.uniform(0.3, 0.7), 2)
            else:
                balance = round(credit_limit * random.uniform(0.6, 0.95), 2)
            original_amount = None
        else:
            original_amount = round(random.uniform(500000, 5000000), 2)
            if account_status == "open":
                balance = round(original_amount * random.uniform(0.2, 0.8), 2)
            else:
                balance = 0
            credit_limit = None
        
        # Payment history based on profile
        if profile_type == "excellent":
            payment_history_score = random.randint(95, 100)
            on_time = random.randint(45, 50)
            late = random.randint(0, 2)
        elif profile_type == "good":
            payment_history_score = random.randint(85, 94)
            on_time = random.randint(38, 45)
            late = random.randint(2, 5)
        elif profile_type == "marginal":
            payment_history_score = random.randint(70, 84)
            on_time = random.randint(30, 40)
            late = random.randint(5, 10)
        else:
            payment_history_score = random.randint(40, 69)
            on_time = random.randint(15, 30)
            late = random.randint(10, 20)
        
        # Calculate utilization for credit cards
        utilization = None
        if account_type == "credit_card" and credit_limit and credit_limit > 0:
            utilization = round((balance / credit_limit) * 100, 2)
        
        account = {
            "applicant_id": applicant_id,
            "account_type": account_type,
            "account_status": account_status,
            "account_number": f"ACC{random.randint(100000, 999999)}",
            "balance": balance,
            "credit_limit": credit_limit,
            "original_amount": original_amount,
            "opened_date": opened_date,
            "closed_date": closed_date,
            "last_payment_date": random_date(60, 0) if account_status == "open" else closed_date,
            "payment_history_score": payment_history_score,
            "on_time_payments": on_time,
            "late_payments": late,
            "missed_payments": random.randint(0, late // 2),
            "credit_utilization": utilization,
            "months_since_last_delinquency": random.randint(6, 36) if late > 0 else None,
            "derogatory_marks": 1 if account_status == "charged_off" else 0,
            "lender_name": random.choice(LENDERS),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        accounts.append(account)
    
    return accounts

def determine_profile_type(credit_score: int) -> str:
    """Determine applicant profile type from credit score"""
    if credit_score >= 800:
        return "excellent"
    if credit_score >= 740:
        return "very_good"
    if credit_score >= 670:
        return "good"
    if credit_score >= 580:
        return "fair"
    return "poor"

# ============================================
# REPAYMENT HISTORY GENERATORS
# ============================================

def generate_loan_history(
    profile_type: str,
    applicant_id: str,
    primary_loan_amount: float = None,
    primary_term_months: int = None
) -> List[Dict[str, Any]]:
    """Generate loan repayment history based on profile type"""
    num_loans = random.randint(1, 3)
    loans = []
    
    for i in range(num_loans):
        loan_type = random.choice(["personal_loan", "auto_loan", "mortgage", "student_loan"])
        
        # Determine loan status
        if i < num_loans - 1:  # Earlier loans are more likely to be closed
            loan_status = random.choices(["closed", "paid_off"], weights=[0.6, 0.4])[0]
        else:  # Most recent loan
            if profile_type in ["excellent", "good"]:
                loan_status = random.choices(["active", "paid_off"], weights=[0.7, 0.3])[0]
            else:
                loan_status = random.choices(["active", "defaulted"], weights=[0.8, 0.2])[0]
        
        if primary_loan_amount and i == num_loans - 1:
            original_amount = float(primary_loan_amount)
        else:
            original_amount = round(random.uniform(300000, 5000000), 2)
        start_date = random_date(365 * 10, 365 * (i + 1))
        
        if loan_status in ["closed", "paid_off"]:
            end_date = random_date(365 * (i + 1), 30)
            remaining_balance = 0
            next_due_date = None
        elif loan_status == "defaulted":
            end_date = random_date(365 * 2, 180)
            remaining_balance = round(original_amount * random.uniform(0.4, 0.8), 2)
            next_due_date = None
        else:  # active
            end_date = None
            remaining_balance = round(original_amount * random.uniform(0.2, 0.7), 2)
            next_due_date = random_date(0, -30)  # Future date
        
        # Calculate term and monthly payment
        if primary_term_months and i == num_loans - 1:
            term_months = int(primary_term_months)
        else:
            term_months = random.choice([12, 24, 36, 48, 60, 84, 120])
        monthly_payment = round(original_amount / term_months * 1.1, 2)  # Simplified with interest
        
        # Payment performance based on profile
        total_payments = random.randint(12, min(60, term_months))
        
        if profile_type == "excellent":
            on_time_pct = random.uniform(95, 100)
            on_time = int(total_payments * on_time_pct / 100)
            late = total_payments - on_time
            avg_days_late = random.uniform(0, 2)
        elif profile_type == "good":
            on_time_pct = random.uniform(85, 94)
            on_time = int(total_payments * on_time_pct / 100)
            late = total_payments - on_time
            avg_days_late = random.uniform(2, 7)
        elif profile_type == "marginal":
            on_time_pct = random.uniform(70, 84)
            on_time = int(total_payments * on_time_pct / 100)
            late = total_payments - on_time
            avg_days_late = random.uniform(7, 15)
        else:
            on_time_pct = random.uniform(40, 69)
            on_time = int(total_payments * on_time_pct / 100)
            late = total_payments - on_time
            avg_days_late = random.uniform(15, 45)

        if loan_status in ["closed", "paid_off"]:
            payment_status = "closed"
        elif loan_status == "defaulted":
            payment_status = "defaulted"
        else:
            if on_time_pct >= 90:
                payment_status = "current"
            elif on_time_pct >= 75:
                payment_status = "late"
            else:
                payment_status = "delinquent"
        
        # Generate recent payments (last 6 months)
        recent_payments = []
        for month in range(6):
            payment_date = (datetime.now() - timedelta(days=30 * month)).strftime("%Y-%m-%d")
            is_late = random.random() > (on_time_pct / 100)
            days_late = random.randint(1, 30) if is_late else 0
            
            recent_payments.append({
                "date": payment_date,
                "amount": monthly_payment,
                "status": "late" if is_late else "paid",
                "days_late": days_late
            })
        
        loan = {
            "applicant_id": applicant_id,
            "loan_id": f"LOAN{random.randint(1000, 9999)}",
            "loan_type": loan_type,
            "loan_status": loan_status,
            "original_amount": original_amount,
            "remaining_balance": remaining_balance,
            "monthly_payment": monthly_payment,
            "interest_rate": round(random.uniform(6.5, 18.5), 2),
            "payment_status": payment_status,
            "start_date": start_date,
            "end_date": end_date,
            "maturity_date": (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=30 * term_months)).strftime("%Y-%m-%d"),
            "next_due_date": next_due_date,
            "on_time_payments": on_time,
            "late_payments": late,
            "missed_payments": random.randint(0, late // 2),
            "total_payments_made": total_payments,
            "recent_payments": recent_payments,
            "average_days_late": round(avg_days_late, 2),
            "largest_late_days": int(avg_days_late * random.uniform(2, 4)) if late > 0 else 0,
            "on_time_payment_percentage": round(on_time_pct, 2),
            "lender_name": random.choice(LENDERS),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        loans.append(loan)
    
    return loans

# ============================================
# TRANSACTION HISTORY GENERATORS
# ============================================

PAYMENT_METHODS = ["bank_transfer", "card", "cash", "online"]

def format_transaction_date(date_value: str, hour: int = 10) -> str:
    """Convert date string to ISO timestamp for transactions"""
    try:
        parsed = datetime.fromisoformat(str(date_value).replace("Z", ""))
    except Exception:
        try:
            parsed = datetime.strptime(str(date_value), "%Y-%m-%d")
        except Exception:
            parsed = datetime.utcnow()
    parsed = parsed.replace(
        hour=hour,
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=0
    )
    return parsed.isoformat()

def generate_transactions_for_loans(applicant_id: int, loans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate transaction history aligned to repayment history"""
    transactions = []
    
    for loan in loans:
        loan_id = loan.get("loan_id") or f"LOAN{random.randint(1000, 9999)}"
        original_amount = float(loan.get("original_amount", 0))
        start_date = loan.get("start_date") or datetime.utcnow().strftime("%Y-%m-%d")
        monthly_payment = float(loan.get("monthly_payment") or 0)
        
        if monthly_payment <= 0 and original_amount > 0:
            monthly_payment = round(original_amount / random.choice([12, 24, 36, 48, 60]), 2)
        
        balance = original_amount
        
        # Disbursement
        transactions.append({
            "applicant_id": applicant_id,
            "loan_id": loan_id,
            "transaction_date": format_transaction_date(start_date, hour=9),
            "transaction_type": "disbursement",
            "amount": original_amount,
            "description": "Loan disbursement",
            "status": "completed",
            "payment_method": "bank_transfer",
            "reference_number": f"DISB-{loan_id}",
            "balance": balance,
            "notes": None
        })
        
        # Origination fee
        fee_amount = round(original_amount * random.uniform(0.005, 0.02), 2)
        if fee_amount > 0:
            balance += fee_amount
            transactions.append({
                "applicant_id": applicant_id,
                "loan_id": loan_id,
                "transaction_date": format_transaction_date(start_date, hour=11),
                "transaction_type": "fee",
                "amount": fee_amount,
                "description": "Loan origination fee",
                "status": "completed",
                "payment_method": "bank_transfer",
                "reference_number": f"FEE-{loan_id}",
                "balance": balance,
                "notes": None
            })
        
        # Payments
        recent_payments = loan.get("recent_payments", [])
        if not recent_payments:
            recent_payments = []
            for month in range(6):
                payment_date = (datetime.now() - timedelta(days=30 * month)).strftime("%Y-%m-%d")
                recent_payments.append({
                    "date": payment_date,
                    "amount": monthly_payment,
                    "status": "paid",
                    "days_late": 0
                })
        
        for idx, payment in enumerate(recent_payments):
            payment_amount = float(payment.get("amount", monthly_payment))
            payment_status = payment.get("status", "paid")
            transaction_status = "completed" if payment_status == "paid" else "pending"
            if transaction_status == "completed":
                balance = max(balance - payment_amount, 0)
            
            transactions.append({
                "applicant_id": applicant_id,
                "loan_id": loan_id,
                "transaction_date": format_transaction_date(payment.get("date"), hour=10),
                "transaction_type": "payment",
                "amount": payment_amount,
                "description": "Loan repayment",
                "status": transaction_status,
                "payment_method": random.choice(PAYMENT_METHODS),
                "reference_number": f"PAY-{loan_id}-{idx + 1}",
                "balance": balance,
                "notes": "Late payment" if payment.get("days_late", 0) > 0 else None
            })
            
            if payment.get("days_late", 0) > 0:
                penalty_amount = round(payment_amount * random.uniform(0.01, 0.03), 2)
                balance += penalty_amount
                transactions.append({
                    "applicant_id": applicant_id,
                    "loan_id": loan_id,
                    "transaction_date": format_transaction_date(payment.get("date"), hour=15),
                    "transaction_type": "penalty",
                    "amount": penalty_amount,
                    "description": "Late payment penalty",
                    "status": "completed",
                    "payment_method": "bank_transfer",
                    "reference_number": f"PEN-{loan_id}-{idx + 1}",
                    "balance": balance,
                    "notes": f"Late by {payment.get('days_late', 0)} days"
                })
    
    return transactions

# ============================================
# AUDIT LOG GENERATORS
# ============================================

def generate_audit_logs_for_applicant(
    applicant: Dict[str, Any],
    loans: List[Dict[str, Any]],
    transactions: List[Dict[str, Any]],
    default_user_id: str
) -> List[Dict[str, Any]]:
    """Generate audit logs aligned with loan and transaction history"""
    applicant_id = applicant.get("id")
    created_by = applicant.get("created_by") or default_user_id
    logs = []
    
    # Creation log
    logs.append({
        "user_id": created_by,
        "action": "created",
        "resource_type": "applicant",
        "resource_id": str(applicant_id),
        "details": {
            "description": "Loan application created",
            "performed_by": {
                "id": created_by,
                "name": "Loan Officer",
                "role": "loan_officer"
            }
        },
        "created_at": applicant.get("created_at", datetime.utcnow().isoformat())
    })
    
    # Eligibility review log
    if applicant.get("eligibility_status"):
        logs.append({
            "user_id": created_by,
            "action": "reviewed",
            "resource_type": "applicant",
            "resource_id": str(applicant_id),
            "details": {
                "description": f"Eligibility check completed - {applicant.get('eligibility_status')}",
                "performed_by": {
                    "id": "system",
                    "name": "System",
                    "role": "system"
                }
            },
            "created_at": applicant.get("updated_at", datetime.utcnow().isoformat())
        })
    
    # Status change log
    status = applicant.get("status", "pending")
    if status == "under_review":
        logs.append({
            "user_id": created_by,
            "action": "status_changed",
            "resource_type": "applicant",
            "resource_id": str(applicant_id),
            "details": {
                "description": "Application sent for manager review",
                "performed_by": {
                    "id": created_by,
                    "name": "Loan Officer",
                    "role": "loan_officer"
                },
                "changes": [
                    {"field": "status", "old_value": "pending", "new_value": "under_review"}
                ]
            },
            "created_at": applicant.get("updated_at", datetime.utcnow().isoformat())
        })
    elif status == "approved":
        approved_by = applicant.get("approved_by") or default_user_id
        logs.append({
            "user_id": approved_by,
            "action": "approved",
            "resource_type": "applicant",
            "resource_id": str(applicant_id),
            "details": {
                "description": "Loan application approved",
                "performed_by": {
                    "id": approved_by,
                    "name": "Bank Manager",
                    "role": "manager"
                },
                "metadata": {"amount": applicant.get("loan_amount")}
            },
            "created_at": applicant.get("approved_at", applicant.get("updated_at", datetime.utcnow().isoformat()))
        })
    elif status == "rejected":
        rejected_by = applicant.get("rejected_by") or default_user_id
        logs.append({
            "user_id": rejected_by,
            "action": "rejected",
            "resource_type": "applicant",
            "resource_id": str(applicant_id),
            "details": {
                "description": f"Loan application rejected: {applicant.get('rejection_reason', 'Not specified')}",
                "performed_by": {
                    "id": rejected_by,
                    "name": "Bank Manager",
                    "role": "manager"
                }
            },
            "created_at": applicant.get("rejected_at", applicant.get("updated_at", datetime.utcnow().isoformat()))
        })
    
    # Payment logs
    payment_transactions = [
        tx for tx in transactions
        if tx.get("transaction_type") == "payment" and tx.get("status") == "completed"
    ]
    payment_transactions.sort(key=lambda t: t.get("transaction_date", ""), reverse=True)
    
    for payment in payment_transactions[:2]:
        logs.append({
            "user_id": created_by,
            "action": "payment_made",
            "resource_type": "applicant",
            "resource_id": str(applicant_id),
            "details": {
                "description": f"Payment received of LKR {payment.get('amount')}",
                "performed_by": {
                    "id": created_by,
                    "name": "System",
                    "role": "system"
                },
                "metadata": {
                    "reference_number": payment.get("reference_number"),
                    "loan_id": payment.get("loan_id")
                }
            },
            "created_at": payment.get("transaction_date", datetime.utcnow().isoformat())
        })
    
    return logs

# ============================================
# MAIN SEEDING FUNCTION
# ============================================

def seed_applicants():
    """Main function to seed applicants with complete financial profiles"""
    print("=" * 80)
    print("LOAN EVALUATION SYSTEM - DATA SEEDING")
    print("=" * 80)
    print()
    
    # Get a user ID for created_by (use first user or create a system user)
    try:
        # Try to get an existing user
        users_response = db.client.table("users").select("id").limit(1).execute()
        if users_response.data:
            created_by = users_response.data[0]["id"]
        else:
            print("❌ No users found in database. Please create at least one user first.")
            return
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return
    
    print(f"✅ Using user ID: {created_by}")
    print()
    
    # Clear existing data if requested
    if CLEAR_EXISTING_DATA:
        print("⚠️  Clearing existing seed data...")
        try:
            # Note: This will cascade delete credit_history and repayment_history
            db.client.table("applicants").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print("✅ Existing data cleared")
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
    
    print()
    print("📊 Generating applicants...")
    print()
    
    all_applicants = []
    all_credit_history = []
    all_repayment_history = []
    all_transactions = []
    all_audit_logs = []
    
    # Generate applicants by profile type
    profile_generators = [
        ("excellent", NUM_EXCELLENT_CREDIT, generate_excellent_credit_applicant),
        ("very_good", NUM_VERY_GOOD_CREDIT, generate_good_credit_applicant),
        ("good", NUM_GOOD_CREDIT, generate_marginal_applicant),
        ("fair", NUM_FAIR_CREDIT, generate_poor_credit_applicant),
        ("high_dti", NUM_HIGH_DTI, generate_high_dti_applicant),
        ("insufficient_income", NUM_INSUFFICIENT_INCOME, generate_insufficient_income_applicant),
        ("short_employment", NUM_SHORT_EMPLOYMENT, generate_short_employment_applicant),
    ]
    
    for profile_type, count, generator_func in profile_generators:
        print(f"  Generating {count} {profile_type.replace('_', ' ')} applicants...")
        
        for _ in range(count):
            applicant = generator_func(created_by)
            all_applicants.append(applicant)
    
    print()
    print(f"✅ Generated {len(all_applicants)} applicants")
    print()
    
    # Insert applicants
    print("💾 Inserting applicants into database...")
    try:
        response = db.client.table("applicants").insert(all_applicants).execute()
        inserted_applicants = response.data
        print(f"✅ Inserted {len(inserted_applicants)} applicants")
    except Exception as e:
        print(f"❌ Error inserting applicants: {e}")
        return
    
    print()
    print("📈 Generating credit and repayment history...")
    print()
    
    # Generate credit and repayment history for each applicant
    for i, applicant_data in enumerate(inserted_applicants):
        applicant_id = applicant_data["id"]
        credit_score = applicant_data.get("credit_score", 650)
        
        # Determine profile type based on credit score
        if credit_score >= 800:
            profile_type = "excellent"
        elif credit_score >= 740:
            profile_type = "very_good"
        elif credit_score >= 670:
            profile_type = "good"
        elif credit_score >= 580:
            profile_type = "fair"
        else:
            profile_type = "poor"
        
        # Generate credit accounts
        credit_accounts = generate_credit_accounts(profile_type, applicant_id, credit_score)
        all_credit_history.extend(credit_accounts)
        
        # Generate loan history
        loans = generate_loan_history(
            profile_type,
            applicant_id,
            primary_loan_amount=applicant_data.get("loan_amount"),
            primary_term_months=applicant_data.get("loan_term_months")
        )
        all_repayment_history.extend(loans)
        
        # Generate transactions aligned to loans
        transactions = generate_transactions_for_loans(applicant_id, loans)
        all_transactions.extend(transactions)
        
        # Generate audit logs aligned to transactions
        audit_logs = generate_audit_logs_for_applicant(applicant_data, loans, transactions, created_by)
        all_audit_logs.extend(audit_logs)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(inserted_applicants)} applicants...")
    
    print()
    print(f"✅ Generated {len(all_credit_history)} credit accounts")
    print(f"✅ Generated {len(all_repayment_history)} loan records")
    print(f"✅ Generated {len(all_transactions)} transactions")
    print(f"✅ Generated {len(all_audit_logs)} audit logs")
    print()
    
    # Insert credit history
    print("💾 Inserting credit history...")
    try:
        db.bulk_create_credit_history(all_credit_history)
        print(f"✅ Inserted {len(all_credit_history)} credit history records")
    except Exception as e:
        print(f"❌ Error inserting credit history: {e}")
    
    print()
    
    # Insert repayment history
    print("💾 Inserting repayment history...")
    try:
        db.bulk_create_repayment_history(all_repayment_history)
        print(f"✅ Inserted {len(all_repayment_history)} repayment history records")
    except Exception as e:
        print(f"❌ Error inserting repayment history: {e}")

    print()
    
    # Insert transactions
    print("💾 Inserting transactions...")
    try:
        db.bulk_create_transactions(all_transactions)
        print(f"✅ Inserted {len(all_transactions)} transactions")
    except Exception as e:
        print(f"❌ Error inserting transactions: {e}")
    
    print()
    
    # Insert audit logs
    print("💾 Inserting audit logs...")
    try:
        db.bulk_create_audit_logs(all_audit_logs)
        print(f"✅ Inserted {len(all_audit_logs)} audit logs")
    except Exception as e:
        print(f"❌ Error inserting audit logs: {e}")
    
    print()
    print("=" * 80)
    print("SEEDING COMPLETE!")
    print("=" * 80)
    print()
    print("📊 Summary:")
    print(f"  Total Applicants: {len(inserted_applicants)}")
    print(f"  - Excellent Credit (800-850): {NUM_EXCELLENT_CREDIT}")
    print(f"  - Very Good Credit (740-799): {NUM_VERY_GOOD_CREDIT}")
    print(f"  - Good Credit (670-739): {NUM_GOOD_CREDIT}")
    print(f"  - Fair Credit (580-669): {NUM_FAIR_CREDIT}")
    print(f"  - High DTI: {NUM_HIGH_DTI}")
    print(f"  - Insufficient Income: {NUM_INSUFFICIENT_INCOME}")
    print(f"  - Short Employment: {NUM_SHORT_EMPLOYMENT}")
    print()
    print(f"  Total Credit Accounts: {len(all_credit_history)}")
    print(f"  Total Loan Records: {len(all_repayment_history)}")
    print(f"  Total Transactions: {len(all_transactions)}")
    print(f"  Total Audit Logs: {len(all_audit_logs)}")
    print()
    print("✅ All applicants now have complete financial profiles!")
    print()

def seed_existing_applicants():
    """Seed missing histories and NICs for existing applicants"""
    print("=" * 80)
    print("LOAN EVALUATION SYSTEM - BACKFILL EXISTING APPLICANTS")
    print("=" * 80)
    print()
    
    # Get a default user ID for audit logs
    try:
        users_response = db.client.table("users").select("id").limit(1).execute()
        if users_response.data:
            default_user_id = users_response.data[0]["id"]
        else:
            print("❌ No users found in database. Please create at least one user first.")
            return
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return
    
    # Fetch all applicants with pagination
    applicants = []
    start = 0
    batch_size = 200
    
    while True:
        response = (
            db.client.table("applicants")
            .select("*")
            .range(start, start + batch_size - 1)
            .execute()
        )
        batch = response.data or []
        if not batch:
            break
        applicants.extend(batch)
        if len(batch) < batch_size:
            break
        start += batch_size
    
    if not applicants:
        print("❌ No applicants found to backfill.")
        return
    
    print(f"✅ Found {len(applicants)} applicants")
    print()
    
    updated_nic_count = 0
    credit_seeded = 0
    repayment_seeded = 0
    transaction_seeded = 0
    audit_seeded = 0
    
    for idx, applicant in enumerate(applicants):
        applicant_id = applicant.get("id")
        if not applicant_id:
            continue
        
        # Ensure NIC exists and is valid
        existing_nic = normalize_nic_value(applicant.get("nic"))
        if not existing_nic:
            new_nic = generate_nic_from_dob(
                str(applicant.get("date_of_birth")),
                applicant.get("gender")
            )
            db.update_applicant(applicant_id, {"nic": new_nic})
            applicant["nic"] = new_nic
            updated_nic_count += 1
        
        credit_score = applicant.get("credit_score") or 650
        profile_type = determine_profile_type(int(credit_score))
        
        # Seed credit history if missing
        credit_accounts = db.get_credit_history_by_applicant(applicant_id)
        if not credit_accounts:
            new_credit_accounts = generate_credit_accounts(profile_type, applicant_id, int(credit_score))
            if new_credit_accounts:
                db.bulk_create_credit_history(new_credit_accounts)
                credit_seeded += 1
        
        # Seed repayment history if missing
        loan_records = db.get_repayment_history_by_applicant(applicant_id)
        if not loan_records:
            loan_records = generate_loan_history(
                profile_type,
                applicant_id,
                primary_loan_amount=applicant.get("loan_amount"),
                primary_term_months=applicant.get("loan_term_months")
            )
            if loan_records:
                db.bulk_create_repayment_history(loan_records)
                repayment_seeded += 1
        
        # Seed transactions if missing
        existing_transactions = db.get_transactions_by_applicant(applicant_id)
        if not existing_transactions:
            transactions = generate_transactions_for_loans(applicant_id, loan_records or [])
            if transactions:
                db.bulk_create_transactions(transactions)
                transaction_seeded += 1
                existing_transactions = transactions
        
        # Seed audit logs if missing
        existing_audit_logs = db.get_audit_logs(applicant_id)
        if not existing_audit_logs:
            audit_logs = generate_audit_logs_for_applicant(
                applicant,
                loan_records or [],
                existing_transactions or [],
                default_user_id
            )
            if audit_logs:
                db.bulk_create_audit_logs(audit_logs)
                audit_seeded += 1
        
        if (idx + 1) % 10 == 0:
            print(f"  Processed {idx + 1}/{len(applicants)} applicants...")
    
    print()
    print("=" * 80)
    print("BACKFILL COMPLETE!")
    print("=" * 80)
    print(f"  Applicants updated with NIC: {updated_nic_count}")
    print(f"  Credit history seeded: {credit_seeded}")
    print(f"  Repayment history seeded: {repayment_seeded}")
    print(f"  Transactions seeded: {transaction_seeded}")
    print(f"  Audit logs seeded: {audit_seeded}")
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed applicants and related data")
    parser.add_argument("--existing", action="store_true", help="Backfill data for existing applicants")
    parser.add_argument("--clear-existing", action="store_true", help="Clear existing applicants before seeding")
    args = parser.parse_args()
    
    if args.clear_existing:
        CLEAR_EXISTING_DATA = True
    
    if args.existing:
        seed_existing_applicants()
    else:
        seed_applicants()
