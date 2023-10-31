# -*- coding: utf-8 -*-
# !/usr/bin/python3
from AnonChihayaBot import AnonChihayaBot

app = AnonChihayaBot.run()

while True:
    cmd = input()
    if cmd == '/stop':
        app.stop()
        break
    elif cmd == '/restart':
        app.stop()
        app = AnonChihayaBot.run()
