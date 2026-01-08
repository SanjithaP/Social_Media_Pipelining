# Sports Social Media Analytics: 4chan vs Bluesky

An interactive analytics dashboard analyzing 4.2 million sports-related social media posts from 4chan and Bluesky to uncover platform-specific patterns in sports discourse.

## Project Overview

This project explores how different social media platforms shape sports discussions by comparing anonymous imageboards (4chan) with identity-based networks (Bluesky). Using unsupervised machine learning and interactive visualizations, the system answers three key research questions:

1. **What sports topics dominate each platform?**
2. **How does media content affect user engagement?**
3. **How do posting patterns change around sporting events?**

## System Design

The project has three main parts:

**Data Collection** - Continuous crawlers using Faktory job queue
- Producer queues crawl jobs every 60 seconds
- Workers fetch posts from 4chan API and Bluesky AT Protocol
- Everything stored in PostgreSQL with JSONB for flexibility

**Analysis Pipeline** - Pre-computation for speed
- LDA topic modeling on 50,000 sampled posts per platform
- Engagement metrics (thread size for 4chan, likes for Bluesky)
- Temporal analysis in 6-hour windows
- Results cached in analysis_results.json (47KB)

**Web Dashboard** - Flask backend + vanilla JavaScript frontend
- Network graph visualization with custom physics engine
- Interactive charts using Plotly.js
- 6 REST API endpoints serving pre-computed data
- Live stats from database queries

## Features

### Interactive Network Visualization
- Force-directed graph interface for exploring relationships between platforms, features, and insights
- Physics-based node positioning with spring forces and repulsion
- Click-to-explore navigation pattern
- Custom HTML5 Canvas rendering with 60 FPS animations

### Topic Discovery (LDA)
- Unsupervised Latent Dirichlet Allocation topic modeling
- Automated topic labeling based on word distributions
- Platform-specific topic prevalence analysis
- Discovers 6 topics per platform from 50,000 sampled posts

### Engagement Analytics
- Cross-platform engagement comparison (thread size vs. likes)
- Media vs. text-only content performance analysis
- Statistical aggregations with PostgreSQL queries
- Platform-specific engagement metric definitions

### Temporal Pattern Analysis
- Event-based posting pattern detection
- 6-hour window segmentation (before/during/after games)
- Time-series visualization with Plotly.js
- Hourly and daily aggregation views

### Live Statistics Dashboard
- Real-time crawler status monitoring
- Posts per hour rate calculation
- Platform-specific post counts
- Last-seen timestamps for data freshness

## Dataset

- **4chan Data**: 3.8M posts from /sp/ (sports) and /pol/ (politics) boards
- **Bluesky Data**: 400K posts from manually-curated sports communities
- **Collection Period**: November 1-14, 2024
- **Storage**: PostgreSQL with JSONB for flexible schema

### Sampling Strategy

**4chan**: Comprehensive board-wide collection
- All threads from /sp/ and /pol/ boards
- Every post in each thread captured
- No sampling bias - complete board coverage

**Bluesky**: Manual seed-based network sampling
- Manually selected 5-6 highly active sports accounts per sport
- Followed their author feeds and networks
- **Limitation**: Represents specific communities, not entire platform
- Documented sampling bias in research findings

## Technology Stack

### Data Collection Layer
- **Faktory (1.0.0)**: Job queue system for distributed crawling
- **Python atproto (0.0.51)**: Official Bluesky AT Protocol client
- **Requests (2.32.3)**: HTTP library for 4chan API calls
- **python-dotenv (1.0.1)**: Environment configuration management

### Backend & Analysis
- **Flask (3.0.0)**: Lightweight web framework
- **Flask-CORS (4.0.0)**: Cross-origin resource sharing
- **PostgreSQL**: Primary database with JSONB support
- **psycopg2-binary (2.9.9)**: PostgreSQL adapter
- **pandas (2.1.3)**: Data manipulation and analysis
- **scikit-learn (1.3.2)**: LDA topic modeling
- **BeautifulSoup4 (4.12.2)**: HTML parsing and text extraction

### Frontend
- **Vanilla JavaScript**: No framework dependencies for maximum control
- **Plotly.js (2.27.0)**: Interactive charts and visualizations
- **HTML5 Canvas**: Custom network graph rendering
- **CSS3**: Modern styling with backdrop-filter effects


## Project Structure

```
social-media-analytics/
│
├── project1_crawler/              # Data Collection System
│   ├── app/
│   │   ├── producer.py           # Job queue producer (Faktory)
│   │   ├── worker.py             # Crawling worker pool
│   │   ├── chan_client.py        # 4chan API wrapper
│   │   ├── bsky_client.py        # Bluesky AT Protocol client
│   │   ├── bsky_client_cached.py # Cached version with state
│   │   ├── db.py                 # Database operations
│   │   ├── db_4chan_split.py     # 4chan-specific DB logic
│   │   ├── state.py              # Crawler state management
│   │   ├── config.py             # Configuration settings
│   │   ├── logutil.py            # Logging utilities
│   │   ├── run_producer_service.py # Producer service runner
│   │   └── requirements.txt      # Crawler dependencies
│   └── state/
│       ├── chan_last_seen.json   # 4chan crawl state
│       └── bsky_cursors.json     # Bluesky pagination state
│
├── project2_analysis/             # Statistical Analysis Scripts
│   ├── figs.py                   # Figure generation
│   └── score_perspective.py      # Perspective API analysis
│
├── project3_dashboard/            # Web Dashboard
│   ├── app_flask_fast.py         # Flask application (main entry)
│   ├── precompute_analysis.py    # Pre-computation pipeline
│   ├── analysis_results.json     # Cached analysis (47KB)
│   ├── feature_lda_topics.py     # LDA topic modeling
│   ├── feature_media_engagement.py # Media vs text analysis
│   ├── feature_event_spike.py    # Temporal pattern detection
│   ├── templates/
│   │   └── index.html            # Main dashboard UI (1312 lines)
│   ├── utils/
│   │   └── db_utils.py           # Database helpers
│   ├── requirements.txt          # Dashboard dependencies
│   ├── README.md                 # Dashboard documentation
│   ├── CREDITS.md                # Attribution
│   └── HONESTY.md                # Academic integrity statement
│
├── README.md                      # This file
└── LICENSE                        # MIT License
```
## Performance Optimizations

1. **Pre-computation**: LDA analysis runs once, results cached in JSON (47KB)
2. **Database Indexing**: Time-based and board-based indexes for fast queries
3. **Sampling Strategy**: 50,000 random posts per platform for LDA (vs. full dataset)
4. **Frontend Caching**: API results stored in browser memory
5. **Aggregated Time Windows**: Daily rollups for overview, hourly for detail

## Key Learnings

### Technical Insights
- Pre-computation vs. on-demand is a fundamental UX trade-off
- JSONB in PostgreSQL provides NoSQL flexibility with SQL querying power
- Force-directed layouts require careful tuning of spring constants and damping

### Research Insights
- Sampling bias is unavoidable in real-world data collection
- Platform architecture fundamentally shapes what "engagement" means
- Temporal patterns can't be separated from collection window effects

### Development Insights
- Interactive visualizations aren't just flashy—they enable data exploration
- Documentation of limitations is as important as showcasing results
- User testing reveals UX issues invisible to developers



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## References

- Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. *Journal of Machine Learning Research*, 3, 993-1022.
- 4chan API Documentation: https://github.com/4chan/4chan-API
- Bluesky AT Protocol: https://atproto.com/


**Note**: This project was developed for educational purposes as part of CS 515 - Data Mining coursework at Binghamton University. The analysis represents a specific time window and sampling methodology, and findings should be interpreted within these constraints.


