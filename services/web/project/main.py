from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from . import db
from .models import Tweet, URL
import re

bp = Blueprint('main', __name__)

def extract_urls(content):
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, content)

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    tweets = Tweet.query.order_by(Tweet.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('main/index.html', tweets=tweets)

@bp.route('/create_message', methods=['GET', 'POST'])
@login_required
def create_message():
    if request.method == 'POST':
        content = request.form['content']
        if not content:
            flash('Tweet content is required!')
            return redirect(url_for('main.create_message'))
        
        # Create tweet
        tweet = Tweet(content=content, author=current_user)
        db.session.add(tweet)
        
        # Extract and save URLs
        urls = extract_urls(content)
        for url in urls:
            url_obj = URL(url=url, tweet=tweet)
            db.session.add(url_obj)
        
        db.session.commit()
        flash('Your tweet has been posted!')
        return redirect(url_for('main.index'))
    
    return render_template('main/create_message.html')

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return render_template('main/search.html', tweets=None, query=query)
    
    # Using the RUM index for full text search with ranking
    search_query = func.to_tsquery('english', ' & '.join(query.split()))
    tweets = db.session.query(Tweet).filter(
        func.to_tsvector('english', Tweet.content).op('@@')(search_query)
    ).order_by(
        func.ts_rank_cd(
            func.to_tsvector('english', Tweet.content),
            search_query
        ).desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('main/search.html', tweets=tweets, query=query) 