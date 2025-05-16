import sys
import psycopg2
from datetime import datetime, timedelta
import random

def generate_quick_data(db_url, num_users=10, tweets_per_user=50):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Sample content for more realistic tweets
    topics = ['Python', 'Flask', 'Web Development', 'Database', 'PostgreSQL', 'Docker', 'Cloud Computing']
    actions = ['Learning', 'Building', 'Debugging', 'Deploying', 'Testing', 'Optimizing']
    adjectives = ['amazing', 'challenging', 'interesting', 'fun', 'complex', 'exciting']
    urls = [
        'https://python.org',
        'https://flask.palletsprojects.com',
        'https://docker.com',
        'https://postgresql.org',
        'https://github.com'
    ]

    # Create users
    users = []
    for i in range(num_users):
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING user_id",
            (f'user_{i}', f'pbkdf2:sha256:123456${i}')
        )
        users.append(cur.fetchone()[0])
    
    # Generate tweets
    base_time = datetime.now()
    for user_id in users:
        for i in range(tweets_per_user):
            # Generate random tweet content
            topic = random.choice(topics)
            action = random.choice(actions)
            adj = random.choice(adjectives)
            
            # 30% chance to include a URL
            url = f" Check out {random.choice(urls)}" if random.random() < 0.3 else ""
            
            content = f"{action} {topic} is {adj}!{url}"
            
            # Insert tweet
            cur.execute(
                "INSERT INTO tweets (user_id, content, created_at) VALUES (%s, %s, %s) RETURNING tweet_id",
                (user_id, content, base_time - timedelta(minutes=random.randint(1, 1000)))
            )
            
            # If tweet has URL, add to urls table
            if url:
                tweet_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO urls (tweet_id, url) VALUES (%s, %s)",
                    (tweet_id, url.split()[-1])
                )
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Generated {num_users} users with {tweets_per_user} tweets each!")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python quick_data.py <database_url>")
        sys.exit(1)
    
    generate_quick_data(sys.argv[1]) 