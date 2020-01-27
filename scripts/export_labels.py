import argparse, csv, os, sys, json, re
import _root
import _helper


def main(dataset):
    # Read start time from config
    with open(_helper.datasetConfigFilename(dataset), 'rt') as json_file:
        data = json.load(json_file)
        start_time_ms = data['start_time_ms']
        sample_rate = data['sample_rate']

    # Read the last stored label of each unique player or session
    session_labels = _helper.getLabelsLatest(dataset)

    # Write to csv
    csvOutputPath = _helper.exportFilename(dataset)
    _helper.ensureDirExists(csvOutputPath, True)
    with open(csvOutputPath, 'wt') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['START_TIME', 'STOP_TIME', 'PREDICTION', 'SOURCE', 'SESSION'])

        for session_data in session_labels:
            session = session_data['session']
            source = session_data['source']
            for label in session_data['labels']:
                start_time_in_ms = start_time_ms + label['lo'] * 1000.0 / sample_rate
                start_time = _helper.timeMillisecondToTimeString(start_time_in_ms)
                stop_time_in_ms = start_time_ms + label['hi'] * 1000.0 / sample_rate
                stop_time = _helper.timeMillisecondToTimeString(stop_time_in_ms)
                prediction = label['label']
                writer.writerow([start_time, stop_time, prediction, source, session])

    print('output written to', csvOutputPath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a json labels file to a csv time stamps.')
    parser.add_argument('dataset', type=str, help='Name of the dataset')
    args = parser.parse_args()

    main(args.dataset)
