"""
Test budget sheet generation and calculator functionality
"""

import pytest
import tempfile
import os
from backend.app.calculators import (
    calculate_loan_payment, 
    calculate_compound_interest, 
    generate_budget_template,
    LoanCalculator
)


class TestBudgetSheet:
    """Test budget template generation"""
    
    def test_budget_template_generation(self):
        """Test budget template with proper categories and formulas"""
        params = {
            'monthly_income': 2000,
            'user_name': 'TestStudent'
        }
        
        result = generate_budget_template(params)
        
        # Should not have errors
        assert 'error' not in result
        
        # Should have required fields
        assert 'monthly_income' in result
        assert 'budget_categories' in result
        assert 'total_expenses' in result
        assert 'remaining_balance' in result
        assert 'user_name' in result
        
        # Check budget categories
        categories = result['budget_categories']
        required_categories = [
            'Housing', 'Food', 'Transportation', 'Textbooks', 
            'Personal Care', 'Entertainment', 'Emergency Fund', 'Savings'
        ]
        
        for category in required_categories:
            assert category in categories
            assert 'amount' in categories[category]
            assert 'percentage' in categories[category]
            assert categories[category]['amount'] > 0
            assert 0 < categories[category]['percentage'] <= 100
        
        # Check math
        total_from_categories = sum(cat['amount'] for cat in categories.values())
        assert abs(result['total_expenses'] - total_from_categories) < 0.01
        
        expected_remaining = result['monthly_income'] - result['total_expenses']
        assert abs(result['remaining_balance'] - expected_remaining) < 0.01
    
    def test_budget_percentages(self):
        """Test that budget percentages add up correctly"""
        params = {'monthly_income': 1500, 'user_name': 'TestStudent'}
        result = generate_budget_template(params)
        
        categories = result['budget_categories']
        total_percentage = sum(cat['percentage'] for cat in categories.values())
        
        # Should add up to 100%
        assert total_percentage == 100
        
        # Housing should be largest category (35%)
        assert categories['Housing']['percentage'] == 35
        assert categories['Housing']['amount'] == 1500 * 0.35
    
    def test_invalid_budget_inputs(self):
        """Test budget generation with invalid inputs"""
        # Zero income
        result = generate_budget_template({'monthly_income': 0})
        assert 'error' in result
        
        # Negative income
        result = generate_budget_template({'monthly_income': -100})
        assert 'error' in result
        
        # Missing income
        result = generate_budget_template({})
        assert 'error' in result


class TestLoanCalculator:
    """Test loan calculation functionality"""
    
    def test_loan_payment_calculation(self):
        """Test basic loan payment calculation"""
        params = {
            'principal': 10000,
            'annual_rate': 5.0,
            'years': 10
        }
        
        result = calculate_loan_payment(params)
        
        # Should not have errors
        assert 'error' not in result
        
        # Should have required fields
        assert 'monthly_payment' in result
        assert 'total_cost' in result
        assert 'total_interest' in result
        
        # Payment should be reasonable
        assert result['monthly_payment'] > 0
        assert result['monthly_payment'] < params['principal']  # Monthly should be less than total
        
        # Total cost should be more than principal (due to interest)
        assert result['total_cost'] > params['principal']
        assert result['total_interest'] > 0
    
    def test_zero_interest_loan(self):
        """Test loan calculation with 0% interest"""
        params = {
            'principal': 12000,
            'annual_rate': 0.0,
            'years': 4
        }
        
        result = calculate_loan_payment(params)
        
        # Monthly payment should be principal / months
        expected_payment = 12000 / (4 * 12)
        assert abs(result['monthly_payment'] - expected_payment) < 0.01
        
        # Total interest should be zero
        assert result['total_interest'] == 0
    
    def test_invalid_loan_inputs(self):
        """Test loan calculation with invalid inputs"""
        # Zero principal
        result = calculate_loan_payment({'principal': 0, 'annual_rate': 5, 'years': 10})
        assert 'error' in result
        
        # Negative principal
        result = calculate_loan_payment({'principal': -1000, 'annual_rate': 5, 'years': 10})
        assert 'error' in result
        
        # Zero years
        result = calculate_loan_payment({'principal': 10000, 'annual_rate': 5, 'years': 0})
        assert 'error' in result


class TestCompoundInterestCalculator:
    """Test compound interest calculation functionality"""
    
    def test_compound_interest_calculation(self):
        """Test basic compound interest calculation"""
        params = {
            'principal': 1000,
            'monthly_contribution': 100,
            'annual_rate': 7.0,
            'years': 5
        }
        
        result = calculate_compound_interest(params)
        
        # Should not have errors
        assert 'error' not in result
        
        # Should have required fields
        assert 'future_value' in result
        assert 'total_contributions' in result
        assert 'interest_earned' in result
        
        # Future value should be greater than contributions
        assert result['future_value'] > result['total_contributions']
        assert result['interest_earned'] > 0
        
        # Check basic math
        expected_contributions = 1000 + (100 * 5 * 12)  # Principal + monthly * years * 12
        assert abs(result['total_contributions'] - expected_contributions) < 0.01
    
    def test_zero_rate_compound(self):
        """Test compound interest with 0% rate"""
        params = {
            'principal': 1000,
            'monthly_contribution': 50,
            'annual_rate': 0.0,
            'years': 2
        }
        
        result = calculate_compound_interest(params)
        
        # With 0% interest, future value should equal contributions
        expected_value = 1000 + (50 * 2 * 12)
        assert abs(result['future_value'] - expected_value) < 0.01
        assert result['interest_earned'] == 0
    
    def test_invalid_compound_inputs(self):
        """Test compound interest with invalid inputs"""
        # Negative principal
        result = calculate_compound_interest({
            'principal': -100, 'monthly_contribution': 50, 'annual_rate': 5, 'years': 5
        })
        assert 'error' in result
        
        # Negative contribution
        result = calculate_compound_interest({
            'principal': 1000, 'monthly_contribution': -50, 'annual_rate': 5, 'years': 5
        })
        assert 'error' in result


class TestAPIIntegration:
    """Test API integration with calculators"""
    
    def test_calculator_response_format(self):
        """Test that calculator responses match expected API format"""
        # Test loan calculator
        loan_params = {'principal': 5000, 'annual_rate': 4.5, 'years': 5}
        loan_result = calculate_loan_payment(loan_params)
        
        assert isinstance(loan_result, dict)
        assert 'monthly_payment' in loan_result
        
        # Test compound interest calculator
        compound_params = {'principal': 1000, 'monthly_contribution': 100, 'annual_rate': 6, 'years': 10}
        compound_result = calculate_compound_interest(compound_params)
        
        assert isinstance(compound_result, dict)
        assert 'future_value' in compound_result
        
        # Test budget generator
        budget_params = {'monthly_income': 2500, 'user_name': 'APITest'}
        budget_result = generate_budget_template(budget_params)
        
        assert isinstance(budget_result, dict)
        assert 'budget_categories' in budget_result 