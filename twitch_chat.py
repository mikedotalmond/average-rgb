import asyncio
import threading
import pytmi

class TwitchChat:

    loop = None
    channel_name: str = None
    client: pytmi.TmiClient = None
    current_message: pytmi.TmiMessage = None

    def __init__(self, channel_name='bubbletelevision', on_message=None):
        self.channel_name = channel_name
        self.client = pytmi.TmiClient(ssl=False)
        self.on_message = on_message

    #
    def start(self):
        self.stopped = False
        t = threading.Thread(target=self._start_loop, args=())
        t.daemon = True
        t.start()
        return self

    #
    def stop(self):
        self.stopped = True
        if self.loop is not None:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
            del self.loop

    #
    def _start_loop(self):
        self.loop = asyncio.new_event_loop()
        try:
            self.loop.run_until_complete(self._run())
        finally:
            self.stop()

    #
    async def _run(self):

        await self.client.login_anonymous()
        await self.client.join(self.channel_name)

        async for result in self._message_handler():
            if self.on_message is not None:
                self.on_message(result)
            else:
                print(result)
            
    #
    async def _message_handler(self):
        
        while not self.stopped:

            await asyncio.sleep(1)
            try:
                raw = await self.client.get_privmsg()
                msg = pytmi.TmiMessage(raw.lstrip())

                if msg == None or not "PRIVMSG" in msg.command:
                    continue

                yield self._process_message(msg)

                del raw
                del msg
            except OSError:
                raise
            except Exception:
                continue

    """
    Process incoming message data
    returns - tuple (name:str, text:str, is_broadcaster:bool, is_mod:bool, is_sub:bool)
    """
    def _process_message(self, msg: pytmi.TmiMessage):

        # print(msg.tags)
        # a broadcaster user
        #{'badge-info': None, 'badges': 'broadcaster/1,premium/1', 'client-nonce': '###', 'color': '#5F9EA0', 'display-name': 'xyz', 'emotes': None, 'first-msg': 0, 'flags': None, 'id': '###', 'mod': 0, 'room-id': ###, 'subscriber': 0, 'tmi-sent-ts': 1640668543093, 'turbo': 0, 'user-id': ###, 'user-type': None}
        
        # a mod user
        #{'badge-info': None, 'badges': 'moderator/1', 'client-nonce': '###', 'color': '#5F9EA0', 'display-name': 'xyz', 'emotes': None, 'first-msg': 0, 'flags': None, 'id': '', 'mod': 1, 'room-id': ###, 'subscriber': 0, 'tmi-sent-ts': 1640668692424, 'turbo': 0, 'user-id': ###, 'user-type': 'mod'}
        

        is_broadcaster = self.message_user_is_broadcaster(msg)
        is_mod = self.message_user_is_mod(msg)
        is_sub =  self.message_user_is_sub(msg)

        text = msg.command.split(" :", 1)[1]
        name = msg.tags.get("display-name", "anon")

        self.current_message = msg

        return name, text, is_broadcaster, is_mod, is_sub


    def message_is_first(self, msg: pytmi.TmiMessage):
        return msg.tags.get('first-msg') == 1

    def message_user_is_sub(self, msg: pytmi.TmiMessage):
        return msg.tags.get('subscriber') == 1

    def message_user_is_mod(self, msg: pytmi.TmiMessage):
        return msg.tags.get('mod') == 1

    def message_user_is_broadcaster(self, msg: pytmi.TmiMessage):
        return 'broadcaster' in msg.tags.get('badges')
