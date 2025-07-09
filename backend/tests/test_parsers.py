import pytest
from app.main import parse_financial_message

@pytest.mark.parametrize("message, expected", [
    ("my income is 5200", {"income": 5200}),
    ("I have expenses of $1,200.50", {"expenses": 1200}),
    ("my debts are 45,000", {"debts": 45000}),
    ("i make $60k a year, have $2000 in monthly expenses, and $15,000 in debt", {"income": 60, "expenses": 2000, "debts": 15000}),
    ("down payment will be 5,000", {"down_payment": 5000}),
    ("my income is $5,200 and my rent expense is 1200", {"income": 5200, "expenses": 1200}),
    ("No financial info here", {}),
    ("downpayment: 10000, debts: 5000", {"down_payment": 10000, "debts": 5000}),
])
def test_parse_financial_message(message, expected):
    """Tests the parse_financial_message function with various inputs."""
    assert parse_financial_message(message) == expected 