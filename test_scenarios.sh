#!/bin/bash

# Base URL
API_URL="http://localhost:8000/api"

# Login to get token (Update with your credentials)
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "mgamagethanuja21@gmail.com", "password": "#MGt@0621"}')

# Extract token (requires jq)
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Login failed. Please check credentials in the script."
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "Token received: ${TOKEN:0:10}..."

# Function to create applicant
create_applicant() {
    echo "Creating applicant: $1"
    curl -s -X POST "$API_URL/applicants" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "$2" | jq .
    echo "----------------------------------------"
}

# 1. High Loan Amount (Risk: Debt-to-Income / Loan Amount)
# Income: 100,000, Loan: 5,000,000 (50x income), Term: 60 months
create_applicant "High Loan Risk" '{
    "first_name": "Risk",
    "last_name": "HighLoan",
    "email": "risk.highloan@example.com",
    "phone": "0771234567",
    "nic": "199012345678",
    "date_of_birth": "1990-01-01",
    "gender": "M",
    "marital_status": "Single",
    "address": "123 High St",
    "city": "Colombo",
    "district": "Colombo",
    "postal_code": "00100",
    "employment_type": "Salaried",
    "employer_name": "Tech Corp",
    "job_title": "Engineer",
    "employment_length": 5,
    "monthly_income": 100000,
    "education_level": "Bachelors",
    "loan_amount": 5000000,
    "loan_purpose": "Home",
    "loan_term_months": 60,
    "credit_score": 750,
    "existing_loans": 0
}'

# 2. Low Credit Score (Risk: Credit History)
# Income: 150,000, Loan: 500,000, Term: 24, Credit Score: 400 (Poor)
create_applicant "Low Credit Score Risk" '{
    "first_name": "Risk",
    "last_name": "LowCredit",
    "email": "risk.lowcredit@example.com",
    "phone": "0777654321",
    "nic": "199212345678",
    "date_of_birth": "1992-05-05",
    "gender": "F",
    "marital_status": "Married",
    "address": "456 Low St",
    "city": "Kandy",
    "district": "Kandy",
    "postal_code": "20000",
    "employment_type": "Salaried",
    "employer_name": "Retail Co",
    "job_title": "Manager",
    "employment_length": 3,
    "monthly_income": 150000,
    "education_level": "Diploma",
    "loan_amount": 500000,
    "loan_purpose": "Personal",
    "loan_term_months": 24,
    "credit_score": 400,
    "existing_loans": 1
}'

# 3. Short Employment (Risk: Stability)
# Income: 200,000, Loan: 1,000,000, Employment: 0.5 years (6 months)
create_applicant "Short Employment Risk" '{
    "first_name": "Risk",
    "last_name": "ShortJob",
    "email": "risk.shortjob@example.com",
    "phone": "0712345678",
    "nic": "199512345678",
    "date_of_birth": "1995-10-10",
    "gender": "M",
    "marital_status": "Single",
    "address": "789 New Job Rd",
    "city": "Galle",
    "district": "Galle",
    "postal_code": "80000",
    "employment_type": "Salaried",
    "employer_name": "Startup Inc",
    "job_title": "Developer",
    "employment_length": 0,
    "monthly_income": 200000,
    "education_level": "Bachelors",
    "loan_amount": 1000000,
    "loan_purpose": "Vehicle",
    "loan_term_months": 36,
    "credit_score": 700,
    "existing_loans": 0
}'

# 4. Low Income / High Debt (Risk: Affordability)
# Income: 30,000, Loan: 500,000, Monthly payment > 60% of income
create_applicant "Low Income Risk" '{
    "first_name": "Risk",
    "last_name": "LowIncome",
    "email": "risk.lowincome@example.com",
    "phone": "0765432109",
    "nic": "199812345678",
    "date_of_birth": "1998-03-03",
    "gender": "F",
    "marital_status": "Single",
    "address": "321 Budget Ln",
    "city": "Matara",
    "district": "Matara",
    "postal_code": "81000",
    "employment_type": "Self-Employed",
    "employer_name": "Self",
    "job_title": "Freelancer",
    "employment_length": 2,
    "monthly_income": 30000,
    "education_level": "AL",
    "loan_amount": 500000,
    "loan_purpose": "Business",
    "loan_term_months": 24,
    "credit_score": 650,
    "existing_loans": 0
}'

echo "Done."
