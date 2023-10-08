import asyncio
import json

from attrdictionary import AttrDict
import websockets

from ..hook import hook
from . import exception

try:
    from misspy_core_fast import ws

    use_fast = True # method redirect
except:
    pass

class MiWS:
    def __init__(self, address, i, ssl=True) -> None:
        self.i = i
        self.address = address
        self.ssl = ssl
        if use_fast:
            self.miws = ws.MiWS(self.address, self.i, self.ssl)

    async def ws_handler(self):
        if use_fast:
            self.connection = await self.miws.ws_handler.connection()
        else:
            try:
                procotol = "ws://"
                if self.ssl:
                    procotol = "wss://"
                async with websockets.connect(
                    f"{procotol}{self.address}/streaming?i={self.i}"
                ) as self.connection:
                    try:
                        await hook.functions["ready"]()
                    except KeyError:
                        pass
                    while True:
                        try:
                            recv = json.loads(await self.connection.recv())
                        except AttributeError:
                            pass
                        try:
                            if recv["type"] == "channel":
                                if recv["body"]["type"] == "note":
                                    await hook.functions[recv["body"]["type"]](
                                        AttrDict(recv["body"]["body"])
                                    )
                                elif recv["body"]["type"] == "notification":
                                    await hook.functions[recv["body"]["body"]["type"]](
                                        AttrDict(recv["body"]["body"])
                                    )
                                elif recv["body"]["type"] == "follow":
                                    await hook.functions[recv["body"]["type"]](
                                        AttrDict(recv["body"]["body"])
                                    )
                                elif recv["body"]["type"] == "followed":
                                    await hook.functions[recv["body"]["type"]](
                                        AttrDict(recv["body"]["body"])
                                    )
                                elif recv["type"] == "noteUpdated":
                                    await hook.functions[recv["body"]["type"]](
                                        AttrDict(recv["body"])
                                    )
                                else:
                                    await hook.functions[recv["body"]["type"]](
                                        AttrDict(recv["body"])
                                    )
                        except KeyError:
                            pass
            except Exception as e:
                raise exception.WebsocketError(e)