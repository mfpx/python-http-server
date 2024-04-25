# To do:
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
import signal
# Config handling
import yaml
# Path traversal
from os import path
# Logging functions
import logging
# Own logging module
import logger
# Python file type magic
import magic
# Import handling
from importlib import import_module, reload
# Class inspection for reflection
import inspect
# Typehinting for reflection where a class object reference is returned
from typing import Type, Optional
from types import ModuleType
# HTTP response loading
from http_responses import Responses
# URL handling
import urllib.parse
# Request parsing
from request_parser import RequestParser, HTTP
# Debug traces
import traceback
# Output caching
from functools import cache
# Python-based page module hashing
import hashlib

try:
    from yaml import CLoader as Loader # Author suggests using the C version of the loader
except ImportError:
    from yaml import Loader # If above doesn't work, default to generic loader

class HelperFunctions:

    def __init__(self, custom_config = False):
        self.custom_config = custom_config
        self.plugin_list = []
        self.python_page_hashes = {}


    def compute_hash(self, path: str, store: bool = False) -> str:
        """Computes the hash of a given file"""
        # Open the file
        with open(path, "rb") as file:
            # Read the file's contents
            contents = file.read()
            # Compute the hash
            if store is True:
                self.python_page_hashes[path] = hashlib.sha256(contents).hexdigest()
                return self.python_page_hashes[path]
            else:
                return hashlib.sha256(contents).hexdigest()


    def get_hash(self, path: str) -> str:
        """Returns the hash of a given file"""
        # Check if the hash is already cached
        if path in self.python_page_hashes:
            return self.python_page_hashes[path]
        # If not, compute it
        self.compute_hash(path, True)
        # Return the hash
        return self.python_page_hashes[path]


    def __has_method(self, class_obj: Type, method_name: str) -> bool:
        """Check if a class has a method with a given name"""
        if hasattr(class_obj, method_name):
            method = getattr(class_obj, method_name)
            return callable(method) and method.__qualname__.split(".")[0] == class_obj.__name__
        return False


    def __plugin_init_class(self, module: ModuleType) -> Optional[Type]:
        """Finds the plugin's init class"""
        # Get the module's attributes
        attributes = dir(module)
        # Find the plugin's init function
        for attribute in attributes:
            if attribute.startswith("PluginInit_") and inspect.isclass(getattr(module, attribute)):
                return getattr(module, attribute)
        # Use the init class specified in plugin's meta
        if module.PLUGIN_DATA["meta"]["initclass"] in attributes:
            return getattr(module, module.PLUGIN_DATA["meta"]["initclass"])


    def __is_postload(self, module: ModuleType) -> bool:
        """Check if a plugin is marked as postload"""
        if "postload" in module.PLUGIN_DATA["meta"]:
            return module.PLUGIN_DATA["meta"]["postload"]
        return False

    
    def __plugin_obj_to_str(self, obj: ModuleType) -> str:
        """Converts a plugin object to a string"""
        return f'{obj.PLUGIN_DATA["name"]} (v{obj.PLUGIN_DATA["version"]}) by {obj.PLUGIN_DATA["author"]}'


    @cache
    def readcfg(self) -> dict:
        """Loads the configuration file into a dictionary"""
        if self.custom_config:
            try:
                with open(self.custom_config) as f:
                    config_data = yaml.load(f, Loader=Loader)
                    return config_data
            except:
                logging.critical("Unable to find specified config file")
                # Kill the server ungracefully - prevents duplicate stdout messages
                os._exit(1)
        else:
            try:
                with open("conf.yml") as f:
                    config_data = yaml.load(f, Loader=Loader)
                    return config_data
            except:
                logging.critical("Unable to find specified config file")
                os._exit(1)

    
    @cache
    def readblacklist(self) -> list:
        """Reads the IP blacklist"""
        try:
            # blacklist_array
            blacklist_array = []

            # If the blacklist doesn't exist, create a blank file
            if (not path.isfile(cfg["blacklist"])):
                open(cfg["blacklist"], 'x')

            with open(cfg["blacklist"]) as f:
                for line in f:
                    blacklist_array.append(line.rstrip('\n'))
                return blacklist_array
        except:
            logging.error("Unable to read the IP blacklist")


    # Plugin loader function
    def load_plugins(self, postload: bool = False) -> bool:
        """Loads the plugins from the plugins directory"""
        # Load plugins from the plugins directory
        plugin_dir = cfg["plugins_dir"]
        if os.path.exists(plugin_dir):
            plugins = os.listdir(plugin_dir)
            for plugin in plugins:
                if plugin.endswith(".py"):
                    name = plugin[:-3]
                    try:
                        # Set a plugin append flag
                        p_added = False
                        # Importlib to handle the programmatic import
                        plugin_module = import_module(f"{plugin_dir}.{name}")
                        init_class = self.__plugin_init_class(plugin_module)
                        # Call the expected init function
                        if self.__has_method(init_class, "init"):
                            if self.__is_postload(plugin_module) == postload:
                                init_class().init()
                                self.plugin_list.append(plugin_module)
                                p_added = True
                        else:
                            raise ImportError(f"Plugin {name} is missing an init function")
                        # Log that the plugin was loaded
                        if plugin_module in self.plugin_list and p_added == True:
                            logging.debug(self.plugin_list)
                            logging.info(f"Loaded plugin {self.__plugin_obj_to_str(plugin_module)}")
                    except Exception as e:
                        logging.error(f"Error loading plugin: {name}")
                        logging.error(str(e))
                        continue
            return 0
        else:
            return -1


    def __argparser(self) -> argparse.Namespace:
        """Argument parser"""
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--host", help = "Address to listen on", type = str)
        parser.add_argument("-p", "--port", help = "Port to listen on", type = int)
        parser.add_argument("-c", "--custom-config", help = "Custom configuration file to use", type = str)
        
        return parser.parse_args()


    def arg_actions(self) -> dict:
        """Argument actions"""
        args = self.__argparser()
        argdict = {}
        if args.custom_config != None:
            self.custom_config = args.custom_config
        if args.host != None:
            argdict["host"] = args.host
        if args.port != None:
            argdict["port"] = args.port

        if len(argdict) != 0:
            return argdict
        else:
            return {}


class Server:
    """Main server class"""

    def __init__(self, args, host = "127.0.0.1", port = 8080):

            if "host" in args:
                self.host = args["host"]
            elif cfg["hostname"]:
                self.host = cfg["hostname"]
            else:
                self.host = host

            if "port" in args:
                self.port = args["port"]
            elif cfg["port"]:
                self.port = cfg["port"]
            else:
                self.port = port


    async def server_main(self) -> None:
        """Main server method"""
        # Encrypt traffic using a certificate
        if cfg["use_encryption"]:
            try:
                sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                sslctx.load_cert_chain(cfg["path_to_cert"], cfg["path_to_key"])
            except ssl.SSLError as e:
                if cfg["strict_cert_validation"]:
                    logging.critical("Server has encountered a certificate issue! Shutting down...")
                    logging.debug(e)
                    try:
                        sys.exit(1)
                    except SystemExit:
                        os._exit(1)
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
                logging.info("TLS Enabled")

            logging.info(f"Listening on {address[0]}:{address[1]}")

        async with server:
            await server.serve_forever()


    async def response(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handles incoming requests"""
        try:
            r = Responses()
            data = await reader.read(2048)
            request = data.decode("utf-8")
            address = writer.get_extra_info("peername")

            if address[0] in hf.readblacklist():
                # 403 to signify that the client is not allowed to access the resource
                header = r.get_response_header(403)
                if cfg["signature_reporting"]:
                    header += f'Server: {cfg["signature"]}\n' # Server name
                # Tells the client not to cache the responses
                header += "Cache-Control: no-store\n"
                header += "Content-Type: text/html\n\n"  # Set MIMEtype to text/html

                response = r.get_response_body(
                    cfg["blacklist_rcode"]
                ).encode("utf-8")  # Get the 403 page
                if response is False:
                    socket_closed = True
                    await writer.drain()
                    writer.close()

                if response is not False:
                    blacklist_response = header.encode("utf-8")
                    blacklist_response += response
                    writer.write(blacklist_response)
                    await writer.drain()
                    writer.close()  # If in blacklist, close the connection

                    logging.info(f"IP {address[0]} in blacklist. Closing connection.")

                    socket_closed = True
            else:
                socket_closed = False

            # Request parser
            parser = RequestParser()
            try:
                # Parse the request. Request data is stored in the parser object instance.
                parser.parse_request(request)
                method = parser.REQUEST_METHOD
                requested_file = parser.REQUEST_PATH
            except:
                if socket_closed is False:
                    # Client likely wanted to see if the server is alive
                    logging.info("Unable to parse request, ignoring\n")

            if socket_closed is False:
                if not method:
                    socket_closed = True
                    logging.info("Client sent a request with no method\n")
                else:
                    logging.info(f"{method} {requested_file}")

            if socket_closed is False:
                python_page = False
                # Parameters after ? are not relevant
                rfile = requested_file.split('?')[0]
                rfile = rfile.lstrip('/')
                # Replace escape sequences with their actual characters
                rfile = urllib.parse.unquote(rfile)

                # PAGE DEFAULTS
                if rfile == '' or rfile.endswith('/'):
                    # Load index file as default
                    rfile = cfg["default_filename"]
                elif path.isfile(f"htdocs/{rfile}.py"):
                    try:
                        python_page = True
                        if hf.compute_hash(f"htdocs/{rfile}.py") == hf.get_hash(f"htdocs/{rfile}.py"):
                            page = import_module(f"htdocs.{rfile.replace('/', '.')}")
                        else:
                            logging.warning(f"File {rfile}.py has been modified. Reloading...")
                            page = reload(import_module(f"htdocs.{rfile.replace('/', '.')}"))
                            hf.compute_hash(f"htdocs/{rfile}.py", True)
                    except:
                        socket_closed = True
                        logging.error(f"Unable to load {rfile}.py")
                elif path.exists(f"htdocs/{rfile}") and not path.isfile(f"htdocs/{rfile}"):
                    # Load index file as default
                    rfile += '/' + cfg["default_filename"]

                try:
                    # open file, r => read, b => byte format
                    if python_page is not True:
                        file = open(f"htdocs/{rfile}", "rb")
                        response = file.read()  # Read the input stream into response
                        file.close()  # Close the file once read
                    else:
                        if isinstance(page.render(HTTP(request)), tuple):
                            response = page.render(HTTP(request))[1].encode("utf-8")  # Render the page
                            content_type = page.render(HTTP(request))[0] # Get the MIMEtype
                        else:
                            response = page.render(HTTP(request)).encode("utf-8")  # Render the page
                            content_type = "text/html"  # Default to text/html if not MIMEtype is set

                    if socket_closed is False:
                        logging.info("Found requested resource")
                        logging.info(f"Serving /{rfile}")

                    # 200 To signify the server understood and will fulfill the request
                    header = r.get_response_header(200)
                    if cfg["signature_reporting"]:
                        header += f'Server: {cfg["signature"]}\n'  # Server name
                    # Tells the client to validate their cache on load
                    header += 'Cache-Control: no-cache, must-revalidate\n'
                    if not python_page:
                        header += f'Content-Type: {str(magic.from_file(f"htdocs/{rfile}", mime=True))}\n\n'
                    else:
                        header += f"Content-Type: {content_type}\n\n" # Get MIME from content

                except:
                    if socket_closed is False:
                        logging.info("Unable to find requested resource!")
                    # If unable to read the specified file, assume it does not exist and return 404
                    header = r.get_response_header(404)
                    if cfg["signature_reporting"]:
                        header += f'Server: {cfg["signature"]}\n'  # Server name
                    header += "Content-Type: text/html\n\n"  # MIMEtype set to html

                    response = r.get_response_body(404).encode("utf-8")  # Get the 404 page
                    if response is False:
                        socket_closed = True
                        await writer.drain()
                        writer.close()

                if socket_closed is False:
                    final_response = header.encode("utf-8")
                    final_response += response

                    writer.write(final_response)
                    await writer.drain()
                    writer.close()

        except Exception as e:
            logging.error(f"Exception: {e}")
            logging.debug(traceback.format_exc())
            writer.close()
            await writer.wait_closed()


if __name__ == "__main__":
    hf = HelperFunctions()
    cfg = hf.readcfg()
    logger.Logger(cfg).logging_init()
    hf.load_plugins()
    args = hf.arg_actions()
    server = Server(args)
    loop = asyncio.get_event_loop()
    hf.load_plugins(postload = True)

    try:
        asyncio.run(server.server_main())
    except KeyboardInterrupt:
        loop.stop()
        print("Server stopped via interactive keyboard interrupt")

