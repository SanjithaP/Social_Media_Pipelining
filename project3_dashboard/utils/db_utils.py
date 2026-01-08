import psycopg2
import pandas as pd
import streamlit as st

@st.cache_resource
def get_db_connection():
    """Create a cached database connection."""
    return psycopg2.connect(
        host="localhost",
        database="crawler",
        user="postgres",
        password="cs515"
    )

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_bsky_data():
    """Load all Bluesky posts from database."""
    conn = get_db_connection()
    query = """
        SELECT actor, created_at, data, like_count, repost_count, 
               uri, stance, has_media
        FROM posts_bsky
        ORDER BY created_at
    """
    df = pd.read_sql(query, conn)
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    df['source'] = 'bsky'
    return df

@st.cache_data(ttl=300)
def load_4chan_data(board=None):
    """Load 4chan posts from database.
    
    Args:
        board: 'sp', 'pol', or None for both
    """
    conn = get_db_connection()
    
    if board:
        query = f"""
            SELECT board_name, thread_number, post_number, 
                   created_at, data, has_media
            FROM posts_4chan
            WHERE board_name = '{board}'
            ORDER BY created_at
        """
    else:
        query = """
            SELECT board_name, thread_number, post_number,
                   created_at, data, has_media
            FROM posts_4chan
            ORDER BY created_at
        """
    
    df = pd.read_sql(query, conn)
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    df['source'] = '4chan_' + df['board_name']
    return df

def get_latest_stats():
    """Get real-time statistics from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM posts_bsky")
    bsky_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts_4chan WHERE board_name='sp'")
    sp_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts_4chan WHERE board_name='pol'")
    pol_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(created_at) FROM posts_bsky")
    latest_bsky = cursor.fetchone()[0]
    
    cursor.close()
    
    return {
        'bsky': bsky_count,
        'sp': sp_count,
        'pol': pol_count,
        'latest_update': latest_bsky
    }
