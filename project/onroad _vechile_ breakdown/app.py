import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'onroad_breakdown_secret_key'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'onroad.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(50))
    vehicle_number = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    specialty = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanic.id'))
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    user_lat = db.Column(db.Float)
    user_lng = db.Column(db.Float)
    mechanic_lat = db.Column(db.Float)
    mechanic_lng = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        data = request.form
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            vehicle_type=data.get('vehicle_type'),
            vehicle_number=data.get('vehicle_number')
        )
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['user_name'] = user.name
        return redirect(url_for('booking'))
    return render_template('user_register.html')

@app.route('/mechanic/register', methods=['GET', 'POST'])
def mechanic_register():
    if request.method == 'POST':
        data = request.form
        mechanic = Mechanic(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            specialty=data.get('specialty'),
            latitude=float(data.get('latitude', 0)),
            longitude=float(data.get('longitude', 0))
        )
        db.session.add(mechanic)
        db.session.commit()
        session['mechanic_id'] = mechanic.id
        session['mechanic_name'] = mechanic.name
        return redirect(url_for('mechanic_dashboard'))
    return render_template('mechanic_register.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user_id' not in session:
        return redirect(url_for('user_register'))
    
    mechanics = Mechanic.query.filter_by(available=True).all()
    
    if request.method == 'POST':
        data = request.form
        user = User.query.get(session['user_id'])
        user.latitude = float(data.get('latitude', 0))
        user.longitude = float(data.get('longitude', 0))
        
        booking = Booking(
            user_id=session['user_id'],
            issue_description=data['issue_description'],
            user_lat=user.latitude,
            user_lng=user.longitude
        )
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for('track_booking', booking_id=booking.id))
    
    return render_template('booking.html', mechanics=mechanics)

@app.route('/api/nearby-mechanics')
def nearby_mechanics():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 10, type=float)
    
    if not lat or not lng:
        return jsonify([])
    
    mechanics = Mechanic.query.filter_by(available=True).all()
    nearby = []
    
    for m in mechanics:
        if m.latitude and m.longitude:
            distance = ((m.latitude - lat)**2 + (m.longitude - lng)**2)**0.5 * 111
            if distance <= radius:
                nearby.append({
                    'id': m.id,
                    'name': m.name,
                    'phone': m.phone,
                    'specialty': m.specialty,
                    'latitude': m.latitude,
                    'longitude': m.longitude,
                    'distance': round(distance, 2)
                })
    
    return jsonify(nearby)

@app.route('/track-booking/<int:booking_id>')
def track_booking(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('user_register'))
    
    booking = Booking.query.get_or_404(booking_id)
    mechanic = Mechanic.query.get(booking.mechanic_id) if booking.mechanic_id else None
    
    return render_template('track_booking.html', booking=booking, mechanic=mechanic)

@app.route('/api/booking/<int:booking_id>/status')
def booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return jsonify({
        'status': booking.status,
        'mechanic_id': booking.mechanic_id,
        'mechanic_lat': booking.mechanic_lat,
        'mechanic_lng': booking.mechanic_lng,
        'user_lat': booking.user_lat,
        'user_lng': booking.user_lng
    })

@app.route('/mechanic/dashboard')
def mechanic_dashboard():
    if 'mechanic_id' not in session:
        return redirect(url_for('mechanic_register'))
    
    mechanic = Mechanic.query.get(session['mechanic_id'])
    pending_bookings = Booking.query.filter_by(status='pending').all()
    my_bookings = Booking.query.filter(
        Booking.mechanic_id == session['mechanic_id'],
        Booking.status.in_(['accepted', 'in_progress'])
    ).all()
    
    return render_template('mechanic_dashboard.html', 
                         mechanic=mechanic, 
                         pending_bookings=pending_bookings,
                         my_bookings=my_bookings)

@app.route('/mechanic/accept/<int:booking_id>')
def accept_booking(booking_id):
    if 'mechanic_id' not in session:
        return redirect(url_for('mechanic_register'))
    
    booking = Booking.query.get_or_404(booking_id)
    mechanic = Mechanic.query.get(session['mechanic_id'])
    
    booking.mechanic_id = session['mechanic_id']
    booking.status = 'accepted'
    booking.mechanic_lat = mechanic.latitude
    booking.mechanic_lng = mechanic.longitude
    db.session.commit()
    
    return redirect(url_for('mechanic_dashboard'))

@app.route('/mechanic/reject/<int:booking_id>')
def reject_booking(booking_id):
    if 'mechanic_id' not in session:
        return redirect(url_for('mechanic_register'))
    
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'rejected'
    db.session.commit()
    
    return redirect(url_for('mechanic_dashboard'))

@app.route('/mechanic/update-location', methods=['POST'])
def update_location():
    if 'mechanic_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    mechanic = Mechanic.query.get(session['mechanic_id'])
    mechanic.latitude = data.get('latitude')
    mechanic.longitude = data.get('longitude')
    db.session.commit()
    
    bookings = Booking.query.filter_by(mechanic_id=session['mechanic_id'], status='accepted').all()
    for booking in bookings:
        booking.mechanic_lat = mechanic.latitude
        booking.mechanic_lng = mechanic.longitude
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
