import psycopg2
from psycopg2.extras import Json
from typing import List, Dict, Any
from config import DATABASE_URL

def get_conn(url: str = DATABASE_URL):
    return psycopg2.connect(url)

def insert_4chan_posts(conn, rows: List[Dict[str, Any]]) -> int:
    """
    rows = [{
        "board_name": str,
        "thread_number": int,
        "post_number": int,
        "created_at": datetime,
        "data": dict,
        "has_media": bool,
    }, ...]
    """
    if not rows:
        return 0

    # wrap each row's "data" dict so psycopg2 can send it to jsonb
    db_rows = []
    for r in rows:
        db_rows.append({
            "board_name":   r["board_name"],
            "thread_number": r["thread_number"],
            "post_number":   r["post_number"],
            "created_at":    r["created_at"],
            "data":          Json(r["data"]),
            "has_media":     r["has_media"],
        })

    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO posts_4chan
            (board_name, thread_number, post_number, created_at, data, has_media)
        VALUES
            (%(board_name)s, %(thread_number)s, %(post_number)s,
             %(created_at)s, %(data)s, %(has_media)s)
        ON CONFLICT (board_name, thread_number, post_number, created_at)
        DO NOTHING
        """,
        db_rows,
    )
    inserted = cur.rowcount
    conn.commit()
    cur.close()
    return inserted

def insert_bsky_posts(conn, rows: List[Dict[str, Any]]) -> int:
    """
    rows = [{
        "actor": str,
        "uri": str,
        "created_at": datetime,
        "data": dict,
        "stance": str|None,
        "like_count": int|None,
        "repost_count": int|None,
        "has_media": bool|None,
    }, ...]
    """
    if not rows:
        return 0

    # wrap JSON field
    db_rows = []
    for r in rows:
        db_rows.append({
            "actor":         r["actor"],
            "uri":           r["uri"],
            "created_at":    r["created_at"],
            "data":          Json(r["data"]),
            "stance":        r["stance"],
            "like_count":    r["like_count"],
            "repost_count":  r["repost_count"],
            "has_media":     r["has_media"],
        })

    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO posts_bsky
            (actor, uri, created_at, data,
             stance, like_count, repost_count, has_media)
        VALUES
            (%(actor)s, %(uri)s, %(created_at)s, %(data)s,
             %(stance)s, %(like_count)s, %(repost_count)s, %(has_media)s)
        ON CONFLICT (uri, created_at)
        DO NOTHING
        """,
        db_rows,
    )
    inserted = cur.rowcount
    conn.commit()
    cur.close()
    return inserted
