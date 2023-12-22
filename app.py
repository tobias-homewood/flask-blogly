"""Blogly application."""

from flask import Flask, request, redirect, render_template, session, url_for
from models import db, connect_db, User, Post, Tag
from datetime import datetime

def create_app(db_url='postgresql:///blogly', testing=False):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['TESTING'] = testing
    app.config['DEBUG'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    if not testing:
        connect_db(app)
        with app.app_context():
            db.create_all()

    from flask_debugtoolbar import DebugToolbarExtension
    app.config['SECRET_KEY'] = "SECRET!"
    debug = DebugToolbarExtension(app)


    @app.route('/')
    def home():
        """Render homepage"""
        return render_template('home.html')

    @app.route('/users')
    def users():
        """Render users page"""
        return render_template('user_listing.html', users=db.session.query(User).all())


    @app.route('/users/new', methods=['GET', 'POST'])
    def new_user():
        """Render new user form"""
        if request.method == 'GET':
            return render_template('new_user.html')
        
        # Implicit else, 
        # this is the POST request
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        image_url = request.form['image_url']

        # Create new user instance
        new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)

        # Add new user to database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('users'))

    @app.route('/users/<int:user_id>')
    def user_details(user_id):
        """Render user detail page"""  
        return render_template(
            'user_details.html', 
            user = db.session.query(User).get_or_404(user_id)
        )

    @app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
    def edit_user(user_id):
        user = db.session.query(User).get_or_404(user_id)

        """Render edit user form"""
        if request.method == 'GET':
            return render_template('edit_user.html', user=user)
        
        # Implicit else,
        # this is the POST request
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.image_url = request.form['image_url']

        # Update user in database
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('user_details', user_id=user.id))

    @app.route('/users/<int:user_id>/delete', methods=['POST'])
    def delete_user(user_id):
        """Delete user from database"""
        user = db.session.query(User).get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('users'))
    
    @app.route('/posts/<int:post_id>')
    def post_details(post_id):
        """Render post detail page"""
        return render_template('post_details.html', post=db.session.query(Post).get_or_404(post_id))
    
    @app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
    def new_post(user_id):
        """Render new post form"""
        if request.method == 'GET':
            return render_template(
                'new_post.html',
                user=db.session.query(User).get_or_404(user_id),
                tags=db.session.query(Tag).all()
            )
        
        # Implicit else,
        # this is the POST request
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.now()

        # Create new post instance
        new_post = Post(
            title=title,
            content=content,
            user_id=user_id,
            created_at=created_at
        )

        # Add tags to post
        for tag_id in request.form.getlist('tags'):
            tag = db.session.query(Tag).get(tag_id)
            new_post.tags.append(tag)

        # Add new post to database
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('user_details', user_id=user_id))
    
    @app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
    def edit_post(post_id):
        """Render edit post form"""
        post = db.session.query(Post).get_or_404(post_id)
        if request.method == 'GET':
            return render_template('edit_post.html', post=post, tags=db.session.query(Tag).all())
        
        # Implicit else,
        # this is the POST request
        post.title = request.form['title']
        post.content = request.form['content']

        # Update tags
        post.tags.clear()
        for tag_id in request.form.getlist('tags'):
            tag = db.session.query(Tag).get(tag_id)
            post.tags.append(tag)

        # Update post in database
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('post_details', post_id=post_id))
    
    @app.route('/posts/<int:post_id>/delete', methods=['POST'])
    def delete_post(post_id):
        """Delete post from database"""
        post = db.session.query(Post).get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('user_details', user_id=post.user_id))
    
    @app.route('/tags')
    def tags():
        """Render tags page"""
        return render_template('tag_listing.html', tags=db.session.query(Tag).all())

    @app.route('/tags/<int:tag_id>')
    def tag_details(tag_id):
        """Render tag detail page"""
        return render_template('tag_details.html', tag=db.session.query(Tag).get_or_404(tag_id))

    @app.route('/tags/new', methods=['GET', 'POST'])
    def new_tag():
        """Render new tag form"""
        if request.method == 'GET':
            return render_template('new_tag.html')
        
        # Implicit else,
        # this is the POST request

        # Create new tag instance
        new_tag = Tag(name=request.form['name'])

        # Add new tag to database
        db.session.add(new_tag)
        db.session.commit()

        return redirect(url_for('tags'))

    @app.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
    def edit_tag(tag_id):
        """Render edit tag form"""
        tag = db.session.query(Tag).get_or_404(tag_id)
        if request.method == 'GET':
            return render_template('edit_tag.html', tag=tag)
        
        # Implicit else,
        # this is the POST request
        tag.name = request.form['name']

        # Update tag in database
        db.session.add(tag)
        db.session.commit()

        return redirect(url_for('tag_details', tag_id=tag_id))

    @app.route('/tags/<int:tag_id>/delete', methods=['POST'])
    def delete_tag(tag_id):
        tag = db.session.query(Tag).get_or_404(tag_id)
        db.session.delete(tag)
        db.session.commit()

        return redirect(url_for('tags'))



    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
