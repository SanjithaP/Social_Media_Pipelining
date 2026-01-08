import os
import psycopg2

DSN = os.getenv("PG_DSN", "dbname=crawler user=postgres host=timescaledb")

def _get_conn():
    return psycopg2.connect(DSN)

def insert_sp(posts):
    if not posts:
        return 0
    conn = _get_conn()
    cur = conn.cursor()
    for p in posts:
        cur.execute(
            """
            INSERT INTO posts_4chan_sp (board, thread_id, post_id, author, content, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (
                p["board"],
                p.get("thread_id"),
                p["post_id"],
                p.get("author"),
                p.get("content"),
                p["created_at"],
            ),
        )
    conn.commit()
    cur.close()
    conn.close()
    return len(posts)

def insert_pol(posts):
    if not posts:
        return 0
    conn = _get_conn()
    cur = conn.cursor()
    for p in posts:
        cur.execute(
            """
            INSERT INTO posts_4chan_pol (board, thread_id, post_id, author, content, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (
                p["board"],
                p.get("thread_id"),
                p["post_id"],
                p.get("author"),
                p.get("content"),
                p["created_at"],
            ),
        )
    conn.commit()
    cur.close()
    conn.close()
    return len(posts)
