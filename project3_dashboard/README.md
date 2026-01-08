# CS415 Project 3: Social Media Analytics Dashboard

## Student Information
**Name:** Ilaya Raj Mohan
**Project:** Interactive Network Dashboard for Social Media Analysis

## Overview
Network-based interactive dashboard analyzing 4.2M+ posts from 4chan (/sp/, /pol/) and Bluesky, featuring three main analytical components with parameter variation.

## Setup Instructions
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure PostgreSQL database is running with crawler data

3. Run the application:
```bash
python3 app_flask_fast.py
```

4. Access dashboard at: http://localhost:5000

## Features
### Feature 1: Event Spike Analysis
Analyzes posting activity patterns before, during, and after live sporting events. Users can select different platforms and event dates to see how user behavior changes.

### Feature 2: Media vs Text Engagement  
Compares engagement metrics between posts with media (images/videos) versus text-only posts. Reveals platform-specific preferences.

### Feature 3: Topic Distribution
Uses Latent Dirichlet Allocation (LDA, k=6) to identify dominant sports discussion topics across platforms. Shows distribution of MLB, NBA, NFL, soccer, and other sports coverage.

## Data Summary
- **Analysis Period:** November 1-14, 2025
- **Total Posts:** 4.2M (live crawling continues)
- **Platforms:** 
  - 4chan /sp/: 901K posts
  - 4chan /pol/: 3.1M posts  
  - Bluesky: 170K posts

## Technology Stack
- **Backend:** Flask, PostgreSQL with TimescaleDB extension
- **Frontend:** Plotly.js, vanilla JavaScript, HTML5/CSS3
- **Analysis:** scikit-learn (LDA), pandas, BeautifulSoup

## File Structure
```
app_flask_fast.py           - Main Flask application
templates/index.html        - Interactive dashboard frontend
analysis_results.json       - Pre-computed analysis results
precompute_analysis.py      - Script to regenerate analysis
feature_event_spike.py      - Event spike analysis logic
feature_media_engagement.py - Media engagement comparison
feature_lda_topics.py       - LDA topic modeling
utils/db_utils.py          - Database utility functions
```

## How to Regenerate Analysis
If you need to recompute the analysis results:
```bash
python3 precompute_analysis.py
```
Note: This takes 5-10 minutes and requires database access.
