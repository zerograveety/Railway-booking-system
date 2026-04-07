from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
# Use DATABASE_URL from Heroku/Render, otherwise explicitly fall back to local Postgres
db_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/railway')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Form Classes
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    bookings = db.relationship('Booking', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    
class Train(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    train_number = db.Column(db.String(20), unique=True, nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    
    source = db.relationship('Station', foreign_keys=[source_id])
    destination = db.relationship('Station', foreign_keys=[destination_id])
    seats = db.relationship('Seat', backref='train', lazy=True)

class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_type = db.Column(db.String(20), nullable=False)  # e.g., "Window", "Aisle", "Middle"
    coach = db.Column(db.String(5), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    price = db.Column(db.Float, nullable=False)
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('train.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    journey_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Confirmed')
    passenger_name = db.Column(db.String(100), nullable=False)
    cancellation_date = db.Column(db.DateTime, nullable=True)
    
    # Define relationships
    train = db.relationship('Train', backref='bookings')
    seat = db.relationship('Seat', backref='bookings')

# Create database tables
with app.app_context():
    # Create tables; only reset the DB when explicitly requested.
    # Usage: `RESET_DB=1 python app.py`
    if os.getenv('RESET_DB') == '1':
        db.drop_all()
    db.create_all()
    
    # Add sample data if database is empty
    if not Station.query.first():
        # Add stations
        stations = [
            # Northern Region
            Station(name='New Delhi Railway Station', code='NDLS', city='Delhi'),
            Station(name='Mumbai Central', code='MMCT', city='Mumbai'),
            Station(name='Chennai Central', code='MAS', city='Chennai'),
            Station(name='Howrah Junction', code='HWH', city='Kolkata'),
            Station(name='Bengaluru City Junction', code='SBC', city='Bengaluru'),
            Station(name='Jaipur Junction', code='JP', city='Jaipur'),
            Station(name='Lucknow Junction', code='LKO', city='Lucknow'),
            Station(name='Raipur Junction', code='R', city='Raipur'),
            Station(name='Nagpur Junction', code='NGP', city='Nagpur'),
            
            # North-Eastern Region
            Station(name='Guwahati Junction', code='GHY', city='Guwahati'),
            Station(name='Imphal Railway Station', code='IMPL', city='Imphal'),
            Station(name='Shillong Railway Station', code='SHL', city='Shillong'),
            Station(name='Aizawl Railway Station', code='AZL', city='Aizawl'),
            Station(name='Agartala Railway Station', code='AGTL', city='Agartala'),
            Station(name='Kohima Railway Station', code='KOH', city='Kohima'),
            Station(name='Itanagar Railway Station', code='ITNR', city='Itanagar'),
            
            # Other Major Cities
            Station(name='Ahmedabad Junction', code='ADI', city='Ahmedabad'),
            Station(name='Surat Junction', code='ST', city='Surat'),
            Station(name='Bhopal Junction', code='BPL', city='Bhopal'), 
            Station(name='Hyderabad Junction', code='HYB', city='Hyderabad'),
            Station(name='Pune Junction', code='PUNE', city='Pune'),
            Station(name='Kota Junction', code='KOTA', city='Kota'),
            Station(name='Indore Junction', code='INDB', city='Indore'),
            Station(name='Bhubaneswar Junction', code='BBS', city='Bhubaneswar'),
            Station(name='Visakhapatnam Junction', code='VSKP', city='Visakhapatnam'),
            Station(name='Kanpur Central', code='CNB', city='Kanpur'),
            Station(name='Varanasi Junction', code='BSB', city='Varanasi'),
            Station(name='Patna Junction', code='PNBE', city='Patna'),
            Station(name='Amritsar Junction', code='ASR', city='Amritsar'),
            Station(name='Jammu Tawi', code='JAT', city='Jammu'),
            Station(name='Thiruvananthapuram Central', code='TVC', city='Thiruvananthapuram'),
            Station(name='Kochi Junction', code='ERS', city='Kochi')
        ]
        db.session.add_all(stations)
        db.session.commit()
        
        # Add dynamic trains for next 30 days
        train_bases = [
            ('Rajdhani Express', 1, 2, 72, '16:00', '08:00'),
            ('Shatabdi Express', 1, 5, 60, '06:00', '22:00'),
            ('Duronto Express', 4, 3, 72, '20:00', '18:00'),
            ('Humsafar Express', 2, 20, 60, '23:00', '15:00'),
            ('Garib Rath Express', 1, 28, 72, '07:00', '04:00'),
            ('Vande Bharat Express', 17, 20, 60, '06:00', '14:00'),
            ('Northeast Express', 10, 1, 72, '16:30', '06:00'),
            ('Kerala Express', 31, 32, 60, '08:00', '12:00'),
            ('Deccan Queen', 20, 2, 60, '07:15', '10:25'),
            ('Konkan Kanya Express', 2, 31, 72, '15:00', '18:30'),
            ('Golden Temple Mail', 1, 29, 60, '16:30', '03:30'),
            ('Chennai Express', 2, 3, 72, '16:00', '08:30'),
            ('Howrah Rajdhani', 1, 4, 72, '16:50', '10:00'),
            ('Tejas Express', 2, 17, 60, '06:40', '13:10')
        ]
        
        from datetime import timedelta
        import random
        
        trains_to_add = []
        train_counter = 10000
        for name, src, dst, total_seats, dep_time, arr_time in train_bases:
            # Generate this train running every day for the next 45 days
            for day_offset in range(-5, 40):
                today = datetime.now().date()
                journey_date = today + timedelta(days=day_offset)
                
                dep_dt = datetime.strptime(dep_time, '%H:%M').time()
                arr_dt = datetime.strptime(arr_time, '%H:%M').time()
                
                dep_full = datetime.combine(journey_date, dep_dt)
                
                # If arrival time is less than departure time, it arrives next day
                if arr_dt < dep_dt:
                    arr_full = datetime.combine(journey_date + timedelta(days=1), arr_dt)
                else:
                    arr_full = datetime.combine(journey_date, arr_dt)
                
                t = Train(
                    name=name,
                    train_number=str(train_counter),
                    source_id=src,
                    destination_id=dst,
                    departure_time=dep_full,
                    arrival_time=arr_full,
                    total_seats=total_seats
                )
                trains_to_add.append(t)
                train_counter += 1
                
        db.session.add_all(trains_to_add)
        db.session.commit()
        
        # Create seats once (avoid reseeding on every startup).
        if not Seat.query.first():
            coaches = ['A1', 'A2', 'A3']
            seats_to_add = []
            for train in Train.query.all():
                for coach in coaches:
                    for i in range(1, 71):  # 70 seats per coach
                        seat_type = 'Window' if i % 3 == 1 else ('Aisle' if i % 3 == 2 else 'Middle')
                        price = 1200 if seat_type == 'Window' else (1000 if seat_type == 'Aisle' else 800)
                        seats_to_add.append(
                            Seat(
                                train=train,
                                seat_number=str(i),
                                coach=coach,
                                seat_type=seat_type,
                                price=price,
                            )
                        )
            db.session.add_all(seats_to_add)
            db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    bookings = Booking.query.filter_by(user_id=user.id).all()
    
    # Add today's date to the context
    today = datetime.now().date()
    
    return render_template('dashboard.html', user=user, bookings=bookings, today=today)


@app.route('/search', methods=['GET'])
def search():
    if request.method == 'GET':
        from_code = request.args.get('from_code') or request.args.get('from_id')
        to_code = request.args.get('to_code') or request.args.get('to_id')
        date_str = request.args.get('date')
        
        trains = []
        if from_code and to_code and date_str:
            try:
                # Find stations
                src_stn = Station.query.filter_by(code=from_code).first()
                dst_stn = Station.query.filter_by(code=to_code).first()
                
                if src_stn and dst_stn:
                    search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    # Find all trains that match the source, destination and departure date
                    all_trains = Train.query.filter_by(
                        source_id=src_stn.id,
                        destination_id=dst_stn.id
                    ).all()
                    
                    for t in all_trains:
                        if t.departure_time.date() == search_date:
                            trains.append(t)
            except Exception as e:
                print("DB Search Error:", e)
        
        return render_template('search.html', trains=trains, date=date_str, searched=True)
    
    return render_template('search.html', searched=False)

@app.route('/api/stations/search')
def search_stations():
    query = request.args.get('q', '').upper()
    if not query:
        return jsonify([])
    
    try:
        stations = Station.query.filter(
            db.or_(
                Station.name.ilike(f'%{query}%'),
                Station.code.ilike(f'%{query}%'),
                Station.city.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        results = [{
            'id': s.code,
            'name': s.name,
            'city': s.city,
            'code': s.code
        } for s in stations]
        
        return jsonify(results)
    except Exception as e:
        print("DB Station Search Error:", e)
        
    return jsonify([])

@app.route('/train/<int:train_id>/seats/<journey_date>')
def select_seat(train_id, journey_date):
    if not current_user.is_authenticated:
        flash('Please login first.')
        return redirect(url_for('login'))
    
    train = Train.query.get_or_404(train_id)
    seats = Seat.query.filter_by(train_id=train_id).all()
    
    # Check which seats are already booked for this date
    booked_seats = Booking.query.filter_by(
        train_id=train_id, 
        journey_date=datetime.strptime(journey_date, '%Y-%m-%d').date()
    ).all()
    
    booked_seat_ids = [booking.seat_id for booking in booked_seats]
    
    return render_template('select_seat.html', train=train, seats=seats, journey_date=journey_date, booked_seat_ids=booked_seat_ids)

@app.route('/book', methods=['POST'])
def book_ticket():
    if not current_user.is_authenticated:
        flash('Please login first.')
        return redirect(url_for('login'))
    
    train_id = request.form.get('train_id')
    journey_date = request.form.get('journey_date')
    seat_ids = request.form.getlist('seat_ids[]')
    passenger_names = request.form.getlist('passenger_names[]')
    
    if not all([train_id, journey_date, seat_ids, passenger_names]):
        flash('Missing required information.')
        return redirect(url_for('select_seat', train_id=train_id, journey_date=journey_date))
    
    if len(seat_ids) != len(passenger_names):
        flash('Number of seats and passenger names do not match.')
        return redirect(url_for('select_seat', train_id=train_id, journey_date=journey_date))
    
    # Check if any of the seats are already booked
    for seat_id in seat_ids:
        existing_booking = Booking.query.filter_by(
            train_id=train_id,
            seat_id=seat_id,
            journey_date=datetime.strptime(journey_date, '%Y-%m-%d').date()
        ).first()
        
        if existing_booking:
            flash(f'Seat {seat_id} is already booked for the selected date.')
            return redirect(url_for('select_seat', train_id=train_id, journey_date=journey_date))
    
    # Create bookings for each seat
    bookings = []
    for seat_id, passenger_name in zip(seat_ids, passenger_names):
        booking = Booking(
            user_id=current_user.id,
            train_id=train_id,
            seat_id=seat_id,
            journey_date=datetime.strptime(journey_date, '%Y-%m-%d').date(),
            passenger_name=passenger_name
        )
        bookings.append(booking)
    
    try:
        db.session.add_all(bookings)
        db.session.commit()
        flash('Tickets booked successfully!')
        return redirect(url_for('booking_confirmation', booking_ids=','.join(str(b.id) for b in bookings)))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while booking the tickets. Please try again.')
        return redirect(url_for('select_seat', train_id=train_id, journey_date=journey_date))

@app.route('/booking/<booking_ids>')
def booking_confirmation(booking_ids):
    if not current_user.is_authenticated:
        flash('Please login first.')
        return redirect(url_for('login'))
    
    try:
        # Convert booking IDs from string to list of integers
        booking_ids = [int(id) for id in booking_ids.split(',')]
        
        # Get all bookings for these IDs
        bookings = Booking.query.filter(Booking.id.in_(booking_ids)).all()
        
        if not bookings:
            flash('No bookings found.')
            return redirect(url_for('dashboard'))
        
        # Ensure all bookings belong to the logged-in user
        if not all(booking.user_id == current_user.id for booking in bookings):
            flash('Unauthorized access.')
            return redirect(url_for('dashboard'))
        
        # If it's a single booking and it's cancelled, show the cancelled ticket template
        if len(bookings) == 1 and bookings[0].status == 'Cancelled':
            booking = bookings[0]
            train = Train.query.get(booking.train_id)
            seat = Seat.query.get(booking.seat_id)
            source_station = Station.query.get(train.source_id)
            dest_station = Station.query.get(train.destination_id)
            
            if not all([train, seat, source_station, dest_station]):
                flash('Error retrieving booking details.')
                return redirect(url_for('dashboard'))
            
            booking_data = {
                'id': booking.id,
                'passenger_name': booking.passenger_name,
                'train_name': train.name,
                'train_number': train.train_number,
                'source': source_station.name,
                'destination': dest_station.name,
                'departure_time': train.departure_time.strftime('%H:%M'),
                'arrival_time': train.arrival_time.strftime('%H:%M'),
                'journey_date': booking.journey_date.strftime('%Y-%m-%d'),
                'seat_number': seat.seat_number,
                'coach': seat.coach,
                'seat_type': seat.seat_type,
                'price': seat.price,
                'booking_date': booking.booking_date,
                'cancellation_date': booking.cancellation_date
            }
            
            return render_template('cancelled_ticket.html', booking=booking_data)
        
        # For multiple bookings or confirmed bookings, show the regular confirmation template
        booking_data = []
        for booking in bookings:
            train = Train.query.get(booking.train_id)
            seat = Seat.query.get(booking.seat_id)
            source_station = Station.query.get(train.source_id)
            dest_station = Station.query.get(train.destination_id)
            
            if not all([train, seat, source_station, dest_station]):
                flash('Error retrieving booking details.')
                return redirect(url_for('dashboard'))
            
            booking_data.append({
                'id': booking.id,
                'passenger_name': booking.passenger_name,
                'train_name': train.name,
                'train_number': train.train_number,
                'source': source_station.name,
                'destination': dest_station.name,
                'departure_time': train.departure_time.strftime('%H:%M'),
                'arrival_time': train.arrival_time.strftime('%H:%M'),
                'journey_date': booking.journey_date.strftime('%Y-%m-%d'),
                'seat_number': seat.seat_number,
                'coach': seat.coach,
                'seat_type': seat.seat_type,
                'price': seat.price
            })
        
        return render_template('booking_confirmation.html', bookings=booking_data)
    except Exception as e:
        print(f"Error in booking_confirmation: {str(e)}")
        flash('Error retrieving booking details.')
        return redirect(url_for('dashboard'))

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if not current_user.is_authenticated:
        flash('Please login first.')
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the booking belongs to the current user
    if booking.user_id != current_user.id:
        flash('Unauthorized access.')
        return redirect(url_for('dashboard'))
    
    # Check if the booking is already cancelled
    if booking.status == 'Cancelled':
        flash('This booking is already cancelled.')
        return redirect(url_for('dashboard'))
    
    # Check if the journey date is in the future
    if booking.journey_date <= datetime.utcnow().date():
        flash('Cannot cancel past or ongoing journeys.')
        return redirect(url_for('dashboard'))
    
    try:
        # Update booking status and cancellation date
        booking.status = 'Cancelled'
        booking.cancellation_date = datetime.utcnow()
        
        # Make the seat available again
        seat = Seat.query.get(booking.seat_id)
        seat.is_available = True
        
        db.session.commit()
        flash('Booking cancelled successfully!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while cancelling the booking. Please try again.')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)

print("Flask application initialized with database models and routes")