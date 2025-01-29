from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Mock database
users = {}  # Format: {email: {"password": "hashed_password", "username": "user_name", "phone": "phone_number", "bookings": []}}
photographers = [
    {"id": 1, "name": "John Doe", "bio": "Wedding Specialist", "rate_per_hour": 100, "phone": "123-456-7890", "image": "photographer1.jpg", "sample_images": ["sample1.jpg", "sample2.jpg"]},
    {"id": 2, "name": "Jane Smith", "bio": "Portrait Expert", "rate_per_hour": 120, "phone": "123-456-7891", "image": "photographer2.jpg", "sample_images": ["sample1.jpg", "sample2.jpg"]},
    {"id": 3, "name": "Emily Brown", "bio": "Travel Photographer", "rate_per_hour": 150, "phone": "123-456-7892", "image": "photographer3.jpg", "sample_images": ["sample1.jpg", "sample2.jpg"]},
]

@app.route('/')
def home():
   if "user" in session:
        email = session["user"]
        if email in users:
            return render_template('index.html', photographers=photographers, user=email, bookings=users[email]["bookings"])
        else:
            return redirect(url_for('signin'))
   return redirect(url_for('signin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        if email in users:
            return "Error: User already exists!", 400
        hashed_password = generate_password_hash(password)
        users[email] = {"username": username, "phone": phone, "password": hashed_password, "bookings": []}
        session["user"] = email
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email not in users or not check_password_hash(users[email]["password"], password):
            error = "Invalid credentials!"
        else:
            session["user"] = email
            return redirect(url_for('home'))
    return render_template('signin.html', error=error)

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for('signin'))

@app.route('/book', methods=['POST'])
def book():
    if "user" not in session:
        return redirect(url_for('signin'))
    
    email = session["user"]
    photographer_id = int(request.form['photographer-selection'])
    booking_time = request.form['booking-time']
    duration = int(request.form['duration'])
    
    # Convert the booking_time to a datetime object
    booking_time_obj = datetime.strptime(booking_time, "%Y-%m-%dT%H:%M")
    
    # Check if the booking time is in the future
    if booking_time_obj < datetime.now():
        return render_template('index.html', error="Booking time must be in the future!", photographers=photographers)
    
    photographer = next((p for p in photographers if p["id"] == photographer_id), None)
    if not photographer:
        return render_template('index.html', error="Photographer not found!", photographers=photographers)
    
    total_cost = photographer["rate_per_hour"] * duration
    booking = {
        "photographer": photographer["name"],
        "time": booking_time_obj.strftime('%Y-%m-%d %H:%M'),
        "duration": duration,
        "total_cost": total_cost,
    }
    users[email]["bookings"].append(booking)
    
    user_name = users[email]["username"]
    user_email = email
    
    return render_template(
        'confirmation.html',
        photographer_name=photographer["name"],
        booking_time=booking["time"],
        duration=duration,
        total_cost=total_cost,
        user_name=user_name,
        user_email=user_email,
    )

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

if __name__ == '__main__':
    app.run(debug=True)
