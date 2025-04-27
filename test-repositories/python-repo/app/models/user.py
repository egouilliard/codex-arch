from .. import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    """
    User model for authentication and user data
    
    Attributes:
        id (int): Primary key
        email (str): User email, must be unique
        username (str): User username, must be unique
        password_hash (str): Hashed password
        date_created (datetime): Date user was created
        posts (relationship): Relationship to Post model
        role (str): User role (admin, user)
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    posts = db.relationship('Post', backref='author', lazy=True, cascade="all, delete-orphan")
    role = db.Column(db.String(20), default='user')
    
    def set_password(self, password):
        """
        Sets the password hash from a plaintext password
        
        Args:
            password (str): Plaintext password
        """
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """
        Checks if the provided password matches the stored hash
        
        Args:
            password (str): Plaintext password to check
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """
        Checks if user has admin role
        
        Returns:
            bool: True if user is admin, False otherwise
        """
        return self.role == 'admin'
        
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Profile(db.Model):
    """
    User profile model with extended information about users
    
    Attributes:
        id (int): Primary key
        first_name (str): User's first name
        last_name (str): User's last name
        bio (str): User's biography
        user_id (int): Foreign key to User model
        user (relationship): Relationship to User model
    """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
    
    def __repr__(self):
        return f"Profile('{self.first_name} {self.last_name}')" 