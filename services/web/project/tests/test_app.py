"""Comprehensive tests for the Twitter clone application."""
import os
import unittest
from datetime import datetime, timedelta
from project import create_app, db
from project.models import User, Tweet, URL
from werkzeug.security import generate_password_hash

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
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_user(self, username='test_user', password='test_password'):
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    def login(self, username='test_user', password='test_password'):
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def logout(self):
        return self.client.get('/logout', follow_redirects=True)
    
    def test_home_page_no_tweets(self):
        """Test home page with no tweets."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Recent Tweets', response.data)
        self.assertNotIn(b'<div class="card mb-3">', response.data)
    
    def test_home_page_with_tweets(self):
        """Test home page displays tweets correctly."""
        user = self.create_user()
        # Create multiple tweets
        tweets = []
        for i in range(25):  # Create more than one page worth
            tweet = Tweet(
                content=f'Test tweet {i}',
                author=user,
                created_at=datetime.utcnow() - timedelta(minutes=i)
            )
            tweets.append(tweet)
        db.session.add_all(tweets)
        db.session.commit()
        
        # Test first page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test tweet 0', response.data)
        self.assertIn(b'Next', response.data)
        
        # Test pagination
        response = self.client.get('/?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Previous', response.data)
    
    def test_login_validation(self):
        """Test login with various scenarios."""
        # Create test user
        self.create_user()
        
        # Test valid login
        response = self.login()
        self.assertIn(b'Welcome, test_user!', response.data)
        
        # Test logout
        response = self.logout()
        self.assertNotIn(b'Welcome, test_user!', response.data)
        
        # Test invalid password
        response = self.login(password='wrong_password')
        self.assertIn(b'Invalid username or password', response.data)
        
        # Test non-existent user
        response = self.login(username='nonexistent')
        self.assertIn(b'Invalid username or password', response.data)
        
        # Test empty fields
        response = self.client.post('/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_create_account_validation(self):
        """Test account creation with various scenarios."""
        # Test successful account creation
        response = self.client.post('/create_account', data={
            'username': 'new_user',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Congratulations', response.data)
        
        # Test existing username
        response = self.client.post('/create_account', data={
            'username': 'new_user',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Username already exists', response.data)
        
        # Test password mismatch
        response = self.client.post('/create_account', data={
            'username': 'another_user',
            'password': 'password123',
            'password2': 'password456'
        }, follow_redirects=True)
        self.assertIn(b'Passwords do not match', response.data)
        
        # Test empty fields
        response = self.client.post('/create_account', data={
            'username': '',
            'password': '',
            'password2': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please fill in all fields', response.data)
    
    def test_tweet_creation(self):
        """Test tweet creation with various scenarios."""
        self.create_user()
        self.login()
        
        # Test valid tweet
        response = self.client.post('/create_message', data={
            'content': 'Test tweet with https://example.com'
        }, follow_redirects=True)
        self.assertIn(b'Your tweet has been posted!', response.data)
        self.assertIn(b'https://example.com', response.data)
        
        # Verify URL was extracted
        tweet = Tweet.query.first()
        self.assertEqual(len(tweet.urls.all()), 1)
        self.assertEqual(tweet.urls.first().url, 'https://example.com')
        
        # Test empty tweet
        response = self.client.post('/create_message', data={
            'content': ''
        }, follow_redirects=True)
        self.assertIn(b'Tweet content is required!', response.data)
        
        # Test unauthorized access
        self.logout()
        response = self.client.get('/create_message')
        self.assertEqual(response.status_code, 302)  # Redirects to login
    
    def test_search_functionality(self):
        """Test search functionality with various scenarios."""
        user = self.create_user()
        
        # Create test tweets
        tweets = [
            Tweet(content='Python programming is fun', author=user),
            Tweet(content='Flask web development', author=user),
            Tweet(content='Python web development with Flask', author=user),
            Tweet(content='Just a random tweet', author=user)
        ]
        db.session.add_all(tweets)
        db.session.commit()
        
        # Test single word search
        response = self.client.get('/search?q=Python')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<p class="card-text"><mark>Python</mark> programming is fun</p>', response.data)
        self.assertIn(b'<p class="card-text"><mark>Python</mark> web development with Flask</p>', response.data)
        
        # Test multiple word search
        response = self.client.get('/search?q=web+development')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<p class="card-text">Flask <mark>web</mark> <mark>development</mark></p>', response.data)
        self.assertIn(b'<p class="card-text">Python <mark>web</mark> <mark>development</mark> with Flask</p>', response.data)
        
        # Test search with no results
        response = self.client.get('/search?q=nonexistent')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No results found', response.data)
        
        # Test empty search
        response = self.client.get('/search?q=')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Search Results', response.data)
    
    def test_url_extraction(self):
        """Test URL extraction from tweets."""
        self.create_user()
        self.login()
        
        # Test single URL
        response = self.client.post('/create_message', data={
            'content': 'Check this link https://example.com'
        }, follow_redirects=True)
        tweet = Tweet.query.first()
        self.assertEqual(len(tweet.urls.all()), 1)
        
        # Test multiple URLs
        response = self.client.post('/create_message', data={
            'content': 'Multiple links: https://example.com https://test.com'
        }, follow_redirects=True)
        tweet = Tweet.query.order_by(Tweet.tweet_id.desc()).first()
        self.assertEqual(len(tweet.urls.all()), 2)
        
        # Test no URLs
        response = self.client.post('/create_message', data={
            'content': 'No links in this tweet'
        }, follow_redirects=True)
        tweet = Tweet.query.order_by(Tweet.tweet_id.desc()).first()
        self.assertEqual(len(tweet.urls.all()), 0)

if __name__ == '__main__':
    unittest.main() 