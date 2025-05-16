-- Enable the pg_trgm extension for search functionality
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create index on username for faster lookups
CREATE INDEX idx_users_username ON users(username);

-- Tweets table
CREATE TABLE tweets (
    tweet_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX idx_tweets_user_id ON tweets(user_id);
CREATE INDEX idx_tweets_created_at ON tweets(created_at DESC);

-- Create a RUM index for full text search on tweets
CREATE EXTENSION IF NOT EXISTS rum;
CREATE INDEX idx_tweets_rum ON tweets USING rum (to_tsvector('english', content));

-- URLs table (for storing URLs mentioned in tweets)
CREATE TABLE urls (
    url_id SERIAL PRIMARY KEY,
    tweet_id INTEGER REFERENCES tweets(tweet_id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX idx_urls_tweet_id ON urls(tweet_id); 