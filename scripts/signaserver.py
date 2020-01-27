import http.server, argparse, cgi, hashlib, json, os, re, subprocess, sys, time, urllib.parse
import _root
import _folder, _helper



HOST_NAME = ''
DEFAULT_PORT = 3007

VALID_MODES = ['MTURK', 'EXPERT']


ALNUMUN_RE = re.compile(r'(\w+)')
PNG_RE = re.compile(r'/(\w+)\.png')
HTML_RE = re.compile(r'/(\w+)\.html')
JS_RE = re.compile(r'/(\w+)\.js')
CSS_RE = re.compile(r'/(\w+)\.css')



CTYPE_PLAIN='text/plain'
CTYPE_HTML='text/html'
CTYPE_JS='text/javascript'
CTYPE_PNG='image/png'
CTYPE_CSS = 'text/css'



SESSION_ERROR = 'NOSESSION'



_mode = None
_debug_delay = None



_sessions = set()
_mturk_session_codes = {}
def gen_session():
    global _sessions

    while True:
        sess = _helper.makeId()

        if sess not in _sessions:
            _sessions.add(sess)
            return sess



def replace_mode_config(data):
    if '(MODECONFIG)' in data:
        global _mode

        if _mode == None:
            data = data.replace('(MODECONFIG)',
'''
G_modeConfig[MC_HIDE_REMOTE_PLAYER_LABELS] = false;
G_modeConfig[MC_HIDE_REMOTE_ALGO_LABELS] = false;
G_modeConfig[MC_HIDE_REMOTE_MTURK] = false;
G_modeConfig[MC_HIDE_REMOTE_EXPERT] = false;
G_modeConfig[MC_HIDE_GROUND_TRUTH_LABELS] = false;
G_modeConfig[MC_HIDE_IMPORT_DATA_BUTTON] = false;
''')
        elif _mode == 'MTURK':
            data = data.replace('(MODECONFIG)',
'''
G_modeConfig[MC_MODE] = 'MTURK';
''')
        elif _mode == 'EXPERT':
            data = data.replace('(MODECONFIG)',
'''
G_modeConfig[MC_MODE] = 'EXPERT';
''')
        else:
            data = data.replace('(MODECONFIG)', '')

    return data



def replace_vars(data, session, can_gen_session):
    data = data.replace('(SESSION)', session)

    if '(MODE)' in data:
        global _mode
        if _mode == None:
            data = data.replace('(MODE)', '')
        else:
            data = data.replace('(MODE)', _mode)

    if '(GITREV)' in data:
        rev = 'NONE'

        try:
            gitrev = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
            if gitrev != '':
                try:
                    gittag = subprocess.check_output(['git', 'describe', '--tags', '--exact-match', '--abbrev=0']).decode('utf-8').strip()
                    if gittag != '':
                        gitrev = gittag + ' (' + gitrev + ')'
                except:
                    pass

                try:
                    modified = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no']).decode('utf-8').strip()
                    if modified != '':
                        gitrev = gitrev + '+'
                except:
                    gitrev = gitrev + '?'

                rev = gitrev
        except:
            pass

        data = data.replace('(GITREV)', rev)

    if can_gen_session and data.find('(GENSESSION)') != -1:
        data = data.replace('(GENSESSION)', gen_session())
    else:
        data = data.replace('(GENSESSION)', SESSION_ERROR)

    return data



class Handler(http.server.BaseHTTPRequestHandler):
    def setup(self):
        self.timeout = 10
        http.server.BaseHTTPRequestHandler.setup(self)

    def log_message(self, format, *args):
        sys.stderr.write("%s - - [%s] %s\n" %
                         (hashlib.md5(('signaligner' + self.client_address[0]).encode('utf-8')).hexdigest(),
                          self.log_date_time_string(),
                          format % args))

    def _send_header(self, code, ctype, additional={}):
        self.send_response(code)
        self.send_header('Content-type', ctype)
        for key, val in additional.items():
            self.send_header(key, val)
        self.end_headers()

    def _send_data(self, data, binary):
        if not binary:
            data = data.encode('utf-8')

        # Python 3, until 3.6, may not write all the data to wfile in one call
        toWrite = len(data)
        writtenSoFar = 0
        while writtenSoFar < toWrite:
            writtenSoFar += self.wfile.write(data[writtenSoFar:])

    def _send_header_and_file_data(self, filename, binary, ctype, data_cb=None):
        if not os.path.exists(filename):
            self._send_header(404, ctype)
            return

        if binary:
            flags = 'rb'
        else:
            flags = 'rt'
        with open(filename, flags) as dfile:
            data = dfile.read()
            if data_cb:
                data = data_cb(data)
            self._send_header(200, ctype)
            self._send_data(data, binary)

    def _process_request(self, path, vars):
        global _debug_delay
        if _debug_delay:
            time.sleep(_debug_delay)

        if path == '/signaligner.html':
            if 'dataset' in vars and ALNUMUN_RE.match(vars['dataset']):
                dataset = vars['dataset']
            else:
                dataset = 'null'

            if 'session' in vars and ALNUMUN_RE.match(vars['session']):
                session = vars['session']
            else:
                session = SESSION_ERROR

            def replace_data(data):
                data = replace_vars(data, session, False)
                return data

            self._send_header_and_file_data(_folder.file_abspath('signaligner/signaligner.html'), False, CTYPE_HTML, replace_data)

        elif path == '/signaligner.js':
            def replace_data(data):
                data = replace_mode_config(data)
                return data

            self._send_header_and_file_data(_folder.file_abspath('signaligner/signaligner.js'), False, CTYPE_JS, replace_mode_config)

        elif path == '/fetchdatasetlist':
            datasets = _helper.getDatasetList()
            self._send_header(200, CTYPE_PLAIN)
            self._send_data(json.dumps(datasets), False)

        elif path == '/fetchdataset':
            if 'dataset' in vars and ALNUMUN_RE.match(vars['dataset']):
                dataset_name = vars['dataset']

                if 'type' in vars and vars['type'] == 'config':
                    file_path = _helper.datasetConfigFilename(dataset_name)
                elif 'type' in vars and vars['type'] == 'tile' and 'id' in vars and ALNUMUN_RE.match(vars['id']):
                    file_path = os.path.join(_helper.datasetTileDir(dataset_name), vars['id'] + '.json')
                else:
                    self._send_header(404, CTYPE_PLAIN)
                    return

                if not os.path.exists(file_path):
                    self._send_header(404, CTYPE_PLAIN)
                    return

                self._send_header_and_file_data(file_path, False, CTYPE_PLAIN)
            else:
                self._send_header(404, CTYPE_PLAIN)

        elif path == '/fetchlabels':
            if 'dataset' in vars and ALNUMUN_RE.match(vars['dataset']):
                dataset = vars['dataset']

                self._send_header(200, CTYPE_PLAIN)
                labels = _helper.getLabelsLatest(dataset)
                if labels:
                    self._send_data(json.dumps(labels), False)
            else:
                self._send_header(404, CTYPE_PLAIN)

        elif path == '/reportlabels':
            if 'data' in vars:
                data = json.loads(vars['data'])

                if 'dataset' in data and ALNUMUN_RE.match(data['dataset']) and 'session' in data and ALNUMUN_RE.match(data['session']):
                    dataset = data['dataset']
                    session = data['session']

                    with open(_helper.ensureDirExists(_helper.logLabelsFilename(dataset, session), True), 'at') as dfile:
                        dfile.write(json.dumps(data) + '\n')

                    with open(_helper.ensureDirExists(_helper.latestLabelsFilename(dataset, session), True), 'wt') as dfile:
                        dfile.write(json.dumps(data) + '\n')

                    with open(_helper.ensureDirExists(_helper.latestLabelsFilename(dataset, session), True), 'rt') as dfile:
                        response = json.loads(dfile.read())

                    self._send_header(200, CTYPE_PLAIN)
                    self._send_data(json.dumps(response), False)

                else:
                    self._send_header(404, CTYPE_PLAIN)

            else:
                self._send_header(404, CTYPE_PLAIN)

        elif path == '/mturksubmit' or path == '/mturksubmissions':
            if 'data' in vars:
                data = json.loads(vars['data'])

                if 'dataset' in data and ALNUMUN_RE.match(data['dataset']) and 'session' in data and ALNUMUN_RE.match(data['session']):
                    dataset = data['dataset']
                    session = data['session']

                    if path == '/mturksubmit':
                        mturk_submit = _helper.mturkSubmitLabelsFilename(dataset, session)
                        if not os.path.exists(mturk_submit):
                            with open(_helper.ensureDirExists(mturk_submit, True), 'wt') as dfile:
                                dfile.write(json.dumps(data) + '\n')

                    submissions = _helper.mturkGetSubmissions(session)

                    total = 0
                    datasets = []
                    for submission in submissions:
                        score = submission['score'] / 100.0
                        score = score**2
                        score *= submission['daysofdata']
                        # minimum of 1 cent for tutorial levels, 20 cents for challenge
                        score = max(score, 0.20)
                        if submission['istutorial']:
                            score *= 0.05
                        total += score
                        datasets.append(submission['dataset'])

                    total = int(total * 100)
                    if session not in _mturk_session_codes:
                        _mturk_session_codes[session] = _helper.makeId()[:3]


                    code = _mturk_session_codes[session]
                    code = code + ('%03d' % total).upper()
                    code = code + hashlib.md5(code.encode('utf-8')).hexdigest()[:3].upper()

                    response = {
                        'amount': '$%d.%02d' % (total // 100, total % 100),
                        'code': code,
                        'datasets': datasets
                    }

                    self._send_header(200, CTYPE_PLAIN)
                    self._send_data(json.dumps(response), False)

                else:
                    self._send_header(404, CTYPE_PLAIN)

            else:
                self._send_header(404, CTYPE_PLAIN)

        elif path == '/log':
            if 'data' in vars:
                with open(_helper.ensureDirExists(_folder.data_abspath('playlog'), True), 'at') as dfile:
                    dfile.write(vars['data'] + '\n')

            self._send_header(200, CTYPE_PLAIN)

        elif HTML_RE.match(path):
            if path == '/mturk_start.html':
                global _mode
                if _mode != 'MTURK':
                    self._send_header(200, CTYPE_PLAIN)
                    self._send_data('mode must be MTURK to request mturk_start.html', False)
                    return

            if 'session' in vars and ALNUMUN_RE.match(vars['session']):
                session = vars['session']
            else:
                session = SESSION_ERROR

            def replace_data(data):
                return replace_vars(data, session, True)

            self._send_header_and_file_data(_folder.file_abspath('static' + path), False, CTYPE_HTML, replace_data)

        elif PNG_RE.match(path):
            self._send_header_and_file_data(_folder.file_abspath('static' + path), True, CTYPE_PNG)

        elif JS_RE.match(path):
            self._send_header_and_file_data(_folder.file_abspath('static' + path), False, CTYPE_JS)

        elif CSS_RE.match(path):
            self._send_header_and_file_data(_folder.file_abspath('static' + path), False, CTYPE_CSS)

        else:
            self._send_header(404, CTYPE_PLAIN)

    def _extractvars(self, vars):
        newvars = {}
        for key, val in vars.items():
            usekey = key
            if type(usekey) != type(''):
                usekey = usekey.decode('utf-8')

            useval = val[0]
            if type(useval) != type(''):
                useval = useval.decode('utf-8')

            newvars[usekey] = useval

        return newvars

    def do_HEAD(self):
        self._send_header(200, CTYPE_PLAIN)

    def do_GET(self):
        parse = urllib.parse.urlparse(self.path)
        path = parse.path

        # process GET arguments
        getvars = urllib.parse.parse_qs(parse.query)

        self._process_request(path, self._extractvars(getvars))

    def do_POST(self):
        parse = urllib.parse.urlparse(self.path)
        path = parse.path

        # process POST data into dict
        postvars = {}
        if 'content-type' in self.headers:
            content_type_header = self.headers['content-type']
            ctype, pdict = cgi.parse_header(content_type_header)
            if ctype == 'multipart/form-data':
                postvars = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                if 'content-length' in self.headers:
                    length = int(self.headers['content-length'])
                else:
                    length = 0
                postvars = urllib.parse.parse_qs(self.rfile.read(length), keep_blank_values=1)

        self._process_request(path, self._extractvars(postvars))



def main(*, port=DEFAULT_PORT, mode=None, delay=None):
    if mode:
        global _mode
        if mode not in VALID_MODES:
            _helper.errorExit('unrecognized mode: ' + mode)
        _mode = mode
        if _mode == None:
            print('Starting server in default mode.')
        else:
            print('Starting server in mode ' + _mode + '.')

    if delay:
        global _debug_delay
        _debug_delay = delay / 1000.0

    #class ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    #    pass
    #httpd = ThreadedHTTPServer((HOST_NAME, port), Handler)

    httpd = http.server.HTTPServer((HOST_NAME, port), Handler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run server.')
    parser.add_argument('--port', type=int, help='Port to use. (default %d).' % DEFAULT_PORT, default=DEFAULT_PORT)
    parser.add_argument('--mode', type=str, help='Option server mode.', default=None)
    parser.add_argument('--delay', type=int, help='Additional delay to add in ms, for debugging.', default=None)
    args = parser.parse_args()

    main(port=args.port, mode=args.mode, delay=args.delay)
