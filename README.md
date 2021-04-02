# python-http-server
Very simple python HTTP server
Written in Python 3.9.1. Earlier versions might be supported - try and see what happens

It allows you to serve HTML, CSS and some image files.

## Configuration file
Configuration is stored in `conf.json` file.

* **hostname** - This is the address the server will attempt to bind to.
* **port** - This is the port the server will attempt to bind to.
* **blacklist** - Filename for the IP blacklist. This can be edited while the server is running.
* **logfile** - Filename for the logfile. This is where the server will attempt to write log messages to.
* **default_filename** - This is the default file to be served when the client requests a directory instead of a specific file.
* **logging** - Boolean (true/false) for whether the server will write to the logfile.
