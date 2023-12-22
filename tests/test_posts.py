from BaseTest import *
from models import Post
from datetime import datetime


class TestPosts(BaseTest):
    def setUp(self):
        connect_db(self.app)
        with self.app.app_context():
            db.create_all()

            # create a user
            db.session.add(User(first_name="Test", last_name="User", image_url="https://www.example.com"))
            db.session.commit()

            # create 5 posts: post1, post2, post3, post4, post5
            for i in range(1, 6):
                db.session.add(
                    Post(
                        title=f"Test Post{i}",
                        content=f"This is test post {i}",
                        user_id=db.session.query(User).first().id,
                        created_at=datetime.now(),
                    )
                )
            db.session.commit()

    def test_get_posts(self):
        response = self.client.get(url_for("user_details", user_id=1))
        self.assert200(response)
        self.assertIn(b"Test Post1", response.data)
        self.assertIn(b"Test Post2", response.data)
        self.assertIn(b"Test Post3", response.data)
        self.assertIn(b"Test Post4", response.data)
        self.assertIn(b"Test Post5", response.data)

    def test_get_post(self):
        response = self.client.get(url_for("post_details", post_id=1))
        self.assert200(response)
        self.assertIn(b"Test Post1", response.data)
        self.assertIn(b"This is test post 1", response.data)
        self.assertNotIn(b"Test Post2", response.data)
        self.assertNotIn(b"Test Post3", response.data)
        self.assertNotIn(b"Test Post4", response.data)

    def test_add_post(self):
        response = self.client.post(
            url_for("new_post", user_id=1),
            data={"title": "Test Post6", "content": "This is test post 6"},
            follow_redirects=True,
        )
        self.assertTemplateUsed("user_details.html")
        self.assertIn(b"Test Post6", response.data)

        # Check that the post was added to the database
        post = db.session.query(Post).get(6)
        self.assertIsNotNone(post)
        self.assertEqual(post.title, "Test Post6")
        self.assertEqual(post.content, "This is test post 6")

    def test_edit_post(self):
        response = self.client.post(
            url_for("edit_post", post_id=1),
            data={
                "title": "Edited Post1",
                "content": "This is test post 1 after being edited"
            },
            follow_redirects=True,
        )
        self.assertTemplateUsed("post_details.html")
        self.assertIn(b"Edited Post1", response.data)
        self.assertIn(b"This is test post 1 after being edited", response.data)

        # Check that the post was edited in the database
        post = db.session.query(Post).get(1)
        self.assertIsNotNone(post)
        self.assertEqual(post.title, "Edited Post1")
        self.assertEqual(post.content, "This is test post 1 after being edited")

    def test_delete_post(self):
        response = self.client.post(
            url_for("delete_post", post_id=1),
            follow_redirects=True,
        )
        self.assertTemplateUsed("user_details.html")
        self.assertNotIn(b"Test Post1", response.data)

        # Check that the post was deleted from the database
        self.assertIsNone(db.session.query(Post).get(1))
