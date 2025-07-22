# routes/seed.py
from flask import Blueprint
from ..models import db, Vendor

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed_vendors')
def seed_vendors():
    if Vendor.query.first():  # Prevent re-adding if already seeded
        return "Vendors already exist."

    vendors = [
        Vendor(name="ABC Supplies", gst_number="27ABCDE1234F1Z5", address="123 Industrial Area, Chennai"),
        Vendor(name="XYZ Traders", gst_number="33XYZDE5678G1Z9", address="56 Phase II, Coimbatore"),
        Vendor(name="SteelWorld", gst_number="29STEEL0987H1Z3", address="45-B Main Road, Bangalore")
    ]

    db.session.add_all(vendors)
    db.session.commit()
    return "Dummy vendors added successfully!"
