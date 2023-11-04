# -*- coding: utf-8 -*-
# !/usr/bin/python3
from flask import Flask, request
from AnonChihayaBot import AnonChihayaBot

app = AnonChihayaBot.run(serve='Dev')

while True:
    if input() == '/stop':
        app.stop()
        break