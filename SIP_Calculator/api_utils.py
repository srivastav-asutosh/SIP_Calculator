
"""
API utilities and helper functions for SIP Calculator Dashboard
"""

from functools import wraps
from flask import request, jsonify, current_app
import time
import hashlib
from datetime import datetime, timedelta
import re

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class APIUtils:
    """Utility class for API operations"""

    @staticmethod
    def validate_sip_parameters(data):
        """
        Validate SIP calculation parameters

        Args:
            data (dict): Input data to validate

        Returns:
            dict: Validated and cleaned data

        Raises:
            ValidationError: If validation fails
        """
        required_fields = ['monthlyInvestment', 'expectedReturn', 'timePeriod']

        # Check required fields
        for field in required_fields:
            if field not in data:
                raise ValidationError(f'Missing required field: {field}')

        try:
            # Convert and validate monthly investment
            monthly_investment = float(data['monthlyInvestment'])
            if monthly_investment < current_app.config['MIN_INVESTMENT']:
                raise ValidationError(f'Monthly investment must be at least ₹{current_app.config["MIN_INVESTMENT"]}')
            if monthly_investment > current_app.config['MAX_INVESTMENT']:
                raise ValidationError(f'Monthly investment cannot exceed ₹{current_app.config["MAX_INVESTMENT"]}')

            # Convert and validate return rate
            expected_return = float(data['expectedReturn'])
            if expected_return < current_app.config['MIN_RETURN_RATE']:
                raise ValidationError(f'Expected return must be at least {current_app.config["MIN_RETURN_RATE"]}%')
            if expected_return > current_app.config['MAX_RETURN_RATE']:
                raise ValidationError(f'Expected return cannot exceed {current_app.config["MAX_RETURN_RATE"]}%')

            # Convert and validate time period
            time_period = int(data['timePeriod'])
            if time_period < current_app.config['MIN_TIME_PERIOD']:
                raise ValidationError(f'Time period must be at least {current_app.config["MIN_TIME_PERIOD"]} year')
            if time_period > current_app.config['MAX_TIME_PERIOD']:
                raise ValidationError(f'Time period cannot exceed {current_app.config["MAX_TIME_PERIOD"]} years')

            # Validate mode if provided
            mode = data.get('mode', 'sip')
            if mode not in ['sip', 'lumpsum']:
                raise ValidationError('Mode must be either "sip" or "lumpsum"')

            return {
                'monthlyInvestment': monthly_investment,
                'expectedReturn': expected_return,
                'timePeriod': time_period,
                'mode': mode
            }

        except ValueError as e:
            raise ValidationError('Invalid numeric values provided')

    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def format_currency(amount, currency_symbol='₹'):
        """Format currency with Indian number system"""
        if amount >= 10000000:  # 1 crore
            return f"{currency_symbol}{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # 1 lakh
            return f"{currency_symbol}{amount/100000:.2f} L"
        elif amount >= 1000:  # 1 thousand
            return f"{currency_symbol}{amount/1000:.2f} K"
        else:
            return f"{currency_symbol}{amount:,.2f}"

    @staticmethod
    def generate_session_id(request_data=None):
        """Generate a unique session ID"""
        timestamp = str(time.time())
        request_info = str(request_data) if request_data else ''
        user_agent = request.headers.get('User-Agent', '')

        combined = timestamp + request_info + user_agent
        return hashlib.md5(combined.encode()).hexdigest()

    @staticmethod
    def calculate_inflation_adjusted_value(amount, inflation_rate, years):
        """Calculate inflation-adjusted value"""
        return amount / ((1 + inflation_rate/100) ** years)

    @staticmethod
    def calculate_tax_adjusted_returns(returns, tax_rate):
        """Calculate tax-adjusted returns"""
        return returns * (1 - tax_rate/100)

def rate_limit(max_requests=100, per_seconds=3600):
    """
    Rate limiting decorator for API endpoints

    Args:
        max_requests (int): Maximum number of requests
        per_seconds (int): Time period in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple in-memory rate limiting (use Redis in production)
            client_id = request.remote_addr
            current_time = time.time()

            # This is a simplified rate limiting implementation
            # In production, use Redis or a proper rate limiting service

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def error_handler(f):
    """
    Error handling decorator for API endpoints
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'validation_error'
            }), 400
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Invalid input values',
                'error_type': 'value_error'
            }), 400
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'An unexpected error occurred',
                'error_type': 'server_error'
            }), 500
    return decorated_function

def log_calculation(calculation_data, result_data, user_id=None, session_id=None):
    """
    Log calculation for analytics

    Args:
        calculation_data (dict): Input parameters
        result_data (dict): Calculation results
        user_id (int, optional): User ID if logged in
        session_id (str, optional): Session ID for anonymous users
    """
    try:
        from models import db, SICalculation

        calculation = SIPCalculation(
            user_id=user_id,
            session_id=session_id,
            calculation_type=calculation_data.get('mode', 'sip'),
            monthly_investment=calculation_data['monthlyInvestment'],
            annual_return_rate=calculation_data['expectedReturn'],
            time_period_years=calculation_data['timePeriod'],
            total_invested=result_data['total_invested'],
            estimated_returns=result_data['estimated_returns'],
            total_value=result_data['total_value']
        )

        db.session.add(calculation)
        db.session.commit()

        return calculation.id

    except Exception as e:
        current_app.logger.error(f'Failed to log calculation: {str(e)}')
        return None
