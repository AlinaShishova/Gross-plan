from flask import Flask, render_template
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
bootstrap = Bootstrap5(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cubs/')
def cubs():
    return render_template('cubs.html')

@app.route('/order/')
def order():
    return render_template('order.html')

@app.route('/keys/')
def keys():
    return render_template('keys.html')

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/logout/')
def logout():
    return render_template('logout.html')


if __name__ =='__main__':
    app.run(debug=True)