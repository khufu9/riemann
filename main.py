import re
import string

import utils.youtube as youtube
from irc.protocol import IRCProtocolParser
from irc.connection import IRCConnection

class Bot:

    def __init__(self, config):
        self.config = config
        self.parser = IRCProtocolParser(self)
        host = config["server"]["host"]
        port = config["server"]["port"]
        self.connection = IRCConnection(self.parser, host, port)

    def nick_string(self):
        # TODO: Strategy if name is taken (e.g ping timeout)
        return "NICK "+self.config["nick"][0]

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
            if event["code"] == "376": # End of MOTD
                self.connection.send(self.join_string() + "\r\n")
        
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
                        self.connection.send("PRIVMSG " + dst +" :" + test + "\r\n")
            
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
        "user": {
            "username": "riemannbot",
            "hostname": "hyperspace",
            "servername": "indrome.com",
            "realname": ":Mr. Bot" # Colon allows for space
        },
        "channels":[
            "#blashyrk"
        ]
    }

    bot = Bot(config)

    # Will exit after first disconnect
    bot.connect()