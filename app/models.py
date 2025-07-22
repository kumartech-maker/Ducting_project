from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# User Model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

# Vendor Model
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gst_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)

# Project Model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(50), unique=True, nullable=False)
    quotation_no = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    source_diagram = db.Column(db.String(200), nullable=True)

    # Change these 3 to foreign key-style fields if needed
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    gst = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)

    incharge = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    contact = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)

    # Optional relationship if needed
    vendor = db.relationship('Vendor', backref='projects')
