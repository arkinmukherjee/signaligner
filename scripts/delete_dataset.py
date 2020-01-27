import argparse, os, shutil
import _folder, _helper


def main(dataset, *, allfiles=False):
    # Delete the dataset folder
    dataset_folder = _helper.datasetDir(dataset)

    if not os.path.exists(dataset_folder):
        _helper.errorExit('The dataset does not exist ' + dataset_folder)

    shutil.rmtree(dataset_folder)
    print("Deleted dataset ", dataset_folder)

    if allfiles:

        # Delete the labels folder for the given dataset
        labels_folder = _folder.data_abspath(_helper._get_labels_folder(), dataset)

        if os.path.exists(labels_folder):
            shutil.rmtree(labels_folder)
            print("Deleted labels for the dataset ", labels_folder)

        # Delete exported labels files for the given dataset
        export_file = _helper.exportFilename(dataset)
        if os.path.exists(export_file):
            os.remove(export_file)
            print("Deleted exported labels file for the dataset ", export_file)

        # Delete all mturk submissions for the given dataset
        mturk_submit_folder = _folder.data_abspath('mturksubmit')
        if os.path.exists(mturk_submit_folder):
            mturk_session_ids = os.listdir(mturk_submit_folder)

            for session in mturk_session_ids:
                session_datasets = os.listdir(os.path.join(mturk_submit_folder, session))
                if dataset in session_datasets:
                    dataset_folder = os.path.join(mturk_submit_folder, session, dataset)
                    shutil.rmtree(dataset_folder)

            print("Deleted mturk submissions for the dataset ", dataset)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete a dataset and its stored labels')
    parser.add_argument('dataset', type=str, help='Name of dataset to delete.')
    parser.add_argument('--allfiles', action='store_true', help='Delete all files related to the dataset: labels, mturk submissions, exported files.')
    args = parser.parse_args()
    main(args.dataset, allfiles=args.allfiles)
