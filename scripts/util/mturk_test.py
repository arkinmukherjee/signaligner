# Checks if the setup for the mTurk test is configured correctly.

import argparse, csv, io, json, os, sys
import _root
import _folder, _helper



parser = argparse.ArgumentParser(description='Check if the mTurk setup is ready.')
parser.add_argument('--file', type=str, help='Log file name. (default: playlog)', default="playlog")
parser.add_argument('--folder', type=str, help='Labels folder name. (default: playlog)', default="labels")
args = parser.parse_args()



def checkPlaylogFileEmpty():
    if args.file == None:
        path = _folder.data_abspath(args.file)
    else:
        path = args.file
    # Opens the file to check if its empty.
    if os.path.exists(path):
        if os.path.getsize(path) > 0:
            return "[FAIL] Log file is not empty."
        else :
            return "[PASS] Log file exists and is empty."
    else:
        return "[FAIL] Log file doesn't exists."

def getSubDirectories(foldername):
    subdirectories = []
    for root, dirs, files in os.walk(foldername):
        subdirectories += dirs
        break
    return subdirectories


def get_files_from_path(path):
    items = os.listdir(path)
    return [item for item in items if item.endswith("labels.latest.json")]


def checkTruthLabelFolder():
    subdirectories = getSubDirectories("labels")
    for subdir in subdirectories:
        path_to_truth_folder = os.path.join(args.folder, subdir, "TRUTH")
        dataset_name = subdir
        if os.path.isdir(path_to_truth_folder) and os.path.exists(path_to_truth_folder):
            files = get_files_from_path(path_to_truth_folder)
            file_paths = [os.path.join(args.folder, subdir, "TRUTH", filename) for filename in files]
            if len(files):
                for filePath in file_paths:
                    with open(filePath) as f:
                        data = json.load(f)
                        if data.get("source") == "Truth":
                            pass
                        else:
                            return "[FAIL] "+dataset_name+" Doesnt contain correct json in the Truth folder."
            else:
                return "[FAIL] Truth file doesn't exist for - "+dataset_name
        else:
            return "[FAIL] Truth folder doesn't exist for - "+dataset_name
    return "[PASS] Truth folder set correctly for all the datasets."


if __name__ == "__main__":
    # Test playlog
    print("1. Test playlog file setup -")
    print('\t', checkPlaylogFileEmpty())
    print("2. Test truth files setup in lables -")
    print('\t', checkTruthLabelFolder())
