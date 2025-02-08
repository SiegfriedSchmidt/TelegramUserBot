from lib.database import Database
from lib.general.filters import Channel
from lib.general.events import Event
from lib.general.router import Router
from lib.logger import logger
from lib.utils.get_exception import get_exception

router = Router(lambda: Channel())


@router()
async def my_event_handler(event: Event, db: Database):
    try:
        chat = await event.get_chat()
        logger.info(f"New message in channel '{chat.title}'")
        text = event.message.text.strip()
        if not text:
            logger.info(f"Post message is empty")
            return

        if not db.is_posting:
            logger.info(f"Posting disabled, nothing to do.")
            return

        # success, meet_requirements, brief_information = await db.post_assistant.check_channel_message(text)
        success, meet_requirements, brief_information = [True, True, 'SUMMARY']
        if not success:
            logger.error(f"Post assistant cannot accomplish task.")
        else:
            logger.info(f"Brief info: {brief_information}, meet_requirements: {meet_requirements}")
            if meet_requirements:
                await db.client.forward_messages(db.neural_networks_channel, event.message)
                await db.client.send_message(
                    db.neural_networks_channel,
                    f'Summary of the previous post: {brief_information}'
                )
    except Exception as e:
        logger.error(f"Error reading message: {get_exception(e)}")
