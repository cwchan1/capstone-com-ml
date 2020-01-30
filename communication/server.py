import socket

class CapstoneTCPServer:
    def __init__(self, host_name, port, timeout):
        # initial variables
        # - host_name String
        # - port Number Port number to bind to
        # - timeout Number Timeout in milliseconds
        self.host_name = host_name
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timeout = timeout

    def initializeSocket(self):
        # setup server socket and wait for connection
        # return socket?
        self.server_socket.settimeout(self.timeout)

        self.server_socket.bind((self.host_name, self.port))
        self.server_socket.listen(1)

        self.connection, self.address = self.server_socket.accept()

        with self.connection:
            return True

        return False

    # Should catch exceptions
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