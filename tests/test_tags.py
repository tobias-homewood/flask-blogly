from BaseTest import *
from models import Post, Tag, PostTag
from datetime import datetime

class TestTags(BaseTest):
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

            # create 5 tags: tag1, tag2, tag3, tag4, tag5
            for i in range(1, 6):
                db.session.add(Tag(name=f"Tag{i}"))
            db.session.commit()

            # add tags to posts
            # post1: tag1, tag2
            # post2: tag2, tag3
            # post3: tag3, tag4
            # post4: tag4, tag5
            for i in range(1, 5):
                db.session.add(PostTag(post_id=i, tag_id=i))
                db.session.add(PostTag(post_id=i, tag_id=i+1))

            # post5: tag1, tag2, tag3, tag4, tag5
            post = db.session.query(Post).get(5)
            for i in range(1, 6):
                tag = db.session.query(Tag).get(i)
                post.tags.append(tag)
                db.session.add(post)
            db.session.commit()

    def test_relationships(self):
        # Check that post5 has tag1, tag2, tag3, tag4, tag5
        post5 = db.session.query(Post).get(5)
        self.assertEqual(len(post5.tags), 5)
        for i in range(1, 6):
            self.assertIn(db.session.query(Tag).get(i), post5.tags)
            
            # look for the entry in the posts_tags table
            self.assertIn(db.session.query(PostTag).get((5, i)), db.session.query(PostTag).all())

        # Check that tag5 has post5
        tag5 = db.session.query(Tag).get(5)
        self.assertEqual(len(tag5.posts), 2)
        self.assertIn(db.session.query(Post).get(4), tag5.posts)
        self.assertIn(db.session.query(Post).get(5), tag5.posts)

    def test_tag_listing(self):
        # Check that tag listing page has 5 tags
        response = self.client.get(url_for('tags'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tag1', response.data)
        self.assertIn(b'Tag2', response.data)
        self.assertIn(b'Tag3', response.data)
        self.assertIn(b'Tag4', response.data)
        self.assertIn(b'Tag5', response.data)

    def test_tag_details(self):
        # Check that tag details page has 2 posts
        response = self.client.get(url_for('tag_details', tag_id=2))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Post1', response.data)
        self.assertIn(b'Test Post2', response.data)
        self.assertIn(b'Test Post5', response.data)
        self.assertNotIn(b'Test Post3', response.data)

    def test_new_tag(self):
        # Check that new tag form works
        response = self.client.post(
            url_for('new_tag'),
            data={'name': 'New Tag'},
            follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed('tag_listing.html')
        self.assertIn(b'New Tag', response.data)

        # Check that new tag is in database
        self.assertEqual(len(db.session.query(Tag).all()), 6)
        self.assertIsNotNone(db.session.query(Tag).get(6))

    def test_edit_tag(self):
        # Check that edit tag form works
        response = self.client.post(
            url_for('edit_tag', tag_id=2),
            data={'name': 'Edited Tag'},
            follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed('tag_details.html')
        self.assertIn(b'Edited Tag', response.data)

        # Check that tag is updated in database
        self.assertEqual(len(db.session.query(Tag).all()), 5)
        self.assertIsNotNone(db.session.query(Tag).get(2))
        self.assertEqual(db.session.query(Tag).get(2).name, 'Edited Tag')

    def test_delete_tag(self):
        # Check that delete tag button works

        # Delete tag with id = 2
        response = self.client.post(
            url_for('delete_tag', tag_id=2),
            follow_redirects=True
        )
        self.assert200(response)
        self.assertTemplateUsed('tag_listing.html')

        # Tag2 is no longer in the tag listing page
        self.assertNotIn(b'Tag2', response.data)

        # Tag with id = 2 is no longer in the database
        self.assertEqual(len(db.session.query(Tag).all()), 4)
        self.assertIsNone(db.session.query(Tag).get(2))