#!/usr/bin/env python3
"""
Investment API handlers
Implements GET, POST endpoints for investment positions and movements.
"""

import json
import sys
import os
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from pathlib import Path

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.investment_service import InvestmentService


class InvestmentAPI:
    """Investment API endpoint handlers"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.investment_service = InvestmentService(db_path)

    def handle_request(self, method: str, path: str, query_params: dict, data: dict) -> tuple:
        """Route investment API requests to appropriate handlers"""

        # Remove /investments prefix
        api_path = path[12:] if path.startswith('/investments') else path

        try:
            if api_path == '/positions' or api_path == '/positions/':
                if method == 'GET':
                    return self._get_positions()
                elif method == 'POST':
                    return self._create_position(data)
                else:
                    return 405, {'error': 'Method not allowed'}

            elif api_path == '/movements' or api_path == '/movements/':
                if method == 'GET':
                    return self._get_movements(query_params)
                elif method == 'POST':
                    return self._create_movement(data)
                else:
                    return 405, {'error': 'Method not allowed'}

            else:
                return 404, {'error': 'Investment endpoint not found'}

        except Exception as e:
            return 500, {'error': f'Internal server error: {str(e)}'}

    def _get_positions(self) -> tuple:
        """GET /api/investments/positions - Get all investment positions"""
        try:
            positions = self.investment_service.get_all_positions()

            # Enhance positions with current holdings data
            enhanced_positions = []
            for position in positions:
                position_summary = self.investment_service.get_position_summary(position.id)

                # Add calculated fields to position data
                position_data = position.to_dict()
                position_data.update({
                    'current_quantity': position_summary.get('current_quantity', 0),
                    'current_value': position_summary.get('total_cost', 0),  # Using cost basis as placeholder
                    'profit_loss': position_summary.get('realized_pnl', 0)
                })

                enhanced_positions.append(position_data)

            return 200, enhanced_positions

        except Exception as e:
            return 500, {'error': f'Failed to get positions: {str(e)}'}

    def _create_position(self, data: dict) -> tuple:
        """POST /api/investments/positions - Create a new investment position"""
        try:
            # Validate required fields
            required_fields = ['asset_type', 'symbol']
            errors = []

            for field in required_fields:
                if field not in data:
                    errors.append(f'Missing required field: {field}')

            if errors:
                return 400, {'error': 'Validation errors', 'details': errors}

            # Validate asset_type
            asset_type = str(data['asset_type']).lower()
            if asset_type not in ['stock', 'crypto']:
                return 400, {'error': 'asset_type must be either "stock" or "crypto"'}

            # Validate symbol
            symbol = str(data['symbol']).strip().upper()
            if not symbol:
                return 400, {'error': 'symbol cannot be empty'}

            # Create position
            position = self.investment_service.create_position(asset_type, symbol)

            # Return enhanced position data
            position_data = position.to_dict()
            position_data.update({
                'current_quantity': 0,
                'current_value': 0,
                'profit_loss': 0
            })

            return 201, position_data

        except ValueError as e:
            return 400, {'error': str(e)}
        except Exception as e:
            return 500, {'error': f'Failed to create position: {str(e)}'}

    def _get_movements(self, query_params: dict) -> tuple:
        """GET /api/investments/movements - Get investment movements with optional filtering"""
        try:
            # Parse query parameters
            position_id = None
            start_date = None
            end_date = None

            if 'positionId' in query_params:
                try:
                    position_id = int(query_params['positionId'][0])
                except (ValueError, IndexError):
                    return 400, {'error': 'Invalid positionId parameter'}

            if 'startDate' in query_params:
                try:
                    start_date = datetime.fromisoformat(query_params['startDate'][0])
                except (ValueError, IndexError):
                    return 400, {'error': 'Invalid startDate format (use ISO format)'}

            if 'endDate' in query_params:
                try:
                    end_date = datetime.fromisoformat(query_params['endDate'][0])
                except (ValueError, IndexError):
                    return 400, {'error': 'Invalid endDate format (use ISO format)'}

            # Get movements based on filters
            if start_date or end_date or position_id:
                movements = self.investment_service.get_movements_by_date_range(
                    start_date, end_date, position_id
                )
            else:
                movements = self.investment_service.get_all_movements()

            return 200, [movement.to_dict() for movement in movements]

        except Exception as e:
            return 500, {'error': f'Failed to get movements: {str(e)}'}

    def _create_movement(self, data: dict) -> tuple:
        """POST /api/investments/movements - Create a new investment movement"""
        try:
            # Validate required fields
            required_fields = ['position_id', 'movement_type', 'quantity', 'price_per_unit', 'movement_datetime']
            errors = []

            for field in required_fields:
                if field not in data:
                    errors.append(f'Missing required field: {field}')

            if errors:
                return 400, {'error': 'Validation errors', 'details': errors}

            # Parse and validate data
            try:
                position_id = int(data['position_id'])
            except (ValueError, TypeError):
                return 400, {'error': 'Invalid position_id format'}

            movement_type = str(data['movement_type']).lower()
            if movement_type not in ['buy', 'sell']:
                return 400, {'error': 'movement_type must be either "buy" or "sell"'}

            try:
                quantity = float(data['quantity'])
                if quantity <= 0:
                    return 400, {'error': 'quantity must be positive'}
            except (ValueError, TypeError):
                return 400, {'error': 'Invalid quantity format'}

            try:
                price_per_unit = float(data['price_per_unit'])
                if price_per_unit <= 0:
                    return 400, {'error': 'price_per_unit must be positive'}
            except (ValueError, TypeError):
                return 400, {'error': 'Invalid price_per_unit format'}

            try:
                movement_datetime = datetime.fromisoformat(data['movement_datetime'])
            except (ValueError, TypeError):
                return 400, {'error': 'Invalid movement_datetime format (use ISO format)'}

            # Optional description
            description = data.get('description')
            if description is not None:
                description = str(description).strip()

            # Create movement
            movement = self.investment_service.create_movement(
                position_id, movement_type, quantity, price_per_unit,
                movement_datetime, description
            )

            return 201, movement.to_dict()

        except ValueError as e:
            return 400, {'error': str(e)}
        except Exception as e:
            return 500, {'error': f'Failed to create movement: {str(e)}'}


class InvestmentUtilsAPI:
    """Additional investment utilities and analytics"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.investment_service = InvestmentService(db_path)

    def get_portfolio_summary(self) -> tuple:
        """Get complete portfolio summary"""
        try:
            summary = self.investment_service.get_portfolio_summary()
            return 200, summary
        except Exception as e:
            return 500, {'error': f'Failed to get portfolio summary: {str(e)}'}

    def get_asset_allocation(self) -> tuple:
        """Get asset allocation breakdown"""
        try:
            allocation = self.investment_service.get_asset_allocation()
            return 200, allocation
        except Exception as e:
            return 500, {'error': f'Failed to get asset allocation: {str(e)}'}

    def get_performance_metrics(self, query_params: dict) -> tuple:
        """Get performance metrics"""
        try:
            position_id = None
            days = 30

            if 'positionId' in query_params:
                try:
                    position_id = int(query_params['positionId'][0])
                except (ValueError, IndexError):
                    return 400, {'error': 'Invalid positionId parameter'}

            if 'days' in query_params:
                try:
                    days = int(query_params['days'][0])
                    if days < 1:
                        days = 30
                except (ValueError, IndexError):
                    days = 30

            metrics = self.investment_service.get_performance_metrics(position_id, days)
            return 200, metrics

        except Exception as e:
            return 500, {'error': f'Failed to get performance metrics: {str(e)}'}

    def get_tax_reporting(self, query_params: dict) -> tuple:
        """Get tax reporting data"""
        try:
            year = datetime.now().year

            if 'year' in query_params:
                try:
                    year = int(query_params['year'][0])
                except (ValueError, IndexError):
                    return 400, {'error': 'Invalid year parameter'}

            tax_data = self.investment_service.get_tax_reporting_data(year)
            return 200, tax_data

        except Exception as e:
            return 500, {'error': f'Failed to get tax reporting data: {str(e)}'}

    def get_rebalancing_suggestions(self, data: dict) -> tuple:
        """Get rebalancing suggestions"""
        try:
            target_allocation = data.get('target_allocation')
            suggestions = self.investment_service.get_rebalancing_suggestions(target_allocation)
            return 200, suggestions

        except Exception as e:
            return 500, {'error': f'Failed to get rebalancing suggestions: {str(e)}'}


# Utility function for server integration
def handle_investments_api(method: str, path: str, query_params: dict, data: dict,
                          db_path: str = "./data/finance.db") -> tuple:
    """Handle investments API requests - for use in server.py"""
    api = InvestmentAPI(db_path)
    return api.handle_request(method, path, query_params, data)


def handle_investments_utils_api(method: str, path: str, query_params: dict, data: dict,
                                db_path: str = "./data/finance.db") -> tuple:
    """Handle investment utilities API requests"""
    utils_api = InvestmentUtilsAPI(db_path)

    if path.endswith('/portfolio'):
        return utils_api.get_portfolio_summary()
    elif path.endswith('/allocation'):
        return utils_api.get_asset_allocation()
    elif path.endswith('/performance'):
        return utils_api.get_performance_metrics(query_params)
    elif path.endswith('/tax'):
        return utils_api.get_tax_reporting(query_params)
    elif path.endswith('/rebalance'):
        return utils_api.get_rebalancing_suggestions(data)
    else:
        return 404, {'error': 'Investment utility endpoint not found'}