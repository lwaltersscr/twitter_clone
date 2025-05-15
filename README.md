# Flask on Docker

## Overview
This repository contains a fully Dockerized Flask web application integrated with PostgreSQL, Gunicorn, and Nginx. The web service allows users to upload images, which are then served from a secure media directory. The project is structured for both development and production environments, following best practices for containerization, database management, and web server configuration.

## Example image ulpoad

![hippo](https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExenBwa2w5aDlweTZyaXd2dng1b3ZtaDhnbXFtdXQyZG16ajk2cmRvYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mhoKQ4AWWLG3c0ha3p/giphy.gif)


## Build Instructions
1. Clone the repo
2. Create the following environment files in the project root:
     - .env.dev (Development)
       ```
       FLASK_APP=project/__init__.py
       FLASK_DEBUG=1
       DATABASE_URL=postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev
       SQL_HOST=db
       SQL_PORT=5432
       DATABASE=postgres
       APP_FOLDER=/usr/src/app
       ```
     - .env.prod (Production)
       ```
       FLASK_APP=project/__init__.py
       FLASK_DEBUG=0
       DATABASE_URL=postgresql://hello_flask:hello_flask@db:5432/hello_flask_prod
       SQL_HOST=db
       SQL_PORT=5432
       DATABASE=postgres
       APP_FOLDER=/home/app/web
       ```
     - .env.prod.db (Database - Production) --  Ensure these files are in .gitignore to avoid uploading sensitive credentials.
       ```
       POSTGRES_USER=hello_flask
       POSTGRES_PASSWORD=hello_flask
       POSTGRES_DB=hello_flask_prod
       ```
4. Build and run in development mode: `docker-compose up -d --build`
     - Access the app at: `http://localhost:8080`
     - Test static files at: `http://localhost:8080/static/hello.txt`
5. Build and run in production mode:
     - `docker-compose -f docker-compose.prod.yml down -v`
     - `docker-compose -f docker-compose.prod.yml up -d --build`
     - `docker-compose -f docker-compose.prod.yml exec web python manage.py create_db`
     - `docker-compose -f docker-compose.prod.yml up -d --build`
     - Access the production app at: `http://localhost:8080/`
7. Test media upload: `http://localhost:8080/upload`
8. View the uploaded media file: `http://localhost:1033/media/IMAGE_FILE_NAME`
9. To stop containers:
      - `docker-compose down -v`
      - `docker-compose -f docker-compose.prod.yml down -v`
