from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Role Model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

# Initialize database and create tables
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create all tables based on defined models

        # Pre-populate roles if they don't exist
        roles = ['Learner', 'HR', 'Manager', 'Instructor']
        for role_name in roles:
            existing_role = Role.query.filter_by(name=role_name).first()
            if not existing_role:
                db.session.add(Role(name=role_name))
        db.session.commit()  # Commit the changes to the database

        print("Database initialized with roles and tables.")
