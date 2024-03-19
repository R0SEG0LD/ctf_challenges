import socket
import threading
from time import sleep

HOST = ("127.0.0.1", 1337)


def knock(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as knock_sock:
        for i in range(10):
            knock_sock.sendto(b"A", (HOST[0], int(port)))
            sleep(0.1)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main:
    main.connect(HOST)
    

    data = main.recv(1024).decode('UTF-8')

    lines = data.split('\n')

    ports = lines[3].split(' ')
    print(ports)
    for port in ports:
        k = threading.Thread(target=knock, args=(port,))
        k.start()

    sleep(1)

    data2 = main.recv(1024).decode('UTF-8')
    data3 = main.recv(1024).decode('UTF-8')
    data4 = main.recv(1024).decode('UTF-8')
    
    print("2:", data2)
    print(data3)
    print(data4)

    while True:
        data = main.recv(1024).decode('UTF-8')

        if not data:
            break
        else:
            print(data)
