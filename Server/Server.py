from Library.Commands import *
import shutil
from Library.Encryption import *
from time import sleep

shutil.rmtree("File_Downloads/", ignore_errors=True)
downloadPath = Path("File_Downloads/")
downloadPath.mkdir(exist_ok=True, parents=True)

Client_List = set()
File_List = set()
ID_Set = set()
encObjects = {}

Command_Map = {"/dm": dm,
               "/r": reply,
               "/dwn": Send_File,
               "/upl": Save_File,
               "/help": Help,
               "/exit": disconnect}

# ip = input("Set server IP")
# port = int(input("Set server port"))

ip = "127.0.0.1"
port = 5820
fPort = 5821
address = (ip, port)
fAddress = (ip, fPort)

socket_object = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

file_socket_object = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

socket_object.bind(address)
file_socket_object.bind(fAddress)

socket_object.listen(1000)
file_socket_object.listen(1000)


def handler(conn, addr):
    client, encryption = Join_Procedure(conn, addr)
    if not client or not encryption:
        return

    send_Thread = threading.Thread(target=sender, args=(client, encryption,))
    send_Thread.start()
    print(f"{client.ID} has connected, with {threading.active_count()} threads running!")

    while True:
        try:
            data = conn.recv(2048)
        except Exception as e:
            _ = e
            disconnect(client=client, Client_List=Client_List, File_List=File_List, ID_Set=ID_Set, encObjects=encObjects)
            return

        message = data.decode()
        message = encryption.decryptMes(message)
        if message[0] != "/":
            full_message = (client.ID + ": " + message)
            print(full_message)
            Add_To_Queue(message=full_message, addr=addr, Client_List=Client_List)
        else:
            Check_Commands(message, client)
            if message == "/exit":
                return


def Join_Procedure(conn, addr):
    try:
        encryption = initialise_Encryption(conn, addr)
    except Exception as e:
        _ = e
        return None, None

    try:
        ID = initialise_Username(conn, addr, encryption)
    except Exception as e:
        _ = e
        return None, None

    client = Chatter(ID, conn, addr)
    ID_Set.add(ID.lower())
    Client_List.add(client)
    encObjects[client] = encryption

    Add_To_Queue(message="[SERVER ALERT] User: " + client.ID + " has connected to the server", addr=client.addr,
                 Client_List=Client_List)
    conn.sendto(encryption.encryptMes("You have connected to the server").encode(), client.addr)
    return client, encryption


def Check_Commands(message, client):
    command = Command_Map.get(message.split(" ")[0], Invalid)
    print(client.ID + " ran " + command.__name__)
    if command:
        command(message=message, client=client, Client_List=Client_List,
                ID_Set=ID_Set, File_List=File_List, file_socket_object=file_socket_object, encObjects=encObjects)


def initialise_Encryption(conn, addr):
    encryption = RSA()
    key1 = int(conn.recv(2048).decode())
    key2 = int(conn.recv(2048).decode())
    encryption.setClientKey((key1, key2))

    conn.sendto(str(encryption.getPublicKey()[0]).encode(), addr)
    sleep(0.5)
    conn.sendto(str(encryption.getPublicKey()[1]).encode(), addr)
    return encryption


def initialise_Username(conn, addr, encryption):
    validName, ID = False, None
    while not validName:
        data = conn.recv(2048)
        ID = encryption.decryptMes(data.decode())
        if ID.lower() not in ID_Set:
            conn.sendto(encryption.encryptMes("TRUE").encode(), addr)
            validName = True
        else:
            conn.sendto(encryption.encryptMes("FALSE").encode(), addr)
    return ID


def sender(client, encryption):
    while True:
        toSend = client.Get_Queued_Message()
        if toSend == "CLIENT_SHUTDOWN":
            return
        try:
            toSend = encryption.encryptMes(toSend)
            client.conn.sendto(toSend.encode(), client.addr)
        except Exception as e:
            _ = e
            pass


def serve_forever(socket_obj):
    while True:
        conn, addr = socket_obj.accept()
        handle_thread = threading.Thread(target=handler, args=(conn, addr,))
        handle_thread.start()


serve_forever(socket_object)
