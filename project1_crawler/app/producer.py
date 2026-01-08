#!/usr/bin/env python3
import os
import time
from faktory import Client

# try config.py first (your repo)
try:
    from config import (
        CHAN_BOARDS as CFG_CHAN_BOARDS,
        BSKY_ACTORS as CFG_BSKY_ACTORS,
        PRODUCER_SLEEP_SECONDS as CFG_SLEEP,
    )
except Exception:
    CFG_CHAN_BOARDS = "sp,pol"
    CFG_BSKY_ACTORS = ""
    CFG_SLEEP = 60


def _split_csv(val: str):
    return [x.strip() for x in val.split(",") if x.strip()]


def main():
    # boards
    env_boards = os.getenv("CHAN_BOARDS")
    if env_boards:
        chan_boards = _split_csv(env_boards)
    else:
        chan_boards = _split_csv(CFG_CHAN_BOARDS)

    # actors
    env_actors = os.getenv("BSKY_ACTORS")
    if env_actors:
        bsky_actors = _split_csv(env_actors)
    else:
        bsky_actors = _split_csv(CFG_BSKY_ACTORS)

    sleep_seconds = int(os.getenv("PRODUCER_SLEEP_SECONDS", str(CFG_SLEEP)))

    while True:
        print("PRODUCER: boards=", chan_boards, "actors=", bsky_actors, "sleep=", sleep_seconds, flush=True)
        # THIS is the faktory client your worker is using too
        with Client() as client:
            for board in chan_boards:
                client.queue("crawl_board", args=[board])

            for actor in bsky_actors:
                client.queue("crawl_bsky_actor", args=[actor])

        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()
