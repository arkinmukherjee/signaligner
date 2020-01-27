import argparse, calendar, datetime, csv, gzip, math, re, os, sys, time
import _root
import _helper

def main(filename, outfolder):
    if filename.endswith('.gz'):
        use_open = gzip.open
    else:
        use_open = open

    with use_open(filename, 'rt') as csvfile:
        header_rate, header_start_ms = _helper.process_actigraph_header(csvfile)

        header_start_sec = header_start_ms / 1000
        if header_start_sec != int(header_start_sec):
            _helper.errorExit('start time can only have second precision')
        header_start_sec = int(header_start_sec)

        csv_header = csvfile.readline().strip()

        if csv_header != 'Accelerometer X,Accelerometer Y,Accelerometer Z':
            _helper.errorExit('unrecognized CSV header: only "Accelerometer X,Accelerometer Y,Accelerometer Z" supported')

        tm = datetime.datetime.utcfromtimestamp(header_start_sec)
        tm_sample = 0

        outfile = None

        for row in csvfile:
            tm_msec = int(1000 * tm_sample / header_rate + 0.5)

            if outfile == None:
                outfilecsvname = 'NONE-NONE-NA.NONE-NONE.%04d-%02d-%02d-%02d-%02d-%02d-%03d-P0000.sensor.csv' % (tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second, tm_msec)
                outfilename = os.path.join(outfolder, 'default', 'MasterSynced', '%04d' % tm.year, '%02d' % tm.month, '%02d' % tm.day, '%02d' % tm.hour, outfilecsvname)
                print('Create new hourly file: %s' % outfilecsvname)

                outfile = open(_helper.ensureDirExists(outfilename, True), 'wt')
                outfile.write('HEADER_TIME_STAMP,X_ACCELERATION_METERS_PER_SECOND_SQUARED,Y_ACCELERATION_METERS_PER_SECOND_SQUARED,Z_ACCELERATION_METERS_PER_SECOND_SQUARED\n')

            tm_str = '%04d-%02d-%02d %02d:%02d:%02d.%03d' % (tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second, tm_msec)
            outfile.write(tm_str + ',' + (','.join([(e if ('.' in e) else (e + '.0')) for e in row.strip().split(',')])) + '\n')

            tm_sample += 1
            if tm_sample == header_rate:
                prev_tm = tm
                tm = tm + datetime.timedelta(seconds=1)
                tm_sample = 0

                if prev_tm.year != tm.year or prev_tm.month != tm.month or prev_tm.day != tm.day or prev_tm.hour != tm.hour:
                    outfile.close()
                    outfile = None

        if outfile != None:
            outfile.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a csv file to mhealth folder structure.')
    parser.add_argument('filename', type=str, help='CSV file to read from.')
    parser.add_argument('outfolder', type=str, help='Root folder for output.')
    args = parser.parse_args()

    main(args.filename, args.outfolder)
