from plugin_interface import Plugin

PLUGIN_DATA = {
    "name": "Example Plugin", # Name of the plugin
    "version": "1.0.0", # Version of the plugin
    "author": "David Stumbra", # Author of the plugin
    "meta": { # Meta data for the plugin
        "initclass": "PluginInit_ExamplePlugin" # Optional. This is used if reflection fails to find the init function
    }
}

"""
Init class must start with "PluginInit_"
"""
class PluginInit_ExamplePlugin(Plugin):
    def init(self): # This function is called when the plugin is loaded
        print("This is an example plugin!")