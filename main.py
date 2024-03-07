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

def indicate():
    decky_plugin.logger.info("happened")
    with open("/tmp/happened", "w") as ff:
        ff.write("happened")

def keyboard_listener():
    keyboard.add_hotkey('ctrl+1', indicate)
    decky_plugin.logger.info("keyboard listener online")
    keyboard.wait()

class Plugin:
    _thread = None
    async def _main(self):
        try:
            Plugin._thread = Thread(target=keyboard_listener)
            Plugin._thread.daemon = True
            Plugin._thread.start()
            decky_plugin.logger.info("Initialized")
        except Exception:
            decky_plugin.logger.exception("main")
