"""
Credit Score & Loan Reasoning Module
=====================================
Provides credit score classification and multi-factor loan evaluation
with actionable suggestions for Sri Lankan banks.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class CreditScoreRating(Enum):
    """Credit score classification per standard ranges"""
    POOR = "Poor"
    FAIR = "Fair"
    GOOD = "Good"
    VERY_GOOD = "Very Good"
    EXCEPTIONAL = "Exceptional"


@dataclass
class CreditScoreInfo:
    """Credit score information"""
    score: int
    rating: CreditScoreRating
    description: str
    
    @classmethod
    def from_score(cls, score: int) -> 'CreditScoreInfo':
        """Create CreditScoreInfo from numeric score - using simple, friendly language"""
        if score < 580:
            return cls(score, CreditScoreRating.POOR, 
                      "Your credit score is low, which usually means there were some payment problems in the past.")
        elif score < 670:
            return cls(score, CreditScoreRating.FAIR,
                      "Your credit score is fair - not bad, but there's room for improvement.")
        elif score < 740:
            return cls(score, CreditScoreRating.GOOD,
                      "Your credit score is good! You have a solid history of paying on time.")
        elif score < 800:
            return cls(score, CreditScoreRating.VERY_GOOD,
                      "Your credit score is very good! You've been great at managing your money.")
        else:
            return cls(score, CreditScoreRating.EXCEPTIONAL,
                      "Your credit score is excellent! You're a top-tier borrower.")


@dataclass
class RiskFactor:
    """A factor contributing to loan risk"""
    factor_name: str
    severity: str  # "critical", "major", "moderate", "minor"
    current_value: str
    expected_value: str
    impact_description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "factor_name": self.factor_name,
            "severity": self.severity,
            "current_value": self.current_value,
            "expected_value": self.expected_value,
            "impact_description": self.impact_description
        }


@dataclass
class Suggestion:
    """Actionable suggestion to improve eligibility"""
    action: str
    reason: str
    expected_improvement: str
    priority: int  # 1 = highest
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "expected_improvement": self.expected_improvement,
            "priority": self.priority
        }


@dataclass
class LoanDecision:
    """Complete loan decision with reasoning"""
    eligible: bool
    decision: str  # "APPROVE" or "REJECT"
    probability: float
    risk_level: str
    confidence: float
    
    # Multi-factor analysis
    risk_factors: List[RiskFactor] = field(default_factory=list)
    protective_factors: List[RiskFactor] = field(default_factory=list)
    
    # Credit score analysis
    credit_score_info: Optional[CreditScoreInfo] = None
    
    # Suggestions
    suggestions: List[Suggestion] = field(default_factory=list)
    
    # Alternative offer
    alternative_amount: Optional[float] = None
    alternative_term: Optional[int] = None
    
    # Summary
    summary: str = ""
    detailed_explanation: str = ""


class LoanReasoningEngine:
    """
    Multi-factor loan evaluation engine with credit score rules
    and actionable suggestions.
    """
    
    # Credit score thresholds
    CREDIT_SCORE_POOR = 580
    CREDIT_SCORE_FAIR = 670
    CREDIT_SCORE_GOOD = 740
    CREDIT_SCORE_VERY_GOOD = 800
    
    # Business rules for Sri Lankan banks
    MAX_LOAN_AMOUNT = 1_000_000  # LKR
    MIN_LOAN_AMOUNT = 50_000
    MAX_DTI_RATIO = 0.40  # 40% debt-to-income
    MAX_LOAN_TO_INCOME = 5.0  # 5x annual income
    
    # Interest rate (annual)
    INTEREST_RATE = 0.12  # 12%
    
    def __init__(self):
        self.risk_factors: List[RiskFactor] = []
        self.protective_factors: List[RiskFactor] = []
        self.suggestions: List[Suggestion] = []
    
    def classify_credit_score(self, score: int) -> CreditScoreInfo:
        """Classify credit score per standard ranges"""
        return CreditScoreInfo.from_score(score)
    
    def calculate_monthly_payment(self, principal: float, term_months: int, annual_rate: float = None) -> float:
        """Calculate EMI using standard formula"""
        if annual_rate is None:
            annual_rate = self.INTEREST_RATE
        
        monthly_rate = annual_rate / 12
        if monthly_rate == 0:
            return principal / term_months
        
        emi = principal * monthly_rate * ((1 + monthly_rate) ** term_months) / (((1 + monthly_rate) ** term_months) - 1)
        return emi
    
    def calculate_max_affordable_loan(self, monthly_income: float, term_months: int) -> float:
        """Calculate maximum affordable loan based on income"""
        max_payment = monthly_income * self.MAX_DTI_RATIO
        monthly_rate = self.INTEREST_RATE / 12
        
        if monthly_rate == 0:
            return max_payment * term_months
        
        # Reverse EMI calculation
        max_loan = max_payment * (((1 + monthly_rate) ** term_months) - 1) / (monthly_rate * ((1 + monthly_rate) ** term_months))
        return min(max_loan, self.MAX_LOAN_AMOUNT)
    
    def analyze_credit_score(self, credit_score: int) -> Tuple[CreditScoreInfo, Optional[RiskFactor], Optional[Suggestion]]:
        """Analyze credit score and generate risk factor/suggestion if needed"""
        
        score_info = self.classify_credit_score(credit_score)
        risk_factor = None
        suggestion = None
        
        if score_info.rating == CreditScoreRating.POOR:
            risk_factor = RiskFactor(
                factor_name="Credit Score",
                severity="critical",
                current_value=f"{credit_score} ({score_info.rating.value})",
                expected_value="670+ (Good)",
                impact_description="Your credit score is too low. This usually happens when there have been missed payments or unpaid debts."
            )
            suggestion = Suggestion(
                action="Work on improving your credit score to at least 670",
                reason=f"Your score of {credit_score} is in the 'Poor' range - banks see this as risky.",
                expected_improvement="Getting to 'Good' (670+) would greatly improve your chances",
                priority=1
            )
        elif score_info.rating == CreditScoreRating.FAIR:
            risk_factor = RiskFactor(
                factor_name="Credit Score",
                severity="major",
                current_value=f"{credit_score} ({score_info.rating.value})",
                expected_value="670+ (Good)",
                impact_description="Your credit score is okay but could be better. You might still qualify if other factors are strong."
            )
            suggestion = Suggestion(
                action="Try to raise your credit score above 670",
                reason=f"Your score of {credit_score} is 'Fair' - good enough for some loans, but not the best rates.",
                expected_improvement="Reaching 'Good' would help you get better loan terms",
                priority=2
            )
        
        return score_info, risk_factor, suggestion
    
    def analyze_income_ratio(self, loan_amount: float, annual_income: float, monthly_income: float, 
                            loan_term_months: int) -> Tuple[Optional[RiskFactor], Optional[Suggestion]]:
        """Analyze loan-to-income and payment-to-income ratios"""
        
        loan_to_income = loan_amount / annual_income if annual_income > 0 else 999
        monthly_payment = self.calculate_monthly_payment(loan_amount, loan_term_months)
        payment_to_income = monthly_payment / monthly_income if monthly_income > 0 else 999
        
        risk_factor = None
        suggestion = None
        
        # Check payment-to-income (DTI)
        if payment_to_income > 0.50:
            risk_factor = RiskFactor(
                factor_name="Payment-to-Income Ratio",
                severity="critical",
                current_value=f"{payment_to_income*100:.1f}%",
                expected_value=f"< {self.MAX_DTI_RATIO*100:.0f}%",
                impact_description=f"The monthly payment of LKR {monthly_payment:,.0f} would take up {payment_to_income*100:.1f}% of your salary - that's too much to be comfortable."
            )
            max_affordable = self.calculate_max_affordable_loan(monthly_income, loan_term_months)
            suggestion = Suggestion(
                action=f"Try a smaller loan of LKR {max_affordable:,.0f} or less",
                reason=f"The current payment would use {payment_to_income*100:.1f}% of your income (we recommend less than {self.MAX_DTI_RATIO*100:.0f}%)",
                expected_improvement=f"A loan of LKR {max_affordable:,.0f} would be more manageable",
                priority=1
            )
        elif payment_to_income > self.MAX_DTI_RATIO:
            risk_factor = RiskFactor(
                factor_name="Payment-to-Income Ratio",
                severity="major",
                current_value=f"{payment_to_income*100:.1f}%",
                expected_value=f"< {self.MAX_DTI_RATIO*100:.0f}%",
                impact_description=f"The monthly payment would take {payment_to_income*100:.1f}% of your salary - a bit too high."
            )
            max_affordable = self.calculate_max_affordable_loan(monthly_income, loan_term_months)
            suggestion = Suggestion(
                action=f"Consider reducing to LKR {max_affordable:,.0f}",
                reason=f"This exceeds our {self.MAX_DTI_RATIO*100:.0f}% guideline",
                expected_improvement=f"LKR {max_affordable:,.0f} would be easier to repay",
                priority=2
            )
        
        # Check loan-to-income ratio
        if loan_to_income > self.MAX_LOAN_TO_INCOME:
            if risk_factor is None or risk_factor.severity != "critical":
                risk_factor = RiskFactor(
                    factor_name="Loan-to-Income Ratio",
                    severity="major",
                    current_value=f"{loan_to_income:.1f}x annual income",
                    expected_value=f"< {self.MAX_LOAN_TO_INCOME:.0f}x annual income",
                    impact_description=f"The loan is {loan_to_income:.1f} times your yearly salary - that's higher than we'd normally approve."
                )
            if suggestion is None:
                suggestion = Suggestion(
                    action=f"Aim for a loan around {self.MAX_LOAN_TO_INCOME:.0f}x your annual income (LKR {annual_income * self.MAX_LOAN_TO_INCOME:,.0f})",
                    reason=f"Currently asking for {loan_to_income:.1f}x income, but our limit is {self.MAX_LOAN_TO_INCOME:.0f}x",
                    expected_improvement="A smaller amount would be more likely to get approved",
                    priority=2
                )
        
        return risk_factor, suggestion
    
    def analyze_employment(self, days_employed: int) -> Tuple[Optional[RiskFactor], Optional[Suggestion]]:
        """Analyze employment stability with simple explanations"""
        
        years_employed = abs(days_employed) / 365 if days_employed else 0
        
        risk_factor = None
        suggestion = None
        
        if years_employed < 0.5:
            risk_factor = RiskFactor(
                factor_name="Employment Duration",
                severity="major",
                current_value=f"{years_employed:.1f} years",
                expected_value="> 1 year",
                impact_description="You're fairly new at your current job. Banks prefer to see at least 1 year of stable employment."
            )
            suggestion = Suggestion(
                action="Wait until you've been at your job for at least 1 year",
                reason=f"You've been at your job for only {years_employed:.1f} years - lenders like to see more stability",
                expected_improvement="Having 1+ year at the same job makes a big difference in getting approved",
                priority=3
            )
        elif years_employed < 1:
            risk_factor = RiskFactor(
                factor_name="Employment Duration",
                severity="moderate",
                current_value=f"{years_employed:.1f} years",
                expected_value="> 1 year",
                impact_description="You're close to 1 year at your job - a bit more time would help your application."
            )
        
        return risk_factor, suggestion
    
    def evaluate_loan(
        self,
        model_probability: float,
        loan_amount: float,
        monthly_income: float,
        loan_term_months: int,
        credit_score: Optional[int] = None,
        days_employed: Optional[int] = None,
        ext_source_mean: Optional[float] = None
    ) -> LoanDecision:
        """
        Complete multi-factor loan evaluation.
        
        Returns a LoanDecision with all risk factors, suggestions, and alternatives.
        """
        
        self.risk_factors = []
        self.protective_factors = []
        self.suggestions = []
        
        annual_income = monthly_income * 12
        monthly_payment = self.calculate_monthly_payment(loan_amount, loan_term_months)
        payment_to_income = monthly_payment / monthly_income if monthly_income > 0 else 999
        loan_to_income = loan_amount / annual_income if annual_income > 0 else 999
        
        # Estimate credit score from EXT_SOURCE if not provided
        if credit_score is None and ext_source_mean is not None:
            # Convert ext_source (0-1) to credit score range (300-850)
            credit_score = int(300 + ext_source_mean * 550)
        elif credit_score is None:
            credit_score = 650  # Default assumption
        
        # 1. Analyze Credit Score
        score_info, score_risk, score_suggestion = self.analyze_credit_score(credit_score)
        if score_risk:
            self.risk_factors.append(score_risk)
        if score_suggestion:
            self.suggestions.append(score_suggestion)
        
        # 2. Analyze Income Ratios
        income_risk, income_suggestion = self.analyze_income_ratio(
            loan_amount, annual_income, monthly_income, loan_term_months
        )
        if income_risk:
            self.risk_factors.append(income_risk)
        if income_suggestion:
            self.suggestions.append(income_suggestion)
        
        # 3. Analyze Employment
        if days_employed is not None:
            emp_risk, emp_suggestion = self.analyze_employment(days_employed)
            if emp_risk:
                self.risk_factors.append(emp_risk)
            if emp_suggestion:
                self.suggestions.append(emp_suggestion)
        
        # 4. Check loan amount limits
        if loan_amount > self.MAX_LOAN_AMOUNT:
            self.risk_factors.append(RiskFactor(
                factor_name="Loan Amount Limit",
                severity="critical",
                current_value=f"LKR {loan_amount:,.0f}",
                expected_value=f"< LKR {self.MAX_LOAN_AMOUNT:,.0f}",
                impact_description=f"The loan amount you're asking for is more than our maximum limit of LKR {self.MAX_LOAN_AMOUNT:,.0f}."
            ))
            self.suggestions.append(Suggestion(
                action=f"Apply for LKR {self.MAX_LOAN_AMOUNT:,.0f} or less",
                reason="This is the maximum we can offer",
                expected_improvement="Staying within our limit will make approval possible",
                priority=1
            ))
        
        # 5. Identify protective factors - using friendly language
        if score_info.rating in [CreditScoreRating.GOOD, CreditScoreRating.VERY_GOOD, CreditScoreRating.EXCEPTIONAL]:
            self.protective_factors.append(RiskFactor(
                factor_name="Credit Score",
                severity="positive",
                current_value=f"{credit_score} ({score_info.rating.value})",
                expected_value="",
                impact_description=f"Great credit score of {credit_score}! This shows you're reliable with payments."
            ))
        
        if payment_to_income < 0.25:
            self.protective_factors.append(RiskFactor(
                factor_name="Payment Affordability",
                severity="positive",
                current_value=f"{payment_to_income*100:.1f}% of income",
                expected_value="",
                impact_description="The monthly payments are very affordable for your income level."
            ))
        
        if days_employed and abs(days_employed) / 365 > 3:
            self.protective_factors.append(RiskFactor(
                factor_name="Job Stability",
                severity="positive",
                current_value=f"{abs(days_employed)/365:.1f} years",
                expected_value="",
                impact_description="You've been at your job for a while - that's a sign of stable income."
            ))
        
        # 6. Make decision
        # Critical risk factors = reject
        critical_risks = [r for r in self.risk_factors if r.severity == "critical"]
        major_risks = [r for r in self.risk_factors if r.severity == "major"]
        
        # Decision logic: model probability + rule-based factors
        threshold = 0.80  # High threshold for high-risk system accuracy
        
        # Stricter for critical risks
        if critical_risks:
            eligible = False
        elif major_risks and model_probability < 0.6:  # If major risks exist, need higher prob
            eligible = False
        elif model_probability < threshold:
            eligible = False
        else:
            eligible = True
        
        # Calculate risk level (Higher Prob = Lower Risk / Better Candidate)
        if model_probability >= 0.8:
            risk_level = "Very Low Risk"
        elif model_probability >= 0.65:
            risk_level = "Low Risk"
        elif model_probability >= 0.5:
            risk_level = "Medium Risk"
        elif model_probability >= 0.35:
            risk_level = "High Risk"
        else:
            risk_level = "Very High Risk"
        
        # Calculate alternative offer if rejected
        alternative_amount = None
        alternative_term = None
        if not eligible:
            max_affordable = self.calculate_max_affordable_loan(monthly_income, loan_term_months)
            if max_affordable >= self.MIN_LOAN_AMOUNT:
                alternative_amount = min(max_affordable * 0.9, self.MAX_LOAN_AMOUNT)  # 90% of max for safety
                alternative_term = loan_term_months
        
        # Generate summary
        summary = self._generate_summary(
            eligible, model_probability, loan_amount, monthly_income,
            payment_to_income, loan_to_income, score_info, critical_risks, major_risks
        )
        
        detailed = self._generate_detailed_explanation(
            eligible, score_info, self.risk_factors, self.protective_factors, self.suggestions
        )
        
        # Sort suggestions by priority
        self.suggestions.sort(key=lambda s: s.priority)
        
        return LoanDecision(
            eligible=eligible,
            decision="APPROVE" if eligible else "REJECT",
            probability=model_probability,
            risk_level=risk_level,
            confidence=0.85 if len(self.protective_factors) > len(self.risk_factors) else 0.75,
            risk_factors=self.risk_factors,
            protective_factors=self.protective_factors,
            credit_score_info=score_info,
            suggestions=self.suggestions,
            alternative_amount=alternative_amount,
            alternative_term=alternative_term,
            summary=summary,
            detailed_explanation=detailed
        )
    
    def _generate_summary(
        self, eligible: bool, probability: float, loan_amount: float,
        monthly_income: float, payment_to_income: float, loan_to_income: float,
        score_info: CreditScoreInfo, critical_risks: List, major_risks: List
    ) -> str:
        """Generate simple, human-readable summary that anyone can understand"""
        
        if eligible:
            return (
                f"✅ Good News - Your Loan is Approved! "
                f"Your credit score of {score_info.score} ({score_info.rating.value}) looks good, "
                f"and your monthly payment of LKR {self.calculate_monthly_payment(loan_amount, 36):,.0f} "
                f"is about {payment_to_income*100:.0f}% of your salary - that's manageable!"
            )
        else:
            reasons = []
            if critical_risks:
                reasons.append(critical_risks[0].impact_description)
            if major_risks and len(reasons) < 2:
                reasons.append(major_risks[0].impact_description)
            if not reasons:
                # If probability is success probability, risk is (1 - prob)
                risk_prob = (1 - probability) * 100
                reasons.append(f"Our assessment shows a {risk_prob:.0f}% chance of payment difficulties.")
            
            return (
                f"❌ Sorry, We Can't Approve This Loan Right Now. "
                + " ".join(reasons)
            )
    
    def _generate_detailed_explanation(
        self, eligible: bool, score_info: CreditScoreInfo,
        risk_factors: List[RiskFactor], protective_factors: List[RiskFactor],
        suggestions: List[Suggestion]
    ) -> str:
        """Generate detailed explanation in simple, friendly language"""
        
        lines = []
        
        # Credit Score Section - Simple
        lines.append(f"**About Your Credit Score:**")
        lines.append(f"Your score is {score_info.score} - that's considered '{score_info.rating.value}'")
        lines.append(score_info.description)
        lines.append("")
        
        # Risk Factors - Simple language
        if risk_factors:
            lines.append("**Things We're Concerned About:**")
            for i, rf in enumerate(risk_factors, 1):
                severity_emoji = "🔴" if rf.severity == "critical" else "🟡" if rf.severity == "major" else "⚪"
                lines.append(f"{severity_emoji} {rf.factor_name}")
                lines.append(f"   Your situation: {rf.current_value}")
                if rf.expected_value:
                    lines.append(f"   What we'd like to see: {rf.expected_value}")
                lines.append(f"   {rf.impact_description}")
            lines.append("")
        
        # Protective Factors - Simple language
        if protective_factors:
            lines.append("**Things Working in Your Favor:**")
            for pf in protective_factors:
                lines.append(f"✅ {pf.factor_name}: {pf.current_value}")
                lines.append(f"   {pf.impact_description}")
            lines.append("")
        
        # Suggestions - Simple, actionable
        if suggestions and not eligible:
            lines.append("**What You Can Do to Improve:**")
            for i, s in enumerate(suggestions, 1):
                lines.append(f"{i}. {s.action}")
                lines.append(f"   Why: {s.reason}")
                lines.append(f"   What to expect: {s.expected_improvement}")
            lines.append("")
        
        return "\n".join(lines)


# Singleton instance
reasoning_engine = LoanReasoningEngine()


def evaluate_loan_application(
    model_probability: float,
    loan_amount: float,
    monthly_income: float,
    loan_term_months: int = 36,
    credit_score: Optional[int] = None,
    days_employed: Optional[int] = None,
    ext_source_mean: Optional[float] = None
) -> Dict[str, Any]:
    """
    Main entry point for loan evaluation.
    Returns complete decision with reasoning as dictionary.
    """
    decision = reasoning_engine.evaluate_loan(
        model_probability=model_probability,
        loan_amount=loan_amount,
        monthly_income=monthly_income,
        loan_term_months=loan_term_months,
        credit_score=credit_score,
        days_employed=days_employed,
        ext_source_mean=ext_source_mean
    )
    
    return {
        "eligible": decision.eligible,
        "decision": decision.decision,
        "probability": decision.probability,
        "risk_level": decision.risk_level,
        "confidence": decision.confidence,
        "credit_score": {
            "score": decision.credit_score_info.score,
            "rating": decision.credit_score_info.rating.value,
            "description": decision.credit_score_info.description
        } if decision.credit_score_info else None,
        "risk_factors": [rf.to_dict() for rf in decision.risk_factors],
        "protective_factors": [pf.to_dict() for pf in decision.protective_factors],
        "suggestions": [s.to_dict() for s in decision.suggestions],
        "alternative_offer": {
            "amount": decision.alternative_amount,
            "term_months": decision.alternative_term
        } if decision.alternative_amount else None,
        "summary": decision.summary,
        "detailed_explanation": decision.detailed_explanation
    }


def get_credit_score_rating(score: int) -> CreditScoreRating:
    """Get credit score rating from numeric score (convenience function)"""
    return CreditScoreInfo.from_score(score).rating
