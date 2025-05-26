from flask import Flask, render_template, request, jsonify, redirect, flash, url_for
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

@app.route('/save_cube_component', methods=['POST']) # Сохранение позиции cube_components
@login_required
def save_cube_component():

    try:
 
        data = request.get_json()
        print("SAVE_PAYLOAD:", data)
        cube_component_id = data.get("cube_component_id")
        
        # Если передан cube_component_id, проверяем, существует ли запись
        if cube_component_id:
            existing = db_oracle.execute_query("check_cube_component", {"cube_component_id": cube_component_id})
            if existing and len(existing) > 0:
                # Запись существует – выполняем UPDATE
                db_oracle.execute_query("update_cube_component", data)
                return jsonify({"success": True, "operation": "update"})
        else:
            # Если записи нет (или cube_component_id не задан), выполняем INSERT
            db_oracle.execute_query("insert_cube_component", data)
            return jsonify({"success": True, "operation": "insert"})
    
    except Exception as e:
        print(f"Ошибка при сохранении записи: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

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
@login_required
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
@login_required
def show_heatmap():
    heatmap_html = generate_heatmap()
    return render_template("heatmap.html", heatmap_html=heatmap_html)
# ===================================================================

# Список рабочих центров
@app.route("/work_center/")
@login_required
def work_center():
    workshops = db_oracle.execute_query("workshop_dp")
    tech_types = db_oracle.execute_query("main_spec_type")
    results = db_oracle.execute_query("work_center")
    return render_template('work_center.html', results=results, workshops=workshops, tech_types=tech_types)

# Состав рабочего центра
@app.route("/wc_composition/") 
@login_required
def wc_composition():
    wc_id = request.args.get('wc_id')
    dep_id = request.args.get('dep_id')
    results = db_oracle.execute_query("wc_pos",{'wc_id': wc_id, 'dep_id': dep_id})
#    print(f"Результаты: {results}") 
    return render_template('wc_composition.html', results=results)

# Добавление рабочего центра
@app.route('/add_work_center', methods=['POST'])
@login_required
def add_work_center():
    try:
        # Получение данных из формы
        dep_id = request.form.get('dep_id')
        name = request.form.get('name')
        tech_type_id = request.form.get('tech_type_id')
        class_num_ws = request.form.get('class_num_ws')
        class_num_all = request.form.get('class_num_all')
        
        # параметры для запроса
        params = {
        'name': request.form['name'],
        'dep_id': request.form['dep_id'],
        'class_num_ws': request.form['class_num_ws'],
        'class_num_all': request.form['class_num_all'],
        'tech_type_id': request.form['tech_type_id']
        }
        
        # Выполнение запроса
        db_oracle.execute_query("insert_wc", params)
    
    except Exception as e:
        flash(f"Ошибка добавления рабочего центра: {e}")
        
    return redirect(url_for('work_center'))  # к списку

# Редактирование рабочего центра
@app.route('/edit_work_center', methods=['POST'])
@login_required
def edit_work_center():
    try:
         # Получение данных из формы
        wc_id = request.form.get('wc_id')
        dep_id = request.form.get('dep_id')
        name = request.form.get('name')
        tech_type_id = request.form.get('tech_type_id')
        class_num_ws = request.form.get('class_num_ws')
        class_num_all = request.form.get('class_num_all')
        
        # Параметры для запроса
        params = {
        'wc_id': wc_id,
        'name': name,
        'dep_id': dep_id,
        'class_num_ws': class_num_ws,
        'class_num_all': class_num_all,
        'tech_type_id': tech_type_id
        }
        db_oracle.execute_query("update_wc", params)
    
    except Exception as e:
        flash(f"Ошибка редактирования рабочего центра: {e}")
    return redirect(url_for('work_center'))  # к списку

# Удаление рабочего центра (пометка на удаление)
@app.route('/delete_work_center', methods=['POST'])
@login_required
def delete_work_center():
    wc_id = request.form.get('wc_id')
    try:
        db_oracle.execute_query("delete_wc", {"wc_id": wc_id})
        # flash('Рабочий центр успешно удален', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении: {str(e)}', 'error')
    
    return redirect(url_for('work_center'))  # к списку

# Добавление рабочего/бригады в РЦ
@app.route('/add_worker_to_wc', methods=['POST'])
@login_required
def add_worker_to_wc():
    worker_id = request.form.get('worker_id')
    wc_id = request.form.get('wc_id')
    dep_id = request.form.get('dep_id')
    # print(worker_id)
    # print(wc_id)
    try:
        # Удаление рабочего из старого РЦ
        # print(worker_id)
        # print(wc_id)
        db_oracle.execute_query("del_workers_wc", {"worker_id": worker_id})
        
        # Добавление рабочего в РЦ
        db_oracle.execute_query("add_worker_wc", {"wc_id": wc_id, "worker_id": worker_id})
        flash('Рабочий успешно добавлен', 'success')
        
    except Exception as e:
        flash(f'Ошибка при добавлении рабочего: {str(e)}', 'danger')
    
    return redirect(url_for('wc_composition', wc_id=wc_id, dep_id=dep_id))

# Удаление рабочего/бригады из РЦ
@app.route('/remove_worker_from_wc', methods=['POST'])
@login_required
def remove_worker_from_wc():
    # Получение данных из формы
    worker_id = request.form.get('worker_id')
    wc_id = request.form.get('wc_id')
    dep_id = request.form.get('dep_id')
    
    try:    
        # Удаление рабочего из РЦ
        db_oracle.execute_query("del_workers_wc", {"worker_id": worker_id})
        
        flash('Рабочий успешно удален', 'success')
        
    except Exception as e:
        flash(f'Ошибка при удалении рабочего: {str(e)}', 'danger')
    
    return redirect(url_for('wc_composition', wc_id=wc_id, dep_id=dep_id))




@app.route('/test_jobs/<int:cc_id>')
@login_required
def test_jobs(cc_id):
    try:

        rows = db_oracle.execute_query("test_jobs", {"cc_id": cc_id})
        result = []
        cc_name = rows[0][1]

        for row in rows:
            
            result.append({
                "id": row[0],
                "start": row[2],
                "end": row[3],
            })


        return render_template('test_jobs.html', jobs_data=result,cc_name=cc_name)
       

    except Exception as e:
        print(f"Ошибка при получении графика: {e}")
        return jsonify({"error": "Ошибка сервера"}), 500


@app.route('/schedule/', methods=['GET','post'])
@login_required
def schedule():
    dep_id = request.args.get('dep_id')  # получаем выбранный цех (если есть)

    try:
        workshops = db_oracle.execute_query("select_dep")
        table_data = []

        if dep_id:
            table_data = db_oracle.execute_query("show_dep", {"dep_id": dep_id})

    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'danger')
        workshops = []
        table_data = []

    return render_template('schedule.html', workshops=workshops, table_data=table_data)
 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
