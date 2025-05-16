from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, desc, text
from . import db
from .models import Tweet, URL
import re

bp = Blueprint('main', __name__)

def extract_urls(content):
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, content)

def get_word_suggestions(word):
    """Get similar words using pg_trgm."""
    #get all words
    sql = text("""
        WITH words AS (
            SELECT DISTINCT word
            FROM (
                SELECT unnest(string_to_array(lower(content), ' ')) as word
                FROM tweets
            ) t
            WHERE length(word) > 2
        )
        SELECT word, similarity(lower(:search_word), lower(word)) as sim
        FROM words
        WHERE word % :search_word
          AND length(word) > 2
        ORDER BY sim DESC
        LIMIT 3;
    """)
    result = db.session.execute(sql, {'search_word': word})
    return [row[0] for row in result]

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
        
        tweet = Tweet(content=content, author=current_user)
        db.session.add(tweet)
        
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
    
    current_app.logger.debug(f"Search query: {query}")
    
    # Using the RUM index for full text search with ranking
    search_query = func.to_tsquery('english', ' & '.join(query.split()))
    
    # Query with ranking and highlighting
    tweets = db.session.query(
        Tweet,
        func.ts_rank_cd(
            func.to_tsvector('english', Tweet.content),
            search_query
        ).label('rank'),
        func.ts_headline(
            'english',
            Tweet.content,
            search_query,
            'StartSel = <mark>, StopSel = </mark>, HighlightAll=TRUE'
        ).label('highlighted_content')
    ).filter(
        func.to_tsvector('english', Tweet.content).op('@@')(search_query)
    ).order_by(
        text('rank DESC')
    ).paginate(page=page, per_page=20, error_out=False)
    
    current_app.logger.debug(f"Found {len(tweets.items)} results")
    
    suggestions = []
    if len(tweets.items) == 0:
        # Get suggestions for each word in the query
        for word in query.split():
            if len(word) > 2:  # Only suggest for words longer than 2 characters
                similar_words = get_word_suggestions(word)
                current_app.logger.debug(f"Suggestions for '{word}': {similar_words}")
                if similar_words:
                    suggestions.append((word, similar_words))
    
    current_app.logger.debug(f"Final suggestions: {suggestions}")
    return render_template('main/search.html', tweets=tweets, query=query, suggestions=suggestions) 