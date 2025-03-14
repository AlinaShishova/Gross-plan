from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from config import Config
import db_oracle
from auth_wraps import login_required 
from routes.auth import auth_bp
from routes.keys import keys_bp
from routes.assembly import assembly_bp


app = Flask(__name__, static_url_path='/static', static_folder='static')
bootstrap = Bootstrap5(app)
app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(keys_bp)
app.register_blueprint(assembly_bp)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/cubs/')
@login_required
def cubs():
    return render_template('cubs.html')


@app.route('/order/')
@login_required
def order():
    results = db_oracle.execute_query("order")
    return render_template('order.html', results=results)


@app.route('/spec/')
@login_required
def spec():
    results = db_oracle.execute_query("spec")
    return render_template('spec.html', results=results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
