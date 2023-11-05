# -*- coding: utf-8 -*-
# !/usr/bin/python3
from flask import Flask, request
from AnonChihayaBot import AnonChihayaBot

flask_app = Flask(__name__)

@flask_app.route("/", methods=["POST"])
def main() -> str:
    payload = request.get_json()
    app.handle(payload)
    return '200'

if __name__ == '__main__':
    app = AnonChihayaBot.run(serve='WebHook')
    flask_app.run(host='0.0.0.0', port=8800)
    app.stop()