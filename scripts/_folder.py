import os
import _root

file_folder = _root.root_abspath()
data_folder = _root.root_abspath('data')

def file_abspath(*dirs):
    return os.path.join(file_folder, *dirs)

def data_abspath(*dirs):
    return os.path.join(data_folder, *dirs)
