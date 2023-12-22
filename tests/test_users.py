from BaseTest import *

class TestUsers(BaseTest):
    def setUp(self):
        connect_db(self.app)
        with self.app.app_context():
            db.create_all()

            # create 5 users: user1, user2, user3, user4, user5
            for i in range(1, 6):
                db.session.add(User(first_name=f'Test', last_name=f'User{i}', image_url=f'http://example{i}.com'))
            db.session.commit()

    def test_home(self):
        response = self.client.get(url_for('home'))
        self.assert200(response)
        self.assertTemplateUsed('home.html')

    def test_user_listing(self):
        response = self.client.get(url_for('users'))
        self.assert200(response)
        self.assertTemplateUsed('user_listing.html')
        self.assertIn('Test User1', response.text)
        self.assertIn('Test User2', response.text)
        self.assertIn('Test User3', response.text)
        self.assertIn('Test User4', response.text)
        self.assertIn('Test User5', response.text)
        self.assertNotIn('Test User6', response.text)

    def test_new_user(self):
        # GET request, should get the form
        response = self.client.get(url_for('new_user'))
        self.assert200(response)
        self.assertTemplateUsed('new_user.html')

        # POST request, should create a new user
        response = self.client.post(url_for('new_user'), data={
            'first_name': 'Test',
            'last_name': 'User6',
            'image_url': 'http://example6.com'
        }, follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('user_listing.html')
        self.assertIn('Test User6', response.text)

        # Check that the user was added to the database
        user = db.session.query(User).get_or_404(6)
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User6')
        self.assertEqual(user.image_url, 'http://example6.com')

    def test_user_details(self):
        response = self.client.get(url_for('user_details', user_id=1))
        self.assert200(response)
        self.assertTemplateUsed('user_details.html')
        self.assertIn('Test User1', response.text)
        self.assertIn('src="http://example1.com"', response.text)
        self.assertNotIn('Test User6', response.text)

    def test_edit_user(self):
        # GET request, should get the form
        response = self.client.get(url_for('edit_user', user_id=1))
        self.assert200(response)
        self.assertTemplateUsed('edit_user.html')
        self.assertIn('Edit "Test User1"', response.text)
        self.assertIn('value="http://example1.com"', response.text)

        # POST request, should edit the user
        response = self.client.post(url_for('edit_user', user_id=1), data={
            'first_name': 'Edited',
            'last_name': 'User1',
            'image_url': 'http://editedexample1.com'
        }, follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('user_details.html')
        self.assertIn('Edited User1', response.text)
        self.assertIn('src="http://editedexample1.com"', response.text)
        self.assertNotIn('Test User1', response.text)

        # Check that the user was edited in the database
        user = db.session.query(User).get_or_404(1)
        self.assertEqual(user.first_name, 'Edited')
        self.assertEqual(user.last_name, 'User1')
        self.assertEqual(user.image_url, 'http://editedexample1.com')


    def test_delete_user(self):
        # POST request, should delete the user
        response = self.client.post(url_for('delete_user', user_id=1), follow_redirects=True)
        self.assert200(response)
        self.assertTemplateUsed('user_listing.html')
        self.assertNotIn('Test User1', response.text)

        # Check that the user was deleted from the database
        user = db.session.query(User).get(1)
        self.assertIsNone(user)

