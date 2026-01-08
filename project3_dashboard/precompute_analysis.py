"""
Pre-compute all analysis results and save to JSON files.
Run this ONCE, then the dashboard loads instantly!
"""
import json
from feature_lda_topics import discover_topics_lda, load_platform_text
from feature_event_spike import get_event_comparison
from feature_media_engagement import get_media_engagement_4chan, get_media_engagement_bsky
import re

print("="*70)
print("PRE-COMPUTING ALL ANALYSIS RESULTS")
print("This takes 5-10 minutes, but only needs to run ONCE!")
print("="*70)

results = {}

# ============================================
# Feature 3: LDA Topics for /sp/
# ============================================
print("\n[1/4] Running LDA analysis on /sp/...")
sp_topics, sp_lda, sp_vec = discover_topics_lda('sp', n_topics=6, n_top_words=10)

# Calculate prevalence
texts = load_platform_text('sp', limit=50000)
cleaned_texts = [re.sub(r'https?://\S+', '', text) for text in texts if len(text) > 20]
doc_term_matrix = sp_vec.transform(cleaned_texts)
doc_topic_dist = sp_lda.transform(doc_term_matrix)
topic_prevalence = doc_topic_dist.mean(axis=0)

sp_results = []
for i, topic_info in enumerate(sp_topics):
    sp_results.append({
        'label': topic_info['label'],
        'top_words': topic_info['top_words'],
        'prevalence': float(topic_prevalence[i])
    })

sp_results.sort(key=lambda x: x['prevalence'], reverse=True)
results['sp_topics'] = sp_results

print(f"   ✅ Found {len(sp_results)} topics for /sp/")

# ============================================
# Feature 3: LDA Topics for Bluesky
# ============================================
print("\n[2/4] Running LDA analysis on Bluesky...")
bsky_topics, bsky_lda, bsky_vec = discover_topics_lda('bsky', n_topics=6, n_top_words=10)

# Calculate prevalence
texts = load_platform_text('bsky', limit=50000)
cleaned_texts = [re.sub(r'https?://\S+', '', text) for text in texts if len(text) > 20]
doc_term_matrix = bsky_vec.transform(cleaned_texts)
doc_topic_dist = bsky_lda.transform(doc_term_matrix)
topic_prevalence = doc_topic_dist.mean(axis=0)

bsky_results = []
for i, topic_info in enumerate(bsky_topics):
    bsky_results.append({
        'label': topic_info['label'],
        'top_words': topic_info['top_words'],
        'prevalence': float(topic_prevalence[i])
    })

bsky_results.sort(key=lambda x: x['prevalence'], reverse=True)
results['bsky_topics'] = bsky_results

print(f"   ✅ Found {len(bsky_results)} topics for Bluesky")

# ============================================
# Feature 2: Media Engagement
# ============================================
print("\n[3/4] Computing media engagement stats...")

results['sp_media'] = get_media_engagement_4chan('sp').to_dict('records')
results['pol_media'] = get_media_engagement_4chan('pol').to_dict('records')
results['bsky_media'] = get_media_engagement_bsky().to_dict('records')

print("   ✅ Media engagement computed for all platforms")

# ============================================
# Feature 1: Event Examples (pre-compute a few dates)
# ============================================
print("\n[4/4] Computing event examples...")

event_dates = {
    'sp': ['2025-11-02', '2025-11-10'],  # Saturdays/Sundays
    'bsky': ['2025-11-03', '2025-11-10']
}

results['event_examples'] = {}
for platform, dates in event_dates.items():
    results['event_examples'][platform] = {}
    for date in dates:
        df = get_event_comparison(platform, date)
        results['event_examples'][platform][date] = df.to_dict('records')

print("   ✅ Event examples pre-computed")

# ============================================
# Save to JSON
# ============================================
print("\n" + "="*70)
print("SAVING RESULTS...")

with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("✅ All results saved to analysis_results.json")
print("="*70)
print("\nDashboard will now load INSTANTLY!")
print("File size:", round(len(json.dumps(results)) / 1024, 1), "KB")
