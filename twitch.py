import asyncio

import pytmi

def msg_is_users_first_message(msg):
    return msg.tags['first-msg'] == 1

def msg_user_is_sub(msg):
    return msg.tags['subscriber'] == 1

def msg_user_is_mod(msg):
    return msg.tags['mod'] == 1

def msg_user_is_broadcaster(msg):
    return 'broadcaster' in str(msg.tags['badges'])

def process_message(msg):

   # print(msg.tags)

    # a broadcaster user
    #{'badge-info': None, 'badges': 'broadcaster/1,premium/1', 'client-nonce': '###', 'color': '#5F9EA0', 'display-name': 'xyz', 'emotes': None, 'first-msg': 0, 'flags': None, 'id': '###', 'mod': 0, 'room-id': ###, 'subscriber': 0, 'tmi-sent-ts': 1640668543093, 'turbo': 0, 'user-id': ###, 'user-type': None}
    
    # a mod user
    #{'badge-info': None, 'badges': 'moderator/1', 'client-nonce': '###', 'color': '#5F9EA0', 'display-name': 'xyz', 'emotes': None, 'first-msg': 0, 'flags': None, 'id': '', 'mod': 1, 'room-id': ###, 'subscriber': 0, 'tmi-sent-ts': 1640668692424, 'turbo': 0, 'user-id': ###, 'user-type': 'mod'}
    
    is_broadcaster = msg_user_is_broadcaster(msg)
    is_mod = msg_user_is_mod(msg)
    is_sub =  msg_user_is_sub(msg)

    text = msg.command.split(" :", 1)[1]
    name = msg.tags.get("display-name", "anon")

    return name, text, is_broadcaster, is_mod, is_sub


async def message_handler(client):
    
    while True:
        await asyncio.sleep(1)
        try:
            raw = await client.get_privmsg()
            msg = pytmi.TmiMessage(raw.lstrip())

            if msg == None or not "PRIVMSG" in msg.command:
                continue

            yield process_message(msg)
           
            del raw
            del msg
        except OSError:
            raise
        except Exception:
            continue


async def main(channel: str) -> None:
    client = pytmi.TmiClient(ssl=False)

    await client.login_anonymous()
    await client.join(channel)

    async for result in message_handler(client):
        name, text, is_broadcaster, is_mod, is_sub = result
        print(name, text, is_broadcaster, is_mod, is_sub)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main("bubbletelevision"))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())  # see: https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.shutdown_asyncgens
        loop.close()
  