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
                    gauge, area, g24, g22, g20, g18
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry['duct_no'], entry['duct_type'], entry['w1'], entry['h1'],
                entry['w2'], entry['h2'], entry['length'], entry['degree'], entry['quantity'],
                entry.get('factor', 1), entry['gauge'], entry['area'],
                entry['g24'], entry['g22'], entry['g20'], entry['g18']
            ))
        conn.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
