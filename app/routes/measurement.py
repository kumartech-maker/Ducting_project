from flask import Blueprint, request, jsonify
import sqlite3

measurement_bp = Blueprint('measurement', __name__)

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


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
                entry['duct_no'], entry['duct_type'],
                entry['w1'], entry['h1'], entry['w2'], entry['h2'],
                entry['length'], entry['degree'], entry['quantity'], entry.get('factor', 1),
                entry['gauge'], entry['area'],
                entry['g24'], entry['g22'], entry['g20'], entry['g18'],
                entry['nuts_bolts'], entry['cleat'], entry['gasket'], entry['corner']
            ))
        conn.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@measurement_bp.route('/calculate_measurement', methods=['POST'])
def calculate_measurement():
    try:
        data = request.get_json()

        duct_type = data.get('duct_type', '').upper()
        w1 = float(data.get('width1', 0))
        h1 = float(data.get('height1', 0))
        w2 = float(data.get('width2') or 0)
        h2 = float(data.get('height2') or 0)
        length = float(data.get('length', 0))
        degree = float(data.get('degree', 0))
        qty = int(data.get('quantity', 1))
        factor = float(data.get('factor', 1))

        max_dim = max(w1, h1)
        if max_dim <= 750:
            gauge = '24g'
        elif max_dim <= 1200:
            gauge = '22g'
        elif max_dim <= 1800:
            gauge = '20g'
        else:
            gauge = '18g'

        # Area calculation
        if duct_type == 'ST':
            area = 2 * (w1 + h1) / 1000 * (length / 1000) * qty
        elif duct_type == 'RED':
            area = (w1 + h1 + w2 + h2) / 1000 * (length / 1000) * qty * factor
        elif duct_type == 'DM':
            area = (w1 * h1) / 1_000_000 * qty
        elif duct_type == 'OFFSET':
            area = (w1 + h1 + w2 + h2) / 1000 * ((length + degree) / 1000) * qty * factor
        elif duct_type == 'SHOE':
            area = (w1 + h1) * 2 / 1000 * (length / 1000) * qty * factor
        elif duct_type == 'VANES':
            area = w1 / 1000 * (2 * 3.14 * (w1 / 1000) / 4) * qty
        elif duct_type == 'ELB':
            area = 2 * (w1 + h1) / 1000 * ((h1 / 2 / 1000) + (length / 1000) * (3.14 * (degree / 180))) * qty * factor
        else:
            area = 0

        # Material counts
        nuts_bolts = qty * 4

        if gauge == '24g':
            cleat = qty * 4
        elif gauge == '22g':
            cleat = qty * 8
        elif gauge == '20g':
            cleat = qty * 10
        elif gauge == '18g':
            cleat = qty * 12
        else:
            cleat = 0

        gasket = (w1 + h1 + w2 + h2) / 1000 * qty
        corner = 0 if duct_type == 'DM' else qty * 8

        # Gauge-wise area
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
        
