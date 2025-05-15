"""Script to generate test data for the Twitter clone application."""
import sys
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from project.models import User, Tweet, URL, db

def generate_test_data(num_users=10, num_tweets=100):
    """Generate test data with the specified number of users and tweets."""
    # Create database connection
    engine = create_engine(sys.argv[1])  # Database URL passed as argument
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Generate users
    users = []
    for i in range(num_users):
        user = User(username=f'test_user_{i}')
        user.set_password(f'password_{i}')
        users.append(user)
        session.add(user)
    
    # Commit users to get their IDs
    session.commit()
    
    # Sample text for generating tweets
    words = ['Hello', 'World', 'Testing', 'Twitter', 'Clone', 'Project', 
             'Database', 'Performance', 'Scale', 'Web', 'Application']
    urls = [
        'https://example.com',
        'https://github.com',
        'https://python.org',
        'https://flask.palletsprojects.com',
        'https://postgresql.org'
    ]
    
    # Generate tweets
    start_date = datetime.utcnow() - timedelta(days=365)
    for _ in range(num_tweets):
        # Random content generation
        content_words = [random.choice(words) for _ in range(random.randint(5, 15))]
        if random.random() < 0.3:  # 30% chance to include URL
            content_words.append(random.choice(urls))
        content = ' '.join(content_words)
        
        # Random user and date
        user = random.choice(users)
        tweet_date = start_date + timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Create tweet
        tweet = Tweet(
            content=content,
            author=user,
            created_at=tweet_date
        )
        session.add(tweet)
        
        # Extract and save URLs if present
        for word in content_words:
            if word.startswith('http'):
                url = URL(url=word, tweet=tweet)
                session.add(url)
    
    # Commit all changes
    session.commit()
    session.close()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python generate_test_data.py <database_url> <num_users> <num_tweets>")
        sys.exit(1)
    
    generate_test_data(int(sys.argv[2]), int(sys.argv[3])) 