
from socket import *
from threading import Thread
import time
import datetime

portNum = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', portNum))

messages = []

def send_message():
    receiver_IP = input("IP Address of receiver: ")
    message = input("Message to send: ")
    try:
        clientSocket.sendto(message.encode(), (receiver_IP, portNum))
    except Exception:
        print(f"Error: Failed to send message to: {receiver_IP}\n")
    return None

def read_messages():
    n = len(messages)
    if n == 0:
        print("No new messages")
        return None
    
    for i in range(n):
        m,a,d = messages.pop(0)
        print(f"message from {a} at {d}:\n{m.decode()}\n")
    return None

def receiving_thread(connection, bufferSize):
    print("receiving thread start")
    while True:
        message, address = connection.recvfrom(bufferSize)
        messages.append((message, address, datetime.datetime.now()))

def main():
    rThread = Thread(target=receiving_thread, args=(serverSocket, 4096))
    rThread.start()
    time.sleep(1)
    while True:
        print("To send a message enter 1, To read messages enter 2")
        function = int(input(">>> "))
        
        if function == 1:
            send_message()
        elif function == 2:
            read_messages()
        else:
            break


if __name__ == "__main__":
    main()
