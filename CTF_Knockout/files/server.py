import socket
import threading
from random import randint
from time import sleep

def printAddr(addr):
    return f"{addr[0]}:{str(addr[1])}"

def server(HOST="127.0.0.1", PORT=1337):
    global activePorts
    activePorts = set()
    client_threads = []
    #main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if args.interactive:
        thread = threading.Thread(target=command_handle)
        thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_socket:
        main_socket.settimeout(1)
        main_socket.bind((HOST, PORT))
        #main_socket.setblocking(0)
        main_socket.listen()
        if args.logging:
            print(f"[LISTENING] Server listening on {HOST}:{PORT}")
        while True:
            try:
                conn, addr = main_socket.accept()
            except socket.timeout:
                if GLOBAL_SHUTDOWN:
                    if args.logging:
                        print(f"[CLOSING] Main socket closing, waiting on clients...")
                    for client in client_threads:
                        client.join()
                    main_socket.close()
                    if args.logging:
                        print(f"[CLOSING] Main socket SHUTDOWN.")
                    break
                else:
                    continue

            thread = threading.Thread(target=client_handle, args=(conn, addr, False))
            thread.start()
            client_threads.append(thread)
            if args.logging:
                print(f"[ACTIVE] Active connections: {threading.active_count() - 2}")

def client_handle(conn_socket, addr, recieve = True):
    with conn_socket:
        if args.logging:
            print(f"[CONNECTION] Connection from: {printAddr(addr)}")
        port_count = DIFFICULTY
        ports = gen_challenge(count=port_count)
        conn_socket.sendall(b"Hello Bear Fellow!\n\nIf you are sure, then knock on the following ports:\n"+" ".join(ports).encode('UTF-8')+b"\n")
        
        addr = (addr[0], str(addr[1]))

        connected = True
        while connected:
            if recieve: # Should the server recieve data from the client
                recieving = True
                msg = b""
                #while recieving:
                try:
                    data = conn_socket.recv(1024)
                    msg += data
                except:
                    break
                if args.logging:
                    print(f"[{':'.join(addr)}] {msg.decode('UTF-8')}")
                if (not msg or msg.decode('UTF-8') == '\n'):
                    connected = False
                else:
                    conn_socket.sendall(msg)
            else:
                success = [False]
                thread = threading.Thread(target=knockout_handle, args=(ports, addr, success))
                thread.start()
                # Wait for the client to knock correctly. Or fail
                thread.join()
                break
        if success[0]:
            conn_socket.sendall(b"\nWARNING: Self destruction Imminent!\n")
            sleep(1)
            conn_socket.sendall(b"Beginning countdown...\n")
            for i in range(5, 0, -1):
                sleep(1)
                conn_socket.sendall(f"{str(i)}...".encode('UTF-8'))
            sleep(1)
            conn_socket.sendall(f"\nSELFDESTRUCTION COMPLETE\n\n{reward}".encode('UTF-8'))
        else:
            conn_socket.sendall(f"You did not knock it out. Postponing selfdestruction.\n".encode('UTF-8'))
        if args.logging:
            print(f"[CLIENT] Closing: {printAddr(addr)}")
        conn_socket.close()
        

def gen_challenge(count = 10, port_range = (10000, 20000)):
    ports = set()
    while len(ports) < count:
        newPort = str(randint(port_range[0], port_range[1]))
        if newPort in activePorts:
            continue
        ports.add(newPort)
        activePorts.update(ports)
        #ports = set([randint(10000,20000) for x in range(10)])

    return ports

def knockout_handle(ports, addr, returnValue):
    timeout = False
    if args.logging:
        print(f"[KNOCKOUT] Listening for knocks on:\n{' '.join(ports)}")
    subthreads = []
    result = [0] * (len(ports))
    index = 0
    for port in ports:
        thread = threading.Thread(target=knock_handle, args=(int(port), addr, lambda : timeout, result, index))
        thread.start()
        subthreads.append(thread)
        index += 1
    sleep(args.timeout)
    if args.logging:
        print(f"[KNOCKOUT] Client {printAddr(addr)} knocking closing...")
    timeout = True
    # Wait for all the knock handles to complete.
    for subthread in subthreads:
        subthread.join()
    if args.logging:
        print(f"[KNOCKOUT] Knocking for {printAddr(addr)} has closed.")
    success = True
    for knocked in result[1:]:
        if not knocked:
            success = False
            if args.logging:
                print(f"[KNOCKOUT] Client {printAddr(addr)} failed.")
            break
    if success:
        if args.logging:
            print(f"[KNOCKOUT] Clinet {printAddr(addr)} has succeeded! Initializing termination sequence... :P")
        returnValue[0] = True
        # Return some value showing success


def knock_handle(port, addr, SHUTDOWN, result, index):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDP_sock:
        #print(f"[KNOCKOUT] Listening for knocks on {port}"
        UDP_sock.settimeout(1)
        UDP_sock.bind(('', port))
        while True:
            try:
                msg, addr2 = UDP_sock.recvfrom(1024)
            except socket.timeout:
                #print(f"[KNOCKOUT] Timeout value: {SHUTDOWN}")
                if SHUTDOWN():
                    if args.logging:
                        print(f"[KNOCKOUT] {printAddr(addr)} failed to knock on {port}")
                    UDP_sock.close()
                    break
                else:
                    continue

            if addr2[0] == addr[0] and msg:
                if args.logging:
                    print(f"[KNOCKOUT] {printAddr(addr2)} Knocked on {port}")
                result[index] = True
                print(result)
                # Good!
                UDP_sock.close()
                break

    activePorts.remove(str(port))

def command_handle():
    while True:
        cmd = input()
        if cmd == "SHUTDOWN":
            GLOBAL_SHUTDOWN = True
            print(f"[CONTROL] Server shutting down...")
            break
        elif cmd == "PORTS":
            print(f"[CONTROL] Ports in use:\n{' '.join(activePorts) or 'None'}")
        elif cmd == "STATUS":
            print(f"[CONTROL] Active threads: {threading.active_count() - 2}")
        else:
            print(f"[CONTROL] Command not understood: {cmd}")

if __name__ == "__main__":
    import argparse

    GLOBAL_SHUTDOWN = False

    parser = argparse.ArgumentParser("Command line Options")
    parser.add_argument("--host", help="Listening IP", default="")
    parser.add_argument("--port", type=int, help="Listening port", default=1337)
    parser.add_argument("--difficulty", type=int, help="Number of port to be knocked", default=5)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--reward", default="/var/knockout/flag.txt")
    parser.add_argument("-i", "--interactive", action='store_true')
    parser.add_argument("--logging", action='store_true')

    args = parser.parse_args()

    HOST_IP = args.host
    HOST_PORT = args.port
    DIFFICULTY = args.difficulty

    with open(args.reward) as flag:
        reward = flag.read()

    if args.logging:
        print("[START] Server is starting...")
    server(HOST_IP, HOST_PORT)

    #gen_challenge()
