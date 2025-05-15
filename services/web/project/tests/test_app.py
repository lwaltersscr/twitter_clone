"""Basic tests for the Twitter clone application."""
import os
import unittest
from project import create_app, db
from project.models import User, Tweet

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test'
    WTF_CSRF_ENABLED = False

class TwitterCloneTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    def test_home_page(self):
        """Test that home page loads and shows recent tweets."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Recent Tweets', response.data)
    
    def test_login(self):
        """Test login functionality."""
        # Create a test user
        user = User(username='test_user')
        user.set_password('test_password')
        db.session.add(user)
        db.session.commit()
        
        # Test login with correct credentials
        response = self.client.post('/login', data={
            'username': 'test_user',
            'password': 'test_password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome, test_user!', response.data)
        
        # Test login with incorrect password
        response = self.client.post('/login', data={
            'username': 'test_user',
            'password': 'wrong_password'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_create_tweet(self):
        """Test tweet creation."""
        # Create and login a test user
        user = User(username='tweet_test_user')
        user.set_password('test_password')
        db.session.add(user)
        db.session.commit()
        
        self.client.post('/login', data={
            'username': 'tweet_test_user',
            'password': 'test_password'
        })
        
        # Create a tweet
        response = self.client.post('/create_message', data={
            'content': 'Test tweet with https://example.com'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your tweet has been posted!', response.data)
        
        # Verify tweet appears in database
        tweet = Tweet.query.filter_by(content='Test tweet with https://example.com').first()
        self.assertIsNotNone(tweet)
        self.assertEqual(tweet.author.username, 'tweet_test_user')
        self.assertEqual(len(tweet.urls.all()), 1)
    
    def test_search(self):
        """Test tweet search functionality."""
        # Create a test tweet
        user = User(username='search_test_user')
        user.set_password('test_password')
        db.session.add(user)
        tweet = Tweet(content='Unique test tweet for search', author=user)
        db.session.add(tweet)
        db.session.commit()
        
        # Search for the tweet
        response = self.client.get('/search?q=unique+test+tweet')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Unique test tweet for search', response.data)

if __name__ == '__main__':
    unittest.main() 