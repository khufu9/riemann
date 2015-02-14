import re
import string
import time

import utils.youtube as youtube

import irc
from irc.protocol import IRCProtocolParser
from irc.connection import IRCConnection

class Bot:

    def __init__(self, config):
        self.config = config
        self.parser = IRCProtocolParser(self)
        host = config["server"]["host"]
        port = config["server"]["port"]
        self.connection = IRCConnection(self.parser, host, port)

    def nick_string(self, nick = None):
        if nick is None:
            nick = self.config["nick"][self.config["nickIndex"]]
        return "NICK "+nick

    def next_nick(self):
        index = (self.config["nickIndex"] + 1) % len(self.config["nick"])
        self.config["nickIndex"] = index
        return index == 0 # Wrapped
    
    def user_string(self):
        username = self.config["user"]["username"]
        hostname = self.config["user"]["hostname"]
        servername = self.config["user"]["servername"]
        realname = self.config["user"]["realname"]
        return " ".join(["USER", username, hostname, servername, realname])

    def join_string(self):
        channels = ",".join(self.config["channels"])
        return "JOIN " + channels

    def connect(self):
        self.config["nickIndex"] = 0
        self.connection.connect()

    def event_cb(self, event):
        print "event:", event
        if event["event"] == "register":
            self.connection.send(self.nick_string() + "\r\n")
            self.connection.send(self.user_string() + "\r\n")

        elif event["event"] == "ping":
            msg = event["data"]
            print "PING EVENT DETECTED"
            self.connection.send(string.replace(msg, "PING", "PONG")+"\r\n")

        elif event["event"] == "message":
            print event["data"]
            if event["code"] == irc.RPL_ENDOFMOTD or event["code"] == irc.ERR_NOMOTD:
                self.connection.send(self.join_string() + "\r\n")
            elif event["code"] == irc.ERR_NICKNAMEINUSE:
                if self.next_nick():
                    self.config["timeout"] = 300
                    self.connection.quit()
                    return
                
                self.connection.send(self.nick_string() + "\r\n")
        
        elif event["event"] == "PRIVMSG":
            print event
            words = event["content"].split()
            for word in words:
                if "youtube" in word or "youtu.be" in word:
                    test = youtube.getTitle(word)
                    if test is not None:
                        if event["destination"] in self.config["nick"]:
                            dst = event["source"]
                        else:
                            dst = event["destination"]
                        self.connection.send("PRIVMSG " + dst +" : > " + test + "\r\n")

        elif event["event"] == "disconnect":
            pass


if __name__ == "__main__":

    config = {
        "server": {
            "host":"irc.quakenet.org",
            "port":6667
        },
        "nick": [
            "riemann",
            "riemannbot",
            "riemannbot_"
        ],
        "nickIndex": 0,
        "user": {
            "username": "riemannbot",
            "hostname": "hyperspace",
            "servername": "indrome.com",
            "realname": ":Mr. Bot" # Colon allows for space
        },
        "channels":[
            "#blashyrk"
        ],
        "timeout": 0
    }

    bot = Bot(config)

    # Will exit after first disconnect
    while 1:
        bot.connect()
        if bot.config["timeout"] > 0:
            print "timeout:", bot.config["timeout"], "seconds"
            time.sleep(bot.config["timeout"])
            bot.config["timeout"] = 0
        else:
            print "timeout: 5 seconds"
            time.sleep(5)

