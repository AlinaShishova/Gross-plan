from flask import Blueprint, render_template, request
from auth_wraps import login_required
import db_oracle

keys_bp = Blueprint("keys", __name__)

@keys_bp.route('/keys/', methods=['GET', 'POST'])
@login_required
def keys():
    # Получаем значение dm_index_where из запроса, по умолчанию 19408746
    # Получаем значение dm_index_where из запроса, по умолчанию 19408746
    dm_index_where = request.args.get('dm_index_where', 19408746, type=int)
    old_dm_index_where = dm_index_where

    # Получаем результаты из базы данных с помощью функции из db.py
    results = db_oracle.execute_query(
        "key", {"dm_index_where": dm_index_where})

    # Рендерим HTML-страницу с результатами
    return render_template('keys.html', results=results, old_dm_index_where=old_dm_index_where)
