import argparse, calendar, datetime, csv, gzip, json, math, re, os, sys
import _root
import _folder, _helper



SUBSAMPLE = 4
TILE_SIZE = 1024

DEFAULT_MAGNITUDE = 8



# Check if range arg was given in the correct format and extract indices
def parseRange(what, rng):
    groups = re.match(r'(\d*)(-?)(\d*)', rng).groups()

    if groups[0] == '' and groups[1] == '' and groups[2] == '':
        _helper.errorExit('Argument for ' + what + ' range has invalid form. Valid forms include: "1" or "1-3" or "-3" or "1-"')
    elif groups[0] != '' and groups[1] == '' and groups[2] == '':
        start = int(groups[0])
        end = start
    else:
        start = int(groups[0]) if groups[0] != '' else None
        end = int(groups[2]) if groups[2] != '' else None

    if start is not None and end is not None:
        if end < start:
            _helper.errorExit('End ' + what + ' index must be >= than start ' + what + ' index')

    return start, end

def strRange(what, start, end):
    if start == end:
        return '__' + what + '_' + str(start)
    else:
        return '__' + what + '_' + (str(start) if start else '') + 'to' + (str(end) if end else '')

def rangesample(sample, slen):
    ret = [None] * slen

    for s in sample:
        for ii in range(slen):
            if s[ii] != None:
                if ret[ii] == None:
                    ret[ii] = (s[ii], s[ii])
                else:
                    ret[ii] = (min(s[ii], ret[ii][0]),  max(s[ii], ret[ii][1]))

    return ret

def write_startfile(f, ss, fn):
    f.write('{')
    f.write('"meta":{"subsample":%d,"file":[\"%s\"]},' % (ss, fn))
    f.write('"data":[')

def write_sample(f, smp, prev, slen):
    if prev:
        f.write(',')

    f.write('[' + ','.join([(('[%0.3f,%0.3f]' % rng) if rng != None else '[0,0]') for rng in smp]) + ']')

def write_endfile(f):
    f.write(']')
    f.write('}')



def main(filenames, *, name=None, labelfilenames=None, zoom=None, mag=DEFAULT_MAGNITUDE, sample=None, day=None):
    if len(filenames) > 1 and not name:
        _helper.errorExit('Must specify a custom dataset --name when importing multiple files')

    if mag <= 0:
        _helper.errorExit('magnitude must be positive')

    if sample is not None and day is not None:
        _helper.errorExit('Can only provide one of --sample and --day')

    start_sample, end_sample = None, None
    if sample is not None:
        start_sample, end_sample = parseRange('sample', sample)

    start_day, end_day = None, None
    if day is not None:
        start_day, end_day = parseRange('day', day)



    # load labels
    if not labelfilenames:
        labelfilenames = [
            _folder.file_abspath('common', 'labels_test.csv'),
            _folder.file_abspath('common', 'labels_unknown.csv')
        ]

    labels = []
    labels_names = set()

    for labelfile in labelfilenames:
        print('Reading labels from %s...' % labelfile)

        with open(labelfile, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)

            if set(reader.fieldnames) != set(['label', 'red', 'green', 'blue']):
                _helper.errorExit('Incorrect label csv headers')

            for row in reader:
                label_name = row['label'].strip()
                rr = float(row['red'].strip())
                gg = float(row['green'].strip())
                bb = float(row['blue'].strip())

                if re.search('[^\w\- ]', label_name, re.ASCII):
                    _helper.errorExit('Only alphanumeric, underscore, dash, and space allowed in label names: ' + label_name)
                if label_name in labels_names:
                    _helper.errorExit('Duplicate label: ' + label_name)

                labels.append((label_name, rr, gg, bb))
                labels_names.add(label_name)



    # process arguments
    signal_names = []
    for filename in filenames:
        signal_names.append(_helper.makeIdFromFilename(filename))
    if len(signal_names) != len(set(signal_names)):
        _helper.errorExit('Duplicate signal names')

    if name:
        if not _helper.checkId(name, False):
            _helper.errorExit('Only alphanumeric and underscore allowed in dataset names')
        dataset = name
    else:
        dataset = signal_names[0]

    if start_sample is not None or end_sample is not None:
        dataset = dataset + strRange('sample', start_sample, end_sample)
    if start_day is not None or end_day is not None:
        dataset = dataset + strRange('day', start_day, end_day)

    out_folder = _helper.datasetDir(dataset)
    tile_folder = _helper.datasetTileDir(dataset)

    if os.path.exists(out_folder):
        _helper.errorExit('Please remove output folder ' + out_folder)

    print('Using output folder ' + out_folder)

    _helper.ensureDirExists(out_folder, False)
    _helper.ensureDirExists(tile_folder, False)



    # read in data
    print('reading header...')



    # open files
    csvfiles = []
    for filename in filenames:
        if filename.endswith('.gz'):
            use_open = gzip.open
        else:
            use_open = open

        csvfiles.append(use_open(filename, 'rt'))



    # read headers
    files_start_ms = []
    dataset_rate = None

    for filename, csvfile in zip(filenames, csvfiles):
        header_rate, header_start_ms = _helper.process_actigraph_header(csvfile)

        if dataset_rate == None:
            dataset_rate = int(header_rate)
        elif dataset_rate != int(header_rate):
            _helper.errorExit('Multiple sample rates found')

        files_start_ms.append(header_start_ms)



    # determine sample range
    dataset_start_ms = min(files_start_ms)
    dataset_start_date = datetime.datetime.utcfromtimestamp(dataset_start_ms / 1000).date()

    if start_sample is not None or end_sample is not None:
        pass

    if start_day is not None or end_day is not None:
        if start_day is not None:
            output_min_ms = 1000 * calendar.timegm((dataset_start_date + datetime.timedelta(days=(start_day - 1))).timetuple())
            start_sample = (max(output_min_ms, dataset_start_ms) - dataset_start_ms) * dataset_rate / 1000
            if start_sample != int(start_sample):
                _helper.errorExit('day start sample error')
            start_sample = int(start_sample)
        else:
            start_sample = None

        if end_day is not None:
            output_max_ms = 1000 * calendar.timegm((dataset_start_date + datetime.timedelta(days=(end_day))).timetuple())
            end_sample = (output_max_ms - dataset_start_ms) * dataset_rate / 1000
            if end_sample != int(end_sample):
                _helper.errorExit('day end sample error')
            end_sample = int(end_sample)
        else:
            end_sample = None



    # determine starting day index
    start_day_index = 1
    if start_sample:
        start_day_index = 1 + (datetime.datetime.utcfromtimestamp(dataset_start_ms / 1000 + start_sample / dataset_rate).date() - dataset_start_date).days



    # print header summary
    if len(filenames) > 1:
        for filename, signalname, file_start_ms in zip(filenames, signal_names, files_start_ms):
            print('file start:   ', _helper.timeMillisecondToTimeString(file_start_ms), signalname, filename)
    print('input start:  ', _helper.timeMillisecondToTimeString(dataset_start_ms), dataset)



    # read data
    sample_len = 3 * len(filenames)
    sample_data = []

    min_smp = 1e100
    max_smp = -1e100

    for fileindex, (filename, file_start_ms, csvfile) in enumerate(zip(filenames, files_start_ms, csvfiles)):
        print('reading ' + filename + '...')

        # Checks if csv header is absent and adds the header if needed
        csvstartpos = csvfile.tell()
        firstrow = next(csvfile)
        csvfile.seek(csvstartpos)

        fieldnames = None
        if 'Accelerometer' not in firstrow:
            # No headers present
            DEFAULT_FIELDNAMES = ['Timestamp', 'Accelerometer X', 'Accelerometer Y', 'Accelerometer Z']
            no_of_fields = len(firstrow.split(','))
            if no_of_fields == 4:
                fieldnames = DEFAULT_FIELDNAMES
            elif no_of_fields == 3:
                fieldnames = DEFAULT_FIELDNAMES[1:]
            else:
                _helper.errorExit('missing header has unrecognized number of fields')

        if fieldnames != None:
            _helper.warning('input file missing field names, using ' + ','.join(fieldnames))

        reader = csv.DictReader(csvfile, fieldnames=fieldnames)

        if 'Timestamp' in reader.fieldnames:
            _helper.warning('input file has Timestamp field, but it will be ignored')



        # process rows
        reader_sample_index = 0

        sample_offset = (file_start_ms - dataset_start_ms) * dataset_rate / 1000
        if sample_offset != int(sample_offset):
            _helper.errorExit('sample offset error')
        sample_offset = int(sample_offset)

        if start_sample != None:
            sample_offset -= start_sample

        for row in reader:
            data_sample_index = reader_sample_index + sample_offset
            reader_sample_index += 1

            if data_sample_index < 0:
                continue
            if end_sample != None and data_sample_index >= end_sample - (start_sample if start_sample != None else 0):
                break

            x = float(row['Accelerometer X'])
            y = float(row['Accelerometer Y'])
            z = float(row['Accelerometer Z'])

            min_smp = min(min_smp, x, y, z)
            max_smp = max(max_smp, x, y, z)

            while data_sample_index >= len(sample_data):
                sample_data.append([None] * sample_len)

            sample_data[data_sample_index][3 * fileindex + 0] = x
            sample_data[data_sample_index][3 * fileindex + 1] = y
            sample_data[data_sample_index][3 * fileindex + 2] = z

            if reader_sample_index % (60 * 60 * dataset_rate) == 0:
                print('read %d hours...' % (reader_sample_index / (60 * 60 * dataset_rate)))

    if min_smp < -mag or mag < max_smp:
        _helper.warning('sample exceeds magnitude')
    output_start_ms = dataset_start_ms
    if start_sample != None:
        output_start_ms_offset = start_sample * 1000 / dataset_rate
        if output_start_ms_offset != int(output_start_ms_offset):
            _helper.errorExit('output start offset sample error')
        output_start_ms += int(output_start_ms_offset)
    output_end_ms = output_start_ms + (len(sample_data) - 1) * 1000 / dataset_rate



    # figure out max zoom level, if needed
    if zoom is None:
        for zz in range(10):
            zoom = zz
            if len(sample_data) / math.pow(SUBSAMPLE, zz + 1) <= 2 * TILE_SIZE:
                break



    # print summary
    print('length:       ', len(sample_data))
    print('rate:         ', dataset_rate)
    print('max zoom:     ', zoom)
    print('output start: ', _helper.timeMillisecondToTimeString(output_start_ms))
    print('output end:   ', _helper.timeMillisecondToTimeString(output_end_ms))



    # write tiles
    for zoom_level in range(zoom + 1):
        print('writing zoom %d...' % zoom_level)

        zoom_subsample = SUBSAMPLE ** zoom_level
        zoom_tile_size = TILE_SIZE * zoom_subsample

        ntiles = int(len(sample_data) / zoom_tile_size)
        if len(sample_data) % zoom_tile_size != 0:
            ntiles += 1

        for tt in range(ntiles):
            tile_id = 'z%02dt%06d' % (zoom_level, tt)

            outfilename = os.path.join(tile_folder, tile_id + '.json')

            with open(outfilename, 'wt') as outfile:
                write_startfile(outfile, zoom_subsample, dataset + ':' + tile_id)

                prev = False
                for ss in range(tt * TILE_SIZE, (tt + 1) * TILE_SIZE + 1):
                    rangesmp = sample_data[ss * zoom_subsample:(ss + 1) * zoom_subsample]
                    write_sample(outfile, rangesample(rangesmp, sample_len), prev, sample_len)
                    prev = True

                write_endfile(outfile)

            if (tt + 1) % 1000 == 0:
                print('wrote %d tiles...' % (tt + 1))



    print('writing origin...')

    outfilename = _helper.datasetOriginFilename(dataset)

    with open(outfilename, 'wt') as outfile:
        outfile.write("{\n")
        outfile.write('    "origin": %s\n' % json.dumps(filenames))
        outfile.write('}\n')



    print('writing config...')

    outfilename = _helper.datasetConfigFilename(dataset)

    with open(outfilename, 'wt') as outfile:
        outfile.write('{\n')
        outfile.write('    "title": "%s",\n' % dataset)
        outfile.write('    "tile_size": %d,\n' % TILE_SIZE)
        outfile.write('    "tile_subsample": %d,\n' % SUBSAMPLE)
        outfile.write('    "zoom_max": %d,\n' % zoom)
        outfile.write('    "length": %d,\n' % len(sample_data))
        outfile.write('    "start_time_ms": %s,\n' % output_start_ms)
        outfile.write('    "sample_rate": %d,\n' % dataset_rate)
        outfile.write('    "start_day_idx": %d,\n' % start_day_index)
        outfile.write('    "magnitude": %d,\n' % mag)
        outfile.write('    "signals": ["%s"],\n' % ('", "'.join(signal_names)))
        outfile.write('    "labels": [\n')
        for ii, (ll, rr, gg, bb) in enumerate(labels):
            outfile.write('        { "label": "%s", "color": [ %0.2f, %0.2f, %0.2f ] }%s\n' % (ll, rr, gg, bb, ',' if ii + 1 < len(labels) else ''))
        outfile.write('    ]\n')
        outfile.write('}\n')



    print('dataset written to ' + out_folder)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a csv file to a dataset.')
    parser.add_argument('filenames', type=str, help='CSV file(s) to read from.', nargs='+')
    parser.add_argument('--name', type=str, help='Custom dataset name.', default=None)
    parser.add_argument('--labelfilenames', type=str, help='Custom label csv(s).', default=None, nargs='+')
    parser.add_argument('--zoom', type=int, help='Maximum zoom level.', default=None)
    parser.add_argument('--mag', type=int, help='Magnitude of signal (default %d).' % DEFAULT_MAGNITUDE, default=DEFAULT_MAGNITUDE)
    parser.add_argument('--sample', type=str, help='Sample index range to output.', default=None)
    parser.add_argument('--day', type=str, help='Day index range to output.', default=None)
    args = parser.parse_args()

    main(args.filenames, name=args.name, labelfilenames=args.labelfilenames, zoom=args.zoom, mag=args.mag, sample=args.sample, day=args.day)
