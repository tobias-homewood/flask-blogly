"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User."""

    __tablename__ = 'users'

    def __repr__(self):
        u = self
        return f"<User id={u.id} first_name={u.first_name} last_name={u.last_name} image_url={u.image_url}>"
    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False, unique=False)
    last_name = db.Column(db.String(50), nullable=False, unique=False)
    image_url = db.Column(db.String(200), nullable=False, unique=False)
    posts = db.relationship('Post', backref='user', cascade='all')


class Post(db.Model):
    """Post."""

    __tablename__ = 'posts'

    def __repr__(self):
        p = self
        return f"<Post id={p.id} title={p.title} content={p.content} created_at={p.created_at} user_id={p.user_id}>"
    
    def __str__(self) -> str:
        return f"{self.title}"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False, unique=False)
    content = db.Column(db.String(200), nullable=False, unique=False)
    created_at = db.Column(db.DateTime, nullable=False, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=False)
    tags = db.relationship('Tag', secondary='posts_tags', backref='posts')


class Tag(db.Model):
    """Tag."""

    __tablename__ = 'tags'

    def __repr__(self):
        t = self
        return f"<Tag id={t.id} name={t.name}>"
    
    def __str__(self) -> str:
        return f"{self.name}"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class PostTag(db.Model):
    """PostTag."""

    __tablename__ = 'posts_tags'

    def __repr__(self):
        pt = self
        return f"<PostTag post_id={pt.post_id} tag_id={pt.tag_id}>"
    
    def __str__(self) -> str:
        return f"{self.post_id} {self.tag_id}"

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True, nullable=False, unique=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True, nullable=False, unique=False)

