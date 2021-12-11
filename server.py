# To do:
# -Implement multi-port listeners for HTTP/HTTPS
# -Add classes (cleanup code a bit)
# -Fix a crash where the certificate is untrusted (WORKAROUND DONE)
# -Implement better SSL-related crash handling
# -Change config from JSON to YAML to handle comments
# -Add threading to support multiple clients (PART DONE)
# -Add fuzzing using atheris
# --Add fuzzing/not fuzzing badge to the repo (shield.io?)

import socket
import sys
import datetime
import json
import os
import ssl
import getopt
import concurrent.futures
import yaml
from os import path

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

content_array = []
CUSTOM_CONFIG = False


# Returns an argument list array
def getopts(argv):
    try:
        opts, args = getopt.getopt(
            argv, "hi:p:c:", ["host=", "port=", "custom-config="])
        return opts
    except getopt.GetoptError:
        print("server.py -h <hostname> -p <port> -c <path_to_config_file>")
        sys.exit(1)

# Parses arguments from the array
for opt, arg in getopts(sys.argv[1:]):
    if opt == '-h':
        # Print syntax if -h was given
        print("server.py -h <hostname> -p <port> -c <path_to_config_file>")
        sys.exit()  # Kill the server after printing help
    elif opt in ("-i", "--host"):
        HOST = str(arg)
    elif opt in ("-p", "--port"):
        PORT = int(arg)
    elif opt in ("-c", "--custom-config"):
        CUSTOM_CONFIG = arg


# Reads the configuration file into an array
def readcfg():
    global content_array
    if not content_array:  # Is the configuration file loaded into memory?
        if CUSTOM_CONFIG:
            try:
                with open(CUSTOM_CONFIG) as f:
                    content_array = json.load(f)
                    return content_array
            except:
                msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c'))
                              + str(']: '), 'Unable to find specified config file'))
                print(msg)
                # Kill the server ungracefully - prevents duplicate stdout messages
                os._exit(1)
        else:
            try:
                with open('conf.json') as f:
                    content_array = json.load(f)
                    return content_array
            except:
                msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')
                                         ) + str(']: '), 'Unable to read configuration file!'))
                print(msg)
                # Kill the server ungracefully - prevents duplicate stdout messages
                os._exit(1)
    # If it is, return the array instead of reading the config file again (reduces iops)
    else:
        return content_array

try:
    if readcfg()["logging"] is True:
        LOG = True
    else:
        LOG = False
except:
    LOG = True

# Converts old format config to new (json -> yaml)
def jsonToYaml():
    with open('conf.yml') as conf:
        return(yaml.load(conf, Loader=Loader))

# Writes to the log file
def logwrite(msg):
    try:
        if LOG is True:
            f = open(readcfg()["logfile"], "a")
            f.write(msg + '\n')
            f.close()  # Its better to close the file after every write to prevent corruption, theres also no point in keeping the file open if there are no more messages to log
    except:
        print("Unable to write to log file!")


# Reads an IP blacklist
def readblacklist():
    try:
        # global blacklist_array
        blacklist_array = []

        # If the blacklist doesn't exist, create a blank file
        if (not path.isfile(readcfg()["blacklist"])):
            open(readcfg()["blacklist"], "x")

        # if not blacklist_array: # Is the blacklist loaded into memory?
        with open(readcfg()["blacklist"]) as f:
            for line in f:
                blacklist_array.append(line.rstrip('\n'))
            return blacklist_array
        # else: # Returns the blacklist if in memory
        #    return blacklist_array
    except:
        msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')
                                 ) + str(']: '), 'Unable to read the IP blacklist!'))
        print(msg)
        logwrite(msg)


# If hostname has not been defined, read config
if 'HOST' not in locals():
    HOST = readcfg()["hostname"].rstrip()  # Read config file

# If port has not been defined, read config
if 'PORT' not in locals():
    PORT = int(readcfg()["port"])  # Read config file


def httpResponseLoader(status):
    try:
        # Open file, r => read , b => byte format
        file = open("http_responses/" + status + '.html', 'rb')
        response = file.read()  # Read the input stream into response
        file.close()  # Close the file once read
        return response

    except:
        msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(']: '), 'Page for HTTP '
                      + str(status), ' not found! Closing connection\n'))  # Contains \n to separate requests
        print(msg)
        logwrite(msg)
        return False


# AF_INET specifies ipv4
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# SO_REUSEADDR specifies that we are only able to bind to the socket if its not currently in use
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    sock.bind((HOST, PORT))
    sock.listen(1)
    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c'))
                  + str(']: '), 'Successfully bound to ', HOST + str(':') + str(PORT)))
    print(msg)
    logwrite(msg)

except Exception as e:
    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c'))
                  + str(']: '), 'Unable to bind to ', HOST + str(':') + str(PORT)))
    print(msg)
    print(e)  # For verbose logging purposes - helps with troubleshooting
    logwrite(msg)
    sys.exit()


def thread_function(name):
    print("Thread {} starting!".format(name))
    try:
        while True:
            connection, address = sock.accept()  # Accept incoming connections

            # Encrypt traffic using a certificate
            if readcfg()["use_encryption"]:
                socket = ssl.wrap_socket(
                                        connection,
                                        server_side=True,
                                        certfile=readcfg()["path_to_cert"],
                                        keyfile=readcfg()["path_to_key"],
                                        ssl_version=ssl.PROTOCOL_TLS_SERVER,
                                        do_handshake_on_connect=False
                                        )
                try:
                    socket.do_handshake()
                except ssl.SSLError as e:
                    if readcfg()["strict_cert_validation"]:
                        print(
                            "[OpenSSL]: Server has encountered a certificate issue! Shutting down...")
                        print("[Debug]: " + str(e))
                        try:
                            sys.exit(0)
                        except SystemExit:
                            os._exit(0)
                    else:
                        pass
            else:
                socket = connection

            print("--- Thread {} output ---".format(name))
            msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(']: '),
                          'Incoming connection from ', address[0] + str(':') + str(address[1])))
            print(msg)
            logwrite(msg)
            request = socket.recv(1024).decode('utf-8')
            try:
                readblacklist().index(address[0])

                # 403 to signify that the client is not allowed to access the resource
                header = 'HTTP/1.1 403 Forbidden\n'
                header += 'Server: Python HTTP Server\n'  # Server name
                # Tells the client not to cache the responses
                header += 'Cache-Control: no-store\n'
                header += 'Content-Type: text/html\n\n'  # Set MIMEtype to text/html

                response = httpResponseLoader(
                    readcfg()["blacklist_rcode"])  # Get the 403 page
                if response is False:
                    socket_closed = True
                    socket.close()

                if response is not False:
                    blacklist_response = header.encode('utf-8')
                    blacklist_response += response
                    socket.send(blacklist_response)
                    socket.close()  # If in blacklist, close the connection

                    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(
                        ']: '), 'IP ', address[0], (' in blacklist. Closing connection!\n')))
                    print(msg)
                    logwrite(msg)

                    socket_closed = True
            except Exception as e:
                socket_closed = False
            string_list = request.split(' ')  # Split request from spaces
            method = string_list[0]

            try:
                requested_file = string_list[1]
            except IndexError:
                if socket_closed is False:
                    # Client likely wanted to see if the server is alive
                    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(
                        ']: '), '[KEEP-ALIVE]: State check received from client'))
                    print(msg)
                    logwrite(msg)

            if socket_closed is False:
                if not method:
                    socket_closed = True
                    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(']: '),
                                  'Client sent a request with no method\n'))  # Contains \n to separate requests
                else:
                    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')
                                             ) + str(']: ') + str(method), ' ', requested_file))
                print(msg)
                logwrite(msg)

            if socket_closed is False:
                # Parameters after ? are not relevant
                rfile = requested_file.split('?')[0]
                rfile = rfile.lstrip('/')
                # Most browsers replace whitespaces with %20 sequence, this replaces it back for filenames/directories
                rfile = rfile.replace("%20", " ")

                # PAGE DEFAULTS
                if(rfile == ''):
                    # Load index file as default
                    rfile = readcfg()["default_filename"]
                elif rfile.endswith('/'):
                    # Load index file as default
                    rfile += readcfg()["default_filename"]
                elif (path.exists("htdocs/" + rfile) and not(path.isfile("htdocs/" + rfile))):
                    # Load index file as default
                    rfile += '/' + readcfg()["default_filename"]

                try:
                    # open file, r => read , b => byte format
                    file = open("htdocs/" + rfile, 'rb')
                    response = file.read()  # Read the input stream into response
                    file.close()  # Close the file once read

                    if socket_closed is False:
                        msg = ''.join(
                            ('[' + str(datetime.datetime.now().strftime('%c')) + str(']: '), 'Found requested resource!'))
                        print(msg)
                        logwrite(msg)
                        msg = ''.join((('[' + str(datetime.datetime.now().strftime('%c')) + str(
                            ']: '), 'Serving /', rfile, '\n')))  # Contains \n to separate requests
                        print(msg)
                        logwrite(msg)

                    # 200 To signify the server understood and will fulfill the request
                    header = 'HTTP/1.1 200 OK\n'
                    header += 'Server: Python HTTP Server\n'  # Server name
                    # Tells the client to validate their cache on load
                    header += 'Cache-Control: no-cache\n'

                    if(rfile.endswith(".jpg")):
                        mimetype = 'image/jpg'
                    elif(rfile.endswith(".css")):
                        mimetype = 'text/css'
                    elif(rfile.endswith(".png")):
                        mimetype = 'image/png'
                    else:
                        mimetype = 'text/html'

                    header += 'Content-Type: '+str(mimetype)+'\n\n'

                except:
                    if socket_closed is False:
                        msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(
                            ']: '), 'Unable to find requested resource!\n'))  # Contains \n to separate requests
                        print(msg)
                        logwrite(msg)
                    # If unable to read the specified file, assume it does not exist and return 404
                    header = 'HTTP/1.1 404 Not Found\n'
                    header += 'Server: Python HTTP Server\n'  # Server name
                    header += 'Content-Type: text/html\n\n'  # MIMEtype set to html

                    response = httpResponseLoader('404')
                    if response is False:
                        socket_closed = True
                        socket.close()

                if socket_closed is False:
                    final_response = header.encode('utf-8')
                    final_response += response

                    socket.send(final_response)
                    socket.close()

    except KeyboardInterrupt:
        print("\nReceived KeyboardInterrupt!")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == '__main__':
    if (readcfg()["threads"] >= 1):
        print("multi threading ok, continuing")
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=readcfg()["threads"]) as executor:
                executor.map(thread_function, range(readcfg()["threads"]))
        except:
            pass
    else:
        print("Thread count is set to 0! Please set the value to at least 1.")
