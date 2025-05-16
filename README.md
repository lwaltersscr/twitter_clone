# Twitter Clone

A Flask-based Twitter clone with PostgreSQL backend and RUM index support for efficient full-text search.

## Features

- User authentication (login/signup)
- Tweet creation and viewing
- Full-text search with RUM index
- URL extraction and indexing
- Production-ready Docker setup
- Test data generation for performance testing

## Development Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd twitter_clone
```

2. Create environment files:
```bash
# .env.dev
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

5. Generate test data (optional):
```bash
docker compose exec web python project/scripts/generate_prod_data.py postgresql://twitter_user:twitter_password@db:5432/twitter_dev 100 50
```

6. Visit http://localhost:1337

## Production Setup

1. Create production environment file:
```bash
# .env.prod
FLASK_APP=project/__init__.py
FLASK_DEBUG=0
DATABASE_URL=postgresql://twitter_user:twitter_password@db:5432/twitter_prod
```

2. Build and start production services:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## Test Data Generation

The project includes a script to generate large amounts of test data:

```bash
docker compose exec web python project/scripts/generate_prod_data.py <database_url> <num_users> <tweets_per_user>
```

Example for generating 10M+ rows:
```bash
docker compose exec web python project/scripts/generate_prod_data.py postgresql://twitter_user:twitter_password@db:5432/twitter_dev 50000 200
```

## Project Structure

```
twitter_clone/
├── docker-compose.yml          # Development configuration
├── docker-compose.prod.yml     # Production configuration
├── services/
│   ├── postgres/              # PostgreSQL service
│   │   ├── Dockerfile
│   │   └── schema.sql
│   └── web/                   # Flask application
│       ├── Dockerfile
│       ├── Dockerfile.prod
│       ├── manage.py
│       ├── requirements.txt
│       └── project/
│           ├── __init__.py
│           ├── auth.py
│           ├── main.py
│           ├── models.py
│           └── templates/
```
