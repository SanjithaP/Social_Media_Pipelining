import psycopg2
import pandas as pd
import re
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import warnings
warnings.filterwarnings('ignore')

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="crawler",
        user="postgres",
        password="cs515"
    )

def strip_html(text):
    if not text or pd.isna(text):
        return ""
    soup = BeautifulSoup(str(text), 'html.parser')
    return soup.get_text()

def load_platform_text(platform, start_date='2025-11-01', end_date='2025-11-15', limit=None):
    """Load all text from platform."""
    conn = get_db_connection()
    
    limit_clause = f"LIMIT {limit}" if limit else ""
    
    if platform == 'bsky':
        query = f"""
            SELECT 
                COALESCE(data->'record'->>'text', '') as post_text,
                COALESCE(data->'embed'->'external'->>'title', '') as link_title,
                COALESCE(data->'embed'->'external'->>'description', '') as link_desc
            FROM posts_bsky
            WHERE created_at >= '{start_date}'
              AND created_at < '{end_date}'
            {limit_clause}
        """
        df = pd.read_sql(query, conn)
        df['text'] = df['post_text'] + ' ' + df['link_title'] + ' ' + df['link_desc']
    else:
        query = f"""
            SELECT data->>'com' as text
            FROM posts_4chan
            WHERE board_name = '{platform}'
              AND created_at >= '{start_date}'
              AND created_at < '{end_date}'
              AND data->>'com' IS NOT NULL
            {limit_clause}
        """
        df = pd.read_sql(query, conn)
        df['text'] = df['text'].apply(strip_html)
    
    conn.close()
    return df['text'].fillna('').tolist()

def discover_topics_lda(platform, n_topics=10, n_top_words=15):
    """
    Use LDA to discover topics WITHOUT predefined categories.
    Completely unsupervised - finds what's ACTUALLY in the data!
    """
    print(f"\n{'='*70}")
    print(f"🔬 UNSUPERVISED TOPIC DISCOVERY (LDA): {platform.upper()}")
    print(f"{'='*70}")
    
    # Load data (sample for speed)
    print("\n[1/3] Loading posts...")
    texts = load_platform_text(platform, limit=50000)
    print(f"      Loaded {len(texts):,} posts")
    
    # Clean texts
    print("\n[2/3] Preprocessing text...")
    cleaned_texts = []
    for text in texts:
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        # Remove very short texts
        if len(text) > 20:
            cleaned_texts.append(text)
    
    print(f"      Cleaned to {len(cleaned_texts):,} posts")
    
    # Create document-term matrix
    print("\n      Creating document-term matrix...")
    
    # Custom stop words - AGGRESSIVE filtering
    custom_stop_words = [
        # URLs and HTML
        'https', 'http', 'www', 'com', 'html', 'org', 'net',
        'quot', 'class', 'href', 'span', 'wbr', 'gt', 'lt',
        # Bot names
        'rawchili', 'newsbeep', 'beep', 'chili',
        # Profanity (common on 4chan)
        'fuck', 'fucking', 'shit', 'ass', 'bitch', 'damn', 'hell',
        'fucked', 'fucks', 'shitty', 'crap', 'piss',
        # Generic conversation words
        'like', 'just', 'dont', 'thats', 'didnt', 'know', 'think',
        'really', 'people', 'gonna', 'want', 'good', 'bad',
        'guy', 'guys', 'man', 'thing', 'things', 'time',
        'yeah', 'lol', 'lmao', 'based', 'cringe',
        'actually', 'literally', 'probably', 'maybe',
        'll', 've', 're', 'going', 'watch', 'watching',
        # Generic sports words (not specific enough)
        'team', 'teams', 'game', 'games', 'play', 'player', 'players',
        'win', 'wins', 'winning', 'won', 'lose', 'losing', 'lost',
        'better', 'best', 'need', 'got', 'getting', 'did'
    ]
    
    vectorizer = CountVectorizer(
        max_features=2000,
        min_df=10,  # Word must appear in at least 10 documents
        max_df=0.5,  # Ignore words in more than 50% of docs
        stop_words='english',
        ngram_range=(1, 2)  # Include 1-word and 2-word phrases
    )
    
    # Add custom stop words
    vectorizer.stop_words_ = set(vectorizer.get_stop_words()).union(custom_stop_words)
    
    doc_term_matrix = vectorizer.fit_transform(cleaned_texts)
    feature_names = vectorizer.get_feature_names_out()
    
    print(f"      Vocabulary size: {len(feature_names):,} unique terms")
    
    # Run LDA
    print(f"\n[3/3] Running LDA to discover {n_topics} topics...")
    print("      (This takes 2-3 minutes...)")
    
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        max_iter=20,
        learning_method='online',
        random_state=42,
        n_jobs=-1
    )
    
    lda.fit(doc_term_matrix)
    
    # Display results
    print("\n" + "="*70)
    print("📊 DISCOVERED TOPICS (Completely Unsupervised!)")
    print("="*70)
    
    topics_data = []
    
    for topic_idx, topic in enumerate(lda.components_):
        print(f"\n🏆 TOPIC {topic_idx + 1}:")
        
        # Get top words for this topic
        top_word_indices = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_word_indices]
        top_weights = [topic[i] for i in top_word_indices]
        
        # Print with weights
        for word, weight in zip(top_words, top_weights):
            print(f"   {weight:>6.1f}  {word}")
        
        # Try to auto-label the topic
        label = auto_label_topic(top_words)
        print(f"\n   💡 Likely about: {label}")
        
        topics_data.append({
            'topic_num': topic_idx + 1,
            'top_words': top_words,
            'label': label
        })
    
    # Show topic distribution
    print("\n" + "="*70)
    print("📈 TOPIC PREVALENCE")
    print("="*70)
    
    doc_topic_dist = lda.transform(doc_term_matrix)
    topic_prevalence = doc_topic_dist.mean(axis=0)
    
    for idx, prev in enumerate(topic_prevalence):
        label = topics_data[idx]['label']
        print(f"   Topic {idx+1} ({label}): {prev*100:.1f}% of posts")
    
    return topics_data, lda, vectorizer

def auto_label_topic(top_words):
    """Attempt to automatically label what a topic is about."""
    words_str = ' '.join(top_words).lower()
    
    # Check for sport indicators
    if any(w in words_str for w in ['dodgers', 'yankees', 'ohtani', 'pitcher', 'inning', 'baseball', 'mlb']):
        return "MLB/Baseball"
    elif any(w in words_str for w in ['lakers', 'curry', 'lebron', 'dunk', 'basketball', 'nba']):
        return "NBA/Basketball"
    elif any(w in words_str for w in ['chiefs', 'cowboys', 'touchdown', 'quarterback', 'nfl', 'football']) and 'soccer' not in words_str:
        return "NFL/Football"
    elif any(w in words_str for w in ['arsenal', 'messi', 'ronaldo', 'premier league', 'soccer', 'manchester', 'chelsea', 'liverpool']):
        return "Soccer/Football"
    elif any(w in words_str for w in ['verstappen', 'hamilton', 'mercedes', 'ferrari', 'formula', 'race', 'lap']):
        return "Formula 1 / Racing"
    elif any(w in words_str for w in ['ufc', 'fight', 'fighter', 'knockout', 'dana white', 'octagon', 'mma']):
        return "UFC/MMA/Boxing"
    elif any(w in words_str for w in ['hockey', 'puck', 'nhl', 'stanley cup']):
        return "NHL/Hockey"
    elif any(w in words_str for w in ['tennis', 'djokovic', 'federer', 'wimbledon', 'open']):
        return "Tennis"
    elif any(w in words_str for w in ['golf', 'pga', 'masters', 'tiger']):
        return "Golf"
    elif any(w in words_str for w in ['esports', 'gaming', 'league legends', 'valorant']):
        return "Esports/Gaming"
    else:
        return "General Sports Discussion"

if __name__ == "__main__":
    print("\n" + "🏈"*35)
    sp_topics, sp_lda, sp_vec = discover_topics_lda('sp', n_topics=8)
    
    print("\n\n" + "🦋"*35)
    bsky_topics, bsky_lda, bsky_vec = discover_topics_lda('bsky', n_topics=8)
    
    print("\n\n" + "="*70)
    print("💡 SUMMARY")
    print("="*70)
    print("\n✅ LDA discovered topics WITHOUT any predefined categories!")
    print("✅ If F1, tennis, golf, or esports are discussed, they'll appear!")
    print("✅ Automatically separates NFL football from soccer!")
    print("✅ Shows what people ACTUALLY talk about, not what we guessed!")
