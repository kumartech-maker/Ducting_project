from flask import Blueprint, request, jsonify
from models import db, Measurement
import math

measurement_bp = Blueprint('measurement', __name__)

def calculate_area(duct_type, w1, h1, w2, h2, length, degree, factor, quantity):
    w1 = float(w1)
    h1 = float(h1)
    w2 = float(w2)
    h2 = float(h2)
    length = float(length)
    factor = float(factor) if factor else 1
    quantity = int(quantity)

    area = 0

    if duct_type == 'st':
        area = 2 * (w1 + h1) * length / 1000000
    elif duct_type == 'elb':
        area = 1.57 * (w1 + h1) * length / 1000000
    elif duct_type == 'red':
        area = 2 * ((w1 + w2) / 2 + (h1 + h2) / 2) * length / 1000000
    elif duct_type == 'dm':
        area = 2 * (w1 + h1) * length / 1000000
    elif duct_type == 'offset':
        area = 2 * (w1 + h1) * length / 1000000
    elif duct_type == 'shoe':
        area = 2 * ((w1 + w2) / 2 + (h1 + h2) / 2) * length / 1000000
    elif duct_type == 'vanes':
        area = 2 * (w1 + h1) * length / 1000000
    else:
        area = 0

    area *= factor
    total_area = round(area * quantity, 3)
    return total_area

def determine_gauge(w1, h1):
    if 0 <= w1 <= 751 and 0 <= h1 <= 751:
        return '24g'
    elif 751 < w1 <= 1201 and 751 < h1 <= 1201:
        return '22g'
    elif 1201 < w1 <= 1800 and 1201 < h1 <= 1800:
        return '20g'
    elif w1 > 1800 and h1 > 1800:
        return '18g'
    else:
        return '22g'  # default

@measurement_bp.route('/calculate_measurement', methods=['POST'])
def calculate_measurement():
    data = request.json

    duct_type = data['duct_type']
    w1 = int(data['w1'])
    h1 = int(data['h1'])
    w2 = int(data['w2'])
    h2 = int(data['h2'])
    length = int(data['length'])
    degree = data.get('degree', '')
    quantity = int(data['quantity'])
    factor = float(data['factor']) if data.get('factor') else 1.0

    area = calculate_area(duct_type, w1, h1, w2, h2, length, degree, factor, quantity)
    gauge = determine_gauge(w1, h1)

    # Fill area under correct gauge
    g24 = area if gauge == '24g' else 0
    g22 = area if gauge == '22g' else 0
    g20 = area if gauge == '20g' else 0
    g18 = area if gauge == '18g' else 0

    # Additional material calculations
    gasket = round((w1 + h1) * 2 * quantity / 1000, 3)
    nuts_bolts = quantity * 4
    cleat = round(((w1 + h1) * 2 * quantity) / 1000, 3)
    corner = quantity * 4

    return jsonify({
        'gauge': gauge,
        'area': area,
        'g24': g24,
        'g22': g22,
        'g20': g20,
        'g18': g18,
        'nuts_bolts': nuts_bolts,
        'cleat': cleat,
        'gasket': gasket,
        'corner': corner
    })

@measurement_bp.route('/submit_measurement', methods=['POST'])
def submit_measurement():
    data = request.json

    entry = Measurement(
        duct_no=data['duct_no'],
        duct_type=data['duct_type'],
        w1=int(data['w1']),
        h1=int(data['h1']),
        w2=int(data['w2']),
        h2=int(data['h2']),
        length=int(data['length']),
        degree=data.get('degree', ''),
        quantity=int(data['quantity']),
        factor=float(data.get('factor') or 1.0),
        gauge=data['gauge'],
        area=float(data['area']),
        g24=float(data['g24']),
        g22=float(data['g22']),
        g20=float(data['g20']),
        g18=float(data['g18']),
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({'success': True})
