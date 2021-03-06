import logging
import socket

class CapstoneTCPServer:
    def __init__(self, host_name, port, timeout):
        # initial variables
        self.address = None
        self.connection = None
        self.host_name = host_name
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.timeout = timeout

    def initializeSocket(self):
        # setup server socket and wait for connection
        # return True if connection sucessful, False otherwise
        logging.info("Binding server socket on {}, {}".format(self.host_name, self.port))

        server_address = (self.host_name, self.port)

        self.server_socket.bind(server_address)
        self.server_socket.listen()

        try:
            self.connection, self.address = self.server_socket.accept()
            
        except socket.error as msg:
            logging.debug(msg)
            return False
        else:
            if self.connection:
                logging.info("Connection accepted on server socket.")

                self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.connection.settimeout(self.timeout)
                return True

        return False

    def receive(self, bytes):
        try:
            return self.connection.recv(bytes)
        except socket.error as msg:
            logging.debug("Error receiving data with error message: " + str(msg))
            return None
            
    def send(self, data):
        try:
            self.connection.sendall(data)
        except OSError as msg:
            logging.debug("Error sending data with error message: " + str(msg))
            return False
        else:
            return True
    
    def getHostName(self):
        return self.host_name
    def getPort(self):
        return self.port
    def getTimeout(self):
        return self.timeout

    def setHostName(self, host_name):
        self.host_name = host_name
    def setPort(self, port):
        self.port = port
    def setTimeout(self, timeout):
        self.timeout = timeout