from lib.database import Database
from lib.general.filters import Channel
from lib.general.events import Event
from lib.general.router import Router
from lib.logger import main_logger
from lib.post_assistant import Post
from lib.utils.check_time_interval import is_night
from lib.utils.get_exception import get_exception
from lib.utils.telethon_utils import send_post

router = Router(lambda: Channel(exclude_networks_channel=False))


async def check_posting(db: Database):
    if not db.params.is_night_posting and is_night(db):
        main_logger.info(f"At night we don't posting!")
        return False

    if not db.params.is_posting:
        main_logger.info(f"Posting disabled, nothing to forward.")
        return False

    return True


@router()
async def my_event_handler(event: Event, db: Database):
    try:
        chat = await event.get_chat()
        main_logger.info(f"New message in channel '{chat.title}'")
        text = event.message.text.strip()
        if not text:
            main_logger.info(f"Post message is empty")
            return

        if not db.params.is_posting and not db.params.is_pending_posting:
            main_logger.info(f"Posting and pending posting disabled, nothing to do.")
            return

        post = Post(event.message)
        await db.post_assistant.check_channel_message(post)
        if not post.successfully_checked:
            main_logger.error(f"Post assistant failed accomplish task.")
        else:
            main_logger.info(f"Brief info: {post.brief_information}, meet_requirements: {post.meet_requirements}")
            if post.meet_requirements:
                posting = await check_posting(db)
                if not posting:
                    if db.params.is_pending_posting:
                        main_logger.info("Pending posting enabled, saving post for the future.")
                        db.params.pending_posts.append(post)
                    return

                await send_post(db, post)
    except Exception as e:
        main_logger.error(f"Error reading message: {get_exception(e)}")
