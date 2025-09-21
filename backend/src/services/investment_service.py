#!/usr/bin/env python3
"""
Investment Service
Handles CRUD operations for investment positions and movements with portfolio calculations.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import sys
import os

# Add models to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.investment_position import InvestmentPosition, InvestmentPositionDB
from models.movement import Movement, MovementDB


class InvestmentService:
    """Service for investment operations with portfolio calculations"""

    def __init__(self, db_path: str = "./data/finance.db"):
        self.db_path = db_path
        self.position_db = InvestmentPositionDB(db_path)
        self.movement_db = MovementDB(db_path)

    # Position Management
    def create_position(self, asset_type: str, symbol: str) -> InvestmentPosition:
        """Create a new investment position"""
        return self.position_db.create_position(asset_type, symbol)

    def get_position(self, position_id: int) -> Optional[InvestmentPosition]:
        """Get investment position by ID"""
        return self.position_db.get_position(position_id)

    def get_all_positions(self) -> List[InvestmentPosition]:
        """Get all investment positions"""
        return self.position_db.get_all_positions()

    def get_positions_by_type(self, asset_type: str) -> List[InvestmentPosition]:
        """Get positions by asset type (stock/crypto)"""
        return self.position_db.get_positions_by_type(asset_type)

    def update_position(self, position_id: int, symbol: str = None) -> Optional[InvestmentPosition]:
        """Update investment position"""
        return self.position_db.update_position(position_id, symbol)

    def delete_position(self, position_id: int) -> bool:
        """Delete investment position and all movements"""
        return self.position_db.delete_position(position_id)

    # Movement Management
    def create_movement(self, position_id: int, movement_type: str, quantity: float,
                       price_per_unit: float, movement_datetime: datetime,
                       description: str = None) -> Movement:
        """Create a new investment movement with validation"""

        # Validate position exists
        position = self.get_position(position_id)
        if not position:
            raise ValueError(f"Position {position_id} does not exist")

        return self.movement_db.create_movement(
            position_id, movement_type, quantity, price_per_unit,
            movement_datetime, description
        )

    def get_movement(self, movement_id: int) -> Optional[Movement]:
        """Get movement by ID"""
        return self.movement_db.get_movement(movement_id)

    def get_movements_by_position(self, position_id: int) -> List[Movement]:
        """Get all movements for a position"""
        return self.movement_db.get_movements_by_position(position_id)

    def get_all_movements(self) -> List[Movement]:
        """Get all movements"""
        return self.movement_db.get_all_movements()

    def get_movements_by_date_range(self, start_date: datetime = None,
                                   end_date: datetime = None,
                                   position_id: int = None) -> List[Movement]:
        """Get movements filtered by date range"""
        return self.movement_db.get_movements_by_date_range(start_date, end_date, position_id)

    def update_movement(self, movement_id: int, quantity: float = None,
                       price_per_unit: float = None, movement_datetime: datetime = None,
                       description: str = None) -> Optional[Movement]:
        """Update movement"""
        return self.movement_db.update_movement(movement_id, quantity, price_per_unit,
                                               movement_datetime, description)

    def delete_movement(self, movement_id: int) -> bool:
        """Delete movement"""
        return self.movement_db.delete_movement(movement_id)

    # Portfolio Calculations
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get complete portfolio summary"""
        positions = self.get_all_positions()
        portfolio_data = []
        total_cost = 0
        total_current_value = 0

        for position in positions:
            position_summary = self.get_position_summary(position.id)
            if position_summary['current_quantity'] > 0:
                portfolio_data.append(position_summary)
                total_cost += position_summary['total_cost']
                # Note: current_value would need live price data
                # For now, use cost basis as placeholder
                total_current_value += position_summary['total_cost']

        return {
            'positions': portfolio_data,
            'totals': {
                'total_cost': total_cost,
                'total_current_value': total_current_value,
                'unrealized_pnl': total_current_value - total_cost,
                'position_count': len(portfolio_data)
            }
        }

    def get_position_summary(self, position_id: int) -> Dict[str, Any]:
        """Get detailed position summary with calculations"""
        position = self.get_position(position_id)
        if not position:
            return {}

        holdings = self.movement_db.get_position_holdings(position_id)

        return {
            'position': position.to_dict(),
            'current_quantity': holdings['current_quantity'],
            'total_cost': holdings['total_cost'],
            'total_proceeds': holdings['total_proceeds'],
            'average_cost_basis': holdings['average_cost_basis'],
            'realized_pnl': holdings['realized_pnl'],
            'fifo_lots': holdings['fifo_lots']
        }

    def get_asset_allocation(self) -> Dict[str, Any]:
        """Get asset allocation breakdown"""
        positions = self.get_all_positions()
        allocation = {'stock': 0, 'crypto': 0}
        total_value = 0

        for position in positions:
            holdings = self.movement_db.get_position_holdings(position.id)
            if holdings['current_quantity'] > 0:
                # Use cost basis as value (would use current market value in real app)
                value = holdings['total_cost'] - holdings['total_proceeds']
                allocation[position.asset_type] += value
                total_value += value

        # Calculate percentages
        percentages = {}
        for asset_type, value in allocation.items():
            percentages[asset_type] = {
                'value': value,
                'percentage': (value / total_value * 100) if total_value > 0 else 0
            }

        return {
            'allocation': percentages,
            'total_value': total_value
        }

    def get_performance_metrics(self, position_id: int = None, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for a position or entire portfolio"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        if position_id:
            # Single position metrics
            movements = self.get_movements_by_date_range(start_date, end_date, position_id)
            position = self.get_position(position_id)

            if not position:
                return {}

            return self._calculate_position_performance(position, movements, days)
        else:
            # Portfolio-wide metrics
            positions = self.get_all_positions()
            portfolio_metrics = []
            total_pnl = 0

            for position in positions:
                movements = self.get_movements_by_date_range(start_date, end_date, position.id)
                metrics = self._calculate_position_performance(position, movements, days)
                if metrics:
                    portfolio_metrics.append(metrics)
                    total_pnl += metrics.get('realized_pnl', 0)

            return {
                'period_days': days,
                'positions': portfolio_metrics,
                'portfolio_realized_pnl': total_pnl
            }

    def _calculate_position_performance(self, position: InvestmentPosition,
                                      movements: List[Movement], days: int) -> Dict[str, Any]:
        """Calculate performance metrics for a single position"""
        if not movements:
            return {}

        total_bought = sum(m.total_amount for m in movements if m.movement_type == 'buy')
        total_sold = sum(m.total_amount for m in movements if m.movement_type == 'sell')
        quantity_bought = sum(m.quantity for m in movements if m.movement_type == 'buy')
        quantity_sold = sum(m.quantity for m in movements if m.movement_type == 'sell')

        return {
            'position': position.to_dict(),
            'period_days': days,
            'total_invested': total_bought,
            'total_proceeds': total_sold,
            'realized_pnl': total_sold - total_bought,
            'quantity_bought': quantity_bought,
            'quantity_sold': quantity_sold,
            'net_quantity': quantity_bought - quantity_sold,
            'average_buy_price': total_bought / quantity_bought if quantity_bought > 0 else 0,
            'average_sell_price': total_sold / quantity_sold if quantity_sold > 0 else 0
        }

    def get_dividend_tracking(self, position_id: int) -> Dict[str, Any]:
        """Get dividend/interest tracking for a position (placeholder for future feature)"""
        position = self.get_position(position_id)
        if not position:
            return {}

        # This would integrate with external APIs for dividend data
        # For now, return placeholder structure
        return {
            'position': position.to_dict(),
            'dividends': [],  # Would fetch from external API
            'total_dividends': 0,
            'dividend_yield': 0,
            'note': 'Dividend tracking requires external price/dividend API integration'
        }

    def get_tax_reporting_data(self, year: int) -> Dict[str, Any]:
        """Get tax reporting data for a specific year"""
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)

        # Get all sell movements for the year
        all_movements = self.get_movements_by_date_range(start_date, end_date)
        sell_movements = [m for m in all_movements if m.movement_type == 'sell']

        tax_lots = []
        total_realized_gains = 0

        for sell_movement in sell_movements:
            position = self.get_position(sell_movement.position_id)
            if not position:
                continue

            # Get cost basis using FIFO method
            holdings = self.movement_db.get_position_holdings(sell_movement.position_id)

            # Calculate gains/losses for this sale
            proceeds = sell_movement.total_amount
            # This is simplified - would need more complex FIFO tracking for exact cost basis
            cost_basis = sell_movement.quantity * holdings['average_cost_basis']
            gain_loss = proceeds - cost_basis

            tax_lots.append({
                'position': position.to_dict(),
                'sell_date': sell_movement.movement_datetime.isoformat(),
                'quantity': sell_movement.quantity,
                'proceeds': proceeds,
                'cost_basis': cost_basis,
                'gain_loss': gain_loss,
                'term': 'short' if self._is_short_term(sell_movement) else 'long'
            })

            total_realized_gains += gain_loss

        return {
            'year': year,
            'tax_lots': tax_lots,
            'total_realized_gains': total_realized_gains,
            'short_term_gains': sum(lot['gain_loss'] for lot in tax_lots if lot['term'] == 'short'),
            'long_term_gains': sum(lot['gain_loss'] for lot in tax_lots if lot['term'] == 'long'),
            'note': 'This is simplified tax reporting. Consult a tax professional for accurate reporting.'
        }

    def _is_short_term(self, sell_movement: Movement) -> bool:
        """Determine if a sale qualifies as short-term (held < 1 year)"""
        # This is simplified - would need to track specific purchase dates
        # For now, assume all crypto is short-term, stocks held > 1 year are long-term
        position = self.get_position(sell_movement.position_id)
        if not position:
            return True

        if position.asset_type == 'crypto':
            return True  # Simplified assumption

        # For stocks, check if position was created > 1 year ago
        one_year_ago = sell_movement.movement_datetime - timedelta(days=365)
        return position.created_at > one_year_ago

    def get_rebalancing_suggestions(self, target_allocation: Dict[str, float] = None) -> Dict[str, Any]:
        """Get portfolio rebalancing suggestions"""
        if not target_allocation:
            target_allocation = {'stock': 70.0, 'crypto': 30.0}  # Default 70/30 allocation

        current_allocation = self.get_asset_allocation()
        suggestions = []

        for asset_type, target_pct in target_allocation.items():
            current_pct = current_allocation['allocation'].get(asset_type, {}).get('percentage', 0)
            difference = target_pct - current_pct

            if abs(difference) > 5:  # Only suggest if > 5% off target
                action = 'buy' if difference > 0 else 'sell'
                suggestions.append({
                    'asset_type': asset_type,
                    'current_percentage': current_pct,
                    'target_percentage': target_pct,
                    'difference': difference,
                    'action': action,
                    'priority': 'high' if abs(difference) > 15 else 'medium'
                })

        return {
            'target_allocation': target_allocation,
            'current_allocation': current_allocation,
            'suggestions': suggestions,
            'total_value': current_allocation['total_value']
        }

    def get_holding_period_analysis(self, position_id: int) -> Dict[str, Any]:
        """Analyze holding periods for a position"""
        movements = self.get_movements_by_position(position_id)
        position = self.get_position(position_id)

        if not position or not movements:
            return {}

        buy_movements = [m for m in movements if m.movement_type == 'buy']
        sell_movements = [m for m in movements if m.movement_type == 'sell']

        holding_periods = []
        for sell in sell_movements:
            # Find corresponding buy (simplified FIFO matching)
            for buy in buy_movements:
                if buy.movement_datetime <= sell.movement_datetime:
                    days_held = (sell.movement_datetime - buy.movement_datetime).days
                    holding_periods.append({
                        'buy_date': buy.movement_datetime.isoformat(),
                        'sell_date': sell.movement_datetime.isoformat(),
                        'days_held': days_held,
                        'quantity': min(buy.quantity, sell.quantity),
                        'buy_price': buy.price_per_unit,
                        'sell_price': sell.price_per_unit
                    })
                    break

        avg_holding_period = sum(hp['days_held'] for hp in holding_periods) / len(holding_periods) if holding_periods else 0

        return {
            'position': position.to_dict(),
            'holding_periods': holding_periods,
            'average_holding_days': avg_holding_period,
            'shortest_hold': min(hp['days_held'] for hp in holding_periods) if holding_periods else 0,
            'longest_hold': max(hp['days_held'] for hp in holding_periods) if holding_periods else 0
        }


# Utility functions for external use
def create_investment_service(db_path: str = "./data/finance.db") -> InvestmentService:
    """Create an investment service instance"""
    return InvestmentService(db_path)