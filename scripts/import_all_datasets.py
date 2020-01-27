import argparse, subprocess, os
import _root
import _folder, _helper
import import_dataset



def main(foldername):
    if os.path.isfile(foldername):
        _helper.errorExit('Must be a folder, not an individual file')

    # find all the datasets to import
    datasets = []

    for item in os.listdir(foldername):
        itempath = os.path.abspath(os.path.join(foldername, item))
        if os.path.isfile(itempath):
            if _helper.isFilenameDatasetImportable(itempath):
                datasets.append((_helper.makeIdFromFilename(itempath), [itempath]))
        elif os.path.isdir(itempath):
            subitems = _helper.findDatasetImportableFilesRecursively(itempath)
            if len(subitems) > 0:
                datasets.append((_helper.makeIdFromFilename(itempath), subitems))

    # try to import all the daasets
    for name, files in datasets:
        if os.path.exists(_helper.datasetDir(name)):
            print('Dataset %s exists, skipping.' % name)
        else:
            print('Importing dataset %s.' % name)
            import_dataset.main(files, name=name)
        print()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert multiple csv files to a dataset.')
    parser.add_argument('folder', type=str, help='Path of search for files and folder to import to datasets.')
    args = parser.parse_args()
    main(args.folder)
