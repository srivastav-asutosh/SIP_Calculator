
"""
SIP Calculator Dashboard - Flask Backend
A comprehensive Python backend for SIP calculations with real-time API endpoints
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import math
import json
from datetime import datetime, timedelta
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class SIPCalculator:
    """
    Advanced SIP Calculator with multiple calculation methods
    """

    @staticmethod
    def calculate_sip(monthly_investment, annual_return_rate, time_period_years):
        """
        Calculate SIP returns using the standard compound interest formula
        Formula: FV = P × ({[1 + i]^n – 1} / i) × (1 + i)

        Args:
            monthly_investment (float): Monthly SIP amount
            annual_return_rate (float): Expected annual return rate (%)
            time_period_years (int): Investment period in years

        Returns:
            dict: Calculation results with invested amount, returns, and total value
        """
        try:
            # Convert to monthly values
            monthly_rate = annual_return_rate / 12 / 100
            total_months = time_period_years * 12

            # Calculate future value using SIP formula
            if monthly_rate == 0:
                # Handle zero interest rate
                future_value = monthly_investment * total_months
            else:
                future_value = monthly_investment * (
                    ((1 + monthly_rate) ** total_months - 1) / monthly_rate
                ) * (1 + monthly_rate)

            # Calculate total invested amount
            total_invested = monthly_investment * total_months

            # Calculate estimated returns
            estimated_returns = future_value - total_invested

            return {
                'success': True,
                'total_invested': round(total_invested, 2),
                'estimated_returns': round(estimated_returns, 2),
                'total_value': round(future_value, 2),
                'monthly_investment': monthly_investment,
                'annual_return_rate': annual_return_rate,
                'time_period_years': time_period_years,
                'total_months': total_months
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def calculate_lumpsum(lumpsum_amount, annual_return_rate, time_period_years):
        """
        Calculate lumpsum investment returns using compound interest
        Formula: A = P(1 + r/100)^t

        Args:
            lumpsum_amount (float): One-time investment amount
            annual_return_rate (float): Expected annual return rate (%)
            time_period_years (int): Investment period in years

        Returns:
            dict: Calculation results
        """
        try:
            # Calculate compound interest
            future_value = lumpsum_amount * ((1 + annual_return_rate/100) ** time_period_years)
            estimated_returns = future_value - lumpsum_amount

            return {
                'success': True,
                'total_invested': round(lumpsum_amount, 2),
                'estimated_returns': round(estimated_returns, 2),
                'total_value': round(future_value, 2),
                'lumpsum_amount': lumpsum_amount,
                'annual_return_rate': annual_return_rate,
                'time_period_years': time_period_years
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def generate_yearly_breakdown(monthly_investment, annual_return_rate, time_period_years):
        """
        Generate year-wise breakdown of SIP investment

        Returns:
            list: Year-wise data for analytics
        """
        yearly_data = []
        monthly_rate = annual_return_rate / 12 / 100

        for year in range(1, time_period_years + 1):
            months = year * 12

            if monthly_rate == 0:
                future_value = monthly_investment * months
            else:
                future_value = monthly_investment * (
                    ((1 + monthly_rate) ** months - 1) / monthly_rate
                ) * (1 + monthly_rate)

            total_invested = monthly_investment * months
            returns = future_value - total_invested

            yearly_data.append({
                'year': year,
                'total_invested': round(total_invested, 2),
                'estimated_returns': round(returns, 2),
                'total_value': round(future_value, 2)
            })

        return yearly_data

# API Routes
@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    Main calculation endpoint
    Accepts POST requests with calculation parameters
    """
    try:
        data = request.get_json()

        # Validate input data
        required_fields = ['monthlyInvestment', 'expectedReturn', 'timePeriod', 'mode']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        monthly_investment = float(data['monthlyInvestment'])
        annual_return_rate = float(data['expectedReturn'])
        time_period_years = int(data['timePeriod'])
        mode = data['mode']

        # Validate ranges
        if monthly_investment < 500 or monthly_investment > 100000:
            return jsonify({
                'success': False,
                'error': 'Monthly investment must be between ₹500 and ₹100,000'
            }), 400

        if annual_return_rate < 1 or annual_return_rate > 25:
            return jsonify({
                'success': False,
                'error': 'Expected return must be between 1% and 25%'
            }), 400

        if time_period_years < 1 or time_period_years > 50:
            return jsonify({
                'success': False,
                'error': 'Time period must be between 1 and 50 years'
            }), 400

        # Perform calculations based on mode
        if mode == 'sip':
            result = SIPCalculator.calculate_sip(
                monthly_investment, annual_return_rate, time_period_years
            )
        elif mode == 'lumpsum':
            result = SIPCalculator.calculate_lumpsum(
                monthly_investment, annual_return_rate, time_period_years
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid mode. Must be "sip" or "lumpsum"'
            }), 400

        return jsonify(result)

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid input values'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Calculation error: {str(e)}'
        }), 500

@app.route('/api/breakdown', methods=['POST'])
def get_breakdown():
    """
    Get yearly breakdown of SIP investment
    """
    try:
        data = request.get_json()

        monthly_investment = float(data['monthlyInvestment'])
        annual_return_rate = float(data['expectedReturn'])
        time_period_years = int(data['timePeriod'])

        breakdown = SIPCalculator.generate_yearly_breakdown(
            monthly_investment, annual_return_rate, time_period_years
        )

        return jsonify({
            'success': True,
            'breakdown': breakdown
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/goal-planning', methods=['POST'])
def goal_planning():
    """
    Reverse calculation: Calculate required SIP for a target amount
    """
    try:
        data = request.get_json()

        target_amount = float(data['targetAmount'])
        annual_return_rate = float(data['expectedReturn'])
        time_period_years = int(data['timePeriod'])

        monthly_rate = annual_return_rate / 12 / 100
        total_months = time_period_years * 12

        if monthly_rate == 0:
            required_sip = target_amount / total_months
        else:
            # Reverse SIP formula to find required monthly investment
            required_sip = target_amount / (
                (((1 + monthly_rate) ** total_months - 1) / monthly_rate) * (1 + monthly_rate)
            )

        return jsonify({
            'success': True,
            'required_sip': round(required_sip, 2),
            'target_amount': target_amount,
            'annual_return_rate': annual_return_rate,
            'time_period_years': time_period_years
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/comparison', methods=['POST'])
def comparison():
    """
    Compare SIP vs Lumpsum investment
    """
    try:
        data = request.get_json()

        amount = float(data['amount'])  # Monthly SIP or Lumpsum amount
        annual_return_rate = float(data['expectedReturn'])
        time_period_years = int(data['timePeriod'])

        # Calculate SIP
        sip_result = SIPCalculator.calculate_sip(
            amount, annual_return_rate, time_period_years
        )

        # Calculate equivalent lumpsum (same total investment)
        lumpsum_amount = amount * time_period_years * 12
        lumpsum_result = SIPCalculator.calculate_lumpsum(
            lumpsum_amount, annual_return_rate, time_period_years
        )

        return jsonify({
            'success': True,
            'sip': sip_result,
            'lumpsum': lumpsum_result,
            'comparison': {
                'sip_advantage': sip_result['total_value'] - lumpsum_result['total_value']
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000)
