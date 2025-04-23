# Extends WebSocketClient to automatically pass JSON messages...abs

import json
from .client import WebSocketClient

class JSONwsClient(WebsocketClient):

    def send(self, obj):
        data = json.dumps(obj)
        super.send(data)

    def recv(self, default=None):
        data = super.recv()
        try:
            return json.loads(data)
        except Exception as ex:
            return default
