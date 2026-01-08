from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import psycopg2
import json

app = Flask(__name__)
CORS(app)

# Load pre-computed results
with open('analysis_results.json', 'r') as f:
    ANALYSIS_RESULTS = json.load(f)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="crawler",
        user="postgres",
        password="cs515"
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Only live stats - everything else is pre-computed"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM posts_bsky")
    bsky = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts_4chan WHERE board_name='sp'")
    sp = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts_4chan WHERE board_name='pol'")
    pol = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'bsky': bsky,
        'sp': sp,
        'pol': pol,
        'total': bsky + sp + pol
    })

@app.route('/api/live-stats')
def get_live_stats():
    """Get live crawler statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get latest timestamps
    cursor.execute("SELECT MAX(created_at) FROM posts_4chan")
    latest_4chan = cursor.fetchone()[0]
    
    cursor.execute("SELECT MAX(created_at) FROM posts_bsky")
    latest_bsky = cursor.fetchone()[0]
    
    # Get posts in last hour
    cursor.execute("""
        SELECT COUNT(*) FROM posts_4chan
        WHERE created_at > NOW() - INTERVAL '1 hour'
    """)
    posts_last_hour_4chan = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM posts_bsky
        WHERE created_at > NOW() - INTERVAL '1 hour'
    """)
    posts_last_hour_bsky = cursor.fetchone()[0]
    
    # Get posts in last 24 hours
    cursor.execute("""
        SELECT COUNT(*) FROM posts_4chan
        WHERE created_at > NOW() - INTERVAL '24 hours'
    """)
    posts_last_24h_4chan = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM posts_bsky
        WHERE created_at > NOW() - INTERVAL '24 hours'
    """)
    posts_last_24h_bsky = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'latest_4chan': latest_4chan.isoformat() if latest_4chan else None,
        'latest_bsky': latest_bsky.isoformat() if latest_bsky else None,
        'posts_last_hour': posts_last_hour_4chan + posts_last_hour_bsky,
        'posts_last_24h': posts_last_24h_4chan + posts_last_24h_bsky,
        'rate_per_hour': round((posts_last_24h_4chan + posts_last_24h_bsky) / 24, 1)
    })

@app.route('/api/event-data')
def event_data():
    """Load pre-computed event data"""
    platform = request.args.get('platform', 'sp')
    date = request.args.get('date', '2025-11-10')
    
    try:
        return jsonify(ANALYSIS_RESULTS['event_examples'][platform][date])
    except KeyError:
        # Fallback: compute on-the-fly if date not pre-computed
        from feature_event_spike import get_event_comparison
        df = get_event_comparison(platform, date)
        return jsonify(df.to_dict('records'))

@app.route('/api/media-data')
def media_data():
    """Load pre-computed media engagement data"""
    platform = request.args.get('platform', 'sp')
    
    key = f'{platform}_media'
    return jsonify(ANALYSIS_RESULTS[key])

@app.route('/api/topics-data')
def topics_data():
    """Load pre-computed topics data"""
    platform = request.args.get('platform', 'sp')
    
    key = f'{platform}_topics'
    return jsonify(ANALYSIS_RESULTS[key])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
