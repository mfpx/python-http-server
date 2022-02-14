# python-http-server
Very simple python HTTP server<br />
Written in Python 3.10.2. Earlier versions might be supported - try and see what happens. Originally written in 3.9.2, and that is a known working version.

It allows you to serve HTML, CSS and some image files. Later versions will have support for all major MIME types.

[![Python HTTP Server](https://github.com/mfpx/python-http-server/actions/workflows/python-app.yml/badge.svg)](https://github.com/mfpx/python-http-server/actions/workflows/python-app.yml)
[![codecov](https://codecov.io/gh/mfpx/python-http-server/branch/main/graph/badge.svg?token=5BTTCZGJ2E)](https://codecov.io/gh/mfpx/python-http-server)

## Configuration file
Configuration is stored in `conf.yml` file.
Note: Configuration is being migrated from `JSON` to `YAML` to support comments.
There is a converter (`converter.py`) to automate the migration process. It will (might) be removed in the future.

* **hostname** - This is the address the server will attempt to bind to.
* **port** - This is the port the server will attempt to bind to.
* **blacklist** - Filename for the IP blacklist. This can be edited while the server is running.
* **logfile** - Filename for the logfile. This is where the server will attempt to write log messages to.
* **logfile_maxlines** - Integer, number of lines to log before rotating the logfile to a new one.
* **default_filename** - This is the default file to be served when the client requests a directory instead of a specific file.
* **blacklist_rcode** - Specifies which file (HTTP status code) to use when responding to a blacklisted client, this file must be present in *http_responses*.
* **logging** - Boolean (true/false) for whether the server will write to the logfile.
* **use_encryption** - Boolean(true/false) for whether the server will use SSL/TLS encryption
* **strict_cert_validation** - Boolean(true/false) for whether the server will allow the usage of self-signed or otherwise "invalid" certificates.
* **path_to_cert** - Path to the SSL certificate. Won't be used if *use_encryption* is set to *false*.
* **path_to_key** - Path to the SSL certificate key. Won't be used if *use_encryption* is set to *false*.

## SSL Configuration

This feature is highly experimental and self-signed certificates might cause the server to crash. There is a self-signed certificate included for ease of testing, it's located in *certs*. You can use self-signed certificates by setting *strict_cert_validation* to *false*.<br />
Accessing the server running in SSL through a non-SSL connection, will also cause the server to die if *strict_cert_validation* is set to *true*.<br /><br />
In order to use SSL, specify the certificate location in *conf.yml* and set *use_encryption* to *true*.<br />
You might also want to change the server port to something other than 80, the default SSL port is 443.

## CLI arguments

There are a couple of arguments available when running the server through CLI.<br />
* **-h** - This will simply print the available arguments.
* **-i/--host** - This allows you to specify the hostname to bind to.
* **-p/--port** - This allows you to specify the port to bind to.
* **-c/--custom-config** - This allows you to specify a different configuration file.
