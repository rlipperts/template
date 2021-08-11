"""
Provides the top-level load function to users without having to import the loader explicitly.
Additionally, this hides internal functions of the loader.
"""
from .loader import load, load_dict, BadFormatError # NOQA
