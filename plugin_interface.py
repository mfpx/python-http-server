from abc import abstractmethod

class Plugin:
    """
    Plugin interface.
        Methods:
        :param init: must be implemented. It is called when the plugin is loaded.
        :param init_finish: must be implemented. It is called when the plugin loading is finished. It may be empty.
    """

    @abstractmethod
    def init(self):
        """
        Called when the plugin is being loaded.
        """
        pass

    @abstractmethod
    def init_finish(self):
        """
        Called when the plugin has finished loading. Optional.
        """
        pass

