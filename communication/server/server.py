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
        self.timeout = timeout

    def initializeSocket(self):
        # setup server socket and wait for connection
        # return True if connection sucessful, False otherwise
        self.server_socket.settimeout(self.timeout)

        logging.debug("Binding server socket on {}:{}".format(self.host_name, self.port))

        self.server_socket.bind((self.host_name, self.port))
        self.server_socket.listen()

        self.connection, self.address = self.server_socket.accept()

        with self.connection:
            logging.debug("Connection accepted on server socket.")
            return True

        return False

    def receive(self):
        data = self.connection.recv(1024)
        if not data:
            return 0
        else:
            return data
    def send(self, data):
        self.connection.send(data)
    
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