import sqlite3
from flask import Blueprint, abort, render_template, request, redirect, url_for, jsonify, current_app
from models.wheel import Wheel
from models.category import Category
import random

bp = Blueprint('main', __name__)

def get_db():
    return current_app.get_db()

@bp.route('/')
def index():
    db = get_db()
    wheels = Wheel.get_all(db)
    return render_template('index.html', wheels=wheels)

@bp.route('/wheel/new', methods=['GET', 'POST'])
def new_wheel():
    if request.method == 'POST':
        wheel = Wheel(name=request.form['name'], description=request.form['description'])
        db = get_db()
        wheel.save(db)
        return redirect(url_for('main.show_wheel', wheel_id=wheel.id))
    return render_template('wheel_form.html')

@bp.route('/wheel/<int:wheel_id>')
def show_wheel(wheel_id):
    db = get_db()
    wheel = Wheel.get_by_id(db, wheel_id)
    if wheel is None:
        return redirect(url_for('main.index'))
    categories = Category.get_for_wheel(db, wheel_id)
    return render_template('wheel.html', wheel=wheel, categories=categories)

@bp.route('/wheel/<int:wheel_id>/category', methods=['GET', 'POST'])
def add_category(wheel_id):
    db = get_db()
    wheel = Wheel.get_by_id(db, wheel_id)
    if wheel is None:
        return redirect(url_for('main.index'))
    
    categories = Category.get_for_wheel(db, wheel_id)
    
    if request.method == 'POST':
        category = Category(name=request.form['name'], color=request.form['color'])
        category.save(db)
        
        # Add to wheel categories with next position
        db.execute(
            'INSERT INTO WheelCategories (wheel_id, category_id, position) VALUES (?, ?, ?)',
            (wheel_id, category.id, len(categories))
        )
        db.commit()
        
        return redirect(url_for('main.add_category', wheel_id=wheel_id))
    
    return render_template('category_form.html', wheel=wheel, categories=categories)

@bp.route('/wheel/<int:wheel_id>/spin', methods=['POST'])
def spin_wheel(wheel_id):
    db = get_db()
    wheel = Wheel.get_by_id(db, wheel_id)
    if wheel is None:
        return jsonify({'error': 'Wheel not found'}), 404
    
    categories = Category.get_for_wheel(db, wheel_id)
    if not categories:
        return jsonify({'error': 'No categories found'}), 404
    
    selected = random.choice(categories)
    
    # selected is already a dictionary, so we can return it directly
    return jsonify({
        'category': selected
    })

# In routes/main.py

@bp.route('/wheel/<int:wheel_id>/delete', methods=['POST'])
def delete_wheel(wheel_id):
    db = get_db()
    wheel = Wheel.get_by_id(db, wheel_id)  # Pass both db and wheel_id
    
    if wheel is None:
        abort(404)
    
    try:
        # Delete wheel categories first (due to foreign key constraints)
        db.execute('DELETE FROM WheelCategories WHERE wheel_id = ?', (wheel_id,))
        # Delete the wheel
        db.execute('DELETE FROM Wheels WHERE id = ?', (wheel_id,))
        db.commit()
        return redirect(url_for('main.index'))
    except sqlite3.Error as e:
        db.rollback()
        return f"An error occurred: {e}", 500


