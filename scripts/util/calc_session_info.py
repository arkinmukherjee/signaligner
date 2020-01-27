import argparse, csv, io, json, sys
import _root
import _folder, _helper



TIME_GAP_SECONDS = 5 * 60

parser = argparse.ArgumentParser(description='Calculate log info for each user session.')
parser.add_argument('--dataset', type=str, help='The dataset for which you want to find log info. (default: all)', default=None)
parser.add_argument('--session', type=str, help='The session for which you want to find log info. (default: all)', default=None)
parser.add_argument('--file', type=str, help='Log file name. (default: playlog)', default=None)
parser.add_argument('--stdout', action='store_true', help='Write output to stdout.')
args = parser.parse_args()

if args.file is None:
    path = _folder.data_abspath('playlog')
else:
    path = args.file

# Find times of all events for each session
session_event_times = {}
session_event_labels = {}
session_event_mturk_times = {}
session_event_zoom_levels = {}
session_event_article = {}
session_event_video = {}
session_event_slideshow = {}
session_event_submissions = {}

slideshow_pages = ["total"]

with open(path, 'rt') as f:
    for line in f:

        try:
            data = json.loads(line)
        except:
            print("WARNING: Could not decode line " + str(line))

        # Skip line if it does not contain the following keys
        if 'type' not in data:
            continue
        elif 'dataset' not in data:
            continue
        elif 'session' not in data:
            continue
        elif 'run' not in data:
            continue
        elif 'time' not in data:
            continue

        logtype = data['type']
        dataset = data['dataset']
        session = data['session']
        run = data['run']
        time = data['time']
        labels = None
        zoom = None

        # Skip log line if it doesn't match the given parameters
        if args.dataset is not None and args.dataset != dataset:
            continue

        if args.session is not None and args.session != session:
            continue

        if logtype == 'label' and 'info' in data:
            labels = data['info']['labels']

        if logtype == 'tick' and 'info' in data and 'zoom' in data['info']:
            zoom = data['info']['zoom']

        keys = []
        if args.session is None or args.session == session:

            keys.append((session, '', ''))

            if args.dataset is None:
                keys.append((session, run, ''))

            if args.dataset is None or args.dataset == dataset:
                keys.append((session, run, dataset))

        for key in keys:

            # Get time log info
            if key not in session_event_times:
                session_event_times[key] = []
            session_event_times[key].append(time)

            # Get time spent in mturk help modal log info
            if key not in session_event_mturk_times:
                session_event_mturk_times[key] = {"open": [], "close": []}
            if logtype == 'mturk-help-open':
                session_event_mturk_times[key]["open"].append(time)
            elif logtype == 'mturk-help-close':
                session_event_mturk_times[key]["close"].append(time)

            # Get session labels log info
            if labels is not None and len(labels) > 0:
                if key not in session_event_labels:
                    session_event_labels[key] = []
                session_event_labels[key].append((time, labels))

            # Get zoom level log info
            if zoom is not None:
                if key not in session_event_zoom_levels:
                    session_event_zoom_levels[key] = []
                session_event_zoom_levels[key].append((time, zoom))

            # Get article log info
            if key not in session_event_article:
                session_event_article[key] = {"open": [], "close": []}
            if logtype == 'mturk-help-article':
                session_event_article[key]["open"].append(time)
            elif logtype == 'mturk-help-next' and 'fromPage' in data['info'] and data['info']['fromPage'] == "mturk_instructions_article.html":
                session_event_article[key]["close"].append(time)

            # Get video log info
            if key not in session_event_video:
                session_event_video[key] = {"open": [], "close": []}

            if logtype in ['mturk-help-next', 'mturk-help-prev'] and 'fromPage' in data['info']:
                fromPage = data['info']['fromPage']
                if logtype == 'mturk-help-next' and fromPage == 'mturk_instructions_tutorial_1.html':
                    session_event_video[key]["open"].append(time)
                elif logtype == 'mturk-help-prev' and fromPage == 'mturk_instructions_tutorial_3.html':
                    session_event_video[key]["open"].append(time)
                elif fromPage == 'mturk_instructions_tutorial_2.html':
                    session_event_video[key]["close"].append(time)

            # Get slideshow interaction info
            if logtype == 'mturk-help-slideshow' and 'page' in data['info']:
                if key not in session_event_slideshow:
                    session_event_slideshow[key] = {"total":0}
                session_event_slideshow[key]["total"] += 1

                page = data['info']['page']
                if page not in session_event_slideshow[key]:
                    session_event_slideshow[key][page] = 0
                session_event_slideshow[key][page] += 1
                if page not in slideshow_pages:
                    slideshow_pages.append(page)

            # Get submission attempts info
            if key not in session_event_submissions:
                session_event_submissions[key] = 0
            if logtype == 'mturk-submit-attempt':
                session_event_submissions[key] += 1


if len(session_event_times) == 0:
    _helper.warning('no usable entries found')

session_data = {}

# Get session total time spent data
for (session, run, dataset), event_times in session_event_times.items():

    event_times = sorted(event_times)

    total_seconds = 0.0
    seconds_no_gaps = 0.0

    for t0, t1 in zip(event_times, event_times[1:]):
        seconds = (t1 - t0) / 1000.0

        total_seconds += seconds

        if seconds <= TIME_GAP_SECONDS:
            seconds_no_gaps += seconds

    key = (session, run, dataset)
    if key not in session_data:
        session_data[key] = {}

    session_data[key]['total'] = total_seconds
    session_data[key]['no_gaps'] = seconds_no_gaps


# Dictionary must be of format: {(session, run, dataset) : {"open": [], "close": []}}
def get_time_spent_from_dict(dictionary, keyname, session_data):
    for (session, run, dataset), time_spent_dict in dictionary.items():

        open_times = time_spent_dict["open"]
        close_times = time_spent_dict["close"]

        if len(open_times) == 0:
            continue
        key = (session, run, dataset)
        if key not in session_data:
            session_data[key] = {}
        session_data[key][keyname] = 0.0

        for open_time, close_time in zip(open_times, close_times):
            seconds_spent = (close_time - open_time) / 1000.0
            if seconds_spent > 0.0:
                session_data[key][keyname] += seconds_spent


# Get session time spent in mturk help modal
get_time_spent_from_dict(session_event_mturk_times, 'mturk_help_time', session_data)

# Get session time spent reading article
get_time_spent_from_dict(session_event_article, 'mturk_article_time', session_data)

# Get session time spent on demo video page
get_time_spent_from_dict(session_event_video, 'mturk_video_time', session_data)

# Get session number of interactions with slideshow images
for (session, run, dataset), count_dict in session_event_slideshow.items():
    key = (session, run, dataset)
    if key not in session_data:
        session_data[key] = {}
    session_data[key]['mturk_slideshow_interactions'] = count_dict

# Get session number of submission attempts made
for (session, run, dataset), count in session_event_submissions.items():
    key = (session, run, dataset)
    if key not in session_data:
        session_data[key] = {}
    session_data[key]['mturk_submission_attempts'] = count

# Get session labels made data
for (session, run, dataset), times_and_labels in session_event_labels.items():

    times = [item[0] for item in times_and_labels]
    labels = [item[1] for item in times_and_labels]

    # Filter out duplicate labels
    all_labels_created = []
    for label in labels:
        if label not in all_labels_created:
            all_labels_created.append(label)

    # Get time spent labeling
    labeling_start_time_ms = min(times)
    labeling_end_time_ms = max(times)
    seconds_spent_labeling = (labeling_end_time_ms - labeling_start_time_ms) / 1000.0
    final_labels = labels[times.index(max(times))]

    key = (session, run, dataset)
    if key not in session_data:
        session_data[key] = {}

    session_data[key]['total_num_labels'] = len(all_labels_created)
    session_data[key]['final_num_labels'] = len(final_labels)
    session_data[key]['time_labeling'] = seconds_spent_labeling


# Get session time spent at each major zoom level data

major_zoom_levels = []

for (session, run, dataset), times_and_zooms in session_event_zoom_levels.items():

    key = (session, run, dataset)
    if key not in session_data:
        session_data[key] = {}
    session_data[key]['major_zoom_levels'] = {}

    time_per_zoom = session_data[key]['major_zoom_levels']

    times = [item[0] for item in times_and_zooms]
    major_zooms = [item[1][0] for item in times_and_zooms]

    cur_time = times[0]
    cur_zoom = major_zooms[0]

    for i in range(1, len(times_and_zooms)-1):
        next_time = times[i]
        next_zoom = major_zooms[i]

        if cur_zoom != next_zoom:

            if cur_zoom not in major_zoom_levels:
                major_zoom_levels.append(cur_zoom)

            if cur_zoom not in time_per_zoom:
                time_per_zoom[cur_zoom] = 0
            time_per_zoom[cur_zoom] += (next_time - cur_time)

            cur_zoom = next_zoom
            cur_time = next_time

    # Add last zoom level time
    last_time = times[len(times_and_zooms)-1]
    last_zoom = major_zooms[len(times_and_zooms)-1]

    if cur_zoom not in major_zoom_levels:
        major_zoom_levels.append(cur_zoom)

    if cur_zoom not in time_per_zoom:
        time_per_zoom[cur_zoom] = 0

    time_per_zoom[cur_zoom] += (last_time - cur_time)

    session_data[key]['major_zoom_levels'] = time_per_zoom


major_zoom_levels = [zoom for zoom in major_zoom_levels if zoom is not None]

# Export to CSV
buffer = io.StringIO()
writer = csv.writer(buffer)

slideshow_col_titles = [x.title() + " " + "Slideshow Interactions" for x in slideshow_pages]

zoom_col_titles = []
for zoom in sorted(major_zoom_levels):
    zoom_col_titles.append("Seconds in Zoom " + str(zoom))

writer.writerow(['Session', 'Run', 'Dataset', 'Total Seconds', 'Continuous Seconds Sum',
                 'Total Num Labels Made', 'Final Num Labels', 'Seconds Labeling',
                 'Seconds Reading Instructions', 'Seconds Reading Article', 'Seconds on Video Page',
                 'Submission Attempts'] + slideshow_col_titles + zoom_col_titles)

for (session, run, dataset), info in session_data.items():

    session_row_data = []

    session_row_data += [session, run, dataset]
    session_row_data += [info['total'], info['no_gaps']]

    total_num_labels = 0 if 'total_num_labels' not in info else int(info['total_num_labels'])
    final_num_labels = 0 if 'final_num_labels' not in info else int(info['final_num_labels'])
    time_labeling = 0 if 'time_labeling' not in info else int(info['time_labeling'])
    session_row_data += [total_num_labels, final_num_labels, time_labeling]

    sessionInfo = session_data[(session, '', '')]

    mturk_help_time = "" if 'mturk_help_time' not in sessionInfo else sessionInfo['mturk_help_time']
    session_row_data += [mturk_help_time]

    mturk_article_time = "" if 'mturk_article_time' not in sessionInfo else sessionInfo['mturk_article_time']
    session_row_data += [mturk_article_time]

    mturk_video_time = "" if 'mturk_video_time' not in sessionInfo else sessionInfo['mturk_video_time']
    session_row_data += [mturk_video_time]

    mturk_submission_attempts = "" if 'mturk_submission_attempts' not in info else int(info['mturk_submission_attempts'])
    session_row_data += [mturk_submission_attempts]

    session_slideshow_interactions = []
    if 'mturk_slideshow_interactions' not in sessionInfo:
        session_slideshow_interactions += [""] * len(slideshow_pages)
    else:
        mturk_slideshow_count_dict = sessionInfo['mturk_slideshow_interactions']
        for page in slideshow_pages:
            if page not in mturk_slideshow_count_dict:
                session_slideshow_interactions.append(0)
            else:
                session_slideshow_interactions.append(mturk_slideshow_count_dict[page])

    session_row_data += session_slideshow_interactions

    session_zoom_time_spent = []

    if 'major_zoom_levels' not in info:
        session_zoom_time_spent += ["NA"] * len(major_zoom_levels)
    else:
        major_zoom_time_dict = info['major_zoom_levels']
        for zoom in sorted(major_zoom_levels):
            if zoom not in major_zoom_time_dict:
                session_zoom_time_spent.append(0.0)
            else:
                session_zoom_time_spent.append(major_zoom_time_dict[zoom] / 1000.0)

    session_row_data += session_zoom_time_spent

    writer.writerow(session_row_data)


if args.stdout:
    sys.stdout.write(buffer.getvalue())
else:
    csvOutputPath = _helper.exportFilename('log_analysis')
    _helper.ensureDirExists(csvOutputPath, True)
    with open(csvOutputPath, 'wt') as csv_file:
        csv_file.write(buffer.getvalue())
    print('output written to', csvOutputPath)
