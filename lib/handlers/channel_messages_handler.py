# @client.on(events.NewMessage)
# async def my_event_handler(event: NewMessage.Event):
#     chat = await event.get_chat()
#
#     try:
#         if chat.username == admin:
#             event.answer('1')
#             return await commands_handler(event.message.text)
#     except Exception as e:
#         ...
#
#     try:
#         logger.info(f"New message in channel '{chat.title}'")
#         text = event.text.strip()
#         if not text:
#             logger.info(f"Post message is empty")
#             return
#
#         if not is_watching:
#             logger.info(f"Watching disabled, nothing to do.")
#             return
#
#         success, meet_requirements, brief_information = await post_assistant.check_channel_message(text)
#         if not success:
#             ...
#             # await notify('Ошибочка вышла, и по ходу дела не очень хорошая. Проблема в этом посте')
#             # await client.forward_messages(admin, event.message)
#         else:
#             logger.info(f"Brief info: {brief_information}, meet_requirements: {meet_requirements}")
#             if meet_requirements:
#                 await client.forward_messages(neural_networks_channel, event.message)
#                 await client.send_message(
#                     neural_networks_channel,
#                     f'Summary of the previous post: {brief_information}'
#                 )
#     except Exception as e:
#         logger.warning("Error reading message")