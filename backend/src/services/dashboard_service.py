#!/usr/bin/env python3
"""
Dashboard Service
Handles dashboard analytics including summary statistics and chart data generation.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import sys
import os
from calendar import monthrange

# Add models and services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.card import CardDB
from models.transaction import TransactionDB
from models.investment_position import InvestmentPositionDB
from models.movement import MovementDB
from services.transaction_service import TransactionService
from services.investment_service import InvestmentService


class DashboardService:
    """Service for dashboard analytics and chart data"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.db_path = db_path
        self.card_db = CardDB(db_path)
        self.transaction_db = TransactionDB(db_path)
        self.position_db = InvestmentPositionDB(db_path)
        self.movement_db = MovementDB(db_path)
        self.transaction_service = TransactionService(db_path)
        self.investment_service = InvestmentService(db_path)

    def get_dashboard_summary(self, period: str = 'month') -> Dict[str, Any]:
        """Get dashboard summary statistics for a given period"""

        # Calculate period boundaries
        start_date, end_date = self._get_period_boundaries(period)

        # Get all cards and calculate balances
        cards = self.card_db.get_all_cards()
        total_balance = 0
        total_credit_available = 0

        for card in cards:
            if card.type == 'debit':
                total_balance += card.balance
            elif card.type == 'credit':
                # Credit available = credit_limit - current_balance
                available = (card.credit_limit or 0) - card.balance
                total_credit_available += max(0, available)
                # For summary, credit card balance is negative (debt)
                total_balance -= card.balance

        # Get investment portfolio value
        portfolio_summary = self.investment_service.get_portfolio_summary()
        total_investments_value = portfolio_summary['totals']['total_cost']  # Using cost basis

        # Get period transactions (excluding internal transfers)
        transactions = self.transaction_db.get_transactions_by_date_range(start_date, end_date)
        transactions = [t for t in transactions if not t.is_internal_transfer]

        period_income = sum(t.amount for t in transactions if t.amount > 0)
        period_expenses = sum(t.amount for t in transactions if t.amount < 0)
        period_profit_loss = period_income + period_expenses  # expenses are negative

        return {
            'total_balance': round(total_balance, 2),
            'total_credit_available': round(total_credit_available, 2),
            'total_investments_value': round(total_investments_value, 2),
            'period_income': round(period_income, 2),
            'period_expenses': round(period_expenses, 2),
            'period_profit_loss': round(period_profit_loss, 2)
        }

    def get_chart_data(self, chart_type: str, period: str = 'month') -> Dict[str, Any]:
        """Get chart data for dashboard visualizations"""

        if chart_type == 'balance_trend':
            return self._get_balance_trend_chart(period)
        elif chart_type == 'spending_categories':
            return self._get_spending_categories_chart(period)
        elif chart_type == 'investment_performance':
            return self._get_investment_performance_chart(period)
        else:
            return {
                'chart_type': chart_type,
                'labels': [],
                'datasets': [],
                'error': f'Unknown chart type: {chart_type}'
            }

    def _get_balance_trend_chart(self, period: str) -> Dict[str, Any]:
        """Generate balance trend chart data"""
        start_date, end_date = self._get_period_boundaries(period)

        # Get daily balance data
        labels = []
        balance_data = []

        current_date = start_date
        while current_date <= end_date:
            labels.append(current_date.strftime('%Y-%m-%d'))

            # Calculate total balance at this date
            cards = self.card_db.get_all_cards()
            total_balance = 0

            for card in cards:
                # Get transactions up to this date
                card_transactions = self.transaction_db.get_transactions_by_date_range(
                    None, current_date, card.id
                )

                # Calculate balance at this date
                card_balance = card.balance
                for trans in card_transactions:
                    if trans.transaction_date > current_date:
                        card_balance -= trans.amount

                if card.type == 'debit':
                    total_balance += card_balance
                else:  # credit
                    total_balance -= card_balance

            balance_data.append(round(total_balance, 2))

            # Move to next day/week/month based on period
            if period == 'week':
                current_date += timedelta(days=1)
            elif period == 'month':
                current_date += timedelta(days=7)  # Weekly points for month view
            elif period == 'quarter':
                current_date += timedelta(days=14)  # Bi-weekly for quarter
            else:  # year
                current_date += timedelta(days=30)  # Monthly for year

        return {
            'chart_type': 'balance_trend',
            'labels': labels,
            'datasets': [{
                'label': 'Total Balance',
                'data': balance_data,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)'
            }]
        }

    def _get_spending_categories_chart(self, period: str) -> Dict[str, Any]:
        """Generate spending by categories chart data"""
        start_date, end_date = self._get_period_boundaries(period)

        # Get transactions for the period
        transactions = self.transaction_db.get_transactions_by_date_range(start_date, end_date)

        # Filter expenses only (negative amounts) and exclude internal transfers
        expenses = [t for t in transactions if t.amount < 0 and not t.is_internal_transfer]

        # Group by category
        category_totals = {}
        for transaction in expenses:
            category = transaction.category or 'Uncategorized'
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += abs(transaction.amount)  # Make positive for display

        # Sort by amount and take top categories
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        top_categories = sorted_categories[:10]  # Top 10 categories

        labels = [cat[0] for cat in top_categories]
        data = [round(cat[1], 2) for cat in top_categories]

        # Generate colors for each category
        colors = [
            'rgba(255, 99, 132, 0.8)',  # Red
            'rgba(54, 162, 235, 0.8)',  # Blue
            'rgba(255, 205, 86, 0.8)',  # Yellow
            'rgba(75, 192, 192, 0.8)',  # Teal
            'rgba(153, 102, 255, 0.8)', # Purple
            'rgba(255, 159, 64, 0.8)',  # Orange
            'rgba(199, 199, 199, 0.8)', # Grey
            'rgba(83, 102, 255, 0.8)',  # Indigo
            'rgba(255, 99, 255, 0.8)',  # Pink
            'rgba(99, 255, 132, 0.8)'   # Green
        ]

        return {
            'chart_type': 'spending_categories',
            'labels': labels,
            'datasets': [{
                'label': 'Spending by Category',
                'data': data,
                'backgroundColor': colors[:len(data)],
                'borderColor': colors[:len(data)]
            }]
        }

    def _get_investment_performance_chart(self, period: str) -> Dict[str, Any]:
        """Generate investment performance chart data"""
        start_date, end_date = self._get_period_boundaries(period)

        # Get all positions with movements in the period
        positions = self.position_db.get_all_positions()

        labels = []
        cost_data = []
        current_value_data = []  # Would use real-time prices in production

        for position in positions:
            holdings = self.movement_db.get_position_holdings(position.id)

            if holdings['current_quantity'] > 0:
                labels.append(f"{position.symbol} ({position.asset_type})")

                # Calculate cost basis
                total_cost = holdings['total_cost'] - holdings['total_proceeds']
                cost_data.append(round(total_cost, 2))

                # Use cost basis as current value placeholder
                # In production, this would fetch real-time prices
                current_value_data.append(round(total_cost * 1.05, 2))  # Assume 5% gain for demo

        return {
            'chart_type': 'investment_performance',
            'labels': labels,
            'datasets': [
                {
                    'label': 'Cost Basis',
                    'data': cost_data,
                    'backgroundColor': 'rgba(255, 99, 132, 0.8)',
                    'borderColor': 'rgba(255, 99, 132, 1)'
                },
                {
                    'label': 'Current Value (Est.)',
                    'data': current_value_data,
                    'backgroundColor': 'rgba(75, 192, 192, 0.8)',
                    'borderColor': 'rgba(75, 192, 192, 1)'
                }
            ]
        }

    def _get_period_boundaries(self, period: str) -> tuple:
        """Get start and end dates for a given period"""
        end_date = datetime.now()

        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'quarter':
            start_date = end_date - timedelta(days=90)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:
            # Default to month
            start_date = end_date - timedelta(days=30)

        return start_date, end_date

    def get_financial_health_score(self) -> Dict[str, Any]:
        """Calculate a financial health score based on various metrics"""

        # Get basic metrics
        summary = self.get_dashboard_summary('month')
        cards = self.card_db.get_all_cards()

        score_factors = {
            'emergency_fund': 0,      # Emergency fund adequacy
            'debt_ratio': 0,          # Debt to income ratio
            'savings_rate': 0,        # Monthly savings rate
            'diversification': 0,     # Investment diversification
            'credit_utilization': 0   # Credit card utilization
        }

        # Calculate emergency fund score (0-20 points)
        monthly_expenses = abs(summary['period_expenses'])
        total_liquid_assets = sum(card.balance for card in cards if card.type == 'debit')

        if monthly_expenses > 0:
            emergency_months = total_liquid_assets / monthly_expenses
            score_factors['emergency_fund'] = min(20, emergency_months * 4)  # 4 points per month, max 20

        # Calculate debt ratio score (0-20 points)
        total_debt = sum(card.balance for card in cards if card.type == 'credit')
        monthly_income = summary['period_income']

        if monthly_income > 0:
            debt_ratio = total_debt / monthly_income
            score_factors['debt_ratio'] = max(0, 20 - (debt_ratio * 50))  # Penalize high debt ratios

        # Calculate savings rate score (0-20 points)
        if monthly_income > 0:
            savings_rate = summary['period_profit_loss'] / monthly_income
            score_factors['savings_rate'] = max(0, min(20, savings_rate * 100))  # 1 point per 1% savings rate

        # Calculate investment diversification score (0-20 points)
        allocation = self.investment_service.get_asset_allocation()
        if allocation['total_value'] > 0:
            # Simple diversification: having both stocks and crypto
            asset_types = len([t for t, data in allocation['allocation'].items() if data['value'] > 0])
            score_factors['diversification'] = asset_types * 10  # 10 points per asset type

        # Calculate credit utilization score (0-20 points)
        total_credit_limit = sum(card.credit_limit or 0 for card in cards if card.type == 'credit')
        total_credit_used = sum(card.balance for card in cards if card.type == 'credit')

        if total_credit_limit > 0:
            utilization = total_credit_used / total_credit_limit
            score_factors['credit_utilization'] = max(0, 20 - (utilization * 67))  # Penalize high utilization

        # Calculate total score
        total_score = sum(score_factors.values())

        # Determine grade
        if total_score >= 90:
            grade = 'A'
        elif total_score >= 80:
            grade = 'B'
        elif total_score >= 70:
            grade = 'C'
        elif total_score >= 60:
            grade = 'D'
        else:
            grade = 'F'

        return {
            'total_score': round(total_score, 1),
            'grade': grade,
            'score_factors': {k: round(v, 1) for k, v in score_factors.items()},
            'recommendations': self._get_health_recommendations(score_factors, summary)
        }

    def _get_health_recommendations(self, score_factors: Dict[str, float],
                                   summary: Dict[str, Any]) -> List[str]:
        """Generate financial health recommendations"""
        recommendations = []

        if score_factors['emergency_fund'] < 15:
            recommendations.append("Build emergency fund to cover 3-6 months of expenses")

        if score_factors['debt_ratio'] < 15:
            recommendations.append("Reduce debt burden or increase income")

        if score_factors['savings_rate'] < 10:
            recommendations.append("Increase savings rate by reducing expenses or increasing income")

        if score_factors['diversification'] < 15:
            recommendations.append("Diversify investments across different asset types")

        if score_factors['credit_utilization'] < 15:
            recommendations.append("Reduce credit card utilization below 30%")

        if summary['period_profit_loss'] < 0:
            recommendations.append("Review expenses to achieve positive cash flow")

        if not recommendations:
            recommendations.append("Great job! Your financial health looks strong.")

        return recommendations

    def get_spending_insights(self, period: str = 'month') -> Dict[str, Any]:
        """Get spending insights and patterns"""
        start_date, end_date = self._get_period_boundaries(period)

        # Get spending data
        spending_summary = self.transaction_service.get_spending_summary(start_date, end_date)

        # Compare with previous period
        prev_start = start_date - (end_date - start_date)
        prev_end = start_date
        prev_summary = self.transaction_service.get_spending_summary(prev_start, prev_end)

        # Calculate changes
        current_expenses = abs(spending_summary['totals']['expenses'])
        prev_expenses = abs(prev_summary['totals']['expenses'])

        expense_change = ((current_expenses - prev_expenses) / prev_expenses * 100) if prev_expenses > 0 else 0

        # Find top spending categories
        categories = spending_summary['categories']
        top_categories = sorted(
            [(cat, data) for cat, data in categories.items() if data['expenses'] < 0],
            key=lambda x: x[1]['expenses']
        )[:5]

        # Identify unusual spending patterns
        insights = []

        if expense_change > 20:
            insights.append(f"Spending increased by {expense_change:.1f}% compared to previous period")
        elif expense_change < -20:
            insights.append(f"Spending decreased by {abs(expense_change):.1f}% compared to previous period")

        if top_categories:
            top_category = top_categories[0]
            insights.append(f"Largest expense category: {top_category[0]} (${abs(top_category[1]['expenses']):.2f})")

        return {
            'period': period,
            'current_expenses': current_expenses,
            'expense_change_percent': round(expense_change, 1),
            'top_categories': [(cat, abs(data['expenses'])) for cat, data in top_categories],
            'insights': insights,
            'spending_distribution': {
                cat: {
                    'amount': abs(data['expenses']),
                    'percentage': (abs(data['expenses']) / current_expenses * 100) if current_expenses > 0 else 0
                }
                for cat, data in categories.items() if data['expenses'] < 0
            }
        }


# Utility functions for external use
def create_dashboard_service(db_path: str = "./data/finance.db") -> DashboardService:
    """Create a dashboard service instance"""
    return DashboardService(db_path)