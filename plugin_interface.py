from abc import abstractmethod

"""
Plugin interface.
- Methods
    - `init` must be implemented. It is called when the plugin is loaded.
    - `init_finish` must be implements. It is called when the plugin loading is finished. It may be empty.
"""
class Plugin:

    """
    Called when the plugin is being loaded.
    """
    @abstractmethod
    def init(self):
        pass

    """
    Called when the plugin has finished loading. Optional.
    """
    @abstractmethod
    def init_finish(self):
        pass

