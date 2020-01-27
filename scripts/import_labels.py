import argparse, csv, json, os, sys
import _root
import _helper



VALID_SOURCES = ['Algo', 'Expert', 'Mturk', 'Notes', 'Player', 'Truth']



def trimActivity(activity, trim, lo, hi):
    if trim:
        activity[0] = max(activity[0], lo)
        activity[1] = min(activity[1], hi)

    return activity[1] > activity[0]



def main(dataset, filename, *, source=None, session=None, stdout=False, trim=False, qcfix=False):
    dataset_config_filename = _helper.datasetConfigFilename(dataset)

    if not os.path.exists(dataset_config_filename):
        _helper.errorExit('could not find dataset config file: ' + dataset_config_filename)

    with open(dataset_config_filename, 'rt') as configfile:
        config = json.load(configfile)

    sample_rate = config['sample_rate']
    length = config['length']

    start_millisecond = config['start_time_ms']
    print('start time:', _helper.timeMillisecondToTimeString(start_millisecond))

    FORMAT_NOTES = 'NOTES'
    FORMAT_NOTES_TIME_FORMAT = '%a %b %d %H:%M:%S %Z %Y'
    FORMAT_NOTES_LENGTH_SECONDS = 10 # how long a note label should try to be
    FORMAT_ACTIVITY_GROUP = 'ACTIVITY_GROUP'
    FORMAT_PREDICTION = 'PREDICTION'
    FORMAT_PREDICTED = 'PREDICTED'
    FORMAT_PREDICTED_LABEL_SECONDS = 30

    with open(filename, 'rt') as csvfile:
        reader = csv.DictReader(csvfile)

        # check if file contains session and source columns
        if 'SESSION' in reader.fieldnames and 'SOURCE' in reader.fieldnames and (session or source):
            _helper.errorExit('Session and source info detected in file, will be used instead of given arguments.')
        elif ('SESSION' in reader.fieldnames or 'SOURCE' in reader.fieldnames) and ('SESSION' not in reader.fieldnames or 'SOURCE' not in reader.fieldnames):
            _helper.errorExit('Must provide both session and source fields in file or neither.')
        elif (session is None or source is None) and (session or source):
            _helper.errorExit('Must provide both session and source arguments or neither.')

        if session is None and 'SESSION' not in reader.fieldnames:
            _helper.errorExit("No session argument provided and no session info in file. Cannot import labels.")
        if source is None and 'SOURCE' not in reader.fieldnames:
            _helper.errorExit('No source argument provided and no source info in file. Cannot import labels.')

        use_source_session_from_file = ('SESSION' in reader.fieldnames and 'SOURCE' in reader.fieldnames)

        # figure out format
        format = None
        format_meta = None
        if ('TIME' in reader.fieldnames) and ('TAG' in reader.fieldnames) and ('NOTE' in reader.fieldnames):
            format = FORMAT_NOTES
        elif ('START_TIME' in reader.fieldnames) and ('STOP_TIME' in reader.fieldnames) and ('ACTIVITY_GROUP.y' in reader.fieldnames):
            format = FORMAT_ACTIVITY_GROUP
        elif ('START_TIME' in reader.fieldnames) and ('STOP_TIME' in reader.fieldnames) and ('PREDICTION' in reader.fieldnames):
            format = FORMAT_PREDICTION
        elif ('HEADER_START_TIME' in reader.fieldnames) and ('PREDICTED' in reader.fieldnames):
            format = FORMAT_PREDICTED
            # get label names from header
            format_meta = []
            for field in reader.fieldnames[2:]:
                label = field.split('_')
                if label[0] != 'PROB' or len(label) < 2:
                    sys.stderr.write('unrecognized field in header: expected PROB_...\n')
                    sys.exit(-1)
                label = ' '.join([word.capitalize() for word in label[1:]])
                format_meta.append(label)
        else:
            sys.stderr.write('could not determine format from header fields\n')
            sys.exit(-1)

        sys.stderr.write('detected %s format\n' % format)
        if use_source_session_from_file:
            sys.stderr.write('reading source and session from file\n')
        else:
            sys.stderr.write('using source %s and session %s\n' % (source, session))



        # process rows
        sessions = set()
        session_labels = {}
        session_sources = {}

        # this will keep track of the time the last label started to make sure they are sorted
        last_label_start_millisecond = 0

        for row in reader:
            # figure out sample range
            if format == FORMAT_NOTES:
                label_start_millisecond = _helper.timeStringToTimeMillisecond(row['TIME'], FORMAT_NOTES_TIME_FORMAT)
                label_stop_millisecond = label_start_millisecond + FORMAT_NOTES_LENGTH_SECONDS * 1000
                label_value = row['TAG']
                label_detail = row['NOTE']
            elif format == FORMAT_ACTIVITY_GROUP:
                label_start_millisecond = _helper.timeStringToTimeMillisecond(row['START_TIME'], _helper.DATE_FORMAT_YMD)
                label_stop_millisecond = _helper.timeStringToTimeMillisecond(row['STOP_TIME'], _helper.DATE_FORMAT_YMD)
                label_value = row['ACTIVITY_GROUP.y']
                label_detail = None
            elif format == FORMAT_PREDICTION:
                label_start_millisecond = _helper.timeStringToTimeMillisecond(row['START_TIME'], _helper.DATE_FORMAT_YMD)
                label_stop_millisecond = _helper.timeStringToTimeMillisecond(row['STOP_TIME'], _helper.DATE_FORMAT_YMD)
                label_value = row['PREDICTION']
                label_detail = None
            elif format == FORMAT_PREDICTED:
                if int(row['PREDICTED']) >= len(format_meta):
                    sys.stderr.write('PREDICTED index out of range')
                    sys.exit(-1)
                label_start_millisecond = _helper.timeStringToTimeMillisecond(row['HEADER_START_TIME'], _helper.DATE_FORMAT_YMD)
                label_stop_millisecond = label_start_millisecond + 1000 * FORMAT_PREDICTED_LABEL_SECONDS
                label_value = format_meta[int(row['PREDICTED'])]
                label_detail = None
            else:
                _helper.errorExit('unknown format error')

            # check labels are in order
            if label_start_millisecond <= last_label_start_millisecond:
                _helper.errorExit('label start times not sorted')
            last_label_start_millisecond = label_start_millisecond

            # apply fix for QC end times, if needed
            if qcfix:
                if label_stop_millisecond % 100 == 88:
                    label_stop_millisecond += 12

            # convert from ms to sample
            label_start_sample_thousand = (label_start_millisecond - start_millisecond) * sample_rate
            label_stop_sample_thousand = (label_stop_millisecond - start_millisecond) * sample_rate

            if label_start_sample_thousand % 1000 != 0 or label_stop_sample_thousand % 1000 != 0:
                _helper.errorExit('sample precision error')

            label_start_sample = (label_start_sample_thousand / 1000)
            label_stop_sample = (label_stop_sample_thousand / 1000)

            # figure out source and session
            if use_source_session_from_file:
                current_session = row['SESSION']
                current_source = row['SOURCE']
            else:
                current_session = session
                current_source = source

            if current_source not in VALID_SOURCES:
                _helper.errorExit('unrecognized source: ' + source)

            # for notes, go back and make sure any previous note doesn't overlap this one
            if format == FORMAT_NOTES:
                if current_session in sessions and len(session_labels[current_session]) > 0:
                    session_labels[current_session][-1][1] = min(session_labels[current_session][-1][1], label_start_sample)

            # append this label to the session
            if current_session not in sessions:
                sessions.add(current_session)
                session_labels[current_session] = []
                session_sources[current_session] = current_source

            if session_sources[current_session] != current_source:
                _helper.errorExit('Session with multiple sources detected.')

            session_labels[current_session].append([label_start_sample, label_stop_sample, label_value, label_detail])



        # write labels out
        for session in sessions:
            labels = session_labels[session]
            source = session_sources[session]

            # this will be used to merge adjacent time windows that have the same label
            last_activity = None

            # keep track of information about labels output
            was_prev = False
            any_outside = False
            any_far_outside = False

            output = ''
            output += '{"session":"%s", "source": "%s", "labels":[' % (session, source)

            for label_start_sample, label_stop_sample, label_value, label_detail in session_labels[session]:
                # see if the label extends beyond the dataset time
                if label_start_sample < 0 or length < label_stop_sample:
                    any_outside = True
                if label_start_sample < 0 - 0.1 * length or length + 0.1 * length < label_stop_sample:
                    any_far_outside = True

                # merge adjacent labels that match
                if not last_activity:
                    last_activity = [label_start_sample, label_stop_sample, label_value, label_detail]
                elif last_activity[1] == label_start_sample and last_activity[2] == label_value and last_activity[3] == label_detail:
                    last_activity[1] = label_stop_sample
                else:
                    if trimActivity(last_activity, trim, 0, length):
                        output += _helper.activityJSON(last_activity, was_prev)
                        was_prev = True
                    last_activity = [label_start_sample, label_stop_sample, label_value, label_detail]

            # account for any remaining label
            if last_activity:
                if trimActivity(last_activity, trim, 0, length):
                    output += _helper.activityJSON(last_activity, was_prev)
                    was_prev = True

            output += ']}\n'

            # display warnings about labels
            if any_far_outside:
                _helper.warning('label found FAR OUTSIDE signal in ' + session)
            elif any_outside:
                _helper.warning('label found outside signal in ' + session)

            # do output
            if stdout:
                sys.stdout.write(output)

            else:
                labels_filename = _helper.latestLabelsFilename(dataset, session)
                with open(_helper.ensureDirExists(labels_filename, True), 'wt') as labelsfile:
                    labelsfile.write(output)

                print('labels added to', labels_filename)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import algorithm labels.')
    parser.add_argument('dataset', type=str, help='Name of dataset to use.')
    parser.add_argument('filename', type=str, help='CSV file to read from.')
    parser.add_argument('--source', type=str, help='Label source (' + (', '.join(VALID_SOURCES)) + ')', default=None)
    parser.add_argument('--session', type=str, help='Session ID.', default=None)
    parser.add_argument('--stdout', action='store_true', help='Write output to stdout.')
    parser.add_argument('--trim', action='store_true', help='Trim labels to signal duration.')
    parser.add_argument('--qcfix', action='store_true', help='Fix for QC output.')
    args = parser.parse_args()

    main(args.dataset, args.filename, source=args.source, session=args.session, stdout=args.stdout, trim=args.trim, qcfix=args.qcfix)
