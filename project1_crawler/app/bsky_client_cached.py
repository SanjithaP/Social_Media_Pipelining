import os
import time
from atproto_client import Client

# we still want to reuse the helper fns from the original file
# (these are the ones your worker already uses)
from bsky_client import get_author_feed, as_primitive

# read creds from env
BSKY_HANDLE = os.getenv("BSKY_HANDLE")
BSKY_APP_PASSWORD = os.getenv("BSKY_APP_PASSWORD")

# global cached client
_CACHED_CLIENT = None

def get_bsky_client(handle: str = None, app_password: str = None) -> Client:
    """
    Return ONE shared, logged-in Bluesky client.
    We login once, then reuse, so we don't spam /createSession and hit 429.
    """
    global _CACHED_CLIENT

    if _CACHED_CLIENT is not None:
        return _CACHED_CLIENT

    handle = handle or BSKY_HANDLE
    app_password = app_password or BSKY_APP_PASSWORD

    if not handle or not app_password:
        raise RuntimeError("BSKY_HANDLE / BSKY_APP_PASSWORD not set in env")

    last_exc = None
    # a few retries just in case
    for _ in range(5):
        try:
            client = Client()
            client.login(handle, app_password)
            _CACHED_CLIENT = client
            return _CACHED_CLIENT
        except Exception as e:
            last_exc = e
            time.sleep(2)

    raise RuntimeError(f"Could not login to Bluesky after retries: {last_exc}")
