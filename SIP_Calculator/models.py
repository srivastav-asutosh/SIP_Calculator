
"""
Database models for SIP Calculator Dashboard
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for storing user information"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    calculations = db.relationship('SIPCalculation', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('InvestmentGoal', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class SIPCalculation(db.Model):
    """Model for storing SIP calculation history"""

    __tablename__ = 'sip_calculations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Allow anonymous calculations

    # Calculation parameters
    calculation_type = db.Column(db.String(20), nullable=False)  # 'sip' or 'lumpsum'
    monthly_investment = db.Column(db.Float, nullable=False)
    annual_return_rate = db.Column(db.Float, nullable=False)
    time_period_years = db.Column(db.Integer, nullable=False)

    # Results
    total_invested = db.Column(db.Float, nullable=False)
    estimated_returns = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    session_id = db.Column(db.String(100), nullable=True)  # For anonymous users

    def to_dict(self):
        return {
            'id': self.id,
            'calculation_type': self.calculation_type,
            'monthly_investment': self.monthly_investment,
            'annual_return_rate': self.annual_return_rate,
            'time_period_years': self.time_period_years,
            'total_invested': self.total_invested,
            'estimated_returns': self.estimated_returns,
            'total_value': self.total_value,
            'created_at': self.created_at.isoformat()
        }

class InvestmentGoal(db.Model):
    """Model for storing user investment goals"""

    __tablename__ = 'investment_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    goal_name = db.Column(db.String(200), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)

    # Calculation parameters
    required_monthly_sip = db.Column(db.Float, nullable=True)
    expected_return_rate = db.Column(db.Float, nullable=False)

    # Status tracking
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'goal_name': self.goal_name,
            'target_amount': self.target_amount,
            'target_date': self.target_date.isoformat(),
            'current_amount': self.current_amount,
            'required_monthly_sip': self.required_monthly_sip,
            'expected_return_rate': self.expected_return_rate,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CalculationHistory(db.Model):
    """Model for detailed calculation history and analytics"""

    __tablename__ = 'calculation_history'

    id = db.Column(db.Integer, primary_key=True)
    calculation_id = db.Column(db.Integer, db.ForeignKey('sip_calculations.id'), nullable=False)

    # Yearly breakdown data (stored as JSON)
    yearly_breakdown = db.Column(db.Text, nullable=False)  # JSON string

    # Additional analytics
    inflation_adjusted = db.Column(db.Boolean, default=False)
    inflation_rate = db.Column(db.Float, nullable=True)
    tax_adjusted = db.Column(db.Boolean, default=False)
    tax_rate = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_yearly_breakdown(self, breakdown_data):
        """Set yearly breakdown data as JSON"""
        self.yearly_breakdown = json.dumps(breakdown_data)

    def get_yearly_breakdown(self):
        """Get yearly breakdown data from JSON"""
        return json.loads(self.yearly_breakdown) if self.yearly_breakdown else []

    def to_dict(self):
        return {
            'id': self.id,
            'calculation_id': self.calculation_id,
            'yearly_breakdown': self.get_yearly_breakdown(),
            'inflation_adjusted': self.inflation_adjusted,
            'inflation_rate': self.inflation_rate,
            'tax_adjusted': self.tax_adjusted,
            'tax_rate': self.tax_rate,
            'created_at': self.created_at.isoformat()
        }
