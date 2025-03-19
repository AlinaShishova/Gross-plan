from flask import Blueprint, render_template, request
from auth_wraps import login_required
import db_oracle

scheme_bp = Blueprint("scheme", __name__)

@scheme_bp.route('/scheme/',methods=['GET', 'POST'])
@login_required
def scheme():

    results = []
    if request.method == 'POST':
        filter_value = request.form.get('filter_value', "").strip()
        if not filter_value:
            results = []
        else:
            filter_param = f"{filter_value}%"
            results = db_oracle.execute_query("scheme",{"filter_value": filter_param})
    return render_template('scheme.html', results=results)

