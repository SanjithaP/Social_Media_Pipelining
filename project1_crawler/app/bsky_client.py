from typing import Optional, Tuple, List
from atproto import Client

# Small wrapper so worker code stays clean

def get_bsky_client(handle: str, app_password: str) -> Client:
    client = Client()
    client.login(handle, app_password)
    return client

def get_author_feed(client: Client, actor: str, cursor: Optional[str] = None) -> Tuple[List[object], Optional[str]]:
    """
    Returns (feed_items, next_cursor)
    """
    resp = client.app.bsky.feed.get_author_feed({'actor': actor, 'cursor': cursor, 'limit': 100})
    # resp.feed is a list of feed items (Pydantic models)
    next_cursor = getattr(resp, 'cursor', None)
    return list(resp.feed or []), next_cursor

def as_primitive(obj):
    """Return a JSON-serializable structure for Pydantic models."""
    if obj is None:
        return None
    # atproto models are Pydantic v2 models
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    # fallback
    try:
        return obj.__dict__
    except Exception:
        return str(obj)
