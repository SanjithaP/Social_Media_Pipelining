import os
from pathlib import Path
from dotenv import load_dotenv

# Load ../.env
BASE_DIR = Path(__file__).resolve().parent.parent  # ~/social-pipeline
load_dotenv(BASE_DIR / '.env')

def _split_csv(s: str):
    return [x.strip() for x in (s or '').split(',') if x.strip()]

# --- core ---
DATABASE_URL = os.getenv('DATABASE_URL', 'postgres://postgres:cs515@localhost:5432/crawler')

# --- faktory ---
FAKTORY_URL = os.getenv('FAKTORY_URL', os.getenv('FACTORY_SERVER_URL', 'tcp://:cs515@localhost:7419'))

# --- 4chan ---
BOARDS = _split_csv(os.getenv('BOARDS', 'sp'))
POLL_SECONDS = int(os.getenv('POLL_SECONDS', '60'))
CHAN_BOARDS = os.getenv("CHAN_BOARDS", "sp,pol")

# --- bluesky login ---
BSKY_HANDLE = os.getenv('BSKY_HANDLE', '')
BSKY_APP_PASSWORD = os.getenv('BSKY_APP_PASSWORD', '')

# ===== NEW SPORTS ACTORS (HARDCODED) =====
_BSKY_ACTORS_DEFAULT = (
    "fabriziorom.bsky.social,"
    "tomwfootball.bsky.social,"
    "kitmag.bsky.social,"
    "anfieldrd96.bsky.social,"
    "terracepodcast.bsky.social,"
    "footyshirthvn.bsky.social,"
    "nba.com.bsky.social,"
    "nbaworld.bsky.social,"
    "legionhoops.bsky.social,"
    "hoopsingsider.bsky.social,"
    "howardbeck.bsky.social,"
    "jonbois.bsky.social,"
    "mlb.com.bsky.social,"
    "mlbbluesky.bsky.social,"
    "mets.com.bsky.social,"
    "pirates.com.bsky.social,"
    "yankees.com.bsky.social,"
    "nflgoated.bsky.social,"
    "nflclips.bsky.social,"
    "cfbclips.bsky.social,"
    "minakimes.bsky.social,"
    "pplinsider.bsky.social,"
    "thefsa.bsky.social,"
    "redcornermma.bsky.social,"
    "mmamania.com.web.brid.gy,"
    "boxinghistory.bsky.social,"
    "caposa.bsky.social,"
    "lukethomas.bsky.social,"
    "themmalawyer.bsky.social,"
    "fightgoddess.bsky.social,"
    "remymac.bsky.social,"
    "andymfsw.bsky.social,"
    "statsowar.bsky.social,"
    "awfulannouncing.bsky.social,"
    "theathletic.bsky.social"
)

# try env first, else use our hardcoded list
BSKY_ACTORS = _split_csv(os.getenv("BSKY_ACTORS", _BSKY_ACTORS_DEFAULT))

# --- crawl depth ---
BSKY_HEAD_PAGES = int(os.getenv('BSKY_HEAD_PAGES', '2'))
BSKY_BACKFILL_PAGES = int(os.getenv('BSKY_BACKFILL_PAGES', '0'))
BSKY_MAX_BACKFILL_HOURS = int(os.getenv('BSKY_MAX_BACKFILL_HOURS', '24'))

# --- state dir ---
STATE_DIR = BASE_DIR / 'state'
STATE_DIR.mkdir(parents=True, exist_ok=True)
CHAN_LAST_SEEN_PATH = STATE_DIR / 'chan_last_seen.json'
BSKY_CURSORS_PATH = STATE_DIR / 'bsky_cursors.json'

# --- producer sleep ---
PRODUCER_SLEEP_SECONDS = int(os.getenv("PRODUCER_SLEEP_SECONDS", "60"))
