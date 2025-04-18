from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap5
from config import Config
from datetime import datetime
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
    data = request.get_json() 

    # Проверяем, что все необходимые поля присутствуют
    required_fields = ["dse_id", "date_general", "stop", "spec_id"]
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
    # in_parent_branch_num = request.args.get('in_parent_branch_num')
    
    # Проверяем обязательные параметры
    if not all([in_cube_spec_id, in_parent_da_path, in_parent_da_index]):
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
        # in_parent_branch_num = int(in_parent_branch_num)
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
        "in_parent_da_index": in_parent_da_index

    })

    return render_template('product.html', results=results)

@app.route('/insert_cube_component', methods=['POST']) # Сохранение позиции cube_components
@login_required
def insert_cube_component():
    # Получаем данные из запроса
    data = request.json

    # Проверяем, что все необходимые поля присутствуют
    required_fields = ["cube_specification_id", "dse_id", "date_start", "date_end", "date_assembling", "da_index", "da_path"]
    print("Полученные данные:", data)  # Временный лог
    if not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Недостаточно данных"}), 400
    db_oracle.execute_query('insert_cube_component',data)
    # Если все ок, возвращаем JSON-ответ
    return jsonify({"status": "success", "message": "Данные успешно добавлены"}), 200

@app.route('/delete_cube_component', methods=['POST'])
@login_required
def delete_cube_component():
    try:
        data = request.get_json()
        component_id = data['cube_component_id']
        
        # Выполняем запрос
        db_oracle.execute_query('delete_cube_component', {
            'component_id': component_id
        })
        
        return jsonify({
            "success": True,
            "message": "Запись успешно удалена"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка удаления: {str(e)}"
        }), 500
        
  
  
@app.route('/delete_spec', methods=['POST'])
@login_required
def delete_spec_component():
    try:
        data = request.get_json()
        component_id = data['spec_id']
        
        # Выполняем запрос
        db_oracle.execute_query('delete_spec', {
            'spec_id': component_id
        })
        
        return jsonify({
            "success": True,
            "message": "Запись успешно удалена"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка удаления: {str(e)}"
        }), 500
          

@app.route('/update_spec_date', methods=['POST'])
@login_required
def update_spec_date():
    data = request.json
    row_id = data["specId"]
    new_date = data["newDate"]
    db_oracle.execute_query("update_spec_date", {"date_start": new_date, "cube_specification_id": row_id})
    return jsonify({"success": True, "cube_specification_id": row_id, "new_date": new_date})




@app.route('/gantt/<int:node_id>')
def gantt(node_id):
    try:
        spec_name = request.args.get('spec_name', default='Без названия')
        rows = db_oracle.execute_query("gantt", {"node_id": node_id})
        result = []
        today = datetime.today()

        for row in rows:
            start = datetime.strptime(row[3], '%Y-%m-%d') if row[3] else None
            end = datetime.strptime(row[4], '%Y-%m-%d') if row[4] else None

            if start and end and start < end:
                total = (end - start).days
                elapsed = (today - start).days
                progress = min(max(elapsed / total, 0), 1)  # Ограничим в пределах [0, 1]
            else:
                progress = 0
    
            result.append({
                "id": row[0],
                "name": row[1],
                "parent": row[2],
                "d_start": row[3],
                "d_end": row[4],
                "color": row[7],
                "dependency":row[6],
                "completed": {
                 "amount": round(progress, 2)}
            })

            
        print(f"start: {start}, end: {end}, today: {today}, elapsed: {elapsed}, total: {total}, progress: {progress}")

        return render_template('gantt.html', gantt_data=result, spec_name=spec_name)
       

    except Exception as e:
        print(f"Ошибка при получении графика: {e}")
        return jsonify({"error": "Ошибка сервера"}), 500

    
# Тест тепловой карты загрузки
# ===================================================================
from chart_generator import generate_heatmap
@app.route("/heatmap/")
def show_heatmap():
    heatmap_html = generate_heatmap()
    return render_template("heatmap.html", heatmap_html=heatmap_html)
# ===================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
