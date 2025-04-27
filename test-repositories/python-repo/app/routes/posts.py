from flask import Blueprint, request, jsonify
from ..models.post import Post, Comment, Tag
from ..models.user import User
from .. import db
from ..utils.helpers import token_required
from sqlalchemy import desc

posts = Blueprint('posts', __name__)

@posts.route('/', methods=['GET'])
def get_posts():
    """
    Get all posts with pagination
    
    Query parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10)
        tag (str): Filter by tag name (optional)
        
    Returns:
        JSON: List of posts with pagination metadata
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    tag = request.args.get('tag')
    
    query = Post.query
    
    if tag:
        tag_obj = Tag.query.filter_by(name=tag).first()
        if tag_obj:
            query = tag_obj.posts
    
    posts_pagination = query.order_by(desc(Post.date_created)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    posts_list = []
    for post in posts_pagination.items:
        author = User.query.get(post.user_id)
        posts_list.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'date_created': post.date_created,
            'date_updated': post.date_updated,
            'author': {
                'id': author.id,
                'username': author.username
            },
            'tags': [tag.name for tag in post.tags]
        })
    
    return jsonify({
        'posts': posts_list,
        'total': posts_pagination.total,
        'pages': posts_pagination.pages,
        'current_page': page
    }), 200


@posts.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    Get a specific post by ID
    
    Path parameters:
        post_id (int): Post ID
        
    Returns:
        JSON: Post details
    """
    post = Post.query.get_or_404(post_id)
    author = User.query.get(post.user_id)
    
    # Get comments
    comments = []
    for comment in post.comments:
        comment_author = User.query.get(comment.user_id)
        comments.append({
            'id': comment.id,
            'content': comment.content,
            'date_created': comment.date_created,
            'author': {
                'id': comment_author.id,
                'username': comment_author.username
            }
        })
    
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'date_created': post.date_created,
        'date_updated': post.date_updated,
        'author': {
            'id': author.id,
            'username': author.username
        },
        'comments': comments,
        'tags': [tag.name for tag in post.tags]
    }), 200


@posts.route('/', methods=['POST'])
@token_required
def create_post(current_user):
    """
    Create a new post
    
    Request body:
        title (str): Post title
        content (str): Post content
        tags (list): List of tag names
        
    Returns:
        JSON: Success message and post ID
    """
    data = request.get_json()
    
    if not all(k in data for k in ('title', 'content')):
        return jsonify({'error': 'Title and content are required'}), 400
    
    new_post = Post(
        title=data['title'],
        content=data['content'],
        user_id=current_user.id
    )
    
    # Add tags if provided
    if 'tags' in data and isinstance(data['tags'], list):
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            new_post.tags.append(tag)
    
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({
        'message': 'Post created successfully',
        'post_id': new_post.id
    }), 201


@posts.route('/<int:post_id>', methods=['PUT'])
@token_required
def update_post(current_user, post_id):
    """
    Update an existing post
    
    Path parameters:
        post_id (int): Post ID
        
    Request body:
        title (str): Post title (optional)
        content (str): Post content (optional)
        tags (list): List of tag names (optional)
        
    Returns:
        JSON: Success message
    """
    post = Post.query.get_or_404(post_id)
    
    # Check if the user is the author
    if post.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        post.title = data['title']
    
    if 'content' in data:
        post.content = data['content']
    
    # Update tags if provided
    if 'tags' in data and isinstance(data['tags'], list):
        # Clear existing tags
        post.tags = []
        
        # Add new tags
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            post.tags.append(tag)
    
    db.session.commit()
    
    return jsonify({'message': 'Post updated successfully'}), 200


@posts.route('/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    """
    Delete a post
    
    Path parameters:
        post_id (int): Post ID
        
    Returns:
        JSON: Success message
    """
    post = Post.query.get_or_404(post_id)
    
    # Check if the user is the author
    if post.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200


@posts.route('/<int:post_id>/comments', methods=['POST'])
@token_required
def add_comment(current_user, post_id):
    """
    Add a comment to a post
    
    Path parameters:
        post_id (int): Post ID
        
    Request body:
        content (str): Comment content
        
    Returns:
        JSON: Success message and comment ID
    """
    Post.query.get_or_404(post_id)  # Check if post exists
    
    data = request.get_json()
    
    if 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    new_comment = Comment(
        content=data['content'],
        post_id=post_id,
        user_id=current_user.id
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({
        'message': 'Comment added successfully',
        'comment_id': new_comment.id
    }), 201 