from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Pavesh'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    rentals = db.relationship('Rental', backref='user', lazy=True)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(150), nullable=False)
    available = db.Column(db.Boolean, default=True)
    rentals = db.relationship('Rental', backref='car', lazy=True)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rental_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    return_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)

# Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    cars = Car.query.all()
    return render_template('admin_dashboard.html', cars=cars)

@app.route('/user')
@login_required
def user_dashboard():
    cars = Car.query.filter_by(available=True).all()
    return render_template('user_dashboard.html', cars=cars)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        data=request.form
        username=data.get("username")
        password=data.get("password")
        is_admin=data.get("is_admin") == 'on'

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists.")
        
        # hashed_password = password
        new_user = User(username=username, password=password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        data = request.form
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not password==user.password:
            return render_template('login.html', error="Invalid credentials.")
        
        login_user(user)
        return redirect(url_for('admin_dashboard') if user.is_admin else url_for('user_dashboard'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Admin endpoints
@app.route('/admin/cars', methods=['POST'])
@login_required
def add_new_car():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    data = request.form
    make = data.get("make")
    model = data.get("model")
    if not make or not model:
        return redirect(url_for('admin_dashboard', error="Make and Model both are required"))
    new_car = Car(make=make, model=model, available=True)
    db.session.add(new_car)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/cars/delete/<int:car_id>', methods=['POST'])
@login_required
def delete_car(car_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    car = Car.query.get(car_id)
    if car:
        db.session.delete(car)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

# User Endpoint
# Rent a Car
@app.route('/user/rent/<int:car_id>', methods=['POST'])
@login_required
def rent_car(car_id):
    car = Car.query.get(car_id)
    if not car or not car.available:
        return redirect(url_for('user_dashboard', error="Car is not available for rent."))

    rental = Rental(user_id=current_user.id, car_id=car.id)
    car.available = False
    db.session.add(rental)
    db.session.commit()
    return redirect(url_for('user_dashboard'))

# Return a Car
@app.route('/user/return/<int:rental_id>', methods=['POST'])
@login_required
def return_car(rental_id):
    rental = Rental.query.get(rental_id)
    if rental and rental.user_id == current_user.id:
        rental.return_date = datetime.now(timezone.utc)
        car = Car.query.get(rental.car_id)
        car.available = True
        db.session.commit()
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('user_dashboard', error="Invalid return request."))

# View Rental History
@app.route('/user/rentals')
@login_required
def rental_history():
    rentals = Rental.query.filter_by(user_id=current_user.id).all()
    return render_template('rental_history.html', rentals = rentals)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
