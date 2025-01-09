from flask import Flask, render_template, request, redirect, url_for, jsonify, g
import sqlite3
import os
from routes.main import bp as main_bp

app = Flask(__name__)
app.config['DATABASE'] = 'data/spinning-wheel.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open('data/spinning-wheel.sql') as f:
            db.executescript(f.read())
        db.commit()

# Make get_db available to blueprints
app.get_db = get_db

# Register blueprints
app.register_blueprint(main_bp)

if __name__ == '__main__':
    if not os.path.exists('data/spinning-wheel.db'):
        init_db()
    app.run(debug=True)