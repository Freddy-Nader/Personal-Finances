#!/usr/bin/env python3
"""
Dashboard API handlers
Implements GET endpoints for dashboard summary and chart data.
"""

import json
import sys
import os
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from pathlib import Path

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.dashboard_service import DashboardService


class DashboardAPI:
    """Dashboard API endpoint handlers"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.dashboard_service = DashboardService(db_path)

    def handle_request(self, method: str, path: str, query_params: dict, data: dict) -> tuple:
        """Route dashboard API requests to appropriate handlers"""

        # Remove /dashboard prefix
        api_path = path[10:] if path.startswith('/dashboard') else path

        try:
            if api_path == '/summary' or api_path == '/summary/':
                if method == 'GET':
                    return self._get_dashboard_summary(query_params)
                else:
                    return 405, {'error': 'Method not allowed'}

            elif api_path == '/charts' or api_path == '/charts/':
                if method == 'GET':
                    return self._get_chart_data(query_params)
                else:
                    return 405, {'error': 'Method not allowed'}

            else:
                return 404, {'error': 'Dashboard endpoint not found'}

        except Exception as e:
            return 500, {'error': f'Internal server error: {str(e)}'}

    def _get_dashboard_summary(self, query_params: dict) -> tuple:
        """GET /api/dashboard/summary - Get dashboard summary statistics"""
        try:
            # Parse period parameter
            period = 'month'  # default

            if 'period' in query_params:
                period = str(query_params['period'][0]).lower()
                valid_periods = ['week', 'month', 'quarter', 'year']
                if period not in valid_periods:
                    return 400, {'error': f'Invalid period. Must be one of: {valid_periods}'}

            # Get dashboard summary
            summary = self.dashboard_service.get_dashboard_summary(period)

            return 200, summary

        except Exception as e:
            return 500, {'error': f'Failed to get dashboard summary: {str(e)}'}

    def _get_chart_data(self, query_params: dict) -> tuple:
        """GET /api/dashboard/charts - Get chart data for dashboard"""
        try:
            # Parse parameters
            chart_type = None
            period = 'month'  # default

            if 'chartType' in query_params:
                chart_type = str(query_params['chartType'][0])
                valid_types = ['balance_trend', 'spending_categories', 'investment_performance']
                if chart_type not in valid_types:
                    return 400, {'error': f'Invalid chartType. Must be one of: {valid_types}'}
            else:
                return 400, {'error': 'chartType parameter is required'}

            if 'period' in query_params:
                period = str(query_params['period'][0]).lower()
                valid_periods = ['week', 'month', 'quarter', 'year']
                if period not in valid_periods:
                    return 400, {'error': f'Invalid period. Must be one of: {valid_periods}'}

            # Get chart data
            chart_data = self.dashboard_service.get_chart_data(chart_type, period)

            return 200, chart_data

        except Exception as e:
            return 500, {'error': f'Failed to get chart data: {str(e)}'}


class DashboardUtilsAPI:
    """Additional dashboard utilities and analytics"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.dashboard_service = DashboardService(db_path)

    def get_financial_health_score(self) -> tuple:
        """Get financial health score and recommendations"""
        try:
            health_score = self.dashboard_service.get_financial_health_score()
            return 200, health_score
        except Exception as e:
            return 500, {'error': f'Failed to get financial health score: {str(e)}'}

    def get_spending_insights(self, query_params: dict) -> tuple:
        """Get spending insights and patterns"""
        try:
            period = 'month'  # default

            if 'period' in query_params:
                period = str(query_params['period'][0]).lower()
                valid_periods = ['week', 'month', 'quarter', 'year']
                if period not in valid_periods:
                    return 400, {'error': f'Invalid period. Must be one of: {valid_periods}'}

            insights = self.dashboard_service.get_spending_insights(period)
            return 200, insights

        except Exception as e:
            return 500, {'error': f'Failed to get spending insights: {str(e)}'}

    def get_budget_analysis(self, data: dict) -> tuple:
        """Analyze budget vs actual spending (placeholder for future feature)"""
        try:
            # This would integrate with budget tracking features
            # For now, return a placeholder structure
            return 200, {
                'budget_analysis': {
                    'total_budget': data.get('total_budget', 0),
                    'total_spent': 0,
                    'remaining_budget': 0,
                    'categories': {},
                    'note': 'Budget analysis requires budget setup feature'
                }
            }

        except Exception as e:
            return 500, {'error': f'Failed to get budget analysis: {str(e)}'}

    def get_cashflow_projection(self, query_params: dict) -> tuple:
        """Get cashflow projection based on historical data"""
        try:
            months = 6  # default

            if 'months' in query_params:
                try:
                    months = int(query_params['months'][0])
                    if months < 1 or months > 24:
                        months = 6
                except (ValueError, IndexError):
                    months = 6

            # This would use historical transaction data to project future cashflow
            # For now, return a simplified projection structure
            from services.transaction_service import TransactionService
            transaction_service = TransactionService(self.dashboard_service.db_path)

            # Get historical data for projection
            monthly_trends = transaction_service.get_monthly_trends(6)

            if monthly_trends:
                avg_income = sum(trend['income'] for trend in monthly_trends) / len(monthly_trends)
                avg_expenses = sum(trend['expenses'] for trend in monthly_trends) / len(monthly_trends)
                avg_net = avg_income + avg_expenses  # expenses are negative

                # Simple projection
                projections = []
                current_balance = self.dashboard_service.get_dashboard_summary()['total_balance']

                for i in range(months):
                    month_date = datetime.now().replace(day=1)
                    if i > 0:
                        # Simple month calculation (not exact)
                        month_date = month_date.replace(month=month_date.month + i)

                    current_balance += avg_net
                    projections.append({
                        'month': month_date.strftime('%Y-%m'),
                        'projected_income': avg_income,
                        'projected_expenses': avg_expenses,
                        'projected_net': avg_net,
                        'projected_balance': round(current_balance, 2)
                    })

                return 200, {
                    'historical_months': len(monthly_trends),
                    'projection_months': months,
                    'avg_monthly_income': round(avg_income, 2),
                    'avg_monthly_expenses': round(avg_expenses, 2),
                    'avg_monthly_net': round(avg_net, 2),
                    'projections': projections,
                    'note': 'Projections based on historical averages and may not reflect future changes'
                }
            else:
                return 200, {
                    'projections': [],
                    'note': 'Insufficient historical data for projections'
                }

        except Exception as e:
            return 500, {'error': f'Failed to get cashflow projection: {str(e)}'}

    def get_net_worth_tracking(self) -> tuple:
        """Get net worth calculation and tracking"""
        try:
            summary = self.dashboard_service.get_dashboard_summary()

            # Calculate net worth components
            liquid_assets = summary['total_balance']  # Cards balance
            investments = summary['total_investments_value']
            credit_available = summary['total_credit_available']

            # Note: This is simplified - real net worth would include:
            # - Property values
            # - Other assets
            # - All debts/liabilities
            # - Investment current market values

            net_worth = liquid_assets + investments

            return 200, {
                'net_worth': round(net_worth, 2),
                'components': {
                    'liquid_assets': round(liquid_assets, 2),
                    'investments': round(investments, 2),
                    'credit_available': round(credit_available, 2)
                },
                'note': 'Simplified net worth calculation based on tracked assets only'
            }

        except Exception as e:
            return 500, {'error': f'Failed to get net worth tracking: {str(e)}'}


# Utility function for server integration
def handle_dashboard_api(method: str, path: str, query_params: dict, data: dict,
                        db_path: str = "./data/finance.db") -> tuple:
    """Handle dashboard API requests - for use in server.py"""
    api = DashboardAPI(db_path)
    return api.handle_request(method, path, query_params, data)


def handle_dashboard_utils_api(method: str, path: str, query_params: dict, data: dict,
                              db_path: str = "./data/finance.db") -> tuple:
    """Handle dashboard utilities API requests"""
    utils_api = DashboardUtilsAPI(db_path)

    if path.endswith('/health'):
        return utils_api.get_financial_health_score()
    elif path.endswith('/insights'):
        return utils_api.get_spending_insights(query_params)
    elif path.endswith('/budget'):
        return utils_api.get_budget_analysis(data)
    elif path.endswith('/cashflow'):
        return utils_api.get_cashflow_projection(query_params)
    elif path.endswith('/networth'):
        return utils_api.get_net_worth_tracking()
    else:
        return 404, {'error': 'Dashboard utility endpoint not found'}