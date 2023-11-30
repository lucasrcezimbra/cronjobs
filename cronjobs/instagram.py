import sys
from pathlib import Path

from decouple import config
from instagrapi import Client
from loguru import logger


class AlreadyExists(Exception):
    pass


SESSION_ID = config("INSTAGRAM_SESSION_ID")


def run(username):
    logger.info("Starting...")
    c = Client()
    assert c.login_by_sessionid(SESSION_ID)
    logger.info(f"Logged. Getting user {username}")
    user_id = c.user_id_from_username(username)
    logger.info(f"Getting stories - user_id: {user_id}")
    stories = c.user_stories(user_id)
    path = Path("data") / Path(username)
    dbpath = path / "db.jsonl"

    try:
        path.mkdir(parents=True)
        logger.info(f"{path} created")
    except FileExistsError:
        logger.info(f"{path} exists")
        pass

    dbpath.touch()

    for s in stories:
        try:
            with open(dbpath) as f:
                if s.pk in f.read():
                    raise AlreadyExists

            with open(dbpath, "a") as f:
                f.write(s.json() + "\n")

            url = s.thumbnail_url if s.media_type == 1 else s.video_url
            c.story_download_by_url(url, s.pk, path)
            logger.info(f"{s.pk} new")
        except AlreadyExists:
            logger.info(f"{s.pk} exists")
            continue


if __name__ == "__main__":
    run(sys.argv[1])
