from lib.database import Database
from lib.general.filters import Channel
from lib.general.events import Event
from lib.general.router import Router
from lib.logger import main_logger
from lib.post_assistant import Post
from lib.utils.check_time_interval import is_night, next_datetime_from_time
from lib.utils.get_exception import get_exception
from lib.utils.telethon_utils import send_post

router = Router(lambda: Channel(exclude_networks_channel=True))


# TODO: Collect users statistic (likes, view)

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
        # TODO: Somehow resolve case with two similar posts at the same time
        await db.post_assistant.check_channel_message(post)
        if not post.successfully_checked:
            main_logger.error(f"Post assistant failed accomplish task.")
        else:
            main_logger.info(f"Brief info: {post.brief_information}, meet_requirements: {post.meet_requirements}")
            if post.meet_requirements:
                if not db.params.is_night_posting and is_night(db):
                    main_logger.info(f"Send scheduled message because of night.")
                    await send_post(db, post, next_datetime_from_time(db.params.night_interval[1]))
                else:
                    main_logger.info(f"Send message now.")
                    await send_post(db, post)
    except Exception as e:
        main_logger.error(f"Error reading message: {get_exception(e)}")
