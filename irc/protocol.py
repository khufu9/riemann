import re
import string

# Protocol implementation
class IRCProtocolParser:

    def __init__(self, actor):
        self.actor = actor

    def event_cb(self, event):
        """
        In contrast to the dictionaries from connection these do not
        have to be exactly the same.
        However, they must all contain the key "event".
        """
        if event["event"] == "connect":
            self.actor.event_cb({"event":"register"})

        elif event["event"] == "data":
            msg = event["data"]
            if re.search("^PING", msg):
                self.actor.event_cb({"event":"ping", "data":msg})
            elif re.search("^:", msg):
                # All messages will be parsed with this pattern
                pass

        elif event["event"] == "disconnect":
            self.actor.event_cb({"event":"disconnect"})

