import threading
import socket
from pathlib import Path
from Library.Encryption import *
from time import sleep


downloadPath = Path("PyChatroom_Downloads/")
downloadPath.mkdir(exist_ok=True, parents=True)

# ip = input("Enter the IP of the server")
# port = int(input("Enter the port to connect to"))

ip = "127.0.0.1"
port = 5820
fPort = 5821
address = (ip, port)
fAddress = (ip, fPort)

socket_object = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

socket_object.connect(address)


def handler(conn, encryption):
    global isReady
    while True:
        data = conn.recv(11264)
        mes = encryption.decryptMes(data.decode())
        isReady.wait()
        print(("\b" * (len(userNick) + 2) + "\b" * len(mes)) + mes + "\n" + userNick + ": ", end="")


def Download_File(fileName, encryption):
    path = Path("PyChatroom_Downloads/" + fileName)
    counter = 1
    while path.exists():
        path = Path("PyChatroom_Downloads/" + str(counter) + fileName)
        counter += 1
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.connect(fAddress)
    f = open(path, "xb")
    sleep(0.5)
    try:
        sc.settimeout(10)
        file = b""
        line = sc.recv(1024)
        while line:
            file += line
            line = sc.recv(1024)
        f.write(encryption.decryptFile(file))
        print("File downloaded at location " + str(path))
    finally:
        sc.close()
        f.close()


def Upload_File(fileName, encryption):
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.connect(fAddress)
    f = open(fileName, "rb")
    try:
        line = f.read(1024)
        while line:
            line = encryption.encryptFile(line)
            sc.sendall(line)
            line = f.read(1024)
    finally:
        sc.shutdown(socket.SHUT_RDWR)
        f.close()


def getUsernameInput():
    uN = input("Please Enter a Username: ")
    while (":" in uN) or (" " in uN) or ("/" in uN):
        uN = input("Please enter a valid username: ")
    return uN


def initialiseEncryption():
    encryption = RSA()
    socket_object.send(str(encryption.getPublicKey()[0]).encode())
    sleep(0.5)
    socket_object.send(str(encryption.getPublicKey()[1]).encode())
    key1 = int(socket_object.recv(2048).decode())
    key2 = int(socket_object.recv(2048).decode())
    encryption.setServerKey((key1, key2))
    return encryption


isConnected = False
encryption = initialiseEncryption()
print("Please enter a Username, the name cannot include a space, slash or colon!")
userNick = getUsernameInput()
while not isConnected:
    socket_object.send(encryption.encryptMes(userNick).encode())
    response = True if encryption.decryptMes(socket_object.recv(2048).decode()) == "TRUE" else False
    if not response:
        print("Username In Use!")
        userNick = getUsernameInput()
    else:
        isConnected = True

isReady = threading.Event()
receiving = threading.Thread(target=handler, args=(socket_object, encryption,))
receiving.start()

while True:
    isReady.clear()
    print(userNick + ": ", end="")
    isReady.set()
    user_Message = input()

    if user_Message[:3] == "/dm" and len(user_Message.split(" ", 2)) != 3:
        print("Error, invalid amount of arguments, requires: /dm [recipient] [message]")
    elif user_Message[:2] == "/r" and len(user_Message.split(" ", 1)) != 2:
        print("Error, invalid amount of arguments, requires: /r [message]")
    elif user_Message[:4] == "/dwn" and len(user_Message.split(" ")) != 2:
        print("Error, invalid amount of arguments, requires /dwn [filename]")
    elif user_Message[:4] == "/upl" and len(user_Message.split(" ")) != 3:
        print("Error, invalid amount of arguments, requires /upl [filename] [recipient]")
    elif user_Message[:5] == "/exit" and len(user_Message.split(" ")) > 1:
        print("Error, no arguments expected for exit command")
    elif user_Message[:5] == "/help" and len(user_Message.split(" ")) > 1:
        print("Error no arguments expected for help command")
    else:
        cipher_Message = encryption.encryptMes(user_Message)
        socket_object.send(str(cipher_Message).encode())

    if user_Message == "/exit":
        socket_object.shutdown(socket.SHUT_RDWR)
        break
    elif user_Message[:4] == "/dwn":
        Download_File(user_Message[5:].strip(), encryption)
    elif user_Message[:4] == "/upl":
        Upload_File(user_Message.split(" ")[1].strip(), encryption)
