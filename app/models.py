from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.String(50), unique=True, nullable=False)
    quotation_no = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    source_diagram = db.Column(db.String(200), nullable=True)
    vendor_name = db.Column(db.String(100), nullable=False)
    gst_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    project_incharge = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    mail_id = db.Column(db.String(100), nullable=True)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    gst_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
