import calendar, json, os, random, re, string, sys, time
import _root
import _folder



def errorExit(message):
    sys.stderr.write('***ERROR: %s\n' % message)
    sys.exit(-1)

def warning(message):
    sys.stderr.write('***WARNING: %s\n' % message)



def _get_dataset_folder():
    if os.path.exists(_folder.data_abspath('datasets_custom')):
        return 'datasets_custom'
    return 'datasets'

def datasetDir(dataset):
    common_dir = _folder.file_abspath('common', 'datasets', dataset)
    if os.path.exists(common_dir):
        return common_dir
    return _folder.data_abspath(_get_dataset_folder(), dataset)

def datasetTileDir(dataset):
    return os.path.join(datasetDir(dataset), 'tiles')

def datasetConfigFilename(dataset):
    return os.path.join(datasetDir(dataset), 'config.json')

def datasetOriginFilename(dataset):
    return os.path.join(datasetDir(dataset), 'origin.json')

def _get_labels_folder():
    if os.path.exists(_folder.data_abspath('labels_custom')):
        return 'labels_custom'
    return 'labels'

def latestLabelsFilename(dataset, session):
    return _folder.data_abspath(_get_labels_folder(), dataset, session, 'labels.latest.json')

def logLabelsFilename(dataset, session):
    return _folder.data_abspath(_get_labels_folder(), dataset, session, 'labels.log.jsons')



def exportFilename(dataset):
    return _folder.data_abspath('export', dataset + '.csv')



def mturkSubmitLabelsFilename(dataset, session):
    return _folder.data_abspath('mturksubmit', session, dataset, 'labels.mturksubmit.json')

def mturkGetSubmissions(session):
    submissions = []

    folder = _folder.data_abspath('mturksubmit', session)
    if os.path.exists(folder):
        for dataset in os.listdir(folder):
            submitfilename = mturkSubmitLabelsFilename(dataset, session)
            if os.path.exists(submitfilename):
                with open(submitfilename, 'rt') as dfile:
                    submission = json.loads(dfile.read())
                    submissions.append(submission)

    return submissions


def mturkGetBonusCode(session):
    submissions = mturkGetSubmissions(session)



def getLabelsSessions(dataset):
    sessions = []

    folder = _folder.data_abspath(_get_labels_folder(), dataset)
    if os.path.exists(folder):
        for fn in os.listdir(folder):
            sessions.append(fn)

    return sessions

def getLabelsLatest(dataset):
    sessions = getLabelsSessions(dataset)

    labelsall = []
    for session in sessions:
        labelfilename = latestLabelsFilename(dataset, session)
        if os.path.exists(labelfilename):
            with open(labelfilename, 'rt') as lfile:
                labels = json.loads(lfile.read())
                labelsall.append(labels)
    return labelsall

def getDatasetList():
    dataset_folder = _folder.data_abspath(_get_dataset_folder())
    if os.path.exists(dataset_folder):
        dataset_folder_contents = os.listdir(dataset_folder)
        dataset_names = [item for item in dataset_folder_contents if os.path.isdir(os.path.join(dataset_folder, item))]
        return dataset_names
    else:
        return []



def ensureDirExists(name, isFile):
    if isFile:
        dirname = os.path.dirname(name)
    else:
        dirname = name
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return name


def activityJSON(a, wasprev):
    comma = ''
    if wasprev:
        comma = ','
    if len(a) >= 4 and a[3] != None:
        return comma + ('{"lo":%d, "hi":%d, "label":"%s", "detail":"%s"}' % (a[0], a[1], a[2], a[3]))
    else:
        return comma + ('{"lo":%d, "hi":%d, "label":"%s"}' % (a[0], a[1], a[2]))



# ID and related functions

# turn a filename into an ID
def makeIdFromFilename(filename):
    return re.sub('[^\w]+', '_', os.path.basename(filename).split('.')[0], re.ASCII)

# generate a random ID with a check character
def makeId():
    text = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(9))

    check = 0
    for c in text:
        check += ord(c)

    text = text + ('%x' % (check % 16)).upper()

    return text

# check an ID is valid, optionally checking check character
def checkId(id, checksum):
    ok = True

    if re.search('[^\w]', id, re.ASCII):
        return False

    if checksum:
        check = 0
        for c in id[:-1]:
            check += ord(c)
        val = ('%x' % (check % 16)).upper()
        if val != id[-1]:
            ok = False

    return ok



# functions related to time string conversions

# standard date formats
DATE_FORMAT_YMD = '%Y-%m-%d %H:%M:%S'

# convert milliseconds into a date string
def timeMillisecondToTimeString(ms):
    sec = ms / 1000
    msec = ms % 1000

    tm = time.gmtime(sec)
    return time.strftime(DATE_FORMAT_YMD, tm) + ('.%03d' % msec)

# convert date string into milliseconds
def timeStringToTimeMillisecond(tm, date_fmt):
    # split off milliseconds if any
    parts = tm.split('.')
    if len(parts) == 1:
        sec = parts[0]
        msec = '000'
    elif len(parts) == 2:
        sec = parts[0]
        msec = parts[1]
        if len(msec) > 3:
            errorExit('time more detailed than milliseconds: ' + tm)
        while len(msec) < 3:
            msec = msec + '0'
    else:
        errorExit('invalid time format: ' + tm)

    # try to parse the string
    parsed = time.strptime(sec, date_fmt)
    if not parsed:
        errorExit('unparseable time format: "%s" and "%s"' % (tm, date_fmt))

    return 1000 * int(calendar.timegm(parsed)) + int(msec)



# read header from actigraph file
def process_actigraph_header(csvfile):
    header_rate = None
    header_date_fmt = None
    header_start_time_part = None
    header_start_date_part = None

    while True:
        line = csvfile.readline()
        if line == '':
            errorExit('Could not find CSV header row')

        result = re.search(r'date format ([MmDdYy/-]+) at (\d+) Hz', line)
        if result:
            header_date_fmt = result.groups()[0]
            header_rate = result.groups()[1]

        result = re.match(r'Start Time ([\d:\.]*)', line)
        if result:
            header_start_time_part = result.groups()[0]

        result = re.match(r'Start Date ([\d/-]*)', line)
        if result:
            header_start_date_part = result.groups()[0]

        if line.find('----------------------------------------') != -1:
            break

    if header_date_fmt == None or header_rate == None or header_start_time_part == None or header_start_date_part == None:
        errorExit('Could not find timing information in ActiGraph header')

    header_rate = int(header_rate)

    header_start_time = header_start_date_part + ' ' + header_start_time_part

    date_fmt_groups = list(re.match(r'(MM|M|dd|d|yyyy)([/-])'
                                    r'(MM|M|dd|d|yyyy)([/-])'
                                    r'(MM|M|dd|d|yyyy)', header_date_fmt).groups())

    date_fmt_matches = ['MM', 'M', 'dd', 'd', 'yyyy']
    for fmt in date_fmt_matches:
        if fmt in date_fmt_groups:
            update_fmt = fmt[0].upper() if fmt == 'yyyy' else fmt[0].lower()
            date_fmt_groups[date_fmt_groups.index(fmt)] = update_fmt

    header_time_fmt = \
        '%' + date_fmt_groups[0] + date_fmt_groups[1] + \
        '%' + date_fmt_groups[2] + date_fmt_groups[3] + \
        '%' + date_fmt_groups[4] + ' %H:%M:%S'

    header_start_ms = timeStringToTimeMillisecond(header_start_time, header_time_fmt)

    return header_rate, header_start_ms



# is a filename importable to a dataset?
def isFilenameDatasetImportable(filename):
    return filename.endswith('.csv') or filename.endswith('.csv.gz')

# recursively find dataset importable files in a folder
def findDatasetImportableFilesRecursively(folder):
    ret = []
    for root, dirs, files in os.walk(folder):
        for name in files:
            if isFilenameDatasetImportable(name):
                ret.append(os.path.join(root, name))
    return ret
