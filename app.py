from itsdangerous import TimedSerializer as Serializer, BadSignature, SignatureExpired
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import random
import string


app = Flask(__name__)

# Configure Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite for simplicity
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Specify the login route

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), default=None)

# Create the database
with app.app_context():
    db.create_all()

# Function to generate a random token
def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=25))

# Email configuration
def send_email(subject, recipients, body):
    msg = Message(subject, sender='your_email@gmail.com', recipients=recipients)
    msg.body = body
    mail.send(msg)

# Login user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Root endpoint
@app.route('/')
def home():
    return render_template('index.html')  # Adjust this based on your file structure

# Register endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    # Send confirmation email
    confirmation_token = generate_token()
    new_user.confirmed = False
    new_user.reset_token = confirmation_token
    db.session.commit()

    confirmation_link = f'http://127.0.0.1:5000/confirm/{confirmation_token}'
    send_email('Confirm Your Email', [email], f'Click the link to confirm your email: {confirmation_link}')

    return jsonify({'message': 'User registered successfully. Confirmation email sent.', 'confirmation_link': confirmation_link})


# Confirm email endpoint
@app.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    user = User.query.filter_by(reset_token=token).first()

    if user:
        user.confirmed = True
        user.reset_token = None
        db.session.commit()
        return jsonify({'message': 'Email confirmed successfully!'})
    else:
        return jsonify({'error': 'Invalid token.'}), 400

# Login endpoint
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.password == password and user.confirmed:
            login_user(user)
            return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
        elif user and not user.confirmed:
            return jsonify({'error': 'Email not confirmed. Please check your email for the confirmation link.'}), 401
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    else:
        # Render the login form
        return render_template('login.html')

# Create an instance of the Serializer for generating secure tokens
serializer = Serializer(app.config['SECRET_KEY'])

# Password reset request endpoint
@app.route('/reset_password_request', methods=['POST'])
def reset_password_request():
    data = request.get_json()
    email = data['email']

    # Check if the email is associated with a registered user
    user = User.query.filter_by(email=email).first()

    if user:
        # Generate a secure token for resetting the password with expiration
        token = serializer.dumps({'user_id': user.id}, expires_in=3600).decode('utf-8')

        # Send the password reset email with the token link
        reset_link = f'http://127.0.0.1:5000/reset_password/{token}'
        send_email('Password Reset Request', [email], f'Click the link to reset your password: {reset_link}')

        return jsonify({'message': 'Password reset email sent. Check your email for instructions.'})
    else:
        return jsonify({'error': 'Email not found in our records.'}), 404



# Password reset endpoint
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        # Handle password reset logic here
        data = request.get_json()
        new_password = data['new_password']

        try:
            # Decode the token and get the user_id
            user_id = serializer.loads(token)['user_id']

            # Update the user's password
            user = User.query.get(user_id)
            user.password = new_password
            db.session.commit()

            return jsonify({'message': 'Password reset successful. You can now log in with your new password.'})
        except Exception as e:
            print(e)
            return jsonify({'error': 'Invalid or expired token. Please request a new password reset.'}), 400
    else:
        # Render the password reset form
        return render_template('reset_password.html')


# Dashboard endpoint
@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}! This is your dashboard.'

# Logout endpoint
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
