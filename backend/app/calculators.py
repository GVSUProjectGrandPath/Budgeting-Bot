"""
pgpfinlitbot Financial Calculators
Deterministic math calculations for loans, compound interest, and budgets.
"""

import math
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from fpdf import FPDF
from pathlib import Path
import tempfile                   # ← NEW (for a portable temp dir)

# ── Configuration ────────────────────────────────────────────
# Use the OS temp directory so it exists on Windows & Unix
DOWNLOADS_DIR = Path(tempfile.gettempdir()) / "pgpbot_downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
# ------------------------------------------------------------

class LoanCalculator:
    """Student loan payment and amortization calculations"""

    @staticmethod
    def calculate_monthly_payment(principal: float, annual_rate: float, years: int) -> float:
        """Calculate monthly payment using standard amortization formula"""
        if annual_rate == 0:
            return principal / (years * 12)

        monthly_rate = annual_rate / 100 / 12
        num_payments = years * 12

        monthly_payment = principal * (
            monthly_rate * (1 + monthly_rate) ** num_payments
        ) / ((1 + monthly_rate) ** num_payments - 1)

        return round(monthly_payment, 2)

    @staticmethod
    def generate_amortization_schedule(
        principal: float,
        annual_rate: float,
        years: int,
        extra_payment: float = 0
    ) -> List[Dict]:
        """Generate complete amortization schedule"""
        monthly_payment = LoanCalculator.calculate_monthly_payment(principal, annual_rate, years)
        monthly_rate = annual_rate / 100 / 12

        schedule = []
        balance = principal
        payment_date = datetime.now()

        payment_num = 1
        total_interest = 0

        while balance > 0.01 and payment_num <= years * 12 + 120:  # Safety limit
            interest_payment = balance * monthly_rate
            principal_payment = min(monthly_payment + extra_payment - interest_payment, balance)

            if principal_payment <= 0:
                principal_payment = balance
                interest_payment = 0

            balance -= principal_payment
            total_interest += interest_payment

            schedule.append({
                'payment_number': payment_num,
                'payment_date': payment_date.strftime('%Y-%m-%d'),
                'beginning_balance': round(balance + principal_payment, 2),
                'payment_amount': round(monthly_payment + extra_payment, 2),
                'principal': round(principal_payment, 2),
                'interest': round(interest_payment, 2),
                'ending_balance': round(balance, 2),
                'cumulative_interest': round(total_interest, 2)
            })

            payment_date += timedelta(days=30)  # Approximate monthly
            payment_num += 1

            if balance <= 0:
                break

        return schedule

    @staticmethod
    def calculate_payoff_scenarios(principal: float, annual_rate: float, years: int) -> Dict:
        """Calculate various payoff scenarios"""
        base_payment = LoanCalculator.calculate_monthly_payment(principal, annual_rate, years)

        scenarios = {
            'minimum_payment': {
                'monthly_payment': base_payment,
                'total_payments': years * 12,
                'total_interest': 0,
                'total_cost': 0
            }
        }

        # Calculate minimum scenario
        schedule = LoanCalculator.generate_amortization_schedule(principal, annual_rate, years)
        scenarios['minimum_payment']['total_payments'] = len(schedule)
        scenarios['minimum_payment']['total_interest'] = schedule[-1]['cumulative_interest']
        scenarios['minimum_payment']['total_cost'] = principal + scenarios['minimum_payment']['total_interest']

        # Extra payment scenarios
        for extra in [50, 100, 200]:
            schedule_extra = LoanCalculator.generate_amortization_schedule(
                principal, annual_rate, years, extra
            )
            scenarios[f'extra_{extra}'] = {
                'monthly_payment': base_payment + extra,
                'total_payments': len(schedule_extra),
                'total_interest': schedule_extra[-1]['cumulative_interest'],
                'total_cost': principal + schedule_extra[-1]['cumulative_interest'],
                'savings_vs_minimum': scenarios['minimum_payment']['total_interest'] - schedule_extra[-1]['cumulative_interest'],
                'time_saved_months': scenarios['minimum_payment']['total_payments'] - len(schedule_extra)
            }

        return scenarios


class CompoundInterestCalculator:
    """Savings and investment growth calculations"""

    @staticmethod
    def calculate_future_value(
        principal: float,
        monthly_contribution: float,
        annual_rate: float,
        years: int,
        compound_frequency: int = 12
    ) -> Dict:
        """Calculate future value with regular contributions"""

        # Convert to effective rates
        periodic_rate = annual_rate / 100 / compound_frequency
        total_periods = years * compound_frequency
        contribution_periods = years * 12  # Monthly contributions

        # Future value of initial principal
        fv_principal = principal * (1 + periodic_rate) ** total_periods

        # Future value of monthly contributions (ordinary annuity)
        if periodic_rate > 0:
            # Adjust for different compounding vs contribution frequency
            effective_monthly_rate = (1 + periodic_rate) ** (compound_frequency / 12) - 1
            fv_contributions = monthly_contribution * (
                ((1 + effective_monthly_rate) ** contribution_periods - 1) / effective_monthly_rate
            )
        else:
            fv_contributions = monthly_contribution * contribution_periods

        total_fv = fv_principal + fv_contributions
        total_contributions = principal + (monthly_contribution * contribution_periods)
        total_interest = total_fv - total_contributions

        return {
            'future_value': round(total_fv, 2),
            'total_contributions': round(total_contributions, 2),
            'total_interest': round(total_interest, 2),
            'effective_rate': round(total_interest / total_contributions * 100, 2) if total_contributions > 0 else 0,
            'monthly_contribution': monthly_contribution,
            'years': years,
            'annual_rate': annual_rate
        }

    @staticmethod
    def calculate_required_savings(target_amount: float, years: int, annual_rate: float) -> Dict:
        """Calculate required monthly savings to reach target"""
        months = years * 12
        monthly_rate = annual_rate / 100 / 12

        if monthly_rate > 0:
            required_monthly = target_amount * monthly_rate / ((1 + monthly_rate) ** months - 1)
        else:
            required_monthly = target_amount / months

        return {
            'required_monthly_savings': round(required_monthly, 2),
            'target_amount': target_amount,
            'years': years,
            'annual_rate': annual_rate,
            'total_contributions': round(required_monthly * months, 2)
        }


class BudgetTemplateGenerator:
    """Generate personalized budget templates"""

    @staticmethod
    def create_student_budget_template(
        monthly_income: float,
        housing_cost: float = None,
        meal_plan: float = None,
        user_name: str = "Student"
    ) -> Dict:
        """Create a comprehensive student budget template"""

        # Standard student expense categories with recommended percentages
        budget_categories = {
            'Housing': {
                'amount': housing_cost or monthly_income * 0.35,
                'percentage': 35,
                'description': 'Rent, utilities, dorm fees'
            },
            'Food': {
                'amount': meal_plan or monthly_income * 0.20,
                'percentage': 20,
                'description': 'Meal plan, groceries, dining out'
            },
            'Transportation': {
                'amount': monthly_income * 0.10,
                'percentage': 10,
                'description': 'Bus pass, gas, car maintenance'
            },
            'Textbooks & Supplies': {
                'amount': monthly_income * 0.08,
                'percentage': 8,
                'description': 'Books, software, lab materials'
            },
            'Personal Care': {
                'amount': monthly_income * 0.05,
                'percentage': 5,
                'description': 'Clothing, hygiene, healthcare'
            },
            'Entertainment': {
                'amount': monthly_income * 0.07,
                'percentage': 7,
                'description': 'Movies, subscriptions, social activities'
            },
            'Emergency Fund': {
                'amount': monthly_income * 0.10,
                'percentage': 10,
                'description': 'Unexpected expenses'
            },
            'Savings': {
                'amount': monthly_income * 0.05,
                'percentage': 5,
                'description': 'Long-term savings goals'
            }
        }

        # Calculate totals
        total_expenses = sum(cat['amount'] for cat in budget_categories.values())
        remaining = monthly_income - total_expenses

        return {
            'user_name': user_name,
            'monthly_income': monthly_income,
            'budget_categories': budget_categories,
            'total_expenses': round(total_expenses, 2),
            'remaining_balance': round(remaining, 2),
            'creation_date': datetime.now().strftime('%Y-%m-%d'),
            'recommendations': BudgetTemplateGenerator._generate_recommendations(
                monthly_income, budget_categories, remaining)
        }

    @staticmethod
    def _generate_recommendations(income: float, categories: Dict, remaining: float) -> List[str]:
        """Generate personalized budget recommendations"""
        recommendations = []

        if remaining < 0:
            recommendations.append(f"⚠️ Budget deficit of ${abs(remaining):.2f}. Consider reducing discretionary spending.")

            discretionary = ['Entertainment', 'Personal Care', 'Food']
            for category in discretionary:
                if category in categories and categories[category]['amount'] > income * 0.05:
                    recommendations.append(f"💡 Consider reducing {category} spending by ${categories[category]['amount'] * 0.1:.2f}")

        elif remaining > income * 0.15:
            recommendations.append(f"✅ Great job! You have ${remaining:.2f} leftover. Consider increasing savings or emergency fund.")

        if categories['Emergency Fund']['amount'] < income * 0.08:
            recommendations.append("🚨 Emergency fund is below recommended 10% of income. Try to increase this gradually.")

        if categories['Savings']['amount'] < income * 0.05:
            recommendations.append("📈 Consider increasing savings to at least 5% of income for long-term goals.")

        if categories['Food']['amount'] > income * 0.25:
            recommendations.append("🍕 Food costs seem high. Consider meal prep and cooking more meals at home.")

        return recommendations


class FileGenerator:
    """Generate downloadable files (CSV, PDF)"""

    @staticmethod
    def create_loan_schedule_csv(schedule: List[Dict], file_id: str = None) -> str:
        """Create CSV file for loan amortization schedule"""
        if not file_id:
            file_id = str(uuid.uuid4())

        file_path = DOWNLOADS_DIR / f"loan_schedule_{file_id}.csv"

        pd.DataFrame(schedule).to_csv(file_path, index=False)
        return file_id

    @staticmethod
    def create_budget_template_csv(budget_data: Dict, file_id: str = None) -> str:
        """Create CSV budget template with formulas"""
        if not file_id:
            file_id = str(uuid.uuid4())

        file_path = DOWNLOADS_DIR / f"budget_template_{file_id}.csv"

        # Create rows
        rows = []
        rows.append(['pgpfinlitbot Budget Template', f"Generated for {budget_data['user_name']}", budget_data['creation_date']])
        rows.append([])
        rows.append(['Category', 'Budgeted Amount', 'Actual Spent', 'Difference', 'Notes'])

        # Income row
        rows.append(['INCOME', budget_data['monthly_income'], '', "=B4-C4", ''])
        rows.append([])

        rows.append(['EXPENSES', '', '', '', ''])
        for category, data in budget_data['budget_categories'].items():
            row_num = len(rows) + 1
            rows.append([
                category,
                data['amount'],
                '',
                f"=B{row_num}-C{row_num}",
                data['description']
            ])

        rows.append([])
        expense_start = 8
        expense_end = expense_start + len(budget_data['budget_categories'])

        rows.append(['TOTAL EXPENSES', f"=SUM(B{expense_start}:B{expense_end})",
                     f"=SUM(C{expense_start}:C{expense_end})", f"=B{len(rows)+1}-C{len(rows)+1}", ''])
        rows.append(['NET INCOME', f"=B4-B{len(rows)}", f"=B4-C{len(rows)-1}",
                     f"=B{len(rows)+1}-C{len(rows)+1}", 'Income minus expenses'])

        pd.DataFrame(rows).to_csv(file_path, index=False, header=False)
        return file_id

    @staticmethod
    def create_budget_pdf(budget_data: Dict, file_id: str = None) -> str:
        """Create PDF budget report"""
        if not file_id:
            file_id = str(uuid.uuid4())

        file_path = DOWNLOADS_DIR / f"budget_report_{file_id}.pdf"

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)

        pdf.cell(0, 10, f"Budget Report for {budget_data['user_name']}", ln=True, align='C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f"Generated on {budget_data['creation_date']}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Budget Summary', ln=True)
        pdf.set_font('Arial', '', 10)

        pdf.cell(60, 8, 'Monthly Income:', 0, 0)
        pdf.cell(0, 8, f"${budget_data['monthly_income']:.2f}", ln=True)

        pdf.cell(60, 8, 'Total Budgeted Expenses:', 0, 0)
        pdf.cell(0, 8, f"${budget_data['total_expenses']:.2f}", ln=True)

        pdf.cell(60, 8, 'Remaining Balance:', 0, 0)
        pdf.cell(0, 8, f"${budget_data['remaining_balance']:.2f}", ln=True)
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Budget Categories', ln=True)
        pdf.set_font('Arial', '', 9)

        for category, data in budget_data['budget_categories'].items():
            pdf.cell(80, 6, f"{category}:", 0, 0)
            pdf.cell(30, 6, f"${data['amount']:.2f}", 0, 0)
            pdf.cell(0, 6, f"({data['percentage']}%)", ln=True)

        pdf.ln(5)

        if budget_data.get('recommendations'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Recommendations', ln=True)
            pdf.set_font('Arial', '', 9)

            for rec in budget_data['recommendations'][:5]:
                clean_rec = ''.join(char for char in rec if ord(char) < 128)
                pdf.cell(0, 6, f"• {clean_rec}", ln=True)

        pdf.output(file_path)
        return file_id

    @staticmethod
    def get_download_path(file_id: str, file_type: str) -> Optional[str]:
        """Get file path for download"""
        if file_type == "csv" and "budget" in file_id:
            return str(DOWNLOADS_DIR / f"budget_template_{file_id}.csv")
        elif file_type == "csv" and "loan" in file_id:
            return str(DOWNLOADS_DIR / f"loan_schedule_{file_id}.csv")
        elif file_type == "pdf":
            return str(DOWNLOADS_DIR / f"budget_report_{file_id}.pdf")
        return None


# ---------- Calculation wrappers for API ---------------------

def calculate_loan_payment(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate loan payment and generate downloadable schedule"""
    try:
        principal = float(params.get('principal', 0))
        annual_rate = float(params.get('annual_rate', 0))
        years = int(params.get('years', 10))

        if principal <= 0 or years <= 0:
            raise ValueError("Principal and years must be positive")

        monthly_payment = LoanCalculator.calculate_monthly_payment(principal, annual_rate, years)

        return {
            'monthly_payment': monthly_payment,
            'principal': principal,
            'annual_rate': annual_rate,
            'years': years,
            'total_cost': monthly_payment * years * 12,
            'total_interest': (monthly_payment * years * 12) - principal
        }

    except Exception as e:
        return {'error': str(e)}


def calculate_compound_interest(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate compound interest growth"""
    try:
        principal = float(params.get('principal', 0))
        monthly_contribution = float(params.get('monthly_contribution', 0))
        annual_rate = float(params.get('annual_rate', 7))
        years = int(params.get('years', 10))

        if principal < 0 or monthly_contribution < 0:
            raise ValueError("Principal and monthly contribution must be non-negative")

        result = CompoundInterestCalculator.calculate_future_value(
            principal, monthly_contribution, annual_rate, years
        )
        return result

    except Exception as e:
        return {'error': str(e)}


def generate_budget_template(params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate personalized budget template"""
    try:
        monthly_income = float(params.get('monthly_income', 0))
        user_name = params.get('user_name', 'Student')

        if monthly_income <= 0:
            raise ValueError("Monthly income must be positive")

        template = BudgetTemplateGenerator.create_student_budget_template(
            monthly_income=monthly_income,
            user_name=user_name
        )
        return template

    except Exception as e:
        return {'error': str(e)}
