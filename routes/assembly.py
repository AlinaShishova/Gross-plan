from flask import Blueprint, request, jsonify
from db_postgres import connect_db

assembly_bp = Blueprint("assembly", __name__)

@assembly_bp.route('/save_dates', methods=['POST'])
def save_dates():
    data = request.json
    id, name, start_date, end_date = data['assembly_id'], data.get(
        'assembly_name'), data['start_date'], data['end_date']

    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO assembly (assembly_id, assembly_name, start_date, end_date) VALUES (%s,%s, %s, %s) ON CONFLICT (assembly_id) DO UPDATE SET start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date",
                               (id, name, start_date, end_date))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})




@assembly_bp.route('/delete_entry', methods=['POST'])
def delete_entry():
    data = request.json
    id = data.get('assembly_id')

    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM assembly WHERE assembly_id = %s", (id,))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
