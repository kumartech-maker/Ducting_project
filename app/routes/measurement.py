from flask import Blueprint, request, jsonify
import math

measurement_bp = Blueprint('measurement', __name__)

@measurement_bp.route('/calculate_measurement', methods=['POST'])
def calculate_measurement():
    data = request.get_json()

    try:
        w1 = float(data.get('w1', 0))
        h1 = float(data.get('h1', 0))
        w2 = float(data.get('w2', 0))
        h2 = float(data.get('h2', 0))
        length = float(data.get('length', 0))
        degree = float(data.get('degree', 0))
        quantity = int(data.get('quantity', 1))
        factor = float(data.get('factor', 1))
        duct_type = data.get('duct_type', 'st')

        # Normalize W2 and H2 for taper types
        if w2 == 0:
            w2 = w1
        if h2 == 0:
            h2 = h1

        # Area logic (example simplified, you can expand per duct_type if needed)
        if duct_type in ['st', 'vanes', 'shoe']:
            perimeter = 2 * (w1 + h1)
            area = (perimeter * length * quantity) / 1000000
        elif duct_type == 'elb':
            area = (math.pi * (w1 + h1) * degree / 360 * quantity) / 1000
        elif duct_type == 'red':
            perimeter_avg = 2 * ((w1 + w2) / 2 + (h1 + h2) / 2)
            area = (perimeter_avg * length * quantity) / 1000000
        elif duct_type == 'dm':
            area = (2 * ((w1 * h1) + (w2 * h2)) + (w1 + w2) * length + (h1 + h2) * length) * quantity / 1000000
        elif duct_type == 'offset':
            area = (2 * (w1 + h1) * length * quantity) / 1000000
        else:
            area = (2 * (w1 + h1) * length * quantity) / 1000000

        area *= factor
        area = round(area, 2)

        # Determine gauge
        if 0 <= w1 <= 750 and 0 <= h1 <= 750:
            gauge = '24g'
        elif 751 <= w1 <= 1200 or 751 <= h1 <= 1200:
            gauge = '22g'
        elif 1201 <= w1 <= 1800 or 1201 <= h1 <= 1800:
            gauge = '20g'
        else:
            gauge = '18g'

        # Assign area to correct gauge
        g24 = area if gauge == '24g' else 0
        g22 = area if gauge == '22g' else 0
        g20 = area if gauge == '20g' else 0
        g18 = area if gauge == '18g' else 0

        # Other calculations
        cleat = round(area * 1.2, 2)
        nuts_bolts = round(area * 0.8, 2)
        gasket = round(area * 0.5, 2)
        corner = round(area * 0.2, 2)

        return jsonify({
            "gauge": gauge,
            "area": area,
            "g24": g24,
            "g22": g22,
            "g20": g20,
            "g18": g18,
            "cleat": cleat,
            "nuts_bolts": nuts_bolts,
            "gasket": gasket,
            "corner": corner
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Optional: Save entries if you want to persist data
@measurement_bp.route('/save_measurements', methods=['POST'])
def save_measurements():
    data = request.get_json()
    try:
        # Connect to DB
        from db import get_db  # You must have this file

        conn = get_db()
        cur = conn.cursor()

        for entry in data:
            cur.execute('''
                INSERT INTO measurement_entries (
                    duct_no, duct_type, w1, h1, w2, h2, length, degree, quantity, factor,
                    gauge, g24, g22, g20, g18, area, cleat, nuts_bolts, gasket, corner
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry['duct_no'], entry['duct_type'], entry['w1'], entry['h1'],
                entry['w2'], entry['h2'], entry['length'], entry['degree'], entry['quantity'], entry['factor'],
                entry['gauge'], entry['g24'], entry['g22'], entry['g20'], entry['g18'],
                entry['area'], entry['cleat'], entry['nuts_bolts'], entry['gasket'], entry['corner']
            ))

        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
