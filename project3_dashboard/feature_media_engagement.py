import psycopg2
import pandas as pd

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="crawler",
        user="postgres",
        password="cs515"
    )

def get_media_engagement_4chan(board):
    """Compare engagement for posts with/without media on 4chan."""
    conn = get_db_connection()
    
    query = f"""
        WITH thread_sizes AS (
            SELECT thread_number, COUNT(*) as size
            FROM posts_4chan
            WHERE board_name = '{board}'
            GROUP BY thread_number
        )
        SELECT 
            CASE WHEN p.has_media THEN 'With Media' ELSE 'Text Only' END as post_type,
            COUNT(p.post_number) as num_posts,
            ROUND(AVG(ts.size)::numeric, 2) as avg_thread_size
        FROM posts_4chan p
        JOIN thread_sizes ts ON p.thread_number = ts.thread_number
        WHERE p.board_name = '{board}'
        GROUP BY p.has_media
        ORDER BY p.has_media DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_media_engagement_bsky():
    """Compare engagement for posts with/without media on Bluesky."""
    conn = get_db_connection()
    
    query = """
        SELECT 
            CASE WHEN has_media THEN 'With Media' ELSE 'Text Only' END as post_type,
            COUNT(*) as num_posts,
            ROUND(AVG(like_count)::numeric, 2) as avg_likes,
            ROUND(AVG(repost_count)::numeric, 2) as avg_reposts
        FROM posts_bsky
        WHERE like_count IS NOT NULL
        GROUP BY has_media
        ORDER BY has_media DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    print("\n=== /sp/ Post-Level Analysis ===")
    sp_data = get_media_engagement_4chan('sp')
    print(sp_data)
    
    print("\n=== /pol/ Post-Level Analysis ===")
    pol_data = get_media_engagement_4chan('pol')
    print(pol_data)
    
    print("\n=== Bluesky Analysis ===")
    bsky_data = get_media_engagement_bsky()
    print(bsky_data)
    
    # Calculate ratios
    print("\n=== Engagement Ratios ===")
    for name, df in [('/sp/', sp_data), ('/pol/', pol_data)]:
        if len(df) == 2:
            media_eng = df[df['post_type'] == 'With Media']['avg_thread_size'].values[0]
            text_eng = df[df['post_type'] == 'Text Only']['avg_thread_size'].values[0]
            ratio = media_eng / text_eng
            print(f"{name}: Media posts in threads {ratio:.2f}x larger than text-only posts")
    
    if len(bsky_data) == 2:
        media_likes = bsky_data[bsky_data['post_type'] == 'With Media']['avg_likes'].values[0]
        text_likes = bsky_data[bsky_data['post_type'] == 'Text Only']['avg_likes'].values[0]
        ratio = media_likes / text_likes if text_likes > 0 else 0
        print(f"Bluesky: Media posts get {ratio:.2f}x likes compared to text-only")
