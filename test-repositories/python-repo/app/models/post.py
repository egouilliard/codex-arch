from .. import db
from sqlalchemy.sql import func

class Post(db.Model):
    """
    Post model for storing user posts
    
    Attributes:
        id (int): Primary key
        title (str): Post title
        content (str): Post content
        date_created (datetime): Date post was created
        date_updated (datetime): Date post was last updated
        user_id (int): Foreign key to User model
        comments (relationship): Relationship to Comment model
        tags (relationship): Many-to-many relationship with Tag model
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    tags = db.relationship('Tag', secondary='post_tags', backref=db.backref('posts', lazy='dynamic'))
    
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_created}')"


class Comment(db.Model):
    """
    Comment model for storing post comments
    
    Attributes:
        id (int): Primary key
        content (str): Comment content
        date_created (datetime): Date comment was created
        post_id (int): Foreign key to Post model
        user_id (int): Foreign key to User model
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    
    def __repr__(self):
        return f"Comment('{self.content[:20]}...', '{self.date_created}')"


# Tag model for categorizing posts
class Tag(db.Model):
    """
    Tag model for categorizing posts
    
    Attributes:
        id (int): Primary key
        name (str): Tag name
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"Tag('{self.name}')"


# Association table for many-to-many relationship between Post and Tag
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
) 