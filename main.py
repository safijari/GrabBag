import os

from click import get_app_dir
import decky_plugin
from pathlib import Path
import json
import os
import subprocess
import sys
import shutil
import time
import asyncio
from threading import Thread

import sys
sys.path.append(os.path.dirname(__file__))

from py_backend import keyboard
from py_backend.websocket_server import WebsocketServer

clients = {}

def new_client(client, server):
    decky_plugin.logger.info("New client connected and was given id %d" % client['id'])
    server.send_message()
    clients[client["id"]] = client
    server.send_message_to_all("Hey all, a new client has joined us")

# Called for every client disconnecting
def client_left(client, server):
    cid = client["id"]
    try:
        del clients[cid]
        decky_plugin.logger.info("Client(%d) disconnected" % client['id'])
    except Exception:
        pass

# Called when a client sends a message
def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200]+'..'
    decky_plugin.logger.info("Client(%d) said: %s" % (client['id'], message))

def indicate(server):
    for client in clients.values():
        server.send_message(client, "pressed")
    decky_plugin.logger.info("happened")
    with open("/tmp/happened", "w") as ff:
        ff.write("happened")

def keyboard_listener(server):
    keyboard.add_hotkey('ctrl+1', lambda: indicate(server))
    decky_plugin.logger.info("keyboard listener online")
    keyboard.wait()

def ws_server(server):
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    decky_plugin.logger.info("ws online as well")
    server.run_forever()

class Plugin:
    _thread = None
    _thread_ws = None
    async def _main(self):
        try:
            PORT=9371
            server = WebsocketServer(port = PORT)
            Plugin._thread = Thread(target=lambda: keyboard_listener(server))
            Plugin._thread.daemon = True
            Plugin._thread.start()
            Plugin._thread_ws = Thread(target=lambda: ws_server(server))
            Plugin._thread_ws.daemon = True
            Plugin._thread_ws.start()
            decky_plugin.logger.info("Initialized")
        except Exception:
            decky_plugin.logger.exception("main")
