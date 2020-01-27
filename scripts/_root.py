import os, sys

_root_folder = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

def root_abspath(*dirs):
    return os.path.join(_root_folder, *dirs)

sys.path.insert(0, os.path.join(_root_folder, 'scripts'))
