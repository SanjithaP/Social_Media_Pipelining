import psycopg2
import pandas as pd
from datetime import datetime, timedelta

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="crawler",
        user="postgres",
        password="cs515"
    )

def get_hourly_activity(platform, start_date, end_date):
    """Get hourly post counts for a platform within date range."""
    conn = get_db_connection()
    
    if platform == 'bsky':
        table = 'posts_bsky'
        where = ""
    else:
        table = 'posts_4chan'
        where = f"AND board_name = '{platform}'"
    
    query = f"""
        SELECT 
            DATE_TRUNC('hour', created_at) as hour,
            COUNT(*) as post_count
        FROM {table}
        WHERE created_at >= '{start_date}'
          AND created_at < '{end_date}'
          {where}
        GROUP BY DATE_TRUNC('hour', created_at)
        ORDER BY hour
    """
    
    df = pd.read_sql(query, conn)
    df['hour'] = pd.to_datetime(df['hour'])
    df['hour_of_day'] = df['hour'].dt.hour
    df['day_of_week'] = df['hour'].dt.dayofweek  # 0=Monday, 6=Sunday
    
    conn.close()
    return df

def get_event_comparison(platform, event_date):
    """
    Compare activity before/during/after a specific event day.
    
    Assumes:
    - BEFORE: 6 hours before event (6am-12pm UTC)
    - DURING: Event time (12pm-6pm UTC) 
    - AFTER: After event (6pm-midnight UTC)
    """
    conn = get_db_connection()
    
    event_start = pd.to_datetime(event_date).replace(hour=0, minute=0, second=0)
    event_end = event_start + timedelta(days=1)
    
    if platform == 'bsky':
        table = 'posts_bsky'
        where = ""
    else:
        table = 'posts_4chan'
        where = f"AND board_name = '{platform}'"
    
    query = f"""
        SELECT 
            CASE 
                WHEN EXTRACT(HOUR FROM created_at) < 12 THEN 'BEFORE'
                WHEN EXTRACT(HOUR FROM created_at) < 18 THEN 'DURING'
                ELSE 'AFTER'
            END as phase,
            COUNT(*) as post_count
        FROM {table}
        WHERE created_at >= '{event_start}'
          AND created_at < '{event_end}'
          {where}
        GROUP BY phase
        ORDER BY phase DESC
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_available_dates(platform):
    """Get date range available in database for a platform."""
    conn = get_db_connection()
    
    if platform == 'bsky':
        table = 'posts_bsky'
        where = ""
    else:
        table = 'posts_4chan'
        where = f"WHERE board_name = '{platform}'"
    
    query = f"""
        SELECT 
            MIN(DATE(created_at)) as min_date,
            MAX(DATE(created_at)) as max_date
        FROM {table}
        {where}
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0]['min_date'], df.iloc[0]['max_date']

if __name__ == "__main__":
    # Test: Get available dates
    print("\n=== Available Data Ranges ===")
    for platform in ['sp', 'bsky']:
        min_d, max_d = get_available_dates(platform)
        print(f"{platform}: {min_d} to {max_d}")
    
    # Test: Event comparison for a Sunday (NFL day)
    print("\n=== Sunday Nov 10, 2024 on /sp/ ===")
    event_data = get_event_comparison('sp', '2024-11-10')
    print(event_data)
    
    # Test: Hourly activity
    print("\n=== Hourly activity Nov 1-7 on /sp/ ===")
    hourly = get_hourly_activity('sp', '2024-11-01', '2024-11-08')
    print(hourly.head(10))
    print(f"\nTotal hours: {len(hourly)}")
