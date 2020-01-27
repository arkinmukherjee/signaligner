import argparse, json
import _root
import _helper



def main(source_dataset, dest_dataset, *, notrim=False):
    # Process arguments to get name of dataset

    source_config = _helper.datasetConfigFilename(source_dataset)
    dest_config = _helper.datasetConfigFilename(dest_dataset)

    source = {}
    dest = {}

    with open(source_config, 'rt') as configfile:
        config = json.load(configfile)
        source['sample_rate'] = config['sample_rate']
        source['start_time_ms'] = config['start_time_ms']

    with open(dest_config, 'rt') as configfile:
        config = json.load(configfile)
        dest['sample_rate'] = config['sample_rate']
        dest['length'] = config['length']
        dest['start_time_ms'] = config['start_time_ms']

    if source['sample_rate'] != dest['sample_rate']:
        _helper.errorExit("Source and dest datasets should have the same sample rate")

    start_sample = ((dest['start_time_ms'] - source['start_time_ms']) / 1000) * source['sample_rate']

    if start_sample != int(start_sample):
        _helper.errorExit("Source and dest datasets are not offset by an integer number of samples")

    start_sample = int(start_sample)
    end_sample = int(start_sample + dest['length'])

    source_labels = _helper.getLabelsLatest(source_dataset)
    if source_labels:
        for session in source_labels:

            session_name = session['session']
            source_name = session['source']
            session_labels = session['labels']
            label_filename = _helper.latestLabelsFilename(dest_dataset, session_name)

            output = ''
            output += ('{"session":"%s", "source": "%s", "labels":[' % (session_name, source_name))
            was_prev = False

            for ll in session_labels:
                label_start = ll['lo']
                label_end = ll['hi']
                label_name = ll['label']
                label = [label_start, label_end, label_name]

                if notrim:
                    output += _helper.activityJSON(label, was_prev)
                    was_prev = True

                elif label_end > start_sample and label_start < end_sample:

                    # Trim label start if needed
                    if label_start < start_sample:
                        label[0] = start_sample

                    # Trim label end if needed
                    if label_end > end_sample:
                        label[1] = end_sample

                    # Start label offset from 0
                    label[0] -= start_sample
                    label[1] -= start_sample

                    output += _helper.activityJSON(label, was_prev)
                    was_prev = True

            output += ']}\n'

            _helper.ensureDirExists(label_filename, True)
            with open(label_filename, 'wt') as labelsfile:
                labelsfile.write(output)
            print('labels added to ', label_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get trimmed labels for sample subrange of a dataset.')
    parser.add_argument('source', type=str, help='Parent dataset to get labels from.', default=None)
    parser.add_argument('dest', type=str, help='Child dataset to trim and copy labels to.', default=None)
    parser.add_argument('--notrim', action='store_true', help='Do not trim parent dataset labels.')
    args = parser.parse_args()

    main(args.source, args.dest, notrim=args.notrim)
