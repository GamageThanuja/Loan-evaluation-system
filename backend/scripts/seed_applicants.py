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

def random_nic() -> str:
    """Generate random NIC number"""
    year = random.randint(70, 99)
    days = random.randint(1, 366)
    suffix = random.randint(1000, 9999)
    return f"{year}{days:03d}{suffix}V"

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
    
    return {
        "name": f"{first_name} {last_name}",
        "email": random_email(first_name, last_name),
        "phone": random_phone(),
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

# ============================================
# REPAYMENT HISTORY GENERATORS
# ============================================

def generate_loan_history(profile_type: str, applicant_id: str) -> List[Dict[str, Any]]:
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
        loans = generate_loan_history(profile_type, applicant_id)
        all_repayment_history.extend(loans)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(inserted_applicants)} applicants...")
    
    print()
    print(f"✅ Generated {len(all_credit_history)} credit accounts")
    print(f"✅ Generated {len(all_repayment_history)} loan records")
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
    print()
    print("✅ All applicants now have complete financial profiles!")
    print()

if __name__ == "__main__":
    seed_applicants()
