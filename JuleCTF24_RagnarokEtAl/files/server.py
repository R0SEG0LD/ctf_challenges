#!/bin/python3

# Multiple socket listening on the same port? If so main proces ensures there is always five processes listening for requests, and starts extras if necessary.
# Main loop continually listens for new connections, when recieved hand off to child proces

# Child proces handle communication, ask for submission and run against data.
# Just dont use shell=true with subproces run.
# After returning results child proces shuts down.
# Cleanup of finished child processes?

import logging
import socket
import threading
from time import sleep
import subprocess
import shutil
import os

def printAddr(addr):
    return f"{addr[0]}:{str(addr[1])}"

def validateRule(addr, rule):
    basedir = f"/tmp/{printAddr(addr)}"
    configfile = f"{basedir}/snort.conf"
    rulefile = f"{basedir}/local.rules"
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    capturefile = f"{scriptdir}/capture.pcap"

    # Write rule to file for the challenger.
    subprocess.run(["mkdir", "-p", basedir])
    try:
        shutil.copytree(f"{scriptdir}/snort", basedir, dirs_exist_ok=True, copy_function=shutil.copy)
    except:
        logging.error("Cant find the snort config directory.")

    if rule.decode('UTF-8').find(' ') != -1 and not rule.decode('UTF-8').split(' ')[0] in ("alert", "log", "pass", "reject"):
        logging.warning(f"Challenger possibly attempting to inject configuration. Input: {rule.decode('UTF-8')}")
        return f"Unknown rule type: {rule.decode('UTF-8').split(' ')[0].rstrip('\n')}"

    with open(rulefile, "wb") as fd:
        fd.write(rule)

    try:
        #result = subprocess.run(["snort", "-XNqA", "cmg", "-r", capturefile, "-c", configfile, "-T"], shell=False, capture_output=True, timeout=10)
        result = subprocess.run(["snort", "-XNqA", "cmg", "-r", capturefile, "-c", configfile, "-t", basedir, "-l", basedir, "-T"], shell=False, capture_output=True, timeout=10)
    except subprocess.TimeoutExpired as e:
        # Time for subprocess ran out.
        logging.error(f"Command: {e.cmd} Timed out {e.timeout} seconds with stderr: {e.stderr.decode('UTF-8')}")
        return 1
    except Exception as e:
        logging.error(f"Unknown error: {e} occurred while validating rule.")
        return 1
    if result.stderr:
        logging.error(f"{result.stderr.decode('UTF-8')}")
        logging.debug(f"Failed with rule: {rule.decode('UTF-8')}")
        error = ' '.join(result.stderr.decode('UTF-8').split('\n')[0].split(' ')[2:])
        logging.debug(f"Reported error: {error}")
        #return result.stderr.decode('UTF-8')
        return error
    logging.debug(f"Validation succeeded")
    return 0

def detectRule(addr, rule): # Return detection result as string.
    basedir = f"/tmp/{printAddr(addr)}"
    configfile = f"{basedir}/snort.conf"
    rulefile = f"{basedir}/local.rules"
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    capturefile = f"{scriptdir}/capture.pcap"

    try:
        #result = subprocess.run(["snort", "-XNqA", "cmg", "-r", capturefile, "-c", configfile], shell=False, capture_output=True, timeout=60)
        result = subprocess.run(["snort", "-XNqA", "cmg", "-r", capturefile, "-c", configfile, "-t", basedir, "-l", basedir], shell=False, capture_output=True, timeout=60)
    except subprocess.TimeoutExpired as e:
        # Time for subprocess ran out.
        logging.error(f"Command: {e.cmd} Timed out after {e.timeout} seconds with stderr: {e.stderr.decode('UTF-8')}")
        return "Timeout from running detection. Please try again."
    except Exception as e:
        logging.error(f"Unknown error: {e} occurred while running detectRule")
        return "Unknown error occurred. Please try again."

    logging.debug(f"Detection finished with rule: |{rule.decode('UTF-8')}| results: {result.stdout}")
    if result.stdout:
        return result.stdout.decode('UTF-8')
    else:
        return "No results."


def server(HOST="0.0.0.0", PORT=1337):
    global SHUTDOWN, client_threads
    SHUTDOWN=False
    client_threads = set()
    threads_lock = threading.Lock()

    th_cleaner = threading.Thread(name="Cleanup_Thread" ,target=cleanup_thread, args=(threads_lock, ))
    th_cleaner.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as main_socket:
        try:
            main_socket.bind((HOST, PORT))
        except OSError as e:
            logging.error(f"Failed while binding to host: {HOST}, port: {PORT}")
            logging.error("Abandoning server startup.")
            SHUTDOWN = True
            th_cleaner.join()
            return
        main_socket.listen()
        logging.info(f"Server listening on {HOST}:{PORT}")

        while True:
            try:
                conn, addr = main_socket.accept()
            except KeyboardInterrupt:
                logging.info(f"KeyboardInterrupt recieved. Starting Shutdown.")
                SHUTDOWN=True
                th_cleaner.join()
                with threads_lock:
                    for client in client_threads:
                        client.join()
                return
                main_socket.close()
                break
            except Exception as e:
                logging.error(f"'{e}' raised while accepting connection.")
                continue
            
            challenger = threading.Thread(name=f"Challenger_{printAddr(addr)}", target=client_handle, args=(conn, addr))
            challenger.start()
            with threads_lock:
                client_threads.add(challenger)
            logging.debug(f"Active connections: {len(client_threads)}")

    logging.info(f"Server shutdown finalized. Enjoy!")

def client_handle(conn, addr):
    with conn:
        conn.settimeout(5)
        logging.info(f"Connection Recieved.")

        #conn.sendall(b"You are now entering state of Ragnarok.\n")
        message_sender(conn, "You are now communicating with Mimir's magic sequence SNORT'er, version 2.9.20.")
        message_sender(conn, "The gateway for puny minds to fathom a small part of the infinite future.")
        message_sender(conn, "###############################################################################")
        waiting = True
        while not SHUTDOWN:
            if waiting:
                msg = b""
                message_sender(conn, "\nPlease input your magical sequence:")
                conn.sendall(">>> ".encode('UTF-8'))
                while True and not SHUTDOWN:
                    try:
                        msg += conn.recv(1024) # Should only wait for message from the user for a limited time.
                        if msg[-1].decode('UTF-8') == '\n':
                            break
                    except socket.timeout: # Socket timeout triggers regularly, then checking whether it should shut down.
                        if SHUTDOWN:
                            message_sender(conn, "\nSomething sudden came up. Server closing down. Goodbye!")
                            break
                        continue
                    except Exception as e:
                        logging.error(f"The following occurred while waiting for a response: {e}")
                        break
                if (not msg or msg.decode('UTF-8') == '\n'):
                    message_sender(conn, "Thank you for your time. May you have a nice Ragnarok.")
                    break
                else:
                    logging.debug(f"Message recieved: {msg.decode('UTF-8').rstrip('\n')}")
                    waiting=False

            else: # Sending
                message_sender(conn, "\nSequence recieved. Validating magic sequence...")
                result = validateRule(addr, msg)
                sleep(2)
                if result:
                    message_sender(conn, "Sequence is Unstable. The following error occurred:")
                    message_sender(conn, result)
                else:
                    message_sender(conn, "Validation succeeded. Beginning sequencing of your submission...")
                    detections = detectRule(addr, msg).splitlines()
                    if len(detections) > 200:
                        logging.info("Length of detection result over 200. Truncating response.")
                        detections = '\n'.join(detections[:200]) + "\n\n...TRUNCATED RESPONSE..."
                    else:
                        detections = '\n'.join(detections)
                    message_sender(conn, "SNORT'er finished with the following results:")
                    message_sender(conn, detections)
                waiting = True

        conn.close()
    try:
        logging.debug(f"Removing Challenger directory.")
        shutil.rmtree(f"/tmp/{printAddr(addr)}")
        logging.debug(f"Directory successfully removed.")
    except FileNotFoundError:
        logging.error(f"Directory '/tmp/{printAddr(addr)}' not found.")
    except Exception as e:
        logging.error(f"Error removing directory '/tmp/{printAddr(addr)}': {e.strerror}")

def message_sender(conn, msg):
    logging.debug(f"Sending message: {msg.encode('UTF-8')}")
    conn.sendall(f"{msg}\n".encode('UTF-8'))

def cleanup_thread(lock):
    while not SHUTDOWN:
        sleep(1)
        with lock:
            removed = set()
            #logging.debug(f"Num of threads before cleanup: {threading.active_count()}")
            for client in client_threads:
                try:
                    #name = client.name
                    client.join(timeout=0.1)
                    if client.is_alive():
                        continue
                    logging.info(f"Joined thread from {client.name}")
                    removed.add(client)
                except RuntimeError:
                    # Thread not ready to be joined yet.
                    continue
            #logging.debug(f"Num of threads after cleanup: {threading.active_count()}")
            for remove in removed:
                client_threads.remove(remove)
            #client_threads = set(client_threads - removed)


if __name__ == "__main__":
    import argparse

    format = "[%(asctime)s][%(levelname)s][%(threadName)s] %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    
    #firstValue = validateRule(("127.0.0.1", "12345"), "false test".encode('UTF-8'))
    #validateRule(("127.0.0.1", "12345"), 'alert tcp any any -> any any (msg:"Test Rule"; content:"FDCA{"; sid:100023;)'.encode('UTF-8'))
    
    #detectRule(("127.0.0.1", "12345"), 'alert tcp any any -> any any (msg:"Test Rule"; content:"FDCA{"; sid:100023;)'.encode('UTF-8'))

    server()
