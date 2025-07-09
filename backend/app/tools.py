"""
Tool registry for the agentic AI chatbot.
Defines all available tools with Pydantic schemas for type-safe function calling.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import pandas as pd
from pathlib import Path

# Tool input/output schemas
class BudgetSheetInput(BaseModel):
    """Input schema for budget sheet generation."""
    income: float = Field(..., description="Total monthly income")
    expenses: Dict[str, float] = Field(..., description="Monthly expenses by category")
    user_name: str = Field(..., description="User's name for personalization")

class BudgetSheetOutput(BaseModel):
    """Output schema for budget sheet generation."""
    filename: str = Field(..., description="Generated Excel file name")
    summary: str = Field(..., description="Budget summary text")
    categories: List[str] = Field(..., description="List of expense categories")

class DebtSimulatorInput(BaseModel):
    """Input schema for debt payoff simulation."""
    debt_balance: float = Field(..., description="Current debt balance")
    interest_rate: float = Field(..., description="Annual interest rate (percentage)")
    current_payment: float = Field(..., description="Current monthly payment")
    extra_payment: float = Field(0.0, description="Additional monthly payment")
    debt_type: str = Field(..., description="Type of debt (student_loan, credit_card, etc.)")

class DebtSimulatorOutput(BaseModel):
    """Output schema for debt payoff simulation."""
    original_payoff_time: int = Field(..., description="Original payoff time in months")
    new_payoff_time: int = Field(..., description="New payoff time with extra payment")
    total_interest_saved: float = Field(..., description="Total interest saved")
    monthly_savings: float = Field(..., description="Monthly payment savings after payoff")

class SavingsCalculatorInput(BaseModel):
    """Input schema for savings goal calculator."""
    goal_amount: float = Field(..., description="Target savings amount")
    months: int = Field(..., description="Timeframe in months")
    current_savings: float = Field(0.0, description="Current savings balance")
    monthly_contribution: Optional[float] = Field(None, description="Fixed monthly contribution")

class SavingsCalculatorOutput(BaseModel):
    """Output schema for savings goal calculator."""
    required_monthly: float = Field(..., description="Required monthly contribution")
    total_contribution: float = Field(..., description="Total contribution needed")
    achievable: bool = Field(..., description="Whether goal is achievable")
    alternative_months: Optional[int] = Field(None, description="Alternative timeframe if not achievable")

class FinancialHealthScoreInput(BaseModel):
    """Input schema for financial health scoring."""
    income: float = Field(..., description="Monthly income")
    expenses: Dict[str, float] = Field(..., description="Monthly expenses")
    debts: Dict[str, Dict[str, float]] = Field(..., description="Debt information")
    savings: float = Field(..., description="Current savings")
    goals: Dict[str, Dict[str, float]] = Field(..., description="Financial goals")

class FinancialHealthScoreOutput(BaseModel):
    """Output schema for financial health scoring."""
    overall_score: float = Field(..., description="Overall financial health score (0-100)")
    category_scores: Dict[str, float] = Field(..., description="Scores by category")
    recommendations: List[str] = Field(..., description="Specific improvement recommendations")
    risk_level: str = Field(..., description="Risk assessment (low, moderate, high)")

class InvestmentRecommendationInput(BaseModel):
    """Input schema for investment recommendations."""
    age: int = Field(..., description="User's age")
    income: float = Field(..., description="Annual income")
    risk_tolerance: str = Field(..., description="Risk tolerance (conservative, moderate, aggressive)")
    investment_experience: str = Field(..., description="Investment experience level")
    time_horizon: int = Field(..., description="Investment time horizon in years")
    current_investments: Dict[str, float] = Field(default_factory=dict, description="Current investment portfolio")

class InvestmentRecommendationOutput(BaseModel):
    """Output schema for investment recommendations."""
    recommended_allocation: Dict[str, float] = Field(..., description="Recommended asset allocation")
    specific_recommendations: List[str] = Field(..., description="Specific investment recommendations")
    risk_assessment: str = Field(..., description="Risk assessment for the portfolio")
    expected_return: float = Field(..., description="Expected annual return percentage")

class GetCurrentDateTimeInput(BaseModel):
    """Input schema for getting current date and time."""
    timezone: Optional[str] = Field("UTC", description="Timezone for the date/time")

class GetCurrentDateTimeOutput(BaseModel):
    """Output schema for getting current date and time."""
    current_date: str = Field(..., description="Current date in YYYY-MM-DD format")
    current_time: str = Field(..., description="Current time in HH:MM:SS format")
    day_of_week: str = Field(..., description="Day of the week")
    timezone: str = Field(..., description="Timezone used")

class GetGeneralInfoInput(BaseModel):
    """Input schema for getting general information."""
    topic: str = Field(..., description="Topic to get information about")

class GetGeneralInfoOutput(BaseModel):
    """Output schema for getting general information."""
    information: str = Field(..., description="General information about the topic")
    source: str = Field(..., description="Source of the information")

# Tool implementations
async def generate_budget_sheet(data: BudgetSheetInput) -> BudgetSheetOutput:
    """Generate a personalized budget Excel sheet."""
    start_time = time.time()
    
    try:
        # Create budget data
        total_expenses = sum(data.expenses.values())
        net_income = data.income - total_expenses
        
        budget_data = {
            'Category': ['Income'] + list(data.expenses.keys()) + ['Net Income'],
            'Amount': [data.income] + list(data.expenses.values()) + [net_income],
            'Type': ['Income'] + ['Expense'] * len(data.expenses) + ['Net']
        }
        
        df = pd.DataFrame(budget_data)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"budget_{data.user_name}_{timestamp}.xlsx"
        filepath = Path(__file__).parent / "exports" / filename
        
        # Ensure exports directory exists
        filepath.parent.mkdir(exist_ok=True)
        
        # Create Excel file
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Budget', index=False)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Budget']
            
            # Add formatting
            money_format = workbook.add_format({'num_format': '$#,##0.00'})
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
            
            # Apply formatting
            worksheet.set_column('B:B', 15, money_format)
            worksheet.set_row(0, 20, header_format)
            
            # Add summary
            worksheet.write('D2', f'Budget Summary for {data.user_name}')
            worksheet.write('D3', f'Generated on: {datetime.now().strftime("%B %d, %Y")}')
            worksheet.write('D4', f'Monthly Income: ${data.income:,.2f}')
            worksheet.write('D5', f'Total Expenses: ${total_expenses:,.2f}')
            worksheet.write('D6', f'Net Income: ${net_income:,.2f}')
        
        summary = f"Budget created for {data.user_name}. Monthly income: ${data.income:,.2f}, expenses: ${total_expenses:,.2f}, net: ${net_income:,.2f}"
        
        return BudgetSheetOutput(
            filename=filename,
            summary=summary,
            categories=list(data.expenses.keys())
        )
        
    except Exception as e:
        raise Exception(f"Failed to generate budget sheet: {str(e)}")

async def simulate_debt_payoff(data: DebtSimulatorInput) -> DebtSimulatorOutput:
    """Simulate debt payoff with different payment scenarios."""
    start_time = time.time()
    
    try:
        monthly_rate = data.interest_rate / 100 / 12
        
        # Calculate original payoff time
        if data.current_payment <= data.debt_balance * monthly_rate:
            original_payoff_time = float('inf')
        else:
            original_payoff_time = -1 * (1 / monthly_rate) * (1 - (data.debt_balance * monthly_rate / data.current_payment))
            original_payoff_time = int(original_payoff_time)
        
        # Calculate new payoff time with extra payment
        new_payment = data.current_payment + data.extra_payment
        if new_payment <= data.debt_balance * monthly_rate:
            new_payoff_time = float('inf')
        else:
            new_payoff_time = -1 * (1 / monthly_rate) * (1 - (data.debt_balance * monthly_rate / new_payment))
            new_payoff_time = int(new_payoff_time)
        
        # Calculate interest savings
        if original_payoff_time != float('inf') and new_payoff_time != float('inf'):
            original_total_interest = (data.current_payment * original_payoff_time) - data.debt_balance
            new_total_interest = (new_payment * new_payoff_time) - data.debt_balance
            interest_saved = original_total_interest - new_total_interest
        else:
            interest_saved = 0
        
        return DebtSimulatorOutput(
            original_payoff_time=original_payoff_time if original_payoff_time != float('inf') else 999,
            new_payoff_time=new_payoff_time if new_payoff_time != float('inf') else 999,
            total_interest_saved=interest_saved,
            monthly_savings=data.current_payment if new_payoff_time != float('inf') else 0
        )
        
    except Exception as e:
        raise Exception(f"Failed to simulate debt payoff: {str(e)}")

async def calculate_savings_requirement(data: SavingsCalculatorInput) -> SavingsCalculatorOutput:
    """Calculate required monthly savings to reach a goal."""
    start_time = time.time()
    
    try:
        remaining_amount = data.goal_amount - data.current_savings
        
        if data.monthly_contribution:
            # Calculate if fixed contribution is sufficient
            total_contribution = data.monthly_contribution * data.months
            achievable = total_contribution >= remaining_amount
            required_monthly = data.monthly_contribution
        else:
            # Calculate required monthly contribution
            required_monthly = remaining_amount / data.months
            achievable = required_monthly > 0
            total_contribution = required_monthly * data.months
        
        # If not achievable, suggest alternative timeframe
        alternative_months = None
        if not achievable and not data.monthly_contribution:
            alternative_months = int(remaining_amount / 100) + 1  # Assuming $100 minimum monthly
        
        return SavingsCalculatorOutput(
            required_monthly=required_monthly,
            total_contribution=total_contribution,
            achievable=achievable,
            alternative_months=alternative_months
        )
        
    except Exception as e:
        raise Exception(f"Failed to calculate savings requirement: {str(e)}")

async def calculate_financial_health_score(data: FinancialHealthScoreInput) -> FinancialHealthScoreOutput:
    """Calculate comprehensive financial health score."""
    start_time = time.time()
    
    try:
        category_scores = {}
        recommendations = []
        
        # Income vs Expenses Score (40% weight)
        total_expenses = sum(data.expenses.values())
        if data.income > 0:
            expense_ratio = total_expenses / data.income
            if expense_ratio <= 0.5:
                category_scores['expense_ratio'] = 100
            elif expense_ratio <= 0.7:
                category_scores['expense_ratio'] = 80
            elif expense_ratio <= 0.9:
                category_scores['expense_ratio'] = 60
            else:
                category_scores['expense_ratio'] = 30
                recommendations.append("Reduce expenses to improve financial health")
        else:
            category_scores['expense_ratio'] = 0
        
        # Debt Score (25% weight)
        total_debt = sum(debt.get('balance', 0) for debt in data.debts.values())
        if data.income > 0:
            debt_ratio = total_debt / (data.income * 12)  # Annual income
            if debt_ratio <= 0.2:
                category_scores['debt_ratio'] = 100
            elif debt_ratio <= 0.4:
                category_scores['debt_ratio'] = 80
            elif debt_ratio <= 0.6:
                category_scores['debt_ratio'] = 60
            else:
                category_scores['debt_ratio'] = 30
                recommendations.append("Focus on debt reduction to improve financial health")
        else:
            category_scores['debt_ratio'] = 50
        
        # Savings Score (20% weight)
        emergency_fund_target = data.income * 3  # 3 months of income
        if data.savings >= emergency_fund_target:
            category_scores['savings'] = 100
        elif data.savings >= emergency_fund_target * 0.5:
            category_scores['savings'] = 80
        elif data.savings >= emergency_fund_target * 0.25:
            category_scores['savings'] = 60
        else:
            category_scores['savings'] = 30
            recommendations.append("Build emergency fund to improve financial security")
        
        # Goals Score (15% weight)
        if data.goals:
            category_scores['goals'] = 80
        else:
            category_scores['goals'] = 40
            recommendations.append("Set specific financial goals to improve planning")
        
        # Calculate overall score
        weights = {'expense_ratio': 0.4, 'debt_ratio': 0.25, 'savings': 0.2, 'goals': 0.15}
        overall_score = sum(category_scores.get(cat, 0) * weight for cat, weight in weights.items())
        
        # Determine risk level
        if overall_score >= 80:
            risk_level = "low"
        elif overall_score >= 60:
            risk_level = "moderate"
        else:
            risk_level = "high"
        
        return FinancialHealthScoreOutput(
            overall_score=overall_score,
            category_scores=category_scores,
            recommendations=recommendations,
            risk_level=risk_level
        )
        
    except Exception as e:
        raise Exception(f"Failed to calculate financial health score: {str(e)}")

async def get_investment_recommendations(data: InvestmentRecommendationInput) -> InvestmentRecommendationOutput:
    """Generate personalized investment recommendations."""
    start_time = time.time()
    
    try:
        # Base allocation by risk tolerance
        allocations = {
            'conservative': {'bonds': 0.6, 'stocks': 0.3, 'cash': 0.1},
            'moderate': {'bonds': 0.4, 'stocks': 0.5, 'cash': 0.1},
            'aggressive': {'bonds': 0.2, 'stocks': 0.7, 'cash': 0.1}
        }
        
        base_allocation = allocations.get(data.risk_tolerance, allocations['moderate'])
        
        # Adjust for age (more conservative as you get older)
        age_factor = max(0.1, 1 - (data.age - 25) / 100)
        base_allocation['bonds'] = min(0.8, base_allocation['bonds'] * age_factor)
        base_allocation['stocks'] = 1 - base_allocation['bonds'] - base_allocation['cash']
        
        # Generate specific recommendations
        recommendations = []
        if data.investment_experience == 'beginner':
            recommendations.extend([
                "Start with low-cost index funds or ETFs",
                "Consider a robo-advisor for automated portfolio management",
                "Focus on tax-advantaged accounts like 401(k) or IRA"
            ])
        elif data.investment_experience == 'intermediate':
            recommendations.extend([
                "Diversify across different asset classes and sectors",
                "Consider adding international exposure",
                "Review and rebalance portfolio quarterly"
            ])
        else:  # advanced
            recommendations.extend([
                "Consider alternative investments for diversification",
                "Implement tax-loss harvesting strategies",
                "Explore sector-specific ETFs for targeted exposure"
            ])
        
        # Calculate expected return
        expected_returns = {'bonds': 0.04, 'stocks': 0.08, 'cash': 0.02}
        expected_return = sum(base_allocation[asset] * expected_returns[asset] for asset in base_allocation)
        
        return InvestmentRecommendationOutput(
            recommended_allocation=base_allocation,
            specific_recommendations=recommendations,
            risk_assessment=f"Moderate risk portfolio suitable for {data.risk_tolerance} investors",
            expected_return=expected_return
        )
        
    except Exception as e:
        raise Exception(f"Failed to generate investment recommendations: {str(e)}")

async def get_current_datetime(data: GetCurrentDateTimeInput) -> GetCurrentDateTimeOutput:
    """Get current date and time information."""
    try:
        from datetime import datetime
        import pytz
        
        # Get current datetime
        if data.timezone and data.timezone != "UTC":
            try:
                tz = pytz.timezone(data.timezone)
                now = datetime.now(tz)
            except pytz.exceptions.UnknownTimeZoneError:
                now = datetime.utcnow()
                data.timezone = "UTC"
        else:
            now = datetime.utcnow()
            data.timezone = "UTC"
        
        return GetCurrentDateTimeOutput(
            current_date=now.strftime("%Y-%m-%d"),
            current_time=now.strftime("%H:%M:%S"),
            day_of_week=now.strftime("%A"),
            timezone=data.timezone
        )
        
    except Exception as e:
        raise Exception(f"Failed to get current date/time: {str(e)}")

async def get_general_info(data: GetGeneralInfoInput) -> GetGeneralInfoOutput:
    """Get general information about a topic."""
    try:
        # Simple knowledge base for common questions
        knowledge_base = {
            "date": "I can provide the current date and time. Would you like me to get that information for you?",
            "time": "I can provide the current date and time. Would you like me to get that information for you?",
            "today": "I can provide the current date and time. Would you like me to get that information for you?",
            "weather": "I don't have access to real-time weather information, but I can help you with financial planning questions!",
            "help": "I'm here to help with financial literacy topics like budgeting, saving, debt management, and investing. What would you like to know?",
            "hello": "Hello! I'm your financial literacy assistant. How can I help you today?",
            "hi": "Hi there! I'm here to help with your financial questions. What would you like to know?",
            "thanks": "You're welcome! I'm happy to help with your financial literacy journey.",
            "thank you": "You're welcome! I'm happy to help with your financial literacy journey."
        }
        
        topic_lower = data.topic.lower().strip()
        
        # Check for exact matches first
        if topic_lower in knowledge_base:
            return GetGeneralInfoOutput(
                information=knowledge_base[topic_lower],
                source="pgpfinlitbot knowledge base"
            )
        
        # Check for partial matches
        for key, value in knowledge_base.items():
            if key in topic_lower or topic_lower in key:
                return GetGeneralInfoOutput(
                    information=value,
                    source="pgpfinlitbot knowledge base"
                )
        
        # Default response for unknown topics
        return GetGeneralInfoOutput(
            information=f"I'm a financial literacy assistant, so I'm best equipped to help with topics related to personal finance, budgeting, saving, debt management, and investing. For '{data.topic}', I'd recommend asking a more specific financial question or using one of my specialized tools.",
            source="pgpfinlitbot knowledge base"
        )
        
    except Exception as e:
        raise Exception(f"Failed to get general information: {str(e)}")

# Tool registry
TOOL_REGISTRY = {
    "generate_budget_sheet": {
        "function": generate_budget_sheet,
        "input_schema": BudgetSheetInput,
        "output_schema": BudgetSheetOutput,
        "description": "Generate a personalized budget Excel sheet with income, expenses, and financial analysis"
    },
    "simulate_debt_payoff": {
        "function": simulate_debt_payoff,
        "input_schema": DebtSimulatorInput,
        "output_schema": DebtSimulatorOutput,
        "description": "Simulate debt payoff scenarios with different payment amounts and calculate interest savings"
    },
    "calculate_savings_requirement": {
        "function": calculate_savings_requirement,
        "input_schema": SavingsCalculatorInput,
        "output_schema": SavingsCalculatorOutput,
        "description": "Calculate required monthly savings to reach a financial goal within a specified timeframe"
    },
    "calculate_financial_health_score": {
        "function": calculate_financial_health_score,
        "input_schema": FinancialHealthScoreInput,
        "output_schema": FinancialHealthScoreOutput,
        "description": "Calculate comprehensive financial health score based on income, expenses, debts, and savings"
    },
    "get_investment_recommendations": {
        "function": get_investment_recommendations,
        "input_schema": InvestmentRecommendationInput,
        "output_schema": InvestmentRecommendationOutput,
        "description": "Generate personalized investment recommendations based on age, risk tolerance, and experience"
    },
    "get_current_datetime": {
        "function": get_current_datetime,
        "input_schema": GetCurrentDateTimeInput,
        "output_schema": GetCurrentDateTimeOutput,
        "description": "Get current date and time information"
    },
    "get_general_info": {
        "function": get_general_info,
        "input_schema": GetGeneralInfoInput,
        "output_schema": GetGeneralInfoOutput,
        "description": "Get general information about a topic"
    }
}

# OpenAI function schemas for LLM function calling
def get_openai_function_schemas() -> List[Dict[str, Any]]:
    """Convert tool registry to OpenAI function calling format."""
    schemas = []
    
    for tool_name, tool_info in TOOL_REGISTRY.items():
        schema = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": tool_info["input_schema"].model_json_schema()
            }
        }
        schemas.append(schema)
    
    return schemas

async def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool with the given arguments."""
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    tool_info = TOOL_REGISTRY[tool_name]
    input_schema = tool_info["input_schema"]
    
    # Validate input
    validated_input = input_schema(**tool_args)
    
    # Execute tool
    result = await tool_info["function"](validated_input)
    
    # Convert to dict
    return result.model_dump() 