from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Secret key for flash messages
app.config['SECRET_KEY'] = 'change_this_secret'

# SQLite database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- DATABASE MODEL -----------------
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Item {self.name}>'

# ----------------- ROUTES -----------------

@app.route('/')
def index():
    items = Item.query.order_by(Item.name).all()
    return render_template('index.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name'].strip()
        quantity = request.form['quantity']
        price = request.form['price']
        description = request.form['description'].strip()

        if not name:
            flash('Item name is required.', 'error')
            return redirect(url_for('add_item'))

        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            flash('Quantity must be an integer and price must be a number.', 'error')
            return redirect(url_for('add_item'))

        new_item = Item(name=name, quantity=quantity, price=price, description=description)
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_item.html')

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)

    if request.method == 'POST':
        name = request.form['name'].strip()
        quantity = request.form['quantity']
        price = request.form['price']
        description = request.form['description'].strip()

        if not name:
            flash('Item name is required.', 'error')
            return redirect(url_for('edit_item', item_id=item_id))

        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            flash('Quantity must be an integer and price must be a number.', 'error')
            return redirect(url_for('edit_item', item_id=item_id))

        item.name = name
        item.quantity = quantity
        item.price = price
        item.description = description

        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_item.html', item=item)

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted.', 'info')
    return redirect(url_for('index'))

# ----------------- CREATE DB & RUN -----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print(app.url_map)  # 👈 shows all URLs in terminal
    app.run(debug=True)
