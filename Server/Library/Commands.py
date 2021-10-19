from pathlib import Path
import threading
import socket
from .Chatter import *


# Util Commands


def Add_To_Queue(message=None, addr=None, Client_List=None, **__):
    for user in Client_List:
        if user.addr != addr:
            user.Queue_Message(message)


def Add_Whisper(message=None, addr=None, Client_List=None, **__):
    for user in Client_List:
        if user.addr == addr:
            user.Queue_Message(message)


# Server Commands


def dm(message=None, client=None, Client_List=None, **__):
    recipient = message.split(" ")[1]
    full_message = str((client.ID + " whispered " + message.split(" ", 2)[2]))
    for user in Client_List:
        if user.ID == recipient:
            Add_Whisper(message=full_message, addr=user.addr, Client_List=Client_List)
            user.Set_Last_Messaged(client.ID)
            print(full_message + " to ", user.ID)
            return
    else:
        client.conn.sendto("[SERVER ALERT] User not found".encode(), client.addr)


def reply(message=None, client=None, Client_List=None, **__):
    full_message = str((client.ID + " whispered " + message.split(" ", 1)[1]))
    recipient = client.Get_Last_Messaged()
    for user in Client_List:
        if user.ID == recipient:
            Add_Whisper(message=full_message, addr=user.addr, Client_List=Client_List)
            print(client.ID + " replied " + message.split(" ", 1)[1])
            return
    else:
        client.conn.sendto("[SERVER ALERT] User not found".encode(), client.addr)


def Help(client=None, Client_List=None, **__):
    message = """ 
    Commands:
    /dm [user] [message]        Sends [message] to [user] privately
    /r  [message]               Sends [message] to person who last private messaged you
    /upl [filename] [user]      Uploads [filename] to server, only [user] can download it,
                                [user] is not notified of this, file must be in same directory as client.py
    /dwn [filename]             Downloads [filename] from server
    /exit                       Exits the program
    /help                       Displays this menu"""
    Add_Whisper(message=message, addr=client.addr, Client_List=Client_List)


def Save_File(message=None, client=None, Client_List=None, file_socket_object=None, File_List=None, encObjects=None, **__):
    fileName, recipient = message.split(" ")[1], message.split(" ")[2]
    for user in Client_List:
        if user.ID == recipient:
            fConn, fAddr = file_socket_object.accept()
            path = Path("File_Downloads/" + fileName)
            counter = 1
            while path.exists():
                path = Path("File_Downloads/" + str(counter) + fileName)
                counter += 1
            file = open(path, "xb")
            try:
                fConn.settimeout(10)
                tempFile = b""
                line = fConn.recv(1024)
                while line:
                    tempFile += line
                    line = fConn.recv(1024)
                encryption = encObjects.get(client)
                tempFile = encryption.decryptFile(tempFile)

                encryption = encObjects.get(user)
                file.write(encryption.encryptFile(tempFile))

                Add_Whisper(message="[FILE SERVER ALERT] File uploaded to server under name: " + path.name,
                            addr=client.addr, Client_List=Client_List)
                print(" File: " + fileName + " was uploaded to server by " + client.ID)
                file_obj = File(fileName, recipient)
                File_List.add(file_obj)
            except TimeoutError:
                Add_Whisper(message="[FILE SERVER ALERT] File upload failed, socket timed out", addr=client.addr,
                            Client_List=Client_List)

            file.close()
            fConn.close()
            return True
    else:
        Add_Whisper(message="[SERVER ALERT] No user found with given name".encode(), addr=client.addr,
                    Client_List=Client_List)
        return


def Send_File(message=None, client=None, Client_List=None, file_socket_object=None, File_List=None, **__):
    fileName = message.split(" ")[1]
    fConn, fAddr = file_socket_object.accept()
    for file in File_List:
        if file.fileID == fileName and client.ID == file.receiver:
            f = open("File_Downloads/" + fileName, "rb")
            try:
                fConn.settimeout(10)
                line = f.read(1024)
                while line:
                    fConn.sendto(line, fAddr)
                    line = f.read(1024)
                File_List.remove(file)
                Add_Whisper(message="[FILE SERVER ALERT] File " + fileName + " downloaded", addr=client.addr,
                            Client_List=Client_List)
                print(client.ID.lower() + " downloaded file: " + fileName)
                downloaded = True
            except TimeoutError:
                Add_Whisper(message="[FILE SERVER ALERT] File not downloaded, socket timed out", addr=client.addr,
                            Client_List=Client_List)
                downloaded = False
            f.close()
            if downloaded:
                p = Path("File_Downloads/" + fileName)
                p.unlink()
            return True
    fConn.shutdown(socket.SHUT_RDWR)
    return False


def Invalid(client=None, Client_List=None, **__):
    Add_Whisper(message="Invalid Command", addr=client.addr, Client_List=Client_List)


def disconnect(client=None, Client_List=None, ID_Set=None, File_List=None, encObjects=None, **__):
    Add_To_Queue(message="[SERVER ALERT]: User: " + client.ID + " has disconnected", addr=client.addr,
                 Client_List=Client_List)
    print(client.ID + " has disconnected")
    Add_Whisper(message="CLIENT_SHUTDOWN", addr=client.addr, Client_List=Client_List)
    Client_List.remove(client)
    ID_Set.remove(client.ID.lower())
    encObjects.pop(client)
    for file in File_List:
        if file.receiver == client.ID.lower():
            path = Path("File_Downloads/" + file.fileID)
            path.unlink()
            File_List.remove(file)
    print(f"{client.ID} has disconnected, with {threading.active_count() -1} threads running!")
