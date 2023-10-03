# To do:
# -Implement multi-port listeners for HTTP/HTTPS - Won't implement
# -Add classes (cleanup code a bit)
# -Fix a crash where the certificate is untrusted (WORKAROUND DONE)
# -Implement better SSL-related crash handling
# -Add threading to support multiple clients (PART DONE)
# -Add fuzzing using atheris - Backlog
# --Add fuzzing/not fuzzing badge to the repo (shield.io?)

# Core server functionality
import socket
# Exit support, positional arguments and reflection
import sys
# For logging
import datetime
# Various OS provided functions
import os
# SSL/TLS support
import ssl
# CLI arguments
import argparse
# Asynchronous IO for performance
import asyncio
# Config handling
import yaml
# Internal modules
import logrot
# Path traversal
from os import path
# Logging functions
import logging
import logging.handlers
# Python file type magic
import magic
# Import handling
from importlib import import_module
# Class inspection for reflection
import inspect
# Coloured text support - mainly for readabilty
from termcolor import colored
# Typehinting for reflection where a class object reference is returned
from typing import Type, Optional
from types import ModuleType

try:
    from yaml import CLoader as Loader # Author suggests using the C version of the loader
except ImportError:
    from yaml import Loader # If above doesn't work, default to generic loader

# Globals
content_array = []
CUSTOM_CONFIG = False

class ConfigLoader:
    # Reads the configuration file into an array
    def readcfg():
        global content_array
        if not content_array:  # Is the configuration file loaded into memory?
            if CUSTOM_CONFIG:
                try:
                    with open(CUSTOM_CONFIG) as f:
                        content_array = yaml.load(f, Loader=Loader)
                        return content_array
                except Exception: # Catch the base class for exceptions
                    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c'))
                                + str(']: '), 'Unable to find specified config file'))
                    print(msg)
                    # Kill the server ungracefully - prevents duplicate stdout messages
                    os._exit(1)
            else:
                try:
                    with open('conf.yml') as f:
                        content_array = yaml.load(f, Loader=Loader)
                        return content_array
                except Exception: # Catch the base class for exceptions
                    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')
                                            ) + str(']: '), 'Unable to read configuration file!'))
                    print(msg)
                    # Kill the server ungracefully - prevents duplicate stdout messages
                    os._exit(1)
        # If it is, return the array instead of reading the config file again (reduces iops)
        else:
            return content_array
 
            
# class stub
class HelperFunctions:

    def __init__(self, custom_config = None):
        self.custom_config = custom_config


    def init_logger(self) -> logging.Logger:
        logging.basicConfig(
            level=readcfg()["logging_level"].upper(),
            format='[%(asctime)s] [%(levelname)s]: %(message)s',
            datefmt='%c',
            handlers=[
                logging.handlers.RotatingFileHandler(
                    readcfg()["logfile"],
                    'a',
                    self.__unit_conversion(
                        readcfg()["logfile_unit"],
                        readcfg()["logfile_maxsize"],
                        'bytes'),
                    5),
                logging.StreamHandler()])
        logging.info("Logging init complete")
        return logging.getLogger("ServerLogger")


    def __unit_conversion(self, in_unit: str, in_unit_value: int, out_unit: str) -> int:
        # Check if passed in types are correct
        if not isinstance(in_unit_value, int):
            raise TypeError("in_unit_value must be an integer")
        if not isinstance(out_unit, str):
            raise TypeError("out_unit must be a string")
        if not isinstance(in_unit, str):
            raise TypeError("in_unit must be a string")
        
        # Function to convert units
        if in_unit == "bytes" and out_unit == "kilobytes":
            return in_unit_value / 1024
        elif in_unit == "bytes" and out_unit == "megabytes":
            return in_unit_value / 1024 / 1024
        elif in_unit == "bytes" and out_unit == "gigabytes":
            return in_unit_value / 1024 / 1024 / 1024
        elif in_unit == "kilobytes" and out_unit == "bytes":
            return in_unit_value * 1024
        elif in_unit == "megabytes" and out_unit == "bytes":
            return in_unit_value * 1024 * 1024
        elif in_unit == "gigabytes" and out_unit == "bytes":
            return in_unit_value * 1024 * 1024 * 1024
        elif in_unit == out_unit:
            return in_unit_value
        else:
            return 0


    def __has_method(self, class_obj: Type, method_name: str) -> bool:
        if hasattr(class_obj, method_name):
            method = getattr(class_obj, method_name)
            return callable(method) and method.__qualname__.split(".")[0] == class_obj.__name__
        return False


    def __plugin_init_class(self, module: ModuleType) -> Optional[Type]:
        # Get the module's attributes
        attributes = dir(module)
        # Find the plugin's init function
        for attribute in attributes:
            if attribute.startswith("PluginInit_") and inspect.isclass(getattr(module, attribute)):
                return getattr(module, attribute)
        # Use the init class specified in plugin's meta
        if module.PLUGIN_DATA["meta"]["initclass"] in attributes:
            return getattr(module, module.PLUGIN_DATA["meta"]["initclass"])


    # Plugin loader function
    def load_plugins(self):
        # Load plugins from the plugins directory
        plugin_dir = readcfg()["plugins_dir"]
        if os.path.exists(plugin_dir):
            plugins = os.listdir(plugin_dir)
            for plugin in plugins:
                if plugin.endswith(".py"):
                    name = plugin[:-3]
                    try:
                        # Importlib to handle the programmatic import
                        plugin_module = import_module(f"{plugin_dir}.{name}")
                        init_class = self.__plugin_init_class(plugin_module)
                        # Call the expected init function
                        if self.__has_method(init_class, "init"):
                            init_class().init()
                        else:
                            raise ImportError(f"Plugin {name} is missing an init function")
                        # Log that the plugin was loaded
                        logging.info(f"Loaded plugin {plugin_module.PLUGIN_DATA['name']}, version {plugin_module.PLUGIN_DATA['version']} by {plugin_module.PLUGIN_DATA['author']}")
                    except Exception as e:
                        logging.error(f"Error loading plugin: {name}")
                        logging.error(str(e))
                        continue


    def __argparser(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--host", help = "Address to listen on", type = str)
        parser.add_argument("-p", "--port", help = "Port to listen on", type = int)
        parser.add_argument("-c", "--custom-config", help = "Custom configuration file to use", type = str)
        
        return parser.parse_args()


    def arg_actions(self) -> dict:
        args = self.__argparser()
        argdict = dict()
        if args.custom_config != None:
            CUSTOM_CONFIG = args.custom_config
        if args.host != None:
            argdict["host"] = args.host
        if args.port != None:
            argdict["port"] = args.port

        if len(argdict) != 0:
            return argdict
        else:
            return {}


# Reads the configuration file into an array
def readcfg():
    global content_array, CUSTOM_CONFIG
    if not content_array:  # Is the configuration file loaded into memory?
        if CUSTOM_CONFIG:
            try:
                with open(CUSTOM_CONFIG) as f:
                    content_array = yaml.load(f, Loader=Loader)
                    return content_array
            except:
                msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c'))
                              + str(']: '), 'Unable to find specified config file'))
                print(msg)
                # Kill the server ungracefully - prevents duplicate stdout messages
                os._exit(1)
        else:
            try:
                with open('conf.yml') as f:
                    content_array = yaml.load(f, Loader=Loader)
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
        logger.error('Unable to read the IP blacklist!')


# If hostname has not been defined, read config
if 'HOST' not in locals():
    HOST = readcfg()["hostname"].rstrip()  # Read config file

# If port has not been defined, read config
if 'PORT' not in locals():
    PORT = int(readcfg()["port"])  # Read config file


class Server:

    def __init__(self, args, host = "127.0.0.1", port = 8080):

            if "host" in args:
                self.host = args["host"]
            else:
                self.host = host

            if "port" in args:
                self.port = args["port"]
            else:
                self.port = port


    def http_response_loader(status):
        try:
            # Open file, r => read, b => byte format
            file = open("http_responses/" + str(status) + '.html', 'rb')
            response = file.read()  # Read the input stream into response
            file.close()  # Close the file once read
            return response

        except:
            msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(']: '), 'Page for HTTP '
                        + str(status), ' not found! Closing connection\n'))  # Contains \n to separate requests
            logger.info(f'Page for HTTP {status} not found! Closing connection')
            return False


    async def server_main(self):
        # Encrypt traffic using a certificate
        if readcfg()["use_encryption"]:
            try:
                sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                sslctx.load_cert_chain(readcfg()["path_to_cert"], readcfg()["path_to_key"])
            except ssl.SSLError as e:
                if readcfg()["strict_cert_validation"]:
                    print("[OpenSSL]: Server has encountered a certificate issue! Shutting down...")
                    print("[Debug]: " + str(e))
                    try:
                        sys.exit(0)
                    except SystemExit:
                        os._exit(0)
                else:
                    pass
        else:
            sslctx = None

        flags = [socket.SOL_SOCKET, socket.SO_REUSEADDR]
        server = await asyncio.start_server(self.response,
                                            self.host,
                                            self.port,
                                            ssl = sslctx,
                                            family = socket.AF_INET,
                                            flags = flags)

        if server:
            for sock in server.sockets:
                address = sock.getsockname()

            if sslctx != None:
                logger.info('TLS Enabled')

            logger.info(f'Listening on {address[0]}:{address[1]}')

        async with server:
            await server.serve_forever()


    async def response(self, reader, writer):
        try:
            data = await reader.read(2048)
            request = data.decode('utf-8')
            address = writer.get_extra_info('peername')
            try:
                readblacklist().index(address[0])

                # 403 to signify that the client is not allowed to access the resource
                header = 'HTTP/1.1 403 Forbidden\n'
                header += 'Server: Python HTTP Server\n'  # Server name
                # Tells the client not to cache the responses
                header += 'Cache-Control: no-store\n'
                header += 'Content-Type: text/html\n\n'  # Set MIMEtype to text/html

                response = self.http_response_loader(
                    readcfg()["blacklist_rcode"])  # Get the 403 page
                if response is False:
                    socket_closed = True
                    await writer.drain()
                    writer.close()

                if response is not False:
                    blacklist_response = header.encode('utf-8')
                    blacklist_response += response
                    writer.write(blacklist_response)
                    await writer.drain()
                    writer.close()  # If in blacklist, close the connection

                    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(
                        ']: '), 'IP ', address[0], (' in blacklist. Closing connection!\n')))
                    log(msg)

                    socket_closed = True
            except Exception as e:
                socket_closed = False

            string_list = request.split(' ')  # Split request by space
            method = string_list[0]

            try:
                requested_file = string_list[1]
            except IndexError:
                if socket_closed is False:
                    # Client likely wanted to see if the server is alive
                    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(
                        ']: '), '[KEEP-ALIVE]: State check received from client'))
                    log(msg)

            if socket_closed is False:
                if not method:
                    socket_closed = True
                    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(']: '),
                                    'Client sent a request with no method\n'))  # Contains \n to separate requests
                else:
                    msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')
                                                ) + str(']: ') + str(method), ' ', requested_file))
                log(msg)

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
                        log(msg)
                        msg = ''.join((('[' + str(datetime.datetime.now().strftime('%c')) + str(
                            ']: '), 'Serving /', rfile, '\n')))  # Contains \n to separate requests
                        log(msg)

                    # 200 To signify the server understood and will fulfill the request
                    header = 'HTTP/1.1 200 OK\n'
                    header += 'Server: Python HTTP Server\n'  # Server name
                    # Tells the client to validate their cache on load
                    header += 'Cache-Control: no-cache\n'
                    header += 'Content-Type: '+str(magic.from_file("htdocs/" + rfile, mime=True))+'\n\n'

                except Exception as e:
                    if socket_closed is False:
                        msg = ''.join(('[' + str(datetime.datetime.now().strftime('%c')) + str(
                            ']: '), 'Unable to find requested resource!\n'))  # Contains \n to separate requests
                        log(msg)
                    print(e)
                    # If unable to read the specified file, assume it does not exist and return 404
                    header = 'HTTP/1.1 404 Not Found\n'
                    header += 'Server: Python HTTP Server\n'  # Server name
                    header += 'Content-Type: text/html\n\n'  # MIMEtype set to html

                    response = self.http_response_loader('404')
                    if response is False:
                        socket_closed = True
                        await writer.drain()
                        writer.close()

                if socket_closed is False:
                    final_response = header.encode('utf-8')
                    final_response += response

                    writer.write(final_response)
                    await writer.drain()
                    writer.close()

        except KeyboardInterrupt:
            print("\nReceived KeyboardInterrupt!")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)

if __name__ == '__main__':
    hf = HelperFunctions()
    logger = hf.init_logger()
    hf.load_plugins()
    args = hf.arg_actions()
    server = Server(args)
    asyncio.run(server.server_main())