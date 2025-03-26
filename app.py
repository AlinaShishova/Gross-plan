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
    return render_template('spec.html', results=results, ps_ind=ps_ind) # КС Добавил параметр

@app.route('/spec_select/')  # КС добавил route
@login_required
def spec_select():
    pay_unit_id = request.args.get('pay_unit_id')  # Получаем параметр из URL
    if not pay_unit_id:
        return "Параметр pay_unit_id отсутствует", 400  # Обработка ошибки

    results = db_oracle.execute_query("spec_select", {"pay_unit_id": pay_unit_id})
    return render_template('spec_select.html', results=results)
##-----------------------------------------

@app.route('/insert_spec', methods=['POST'])
def insert_spec():
    # Получаем данные из запроса
    data = request.json

    # Проверяем, что все необходимые поля присутствуют
    required_fields = ["dse_id", "date_general", "spec_id", "num"]
    print("Полученные данные:", data)  # Временный лог
    if not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Недостаточно данных"}), 400
    db_oracle.execute_query('insert_spec',data)
    # Если все ок, возвращаем JSON-ответ
    return jsonify({"status": "success", "message": "Данные успешно добавлены"}), 200
       


# ##-----------------------------------------

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    row_id = data["cube_specification_id"]
    new_status = data["stop"]
    db_oracle.execute_query("update_status", {"stop": new_status, "cube_specification_id": row_id})
    return jsonify({"success": True, "cube_specification_id": row_id, "new_status": new_status})

@app.route('/product/')
@login_required
def product():
    # Извлекаем параметры из URL
    in_cube_spec_id = request.args.get('in_cube_spec_id') 
    in_parent_da_path = request.args.get('in_parent_da_path')
    in_parent_da_index = request.args.get('in_parent_da_index')
    in_parent_branch_num = request.args.get('in_parent_branch_num')
    
    # Проверяем обязательные параметры
    if not all([in_cube_spec_id, in_parent_da_path, in_parent_da_index,in_parent_branch_num]):
        return "Не все обязательные параметры переданы", 400
    
    # Обработка для in_parent_da_index
    if in_parent_da_index == 'None':
        in_parent_da_index = None
    elif in_parent_da_index is not None:
        try:
            in_parent_da_index = int(in_parent_da_index)
        except ValueError:
            return "Некорректный параметр in_parent_da_index", 400
    
    # Преобразуем в int
    try:
        in_cube_spec_id = int(in_cube_spec_id)
        in_parent_branch_num = int(in_parent_branch_num)
    except ValueError:
        return "Некорректный параметр in_cube_spec_id", 400
    
    # Проверка
    # print(f"in_cube_spec_id: {in_cube_spec_id}")
    # print(f"parent_da_path: {in_parent_da_path}")
    # print(f"in_parent_da_index: {in_parent_da_index} (type: {type(in_parent_da_index)})")
    
    # Обработка запроса
    results = db_oracle.execute_query('level_products', {
        "in_cube_spec_id": in_cube_spec_id,
        "in_parent_da_path": in_parent_da_path,
        "in_parent_da_index": in_parent_da_index,
        "in_parent_branch_num":in_parent_branch_num, 
    })

    return render_template('product.html', results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
