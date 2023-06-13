"""Base class for descriptors"""

from abc import ABCMeta, abstractmethod
import numpy as np
import pyscal.core as pc
import glob


class Descriptor(metaclass=ABCMeta):
    """Base class for descriptors.

    This abstract class specifies an interface for all descriptor classes and
    provides basic common methods.
    """

    def __init__(self, setupFile):
        self.list_files = self._list_files()
        self.setupFile = setupFile

    @abstractmethod
    def _read_setup(self):
        """Read setup file and assign variables"""
        pass

    def _list_files(self):
        """List compatible files in 'Input' directory and read them"""
        return glob.glob('Input/**/*.trj', recursive=True)

    @abstractmethod
    def _compute_descriptors(self):
        """Compute descriptors using the different methods and properties from setup file"""
        pass

    @abstractmethod
    def _write_to_file(self):
        """Save the computed descriptors to files in the 'Descriptors' directory"""
        pass