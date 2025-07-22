from flask import Blueprint, request, jsonify
import sqlite3

measurement_bp = Blueprint('measurement', __name__)

# DB connection
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Route 1: Save measurements to database
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
                    gauge, area, g24, g22, g20, g18,
                    nuts_bolts, cleat, gasket, corner
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry['duct_no'],
                entry['duct_type'],
                entry['w1'],
                entry['h1'],
                entry['w2'],
                entry['h2'],
                entry['length'],
                entry['degree'],
                entry['quantity'],
                entry.get('factor', 1),
                entry['gauge'],
                entry['area'],
                entry['g24'],
                entry['g22'],
                entry['g20'],
                entry['g18'],
                entry['nuts_bolts'],
                entry['cleat'],
                entry['gasket'],
                entry['corner']
            ))
        conn.commit()
        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



# Route 2: Calculate values for a single measurement entry
@measurement_bp.route('/calculate_measurement', methods=['POST'])
def calculate_measurement():
    try:
        data = request.get_json()

        duct_type = data.get('duct_type', '').upper()
        width1 = float(data.get('width1', 0))
        height1 = float(data.get('height1', 0))
        width2 = float(data.get('width2', 0))
        height2 = float(data.get('height2', 0))
        length = float(data.get('length', 0))
        degree = float(data.get('degree', 0))
        quantity = int(data.get('quantity', 1))
        factor = float(data.get('factor', 1))

        # Gauge calculation
        if 0 <= width1 <= 751 and 0 <= height1 <= 751:
            gauge = '24g'
        elif 751 < width1 <= 1201 and 751 < height1 <= 1201:
            gauge = '22g'
        elif 1201 < width1 <= 1800 and 1201 < height1 <= 1800:
            gauge = '20g'
        elif width1 > 1800 and height1 > 1800:
            gauge = '18g'
        else:
            gauge = '18g'  # default/fallback

        # Area calculation by type
        if duct_type == 'ST':
            area = 2 * (width1 + height1) / 1000 * (length / 1000) * quantity
        elif duct_type == 'RED':
            area = (width1 + height1 + width2 + height2) / 1000 * (length / 1000) * quantity * factor
        elif duct_type == 'DUM':
            area = (width1 * height1) / 1_000_000 * quantity
        elif duct_type == 'OFFSET':
            area = (width1 + height1 + width2 + height2) / 1000 * ((length + degree) / 1000) * quantity * factor
        elif duct_type == 'SHOE':
            area = (width1 + height1) * 2 / 1000 * (length / 1000) * quantity * factor
        elif duct_type == 'VANES':
            area = width1 / 1000 * (2 * 3.14 * (width1 / 1000) / 4) * quantity
        elif duct_type == 'ELB':
            area = 2 * (width1 + height1) / 1000 * ((height1 / 2 / 1000) + (length / 1000) * (3.14 * (degree / 180))) * quantity * factor
        else:
            area = 0

        # Material Calculations
        nuts_bolts = quantity * 4

        cleat = (
            quantity * 4 if gauge == '24g' else
            quantity * 8 if gauge == '22g' else
            quantity * 10 if gauge == '20g' else
            quantity * 12
        )

        gasket = (width1 + height1 + width2 + height2) / 1000 * quantity
        corner = 0 if duct_type == 'DUM' else quantity * 8

        # Area breakdown by gauge
        g24 = round(area, 3) if gauge == '24g' else 0
        g22 = round(area, 3) if gauge == '22g' else 0
        g20 = round(area, 3) if gauge == '20g' else 0
        g18 = round(area, 3) if gauge == '18g' else 0

        return jsonify({
            'gauge': gauge,
            'area': round(area, 3),
            'g24': g24,
            'g22': g22,
            'g20': g20,
            'g18': g18,
            'nuts_bolts': nuts_bolts,
            'cleat': cleat,
            'gasket': round(gasket, 3),
            'corner': corner
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
