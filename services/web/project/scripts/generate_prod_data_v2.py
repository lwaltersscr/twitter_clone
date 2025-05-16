import sys
import psycopg2
from datetime import datetime, timedelta
import random
from psycopg2.extras import execute_values

def generate_batch(conn, start_user, end_user, tweets_per_user):
    """Generate a batch of tweets for a range of users."""
    cur = conn.cursor()
    
    # Sample content for more realistic tweets
    topics = ['Python', 'Flask', 'Web Development', 'Database', 'PostgreSQL', 'Docker', 'Cloud Computing',
              'Testing', 'Deployment', 'Security', 'Performance', 'Scalability', 'Frontend', 'Backend']
    actions = ['Learning', 'Building', 'Debugging', 'Deploying', 'Testing', 'Optimizing', 'Studying',
               'Exploring', 'Implementing', 'Designing', 'Reviewing', 'Refactoring']
    adjectives = ['amazing', 'challenging', 'interesting', 'fun', 'complex', 'exciting', 'powerful',
                 'efficient', 'elegant', 'innovative', 'reliable', 'secure']
    urls = [
        'https://python.org',
        'https://flask.palletsprojects.com',
        'https://docker.com',
        'https://postgresql.org',
        'https://github.com',
        'https://aws.amazon.com',
        'https://cloud.google.com',
        'https://azure.microsoft.com'
    ]

    # Create users in batch
    users = []
    user_data = [(f'user_{i}', f'pbkdf2:sha256:123456${i}') 
                 for i in range(start_user, end_user)]
    
    execute_values(
        cur,
        "INSERT INTO users (username, password_hash) VALUES %s RETURNING user_id",
        user_data,
        template="(%s, %s)"
    )
    users = [row[0] for row in cur.fetchall()]
    
    # Generate tweets in batches
    base_time = datetime.now()
    batch_size = 1000
    
    for user_id in users:
        tweets = []
        for i in range(tweets_per_user):
            topic = random.choice(topics)
            action = random.choice(actions)
            adj = random.choice(adjectives)
            has_url = random.random() < 0.3
            url = f" Check out {random.choice(urls)}" if has_url else ""
            
            content = f"{action} {topic} is {adj}!{url}"
            created_at = base_time - timedelta(minutes=random.randint(1, 1000000))
            
            tweets.append((user_id, content, created_at))
            
            if len(tweets) >= batch_size:
                execute_values(
                    cur,
                    "INSERT INTO tweets (user_id, content, created_at) VALUES %s",
                    tweets,
                    template="(%s, %s, %s)"
                )
                tweets = []
        
        if tweets:  # Insert any remaining tweets
            execute_values(
                cur,
                "INSERT INTO tweets (user_id, content, created_at) VALUES %s",
                tweets,
                template="(%s, %s, %s)"
            )
    
    conn.commit()
    cur.close()

def main():
    if len(sys.argv) != 4:
        print("Usage: python generate_prod_data_v2.py <database_url> <num_users> <tweets_per_user>")
        sys.exit(1)
    
    db_url = sys.argv[1]
    num_users = int(sys.argv[2])
    tweets_per_user = int(sys.argv[3])
    
    conn = psycopg2.connect(db_url)
    
    batch_size = 1000
    total_users = 0
    
    try:
        for start_user in range(0, num_users, batch_size):
            end_user = min(start_user + batch_size, num_users)
            generate_batch(conn, start_user, end_user, tweets_per_user)
            total_users += (end_user - start_user)
            print(f"Progress: {total_users}/{num_users} users processed")
    
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main() 