"""Script to generate production-scale test data for the Twitter clone application."""
import os
import sys
import random
import multiprocessing
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from project.models import User, Tweet, URL

def generate_batch(args):
    """Generate a batch of tweets for a subset of users."""
    db_url, start_user, end_user, tweets_per_user = args
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    words = ['Hello', 'World', 'Testing', 'Twitter', 'Clone', 'Project', 
             'Database', 'Performance', 'Scale', 'Web', 'Application',
             'Python', 'Flask', 'PostgreSQL', 'SQLAlchemy', 'Docker',
             'Development', 'Production', 'Cloud', 'Server', 'Client',
             'Frontend', 'Backend', 'FullStack', 'DevOps', 'API']
    
    urls = [
        'https://example.com',
        'https://github.com',
        'https://python.org',
        'https://flask.palletsprojects.com',
        'https://postgresql.org',
        'https://docker.com',
        'https://aws.amazon.com',
        'https://cloud.google.com',
        'https://azure.microsoft.com',
        'https://heroku.com'
    ]
    
    # Create users for this batch
    users = []
    for i in range(start_user, end_user):
        user = User(username=f'user_{i}')
        user.set_password(f'password_{i}')
        users.append(user)
        session.add(user)
    
    session.commit()
    
    # Generate tweets for each user
    start_date = datetime.utcnow() - timedelta(days=365)
    for user in users:
        for _ in range(tweets_per_user):
            # Generate tweet content
            content_words = [random.choice(words) for _ in range(random.randint(5, 20))]
            if random.random() < 0.3:  # 30% chance to include URL
                content_words.append(random.choice(urls))
            content = ' '.join(content_words)
            
            # Create tweet with random date
            tweet_date = start_date + timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            tweet = Tweet(
                content=content,
                author=user,
                created_at=tweet_date
            )
            session.add(tweet)
            
            # Add URLs
            for word in content_words:
                if word.startswith('http'):
                    url = URL(url=word, tweet=tweet)
                    session.add(url)
            
            # Commit every 1000 tweets to avoid memory issues
            if _ % 1000 == 0:
                session.commit()
    
    session.commit()
    session.close()

def generate_production_data(db_url, num_users=50000, tweets_per_user=200):
    """Generate production-scale test data using multiple processes."""
    # Calculate batches based on CPU cores
    num_processes = multiprocessing.cpu_count()
    users_per_process = num_users // num_processes
    
    # Prepare arguments for each process
    process_args = []
    for i in range(num_processes):
        start_user = i * users_per_process
        end_user = start_user + users_per_process if i < num_processes - 1 else num_users
        process_args.append((db_url, start_user, end_user, tweets_per_user))
    
    # Create and start processes
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(generate_batch, process_args)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python generate_prod_data.py <database_url> <num_users> <tweets_per_user>")
        sys.exit(1)
    
    db_url = sys.argv[1]
    num_users = int(sys.argv[2])
    tweets_per_user = int(sys.argv[3])
    
    print(f"Generating {num_users} users with {tweets_per_user} tweets each...")
    generate_production_data(db_url, num_users, tweets_per_user)
    print("Done!") 