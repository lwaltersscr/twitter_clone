# Twitter Clone Demo Guide

## Prerequisites
- Docker and Docker Compose V2 installed
- Git installed
- Ports 1033 (development) and 1337 (production) available

## Quick Start (Development)

1. Clone the repository:
```bash
git clone https://github.com/lwaltersscr/twitter_clone.git
cd twitter_clone
```

2. Create development environment file (.env.dev):
```bash
FLASK_APP=project/__init__.py
FLASK_DEBUG=1
DATABASE_URL=postgresql://twitter_user:twitter_password@db:5432/twitter_dev
```

3. Build and start the development services:
```bash
docker compose up -d --build
```

4. Create database tables:
```bash
docker compose exec web python manage.py create_db
```

5. Generate test data (adjust numbers as needed):
```bash
# For quick testing (100 users, 50 tweets each = 5,000 tweets)
docker compose exec web python project/scripts/generate_prod_data.py postgresql://twitter_user:twitter_password@db:5432/twitter_dev 100 50

# For production-scale testing (50,000 users, 200 tweets each = 10M tweets)
docker compose exec web python project/scripts/generate_prod_data.py postgresql://twitter_user:twitter_password@db:5432/twitter_dev 50000 200
```

6. Access the application:
- Development: http://localhost:1033
- Production: http://localhost:1337

## Production Deployment

1. Create production environment file (.env.prod):
```bash
FLASK_APP=project/__init__.py
FLASK_DEBUG=0
DATABASE_URL=postgresql://twitter_user:twitter_password@db:5432/twitter_prod
```

2. Build and start production services:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

3. Initialize production database:
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py create_db
```

## Testing

Run the test suite:
```bash
docker compose exec web python -m unittest project/tests/test_app.py -v
```

## Useful Commands

### View logs:
```bash
# All services
docker compose logs

# Specific service
docker compose logs web
docker compose logs db
docker compose logs nginx
```

### Stop services:
```bash
# Development
docker compose down

# Production
docker compose -f docker-compose.prod.yml down
```

### Reset database:
```bash
docker compose down -v  # This will delete all data!
docker compose up -d
docker compose exec web python manage.py create_db
```

### Check service status:
```bash
docker compose ps
```

## Features to Demo

1. User Management:
   - Create a new account
   - Log in
   - Log out

2. Tweet Operations:
   - Create a new tweet
   - Add URLs to tweets
   - View tweets on homepage
   - Pagination of tweets

3. Search Functionality:
   - Search for tweets
   - Full-text search with ranking
   - URL extraction and indexing

4. Performance:
   - Show the RUM index in action
   - Demonstrate search speed with large dataset
   - Show pagination performance

## Troubleshooting

1. If ports are already in use:
   - Edit docker-compose.yml and docker-compose.prod.yml
   - Change port mappings (e.g., 1033:80 to another port)

2. If containers won't start:
```bash
docker compose down -v
docker compose up -d --build
```

3. If database errors occur:
```bash
docker compose down -v  # Warning: This deletes all data!
docker compose up -d
docker compose exec web python manage.py create_db
```

4. To check container logs for errors:
```bash
docker compose logs -f
``` 