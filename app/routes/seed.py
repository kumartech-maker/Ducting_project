# routes/seed.py
from flask import Blueprint
from ..models import db, Vendor

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed_vendors')
def seed_vendors():
    if not Vendor.query.first():
        v1 = Vendor(name="ABC Enterprises", gst_number="29ABCDE1234F2Z5", address="Chennai, TN")
        v2 = Vendor(name="XYZ Solutions", gst_number="33XYZDE5678G1Z9", address="Coimbatore, TN")
        db.session.add_all([v1, v2])
        db.session.commit()
        return "Dummy vendors added"
    return "Vendors already exist"
