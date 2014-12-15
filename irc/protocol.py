import re
import string

# Protocol implementation
class IRCProtocolParser:

    def __init__(self, actor):
        self.actor = actor

    def parse_nick(self, msg):
        # RFC 1459 Page 8:
        #<nick>       ::= <letter> { <letter> | <number> | <special> }
        #<letter>     ::= 'a' ... 'z' | 'A' ... 'Z'
        #<number>     ::= '0' ... '9'
        #<special>    ::= '-' | '[' | ']' | '\' | '`' | '^' | '{' | '}'
        nick_split = re.findall(":[a-zA-Z][a-zA-Z0-9_\-[\]{}\^`|]*!", msg)
        if len(nick_split) > 0:
            return nick_split[0][1:-1]
        return None

    def parse_privmsg(self, event):
        msg = event["data"]
        msg_split = msg.split()

        # At least four: ":tednoob!~tednoob@91.201.61.162 PRIVMSG riemann :test"
        if len(msg_split) < 4:
            return None

        # Verify that this is a PRIVMSG
        code = msg_split[1]
        if code != "PRIVMSG":
            return None

        # Source nick
        source_nick = self.parse_nick(msg_split[0])
        if source_nick is None:
            return None

        # Destination
        destination = msg_split[2]

        # Actual message
        colons = [entry.start() for entry in re.finditer(":", msg)]
        colon_len = len(colons)
        if colon_len == 0:
            return None
        elif colon_len == 1:
            content = split[3]
        else:
            print colons
            content = msg[colons[1]+1:]

        privmsg = {
            "event":"PRIVMSG",
            "source":source_nick,
            "destination":destination,
            "content":content,
            "data": event["data"]
        }
        self.actor.event_cb(privmsg)


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

            # All messages will be parsed with this pattern
            elif re.search("^:", msg): 
                msg_split = msg.split()
                msg_split_len = len(msg_split)
                if msg_split_len < 2:
                    return None

                # Common in most messages
                source = msg_split[0]
                code = msg_split[1]

                if code == "PRIVMSG":                
                    self.parse_privmsg(event)
                else:
                    self.actor.event_cb({"code":code,"event":"message", "data":msg})

        elif event["event"] == "disconnect":
            self.actor.event_cb({"event":"disconnect"})

