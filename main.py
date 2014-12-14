import re
import string
import socket

class IRCConnection:
    """
    IRC is a textbased protocol on the form
    COMMAND CONTENT<newline>

    TODO: Consider parallelism
    * Threads (python is always single threaded as only one thread can be active at a time)
        Read from multiple sockets at once
        Wait for long computations
    TODO: How to deal with TCP timeout, reset, and close?
    """

    def __init__(self, event_cb, host, port):
        self.host = host
        self.port = port
        self.event_cb = event_cb
        self.buffer = list()
        
    def main(self):

        # Set up socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.event_cb(self, {"type":"connect", "message":""})

        # Main loop
        while True:
            data = self.socket.recv(1024)

            # Print raw data
            #print "RAW:",data,

            # Exit loop if no data
            if not data: break

            # Check if message contain newline
            if "\r\n" in data:
                while "\r\n" in data:
                    index = data.find("\r\n")

                    # Join message
                    msg = "".join(self.buffer) + data[:index]
                    del self.buffer[:]

                    # Report
                    print "IN:",msg
                    self.event_cb(self, {"type":"message", "message":msg})

                    # Remove used data, +2 for CR LF
                    data = data[index+2:]
                if len(data) > 0:
                    self.buffer.append(data)
            else:
                self.buffer.append(data)

        # Report socket being dead
        self.event_cb(self, {"type":"disconnect", "message":""})

    def send(self, msg):
        print "OUT:", msg,
        self.socket.send(msg)

def event_cb(irc, event):
    if event["type"] == "connect":
        irc.send("NICK riemannoob\r\n")
        irc.send("USER bot hyperspace indrome.com :Some bot\r\n")
    elif event["type"] == "message":
        msg = event["message"]
        if re.search("^PING", msg):
            irc.send(string.replace(msg, "PING", "PONG")+"\r\n")
        elif re.search("^:", msg):
            # All messages will be parsed with this pattern
            pass

    elif event["type"] == "disconnect":
        pass


if __name__ == "__main__":

    # Set up socket and connect
    irc = IRCConnection(event_cb, "irc.quakenet.org", 6667)
    irc.main()