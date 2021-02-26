import socket, sys, signal, datetime, json, os

content_array = []
blacklist_array = []

# Reads the configuration file into an array
def readcfg():
    try:
        global content_array
        if not content_array: # Is the configuration file loaded into memory?
            with open('conf.json') as f:
                    content_array = json.load(f)
                    return content_array
        else: # If it is, return the array instead of reading the config file again (reduces iops)
            return content_array
    except:
        msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'Unable to read configuration file!'))
        print(msg)
        logwrite(msg)
        sys.exit(0) # Kill the server if unable to find the config file (and no parameters were provided)
        
try:
    if readcfg()["logging"] == True:
        LOG = True
    else:
        LOG = False
except:
    LOG = True

# Writes to the log file
def logwrite(msg):
    try:
        if LOG == True:
            f = open(readcfg()["logfile"], "a")
            f.write(msg + '\n')
            f.close() # Its better to close the file after every write to prevent corruption, theres also no point in keeping the file open if there are no more messages to log
        
    except:
        print("Unable to write to log file!")
        
# Reads an IP blacklist
def readblacklist():
    try:
        global blacklist_array
        if not blacklist_array: # Is the blacklist loaded into memory?
            with open(readcfg()["blacklist"]) as f:
                for line in f:
                    blacklist_array.append(line)
                return blacklist_array
        else: # Returns the blacklist if in memory
            return blacklist_array
    except:
        msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'Unable to read the IP blacklist!'))
        print(msg)
        logwrite(msg)

# Allows the user to specify a hostname
try:
    if sys.argv[1] == '--host':
        HOST = str(sys.argv[2])
except:
    HOST = readcfg()["hostname"].rstrip() # Read config file

# Allows the user to specify the port
try:
    if sys.argv[3] == '--port':
        PORT = int(sys.argv[4])
except:
    PORT = int(readcfg()["port"]) # Read config file
 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET specifies ipv4
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # SO_REUSEADDR specifies that we are only able to bind to the socket if its not currently in use
        
try:
    sock.bind((HOST,PORT))
    sock.listen(1)
    msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'Successfully bound to ', HOST +str(':') +str(PORT)))
    print(msg)
    logwrite(msg)
    
except Exception as e:
    msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'Unable to bind to ', HOST +str(':') +str(PORT)))
    print(msg)
    print(e) # For verbose logging purposes - helps with troubleshooting
    logwrite(msg)
    sys.exit()
 
try:
    while True:
        connection, address = sock.accept() # Accept incoming connections
        msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'Incoming connection from ', address[0] +str(':') +str(address[1])))
        print(msg)
        logwrite(msg)
        request = connection.recv(1024).decode('utf-8')
        try:
            readblacklist().index(address[0])
            connection.close() # If in blacklist, close the connection before any data is sent
            socket_closed = True
            msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'IP ', address[0] ,(' in blacklist. Closing connection!\n')))
            print(msg)
            logwrite(msg)
        except Exception as e:
            socket_closed = False
        string_list = request.split(' ') # Split request from spaces
        method = string_list[0]
        
        try:
            requested_file = string_list[1]
        except IndexError:
            if socket_closed == False:
                msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'State check received from client')) # Client likely wanted to see if the server is alive
                print(msg)
                logwrite(msg)
 
        if socket_closed == False:
            if not method:
                socket_closed = True
                msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'Client sent a request with no method\n')) # Contains \n to separate requests
            else:
                msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: ') +str(method), ' ', requested_file))
            print(msg)
            logwrite(msg)
 
        if socket_closed == False:
            rfile = requested_file.split('?')[0] # Parameters after ? are not relevant
            rfile = rfile.lstrip('/')
            rfile = rfile.replace("%20", " ") # Some browsers replace whitespaces with %20 sequence, this replaces it back for filenames
            if(rfile == ''):
                rfile = 'index.html' # Load index file as default
            elif rfile.endswith('/'):
                rfile = rfile + 'index.html' # Load index file as default
    
            try:
                file = open("htdocs/" + rfile, 'rb') # open file , r => read , b => byte format
                response = file.read() # Read the input stream into response
                file.close() # Close the file once read
            
                if socket_closed == False:
                    msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'Found requested resource!'))
                    print(msg)
                    logwrite(msg)
                    msg = ''.join((('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'Serving /', rfile, '\n'))) # Contains \n to separate requests
                    print(msg)
                    logwrite(msg)
        
                header = 'HTTP/1.1 200 OK\n' # 200 To signify the server understood and will fulfill the request
                header += 'Server: Python HTTP Server\n' # Server name
                header += 'Cache-Control: no-cache\n' # Tells the client not to cache the responses
 
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
                if socket_closed == False:
                    msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'Unable to find requested resource!\n')) # Contains \n to separate requests
                    print(msg)
                    logwrite(msg)
                header = 'HTTP/1.1 404 Not Found\n\n' # If unable to read the specified file, assume it does not exist and return 404
                status = '404'
                
                try:
                    file = open("http_responses/" + status + '.html', 'rb') # open file , r => read , b => byte format
                    response = file.read() # Read the input stream into response
                    file.close() # Close the file once read
                    
                    final_response = header.encode('utf-8')
                    final_response += response
                except:
                    msg = ''.join(('[' +str(datetime.datetime.now().strftime('%c')) +str(']: '), 'Page for HTTP ' +str(status), ' not found! Closing connection\n')) # Contains \n to separate requests
                    print(msg)
                    logwrite(msg)
                    
                    socket_closed = True
                    connection.close()
                    
            if socket_closed == False:
                connection.send(final_response)
                connection.close()
        
except KeyboardInterrupt:
    print('KeyboardInterrupt')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
