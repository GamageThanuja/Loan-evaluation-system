#!/usr/bin/env python3
"""
LoanWise - Sri Lankan Loan Applicants
Clean production data for the loan evaluation system.
"""

import sys
import os

# Add the project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from database.client import SupabaseClient

def setup_production_data():
    db = SupabaseClient()
    client = db._client
    
    # Get user ID
    users = client.table('users').select('id').limit(1).execute()
    user_id = users.data[0]['id']
    
    # Clear existing applicants
    print("Clearing existing applicants...")
    client.table('applicants').delete().gte('id', 1).execute()
    print("Database cleared.\n")
    
    # Sri Lankan applicants with complete, realistic details
    applicants = [
        # ELIGIBLE APPLICANTS (2)
        {
            "name": "Kavindu Perera",
            "email": "kavindu.perera@gmail.com",
            "phone": "+94 77 123 4567",
            "date_of_birth": "1985-06-15",
            "gender": "Male",
            "marital_status": "Married",
            "education_level": "Graduate",
            "nic": "198515602345",
            "employment_status": "Employed",
            "occupation": "Senior Software Engineer",
            "employer_name": "Virtusa (Pvt) Ltd",
            "years_employed": 8,
            "monthly_income": 450000,
            "credit_score": 765,
            "existing_loans_count": 1,
            "existing_debt_amount": 800000,
            "assets_value": 4500000,
            "loan_amount": 2500000,
            "loan_purpose": "home_improvement",
            "loan_term_months": 36,
            "address_line1": "45/2 Flower Road",
            "city": "Colombo 07",
            "state": "Western Province",
            "postal_code": "00700",
            "country": "Sri Lanka",
            "status": "pending",
            "created_by": user_id
        },
        {
            "name": "Nimali Fernando",
            "email": "nimali.fernando@yahoo.com",
            "phone": "+94 71 987 6543",
            "date_of_birth": "1990-03-22",
            "gender": "Female",
            "marital_status": "Single",
            "education_level": "Graduate",
            "nic": "199075604321",
            "employment_status": "Employed",
            "occupation": "Chartered Accountant",
            "employer_name": "KPMG Sri Lanka",
            "years_employed": 6,
            "monthly_income": 380000,
            "credit_score": 720,
            "existing_loans_count": 0,
            "existing_debt_amount": 0,
            "assets_value": 3200000,
            "loan_amount": 1800000,
            "loan_purpose": "education",
            "loan_term_months": 48,
            "address_line1": "12 Temple Lane",
            "city": "Kandy",
            "state": "Central Province",
            "postal_code": "20000",
            "country": "Sri Lanka",
            "status": "pending",
            "created_by": user_id
        },
        
        # NON-ELIGIBLE APPLICANTS (2)
        {
            "name": "Ruwan Jayasinghe",
            "email": "ruwan.jayasinghe@gmail.com",
            "phone": "+94 76 555 1234",
            "date_of_birth": "1992-11-08",
            "gender": "Male",
            "marital_status": "Single",
            "education_level": "Not Graduate",
            "nic": "199228901234",
            "employment_status": "Unemployed",
            "occupation": "Currently seeking employment",
            "employer_name": "",
            "years_employed": 0,
            "monthly_income": 25000,
            "credit_score": 420,
            "existing_loans_count": 3,
            "existing_debt_amount": 650000,
            "assets_value": 50000,
            "loan_amount": 1500000,
            "loan_purpose": "debt_consolidation",
            "loan_term_months": 24,
            "address_line1": "78 Old Moor Street",
            "city": "Colombo 12",
            "state": "Western Province",
            "postal_code": "01200",
            "country": "Sri Lanka",
            "status": "pending",
            "created_by": user_id
        },
        {
            "name": "Chamari Wickramasinghe",
            "email": "chamari.w@outlook.com",
            "phone": "+94 75 222 3333",
            "date_of_birth": "1988-07-30",
            "gender": "Female",
            "marital_status": "Divorced",
            "education_level": "High School",
            "nic": "198821205678",
            "employment_status": "Part-Time",
            "occupation": "Sales Assistant",
            "employer_name": "Odel PLC",
            "years_employed": 1,
            "monthly_income": 35000,
            "credit_score": 380,
            "existing_loans_count": 4,
            "existing_debt_amount": 1200000,
            "assets_value": 75000,
            "loan_amount": 2000000,
            "loan_purpose": "other",
            "loan_term_months": 18,
            "address_line1": "23 Station Road",
            "city": "Galle",
            "state": "Southern Province",
            "postal_code": "80000",
            "country": "Sri Lanka",
            "status": "pending",
            "created_by": user_id
        },
        
        # BORDERLINE APPLICANTS (2) - Model will decide
        {
            "name": "Tharushi Silva",
            "email": "tharushi.silva@gmail.com",
            "phone": "+94 70 111 2222",
            "date_of_birth": "1993-09-12",
            "gender": "Female",
            "marital_status": "Married",
            "education_level": "Graduate",
            "nic": "199326305432",
            "employment_status": "Contract",
            "occupation": "Graphic Designer",
            "employer_name": "Leo Burnett Sri Lanka",
            "years_employed": 3,
            "monthly_income": 120000,
            "credit_score": 590,
            "existing_loans_count": 1,
            "existing_debt_amount": 300000,
            "assets_value": 950000,
            "loan_amount": 1200000,
            "loan_purpose": "business",
            "loan_term_months": 36,
            "address_line1": "56 Duplication Road",
            "city": "Colombo 04",
            "state": "Western Province",
            "postal_code": "00400",
            "country": "Sri Lanka",
            "status": "pending",
            "created_by": user_id
        },
        {
            "name": "Asanka Bandara",
            "email": "asanka.bandara@hotmail.com",
            "phone": "+94 78 444 5555",
            "date_of_birth": "1987-01-25",
            "gender": "Male",
            "marital_status": "Married",
            "education_level": "High School",
            "nic": "198702503456",
            "employment_status": "Self-Employed",
            "occupation": "Three-Wheeler Owner",
            "employer_name": "Self",
            "years_employed": 5,
            "monthly_income": 85000,
            "credit_score": 560,
            "existing_loans_count": 2,
            "existing_debt_amount": 450000,
            "assets_value": 800000,
            "loan_amount": 1000000,
            "loan_purpose": "business",
            "loan_term_months": 30,
            "address_line1": "112 Main Street",
            "city": "Negombo",
            "state": "Western Province",
            "postal_code": "11500",
            "country": "Sri Lanka",
            "status": "pending",
            "created_by": user_id
        }
    ]
    
    print("Adding Sri Lankan loan applicants...\n")
    
    for applicant in applicants:
        result = client.table('applicants').insert(applicant).execute()
        if result.data:
            credit = applicant['credit_score']
            income = applicant['monthly_income']
            loan = applicant['loan_amount']
            
            if credit >= 700:
                category = "ELIGIBLE"
            elif credit < 500:
                category = "NON-ELIGIBLE"
            else:
                category = "BORDERLINE"
            
            print(f"  {applicant['name']}")
            print(f"    Category: {category}")
            print(f"    Occupation: {applicant['occupation']}")
            print(f"    Monthly Income: LKR {income:,}")
            print(f"    Loan Request: LKR {loan:,} for {applicant['loan_term_months']} months")
            print(f"    Credit Score: {credit}")
            print()
    
    print("Setup complete. 6 applicants ready for evaluation.")

if __name__ == "__main__":
    setup_production_data()
