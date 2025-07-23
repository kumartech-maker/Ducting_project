from flask import Blueprint, request, jsonify
import sqlite3

measurement_bp = Blueprint('measurement', __name__)

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Gauge calculation based on width and height
def determine_gauge(w1, h1):
    if 0 <= w1 <= 750 and 0 <= h1 <= 750:
        return '24g'
    elif 751 <= w1 <= 1200 or 751 <= h1 <= 1200:
        return '22g'
    elif 1201 <= w1 <= 1800 or 1201 <= h1 <= 1800:
        return '20g'
    elif w1 > 1800 or h1 > 1800:
        return '18g'
    else:
        return '24g'

# Area calculation based on duct type
def calculate_area(duct_type, w1, h1, w2, h2, length, degree, quantity, factor):
    area = 0
    if duct_type == 'st':
        area = ((w1 + h1) * 2 * length) / 1_000_000
    elif duct_type == 'elb':
        area = ((w1 + h1) * 3.14 * degree * 0.5) / 1_000_000
    elif duct_type == 'red':
        area = (((w1 + h1 + w2 + h2) / 2) * length) / 1_000_000
    elif duct_type == 'dm':
        area = ((w1 + h1) * 2 * length) / 1_000_000 * 2
    elif duct_type == 'offset':
        area = (((w1 + h1 + w2 + h2) / 2) * length) / 1_000_000
    elif duct_type == 'shoe':
        area = ((w1 + h1) * length) / 1_000_000
    elif duct_type == 'vanes':
        area = ((w1 + h1) * 2 * length) / 1_000_000
    area *= quantity * factor
    return round(area, 3)

@measurement_bp.route('/calculate_measurement', methods=['POST'])
def calculate_measurement():
    try:
        data = request.get_json()

        duct_type = data.get('duct_type', '').lower()
        w1 = float(data.get('w1', 0))
        h1 = float(data.get('h1', 0))
        w2 = float(data.get('w2', 0))
        h2 = float(data.get('h2', 0))
        length = float(data.get('length', 0))
        degree = float(data.get('degree', 0))
        quantity = int(data.get('quantity', 1))
        factor = float(data.get('factor', 1))

        gauge = determine_gauge(w1, h1)
        area = calculate_area(duct_type, w1, h1, w2, h2, length, degree, quantity, factor)

        # Material calculations
        cleat = round((w1 + h1 + w2 + h2) * quantity / 1000, 2)
        nuts_bolts = quantity * 4
        gasket = round((w1 + h1 + w2 + h2) / 1000 * quantity, 2)
        corner = quantity * 4

        # Gauge-based area split
        g24 = area if gauge == '24g' else 0
        g22 = area if gauge == '22g' else 0
        g20 = area if gauge == '20g' else 0
        g18 = area if gauge == '18g' else 0

        result = {
            'gauge': gauge,
            'area': area,
            'g24': g24,
            'g22': g22,
            'g20': g20,
            'g18': g18,
            'cleat': cleat,
            'nuts_bolts': nuts_bolts,
            'gasket': gasket,
            'corner': corner
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@measurement_bp.route('/save_measurements', methods=['POST'])
def save_measurements():
    data = request.get_json()

    try:
        conn = get_db()
        cur = conn.cursor()
        for entry in data['entries']:
            cur.execute('''
                INSERT INTO measurements (
                    duct_no, duct_type, w1, h1, w2, h2, length, degree, quantity, factor, 
                    gauge, area, g24, g22, g20, g18, cleat, nuts_bolts, gasket, corner
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry['duct_no'], entry['duct_type'], entry['w1'], entry['h1'],
                entry['w2'], entry['h2'], entry['length'], entry['degree'], entry['quantity'],
                entry.get('factor', 1), entry['gauge'], entry['area'],
                entry['g24'], entry['g22'], entry['g20'], entry['g18'],
                entry['cleat'], entry['nuts_bolts'], entry['gasket'], entry['corner']
            ))
        conn.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
