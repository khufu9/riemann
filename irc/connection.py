import socket

# Socket manager
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

    def __init__(self, parser, host, port):
        self.host = host
        self.port = port
        self.parser = parser
        self.buffer = list()
        
    def connect(self):

        # Set up socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.parser.event_cb({"event":"connect", "data":None})

        # Main loop
        while True:
            try:
                data = self.socket.recv(1024)
            except:
                data = None

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
                    self.parser.event_cb({"event":"data", "data":msg})

                    # Remove used data, +2 for CR LF
                    data = data[index+2:]
                if len(data) > 0:
                    self.buffer.append(data)
            else:
                self.buffer.append(data)

        # Report socket being dead
        self.parser.event_cb({"event":"disconnect", "data":None})

    def send(self, msg):
        print "OUT:", msg,
        self.socket.send(msg.encode('utf-8'))

    def quit(self):
        print "QUIT", socket.SHUT_WR
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()

