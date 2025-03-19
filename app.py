from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap5
from config import Config
import db_oracle
from auth_wraps import login_required 
from routes.auth import auth_bp
from routes.keys import keys_bp
from routes.assembly import assembly_bp
from routes.sheme import scheme_bp


app = Flask(__name__, static_url_path='/static', static_folder='static')
bootstrap = Bootstrap5(app)
app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(keys_bp)
app.register_blueprint(assembly_bp)
app.register_blueprint(scheme_bp)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/cubs/')
@login_required
def cubs():
    return render_template('cubs.html')



@app.route('/spec/')
@login_required
def spec():
    ps_ind = request.args.get('ps_ind')  # Получаем переданный параметр из URL
    results = db_oracle.execute_query("spec", {"ps_ind":ps_ind})
    return render_template('spec.html', results=results)


@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    row_id = data["cube_specification_id"]
    new_status = data["stop"]
    db_oracle.execute_query("update_status", {"stop": new_status, "cube_specification_id": row_id})
    return jsonify({"success": True, "cube_specification_id": row_id, "new_status": new_status})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
