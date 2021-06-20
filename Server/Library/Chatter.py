from queue import *


class Chatter:

    def __init__(self, ID, conn, addr):
        self.ID = ID
        self.conn = conn
        self.addr = addr
        self.lastMessaged = None
        self.Messages = Queue(maxsize=0)

    def Set_Last_Messaged(self, addr):
        self.lastMessaged = addr

    def Get_Last_Messaged(self):
        return self.lastMessaged

    def Queue_Message(self, message):
        self.Messages.put(message)

    def Get_Queued_Message(self):
        return self.Messages.get()


class File:

    def __init__(self, fileID, receiver):
        self.fileID = fileID
        self.receiver = receiver
