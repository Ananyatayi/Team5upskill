from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Role Model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    
with app.app_context():
    db.create_all()  # Create the tables in the database
# User Signup Route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    # Ensure the password is strong
    password = data['password']
    confirm_password = data['confirm_password']
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match!"}), 400

    if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password) or not any(c in '!@#$%^&*()_+' for c in password):
        return jsonify({"error": "Password must be at least 8 characters long, contain a digit, a special character, and a capital letter."}), 400
        
    phone_number = data['phone_number']
    if len(phone_number) != 10 or not phone_number.isdigit():
        return jsonify({"error": "Phone number must be exactly 10 digits."}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Get the role name dynamically from the request (e.g., "Instructor" or "Learner")
    role_name = data.get('role', 'Learner')  # Default to 'Learner' if no role is provided
    role = Role.query.filter_by(name=role_name).first()

    if not role:
        return jsonify({"error": f"Role '{role_name}' not found!"}), 500

    # Create the new user
    new_user = User(
        full_name=data['full_name'],
        email=data['email'],
        password=hashed_password,
        phone_number=data['phone_number'],
        country=data['country'],
        role_id=role.id  # Dynamically set the role_id
    )

    # Add user to the database
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Signup successful, waiting for HR approval..."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# User Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"error": "Invalid email or password!"}), 400

# Get All Users Route
@app.route('/get_users', methods=['GET'])
def get_users():
    users = User.query.all()  # Query all users from the database
    user_list = []
    
    # Loop through all users and append them to a list
    for user in users:
        user_data = {
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'country': user.country,
            'role_id': user.role_id,
            'role': user.role.name  # Include role name for clarity
        }
        user_list.append(user_data)
    return jsonify(user_list)

if __name__ == "__main__":
    app.run(debug=True)
