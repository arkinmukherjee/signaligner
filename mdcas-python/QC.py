import csv
import gzip
import math
import os
import sys
import time
from datetime import datetime
import numpy as np
import pandas as pd
import itertools
from collections import Counter, OrderedDict
from glob import glob
from copy import deepcopy
from datetime import datetime, timedelta

contiguous_num = 20
contiguous_num_start_end = 5
anomaly_num = 1

MHEALTH_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
MHEALTH_TIME_FORMAT = "%H:%M:%S"
MHEALTH_DATE_FORMAT = "%Y-%m-%d"

# Prints a slew of information for debugging purposes --Sandarsh/
enable_debug_print = False

# Defined values as given by Prof. Intille
SAMPLES_PER_MINUTE = None
SAMPLES_PER_SECOND = None

zero = 0
max_g_value = 6
min_g_value = -6
error_threshold_for_zero = 0.001
error_threshold_for_max_g_value = 0.05
error_threshold_for_min_g_value = 0.05
spike_threshold = 11

IMPOSSIBLE_G_VALUE_THRESHOLD = 0.01
IMPOSSIBLE_G_MIN_THRESHOLD = 1.25
IMPOSSIBLE_G_MAX_THRESHOLD = 6

MAX_G_COUNT_THRESHOLD = 690
CONTINOUS_G_THRESHOLD = 160

# Chandrika
IMPOSSIBLE_CONTINOUS_G_THRESHOLD = 6
CONTINOUS_ALL_ZEROES_THRESHOLD = 2
CONTINOUS_IDENTICAL_NON_ZEROES_THRESHOLD = 2

# Management Params

prev_x = None
prev_y = None
prev_z = None
prev_loc = None

is_prev_x_max = False
curr_x_max = 0
x_max_temp_loc = None

is_prev_y_max = False
curr_y_max = 0
y_max_temp_loc = None

is_prev_z_max = False
curr_z_max = 0
z_max_temp_loc = None

is_prev_x_min = False
curr_x_min = 0
x_min_temp_loc = None

is_prev_y_min = False
curr_y_min = 0
y_min_temp_loc = None

is_prev_z_min = False
curr_z_min = 0
z_min_temp_loc = None

is_prev_impossible = False
curr_impossible = 0
consecutive_impossible_temp_loc = None

is_prev_all_zeroes = False
curr_all_zeroes = 0
consecutive_all_zeroes_temp_loc = None

is_prev_indentical_non_zeroes = False
curr_indentical_non_zeroes = 0
consecutive_indentical_non_zeroes_temp_loc = None

previous_day = None
day_number = 0

# Tracked parameters
X_max_g_vals = 0
Y_max_g_vals = 0
Z_max_g_vals = 0
X_min_g_vals = 0
Y_min_g_vals = 0
Z_min_g_vals = 0
X_zero_vals = 0
X_zero_vals_with_error_thresh = 0
Y_zero_vals = 0
Y_zero_vals_with_error_thresh = 0
Z_zero_vals = 0
data_quality_flag_count = 0

XYZ_zero_vals = 0  # Added by Chandrika
XYZ_zero_vals_loc = None
XYZ_zero_vals_start_loc = None

Z_zero_vals_with_error_thresh = 0
X_consecutive_max_gs = 0
X_consecutive_max_gs_location = None
Y_consecutive_max_gs = 0
Y_consecutive_max_gs_location = None
Z_consecutive_max_gs = 0
Z_consecutive_max_gs_location = None
X_consecutive_min_gs = 0
X_consecutive_min_gs_location = None
Y_consecutive_min_gs = 0
Y_consecutive_min_gs_location = None
Z_consecutive_min_gs = 0
Z_consecutive_min_gs_location = None
consecutive_impossible_gs = 0
consecutive_impossible_gs_location = None
consecutive_all_zeroes_gs = 0
consecutive_all_zeroes_gs_location = None
consecutive_identical_non_zeroes_gs = 0
consecutive_identical_non_zeroes_gs_location = None

X_spikes = 0
x_spike_start_loc = None
Y_spikes = 0
y_spike_start_loc = None
Z_spikes = 0
z_spike_start_loc = None

X_1s_spikes = 0
Y_1s_spikes = 0
Z_1s_spikes = 0

# Idle Sleep Mode Code variables
percentage_time_in_idle_sleep_mode = 0
total_time = 0
num_samples_in_idle_sleep_mode = 0
total_samples = 0
start_time = None
stop_time = None

temp_output_array = []
current_day = None

sample_num = 0
sample_num_start = 0
sample_num_end = 0

logs_path = ""
rtol = 1e-09
logged = False

x_spike_loc = None
y_spike_loc = None
z_spike_loc = None

ONE_SEC_SPIKES_COUNT_THRESHOLD = 12
curr_x_min_val = None
curr_y_min_val = None
curr_z_min_val = None
curr_x_max_val = None
curr_y_max_val = None
curr_z_max_val = None

x_sec_spike_count = 0
y_sec_spike_count = 0
z_sec_spike_count = 0

x_sec_spike_samples = []
y_sec_spike_samples = []
z_sec_spike_samples = []

is_1s_flagged = 0
flags_triggered = []

x_max_start_loc = None
y_max_start_loc = None
z_max_start_loc = None
x_min_start_loc = None
y_min_start_loc = None
z_min_start_loc = None

x_max_end_loc = None
y_max_end_loc = None
z_max_end_loc = None
x_min_end_loc = None
y_min_end_loc = None
z_min_end_loc = None

prev_x_1s_spike = False
prev_y_1s_spike = False
prev_z_1s_spike = False

curr_x_min_val_no = None
curr_y_min_val_no = None
curr_z_min_val_no = None
curr_x_max_val_no = None
curr_y_max_val_no = None
curr_z_max_val_no = None

sampling_rate = 0
new_flag_impossible_gravity_values = 0


# Interval Jump
interval_jump_x = 0
interval_jump_y = 0
interval_jump_z = 0

QC_STAT_COLUMNS = ["DAY_OF_DATA",  # 0
                   "DAY_OF_WEEK",  # 1
                   "START_TIME",  # 2
                   "STOP_TIME",  # 3`
                   "STARTING_SAMPLE_NUMBER",  # 4
                   "COUNT_MAX_G_VALS_X",  # 5
                                  "COUNT_MAX_G_VALS_Y",  # 6
                                  "COUNT_MAX_G_VALS_Z",  # 7
                                  # "COUNT_MAX_OUT_OF_RANGE_VALS",#8
                                  "COUNT_MIN_G_VALS_X",  # 9 8
                                  "COUNT_MIN_G_VALS_Y",  # 10 9
                                  "COUNT_MIN_G_VALS_Z",  # 11 10
                                  # "COUNT_MIN_OUT_OF_RANGE_VALS",#12
                                  "COUNT_ZERO_VALS_XYZ",  # 19 13 11
                                  "CONTIGUOUS_ADJACENT_ZERO_VALS_XYZ",  # 20 14 12
                                  "CONTIGUOUS_ADJACENT_IDENTICAL_NON_ZERO_VALS_XYZ",  # 21 15 13
                                  "CONTIGUOUS_MAX_G_VALS_X",  # 22 16 14
                                  "CONTIGUOUS_MAX_G_VALS_Y",  # 23 17 15
                                  "CONTIGUOUS_MAX_G_VALS_Z",  # 24 18 16
                                  "CONTIGUOUS_MIN_G_VALS_X",  # 25 19 17
                                  "CONTIGUOUS_MIN_G_VALS_Y",  # 26 20 18
                                  "CONTIGUOUS_MIN_G_VALS_Z",  # 27 21 19
                                  "COUNT_SPIKES_X",  # 28 22 20
                                  "COUNT_SPIKES_Y",  # 29 23 21
                                  "COUNT_SPIKES_Z",  # 30 24 22
                                  "COUNT_SPIKES_X_1S",  # 31 25 23
                                  "COUNT_SPIKES_Y_1S",  # 32  26 24
                                  "COUNT_SPIKES_Z_1S",  # 33 27 25
                                  "COUNT_IMPOSSIBLE_GRAVITY",  # 34 28 26
                                  "PERCENT_IDLE_SLEEP_MODE",  # 35 29 27
                                  "SAMPLES_IN_IDLE_SLEEP_MODE",  # 36 28
                                  "TOTAL_SECONDS_DATA",  # 37 31 29
                                  "TOTAL_SAMPLES",  # 38 32 30
                                  "INTERVALJUMP_X",  # 39 33 31
                                  "INTERVALJUMP_Y",  # 40 34 32
                                  "INTERVALJUMP_Z",  # 41 35 33
                                  "DATA_QUALITY_FLAG_COUNT",  # 42 36 34
                                  "FLAGS_TRIGGERED"  # 43 37 35
                   ]

# Log Flags:


def mhealth_timestamp_parser(val):
    return datetime.strptime(val, MHEALTH_TIMESTAMP_FORMAT)


def mhealth_time_parser_for_string(val):
    return datetime.strptime(val, MHEALTH_TIME_FORMAT)


def mhealth_time_parser(val):
    return datetime.strftime(val, MHEALTH_TIME_FORMAT)


def mhealth_date_parser(val):
    return datetime.strftime(val, MHEALTH_DATE_FORMAT)


def time_diff(stop_time, start_time):
    time_delta = mhealth_timestamp_parser(
        stop_time) - mhealth_timestamp_parser(start_time)

    if time_delta.days < 0:
        time_delta = timedelta(days=0, seconds=0, microseconds=0)

    return time_delta.seconds + time_delta.microseconds / float(1000000)


def check_idle_sleep_mode(cond_values, data):
    tup = ()
    for start, stop in cond_values:
        if (start == 0) | (stop == len(data) - 1):
            if start + contiguous_num_start_end < stop:
                tup = tup + ((start, stop, 1),)
        else:
            if start + contiguous_num < stop:
                tup = tup + ((start, stop, 1),)

    stop = 0
    start = 0
    last_stop = 0
    idle_time = 0
    num_samples_in_idle_sleep_mode = 0

    final_data = []

    if len(tup) > 0:
        final_tup = ()
        if len(tup) == 1:
            final_tup = tup
        else:
            for ind in range(len(tup)):
                if ind == 0:
                    start = tup[ind][0]
                    stop = tup[ind][1]
                else:
                    curr_start = tup[ind][0]
                    curr_stop = tup[ind][1]
                    if stop == curr_start - anomaly_num - 1:
                        stop = curr_stop
                    else:
                        final_tup = final_tup + ((start, stop, 1),)
                        start = curr_start
                        stop = curr_stop

                    if ind == len(tup) - 1:
                        final_tup = final_tup + ((start, stop, 1),)

            copy_final_tup = deepcopy(final_tup)
            length_tuple = len(copy_final_tup)
            for ind in range(length_tuple):
                start_ind, stop_ind, _ = copy_final_tup[ind]
                if ind == 0:
                    if start_ind != 0:
                        final_tup = final_tup + ((0, start_ind - 1, 0),)
                    last_stop = stop_ind
                elif ind == length_tuple - 1:
                    if last_stop != start_ind - 1:
                        final_tup = final_tup + \
                            ((last_stop + 1, start_ind - 1, 0),)
                    if stop_ind != len(data) - 1:
                        final_tup = final_tup + \
                            ((stop_ind + 1, len(data) - 1, 0),)
                else:
                    if last_stop != start_ind - 1:
                        final_tup = final_tup + \
                            ((last_stop + 1, start_ind - 1, 0),)
                    last_stop = stop_ind

        i = 0

        for startInd, stopInd, ISMOn in final_tup:
            start_time = data[startInd][0]
            stop_time = data[stopInd][0]
            final_data.append([start_time, stop_time, ISMOn])

            if ISMOn == 1:
                time_delta = time_diff(stop_time, start_time)
                idle_time += time_delta
                num_samples_in_idle_sleep_mode = num_samples_in_idle_sleep_mode + stopInd - startInd + 1

            i = i + 1
    else:
        final_data.append([data[0][0], data[-1][0], 0])

    # final_data.sort(key=lambda val: val[0]) # if want to display the ranges

    start_time = data[0][0]
    stop_time = data[-1][0]

    total_time = time_diff(stop_time, start_time)
    return idle_time / float(total_time) * 100, num_samples_in_idle_sleep_mode, total_time, start_time, stop_time


def print_params():
    if not enable_debug_print:
        return
    print(("X_max_g_vals", X_max_g_vals))
    print(("Y_max_g_vals", Y_max_g_vals))
    print(("Z_max_g_vals", Z_max_g_vals))
    print(("X_min_g_vals", X_min_g_vals))
    print(("Y_min_g_vals", Y_min_g_vals))
    print(("Z_min_g_vals", Z_min_g_vals))
    print(("X_zero_vals", X_zero_vals))
    print(("X_zero_vals_with_error_thresh", X_zero_vals_with_error_thresh))
    print(("Y_zero_vals", Y_zero_vals))
    print(("Y_zero_vals_with_error_thresh", Y_zero_vals_with_error_thresh))
    print(("Z_zero_vals", Z_zero_vals))
    print(("Z_zero_vals_with_error_thresh", Z_zero_vals_with_error_thresh))
    print(("XYZ_zero_vals", XYZ_zero_vals))
    print(("XYZ_zero_vals_loc", XYZ_zero_vals_loc))
    print(("X_consecutive_max_gs", X_consecutive_max_gs))
    print(("X_consecutive_max_gs_location", X_consecutive_max_gs_location))
    print(("Y_consecutive_max_gs", Y_consecutive_max_gs))
    print(("Y_consecutive_max_gs_location", Y_consecutive_max_gs_location))
    print(("Z_consecutive_max_gs", Z_consecutive_max_gs))
    print(("Z_consecutive_max_gs_location", Z_consecutive_max_gs_location))
    print(("X_consecutive_min_gs", X_consecutive_min_gs))
    print(("X_consecutive_min_gs_location", X_consecutive_min_gs_location))
    print(("Y_consecutive_min_gs", Y_consecutive_min_gs))
    print(("Y_consecutive_min_gs_location", Y_consecutive_min_gs_location))
    print(("Z_consecutive_min_gs", Z_consecutive_min_gs))
    print(("Z_consecutive_min_gs_location", Z_consecutive_min_gs_location))
    print(("X_spikes", X_spikes))
    print(("Y_spikes", Y_spikes))
    print(("Z_spikes", Z_spikes))
    print(("PERCENTAGE_TIME_IN_IDLE_SLEEP_MODE",
           percentage_time_in_idle_sleep_mode))
    print(("TOTAL_TIME", total_time))
    print(("NUM_SAMPLES_IN_IDLE_SLEEP_MODE", num_samples_in_idle_sleep_mode))
    print(("TOTAL_SAMPLES", total_samples))
    print(("START_TIME", start_time))
    print(("STOP_TIME", stop_time))

    print()


def print_management_params():
    if not enable_debug_print:
        return

    print(("prev_x", prev_x))
    print(("prev_y", prev_y))
    print(("prev_z", prev_z))

    print(("is_prev_x_max", is_prev_x_max))
    print(("curr_x_max", curr_x_max))
    print(("x_max_temp_loc", x_max_temp_loc))

    print(("is_prev_y_max", is_prev_y_max))
    print(("curr_y_max", curr_y_max))
    print(("y_max_temp_loc", y_max_temp_loc))

    print(("is_prev_z_max", is_prev_z_max))
    print(("curr_z_max", curr_z_max))
    print(("z_max_temp_loc", z_max_temp_loc))

    print(("is_prev_x_min", is_prev_x_min))
    print(("curr_x_min", curr_x_min))
    print(("x_min_temp_loc", x_min_temp_loc))

    print(("is_prev_y_min", is_prev_y_min))
    print(("curr_y_min", curr_y_min))
    print(("y_min_temp_loc", y_min_temp_loc))

    print(("is_prev_z_min", is_prev_z_min))
    print(("curr_z_min", curr_z_min))
    print(("z_min_temp_loc", z_min_temp_loc))
    print()


def save_params(cache_filename):
    global prev_x
    global prev_y
    global prev_z

    global is_prev_x_max
    global curr_x_max
    global x_max_temp_loc

    global is_prev_y_max
    global curr_y_max
    global y_max_temp_loc

    global is_prev_z_max
    global curr_z_max
    global z_max_temp_loc

    global is_prev_x_min
    global curr_x_min
    global x_min_temp_loc

    global is_prev_y_min
    global curr_y_min
    global y_min_temp_loc

    global is_prev_z_min
    global curr_z_min
    global z_min_temp_loc

    global is_prev_impossible
    global curr_impossible
    global consecutive_impossible_temp_loc

    global previous_day
    global day_number
    global prev_loc

    f = open(cache_filename, 'w')
    f.write(str(prev_x) + "\n")
    f.write(str(prev_y) + "\n")
    f.write(str(prev_z) + "\n")
    f.write(str(is_prev_x_max) + "\n")
    f.write(str(curr_x_max) + "\n")
    f.write(str(x_max_temp_loc) + "\n")
    f.write(str(is_prev_y_max) + "\n")
    f.write(str(curr_y_max) + "\n")
    f.write(str(y_max_temp_loc) + "\n")
    f.write(str(is_prev_z_max) + "\n")
    f.write(str(curr_z_max) + "\n")
    f.write(str(z_max_temp_loc) + "\n")
    f.write(str(is_prev_x_min) + "\n")
    f.write(str(curr_x_min) + "\n")
    f.write(str(x_min_temp_loc) + "\n")
    f.write(str(is_prev_y_min) + "\n")
    f.write(str(curr_y_min) + "\n")
    f.write(str(y_min_temp_loc) + "\n")
    f.write(str(is_prev_z_min) + "\n")
    f.write(str(curr_z_min) + "\n")
    f.write(str(z_min_temp_loc) + "\n")
    f.write(str(current_day) + "\n")
    f.write(str(day_number) + "\n")
    f.write(str(prev_loc) + "\n")
    f.write(str(sample_num) + "\n")
    # Added by Chandrika
    f.write(str(is_prev_impossible) + "\n")  # 25
    f.write(str(curr_impossible) + "\n")  # 26
    f.write(str(consecutive_impossible_temp_loc) + "\n")  # 27

    f.write(str(is_prev_all_zeroes) + "\n")  # 28
    f.write(str(curr_all_zeroes) + "\n")  # 29
    f.write(str(consecutive_all_zeroes_temp_loc) + "\n")  # 30

    f.write(str(is_prev_indentical_non_zeroes) + "\n")  # 31
    f.write(str(curr_indentical_non_zeroes) + "\n")  # 32
    f.write(str(consecutive_indentical_non_zeroes_temp_loc) + "\n")  # 33

    f.write(str(SAMPLES_PER_SECOND) + "\n")  # 34

    f.close()


def get_time_diff(time1, time2):
    time_delta = mhealth_timestamp_parser(time1) - \
        mhealth_timestamp_parser(time2)
    return time_delta


class Line:

    def __init__(self, line):
        self.loc = line[0]
        self.x = float(line[1])
        self.y = float(line[2])
        self.z = float(line[3])

    @staticmethod
    def is_zero(val):
        return val == 0

    @staticmethod
    def is_zero_with_thresh(val):
        return abs(val) <= (zero + error_threshold_for_zero)

    @staticmethod
    def is_max(val):
        return val >= (max_g_value - error_threshold_for_max_g_value)

    @staticmethod
    def is_min(val):
        return val <= (min_g_value + error_threshold_for_min_g_value)

    @staticmethod
    def is_impossible_g(x, y, z):
        return IMPOSSIBLE_G_MIN_THRESHOLD < math.sqrt((x * x) + (y * y) + (z * z))

    @staticmethod
    def is_spike(val1, val2):
        return abs(val2 - val1) >= spike_threshold

    @staticmethod
    def is_close(val1, val2):
        return abs(val1 - val2) <= max(rtol * max(abs(val1), abs(val2)), IMPOSSIBLE_G_VALUE_THRESHOLD)

    def update_zero_g_vals_for_all_axes(self):
        if self.is_zero(self.x):
            global X_zero_vals
            X_zero_vals += 1

        if self.is_zero(self.y):
            global Y_zero_vals
            Y_zero_vals += 1

        if self.is_zero(self.z):
            global Z_zero_vals
            Z_zero_vals += 1

        if self.is_zero(self.x) and self.is_zero(self.y) and self.is_zero(self.z):
            global XYZ_zero_vals, XYZ_zero_vals_loc, XYZ_zero_vals_start_loc
            # Chandrika
            XYZ_zero_vals += 1
            if XYZ_zero_vals == 1:
                XYZ_zero_vals_start_loc = self.loc

            XYZ_zero_vals_loc = self.loc

    def update_zero_g_vals_with_thresh_for_all_axes(self):
        if self.is_zero_with_thresh(self.x):
            global X_zero_vals_with_error_thresh
            X_zero_vals_with_error_thresh += 1

        if self.is_zero_with_thresh(self.y):
            global Y_zero_vals_with_error_thresh
            Y_zero_vals_with_error_thresh += 1

        if self.is_zero_with_thresh(self.z):
            global Z_zero_vals_with_error_thresh
            Z_zero_vals_with_error_thresh += 1

    def update_max_g_vals_for_all_axes(self):
        global X_consecutive_max_gs
        global X_max_g_vals
        global is_prev_x_max
        global curr_x_max
        global x_max_temp_loc
        global X_consecutive_max_gs_location
        global x_max_start_loc
        global x_max_end_loc

        global Y_max_g_vals
        global Y_consecutive_max_gs
        global is_prev_y_max
        global curr_y_max
        global y_max_temp_loc
        global Y_consecutive_max_gs_location
        global y_max_start_loc
        global y_max_end_loc

        global Z_max_g_vals
        global Z_consecutive_max_gs
        global is_prev_z_max
        global curr_z_max
        global z_max_temp_loc
        global Z_consecutive_max_gs_location
        global z_max_start_loc
        global z_max_end_loc

        if self.is_max(self.x):
            X_max_g_vals += 1
            if X_max_g_vals == 1:
                x_max_start_loc = self.loc
            if is_prev_x_max:
                curr_x_max += 1
            else:
                curr_x_max = 1
                x_max_temp_loc = self.loc
                is_prev_x_max = True
            x_max_end_loc = self.loc
        else:
            is_prev_x_max = False
            if curr_x_max > X_consecutive_max_gs and curr_x_max > 1:
                X_consecutive_max_gs = curr_x_max
                X_consecutive_max_gs_location = x_max_temp_loc

                if X_consecutive_max_gs >= CONTINOUS_G_THRESHOLD:
                    write_logs(x_max_temp_loc, prev_loc,
                               "CONTIGUOUS_MAX_G_VALS_X", X_consecutive_max_gs)

            curr_x_max = 0

        if self.is_max(self.y):
            Y_max_g_vals += 1
            if Y_max_g_vals == 1:
                y_max_start_loc = self.loc
            if is_prev_y_max:
                curr_y_max += 1
            else:
                curr_y_max = 1
                y_max_temp_loc = self.loc
                is_prev_y_max = True
            y_max_end_loc = self.loc
        else:
            is_prev_y_max = False
            if curr_y_max > Y_consecutive_max_gs and curr_y_max > 1:
                Y_consecutive_max_gs = curr_y_max
                Y_consecutive_max_gs_location = y_max_temp_loc

                if Y_consecutive_max_gs >= CONTINOUS_G_THRESHOLD:
                    write_logs(y_max_temp_loc, prev_loc,
                               "CONTIGUOUS_MAX_G_VALS_Y", Y_consecutive_max_gs)

            curr_y_max = 0

        if self.is_max(self.z):
            Z_max_g_vals += 1
            if Z_max_g_vals == 1:
                z_max_start_loc = self.loc
            if is_prev_z_max:
                curr_z_max += 1
            else:
                curr_z_max = 1
                z_max_temp_loc = self.loc
                is_prev_z_max = True
            z_max_end_loc = self.loc
        else:
            is_prev_z_max = False
            if curr_z_max > Z_consecutive_max_gs and curr_z_max > 1:
                Z_consecutive_max_gs = curr_z_max
                Z_consecutive_max_gs_location = z_max_temp_loc

                if Z_consecutive_max_gs >= CONTINOUS_G_THRESHOLD:
                    write_logs(z_max_temp_loc, prev_loc,
                               "CONTIGUOUS_MAX_G_VALS_Z", Z_consecutive_max_gs)

            curr_z_max = 0

    def update_min_g_vals_for_all_axes(self):

        global X_min_g_vals
        global X_consecutive_min_gs
        global is_prev_x_min
        global curr_x_min
        global x_min_temp_loc
        global X_consecutive_min_gs_location
        global x_min_start_loc
        global x_min_end_loc

        global Y_min_g_vals
        global Y_consecutive_min_gs
        global is_prev_y_min
        global curr_y_min
        global y_min_temp_loc
        global Y_consecutive_min_gs_location
        global y_min_start_loc
        global y_min_end_loc

        global Z_min_g_vals
        global Z_consecutive_min_gs
        global is_prev_z_min
        global curr_z_min
        global z_min_temp_loc
        global Z_consecutive_min_gs_location
        global z_min_start_loc
        global z_min_end_loc

        if self.is_min(self.x):
            X_min_g_vals += 1
            if X_min_g_vals == 1:
                x_min_start_loc = self.loc
            if is_prev_x_min:
                curr_x_min += 1
            else:
                curr_x_min = 1
                x_min_temp_loc = self.loc
                is_prev_x_min = True
            x_min_end_loc = self.loc
        else:
            is_prev_x_min = False
            if curr_x_min > X_consecutive_min_gs and curr_x_min > 1:
                X_consecutive_min_gs = curr_x_min
                X_consecutive_min_gs_location = x_min_temp_loc
                if X_consecutive_min_gs >= CONTINOUS_G_THRESHOLD:
                    write_logs(x_min_temp_loc, prev_loc,
                               "CONTIGUOUS_MIN_G_VALS_X", X_consecutive_min_gs)
            curr_x_min = 0

        if self.is_min(self.y):
            Y_min_g_vals += 1
            if Y_min_g_vals == 1:
                y_min_start_loc = self.loc
            if is_prev_y_min:
                curr_y_min += 1
            else:
                curr_y_min = 1
                y_min_temp_loc = self.loc
                is_prev_y_min = True
            y_min_end_loc = self.loc
        else:
            is_prev_y_min = False
            if curr_y_min > Y_consecutive_min_gs and curr_y_min > 1:
                Y_consecutive_min_gs = curr_y_min
                Y_consecutive_min_gs_location = y_min_temp_loc
                if Y_consecutive_min_gs >= CONTINOUS_G_THRESHOLD:
                    write_logs(y_min_temp_loc, prev_loc,
                               "CONTIGUOUS_MIN_G_VALS_Y", Y_consecutive_min_gs)
            curr_y_min = 0

        if self.is_min(self.z):
            Z_min_g_vals += 1
            if Z_min_g_vals == 1:
                z_min_start_loc = self.loc
            if is_prev_z_min:
                curr_z_min += 1
            else:
                curr_z_min = 1
                z_min_temp_loc = self.loc
                is_prev_z_min = True
            z_min_end_loc = self.loc
        else:
            is_prev_z_min = False
            if curr_z_min > Z_consecutive_min_gs and curr_z_min > 1:
                Z_consecutive_min_gs = curr_z_min
                Z_consecutive_min_gs_location = z_min_temp_loc
                if Z_consecutive_min_gs >= CONTINOUS_G_THRESHOLD:
                    write_logs(z_min_temp_loc, prev_loc,
                               "CONTIGUOUS_MIN_G_VALS_Z", Z_consecutive_min_gs)

            curr_z_min = 0

    def update_spike_count_for_all_axes(self):
        global prev_x
        global X_spikes
        global prev_y
        global Y_spikes
        global prev_z
        global Z_spikes
        global x_spike_loc
        global x_spike_start_loc
        global y_spike_loc
        global y_spike_start_loc
        global z_spike_loc
        global z_spike_start_loc

        if prev_x is not None:
            if self.is_spike(prev_x, self.x):
                X_spikes += 1
                if X_spikes == 1:
                    x_spike_start_loc = self.loc
                x_spike_loc = self.loc

        if prev_y is not None:
            if self.is_spike(prev_y, self.y):
                # Chandrika
                Y_spikes += 1
                if Y_spikes == 1:
                    y_spike_start_loc = self.loc
                y_spike_loc = self.loc

        if prev_z is not None:
            if self.is_spike(prev_z, self.z):
                # Chandrika
                Z_spikes += 1
                if Z_spikes == 1:
                    z_spike_start_loc = self.loc
                z_spike_loc = self.loc

    def update_impossible_g_vals_count(self):
        global consecutive_impossible_gs
        global is_prev_impossible
        global curr_impossible
        global consecutive_impossible_temp_loc
        global consecutive_impossible_gs_location
        global new_flag_impossible_gravity_values

        global prev_x
        global prev_y
        global prev_z
        global prev_loc

        if prev_x is not None and prev_y is not None and prev_z is not None and \
                self.is_close(self.x, prev_x) and self.is_close(self.y, prev_y) and self.is_close(self.z, prev_z) and \
                not (self.is_close(self.x, max_g_value) or self.is_close(self.x, min_g_value)) and \
                not (self.is_close(self.y, max_g_value) or self.is_close(self.y, min_g_value)) and \
                not (self.is_close(self.z, max_g_value) or self.is_close(self.z, min_g_value)) and \
                self.is_impossible_g(self.x, self.y, self.z):
            if is_prev_impossible:
                curr_impossible += 1
            else:
                curr_impossible = 1
                consecutive_impossible_temp_loc = prev_loc
                is_prev_impossible = True
        else:
            is_prev_impossible = False
            if curr_impossible >= consecutive_impossible_gs and curr_impossible >= 1:
                consecutive_impossible_gs = curr_impossible + 1
                consecutive_impossible_gs_location = consecutive_impossible_temp_loc

                if consecutive_impossible_gs >= IMPOSSIBLE_CONTINOUS_G_THRESHOLD + 1:
                    # Setting a new counter
                    new_flag_impossible_gravity_values += 1
                    write_logs(consecutive_impossible_temp_loc, prev_loc, "CONTIGUOUS_IMPOSSIBLE_GRAVITY",
                               consecutive_impossible_gs)
            curr_impossible = 0

    def update_all_zeroes_for_all_axes(self):
        global consecutive_all_zeroes_gs
        global is_prev_all_zeroes
        global curr_all_zeroes
        global consecutive_all_zeroes_temp_loc
        global consecutive_all_zeroes_gs_location

        global prev_x
        global prev_y
        global prev_z
        global prev_loc

        if prev_x is not None and prev_y is not None and prev_z is not None and \
                self.is_zero(self.x) and self.is_zero(self.x) and self.is_zero(self.x) and \
                self.is_zero(prev_x) and self.is_zero(prev_y) and self.is_zero(prev_z):
            if is_prev_all_zeroes:
                curr_all_zeroes += 1
            else:
                curr_all_zeroes = 1
                consecutive_all_zeroes_temp_loc = prev_loc
                is_prev_all_zeroes = True
        else:
            is_prev_all_zeroes = False
            if curr_all_zeroes >= consecutive_all_zeroes_gs and curr_all_zeroes >= 1:
                consecutive_all_zeroes_gs = curr_all_zeroes + 1
                consecutive_all_zeroes_gs_location = consecutive_all_zeroes_temp_loc
                if consecutive_all_zeroes_gs >= CONTINOUS_ALL_ZEROES_THRESHOLD:
                    write_logs(consecutive_all_zeroes_temp_loc, prev_loc, "CONTIGUOUS_ADJACENT_ZERO_VALS_XYZ",
                               consecutive_all_zeroes_gs)
            curr_all_zeroes = 0

    def update_identical_non_zeroes_for_all_axes(self):
        global consecutive_identical_non_zeroes_gs
        global is_prev_indentical_non_zeroes
        global curr_indentical_non_zeroes
        global consecutive_indentical_non_zeroes_temp_loc
        global consecutive_identical_non_zeroes_gs_location

        global prev_x
        global prev_y
        global prev_z
        global prev_loc

        if prev_x is not None and prev_y is not None and prev_z is not None and \
                not self.is_zero(self.x) and self.x == self.y == self.z and \
                self.x == prev_x and self.y == prev_y and self.z == prev_z:
            if is_prev_indentical_non_zeroes:
                curr_indentical_non_zeroes += 1
            else:
                curr_indentical_non_zeroes = 1
                consecutive_indentical_non_zeroes_temp_loc = prev_loc
                is_prev_indentical_non_zeroes = True
        else:
            is_prev_indentical_non_zeroes = False
            if curr_indentical_non_zeroes >= consecutive_identical_non_zeroes_gs and curr_indentical_non_zeroes >= 1:
                consecutive_identical_non_zeroes_gs = curr_indentical_non_zeroes + 1
                consecutive_identical_non_zeroes_gs_location = consecutive_indentical_non_zeroes_temp_loc
                if consecutive_identical_non_zeroes_gs >= CONTINOUS_IDENTICAL_NON_ZEROES_THRESHOLD:
                    write_logs(consecutive_indentical_non_zeroes_temp_loc, prev_loc,
                               "CONTIGUOUS_ADJACENT_IDENTICAL_NON_ZERO_VALS_XYZ",
                               consecutive_identical_non_zeroes_gs)
            curr_indentical_non_zeroes = 0

    def update_one_sec_spike_count_for_all_axes(self):
        global prev_loc, prev_x, prev_y, prev_z, is_1s_flagged, SAMPLES_PER_SECOND
        global curr_x_max_val, curr_x_min_val, X_1s_spikes, x_sec_spike_samples, x_sec_spike_count, curr_x_min_val_no, \
            curr_x_max_val_no
        global curr_y_max_val, curr_y_min_val, Y_1s_spikes, y_sec_spike_samples, y_sec_spike_count, curr_y_min_val_no, \
            curr_y_max_val_no
        global curr_z_max_val, curr_z_min_val, Z_1s_spikes, z_sec_spike_samples, z_sec_spike_count, curr_z_min_val_no, \
            curr_z_max_val_no

        if SAMPLES_PER_SECOND is None and prev_loc is not None:
            time_diff = get_time_diff(self.loc, prev_loc)
            if time_diff.microseconds == 34000:
                SAMPLES_PER_SECOND = 30
            else:
                SAMPLES_PER_SECOND = 80

        # Added by Chandrika
        # if is_1s_flagged:
        #     return

        # X Axis
        if curr_x_min_val is None:
            curr_x_min_val = self.x
            curr_x_min_val_no = sample_num

        if curr_x_max_val is None:
            curr_x_max_val = self.x
            curr_x_max_val_no = sample_num

        is_spike = False

        if self.x < curr_x_min_val:
            curr_x_min_val = self.x
            curr_x_min_val_no = sample_num
            if abs(curr_x_max_val - curr_x_min_val) >= spike_threshold:
                # see if difference is less than equal to 8 samples otherwise reset
                if SAMPLES_PER_SECOND is not None and \
                        1 < abs(curr_x_max_val_no - curr_x_min_val_no) <= SAMPLES_PER_SECOND / 10:
                    is_spike = True
                    x_sec_spike_count += 1
                curr_x_max_val = self.x
                curr_x_max_val_no = sample_num

        if self.x > curr_x_max_val:
            curr_x_max_val = self.x
            curr_x_max_val_no = sample_num
            if abs(curr_x_max_val - curr_x_min_val) >= spike_threshold:
                # see if difference is less than equal to 8 samples otherwise reset
                if SAMPLES_PER_SECOND is not None and \
                        1 < abs(curr_x_max_val_no - curr_x_min_val_no) <= SAMPLES_PER_SECOND / 10:
                    is_spike = True
                    x_sec_spike_count += 1
                curr_x_min_val = self.x
                curr_x_min_val_no = sample_num

        x_sec_spike_samples.append((self.loc, self.x, is_spike))

        if x_sec_spike_count > ONE_SEC_SPIKES_COUNT_THRESHOLD:
            X_1s_spikes += 1
            # X_1s_spikes = True
            write_1s_spikes_log(x_sec_spike_samples, 'X')
            x_sec_spike_samples = []
            x_sec_spike_count = 0
            curr_x_min_val = None
            curr_x_max_val = None
            # return
        else:
            if SAMPLES_PER_SECOND is not None and \
                    len(x_sec_spike_samples) == SAMPLES_PER_SECOND:
                ele = x_sec_spike_samples[0]
                if ele[1] == curr_x_min_val or ele[1] == curr_x_max_val:
                    x_sec_spike_samples = []
                    x_sec_spike_count = 0
                    curr_x_min_val = None
                    curr_x_max_val = None
                if len(x_sec_spike_samples) > 0:
                    if ele[2]:
                        x_sec_spike_count -= 1
                    x_sec_spike_samples.pop(0)

        # Y Axis

        if curr_y_min_val is None:
            curr_y_min_val = self.y
            curr_y_min_val_no = sample_num

        if curr_y_max_val is None:
            curr_y_max_val = self.y
            curr_y_max_val_no = sample_num

        is_spike = False

        if self.y < curr_y_min_val:
            curr_y_min_val = self.y
            curr_y_min_val_no = sample_num

            if abs(curr_y_max_val - curr_y_min_val) >= spike_threshold:
                if SAMPLES_PER_SECOND is not None and \
                        1 < abs(curr_y_max_val_no - curr_y_min_val_no) <= SAMPLES_PER_SECOND / 10:
                    is_spike = True
                    y_sec_spike_count += 1
                curr_y_max_val = self.y
                curr_y_max_val_no = sample_num

        if self.y > curr_y_max_val:
            curr_y_max_val = self.y
            curr_y_max_val_no = sample_num
            if abs(curr_y_max_val - curr_y_min_val) >= spike_threshold:
                if SAMPLES_PER_SECOND is not None and \
                        1 < abs(curr_y_max_val_no - curr_y_min_val_no) <= SAMPLES_PER_SECOND / 10:
                    is_spike = True
                    y_sec_spike_count += 1
                curr_y_min_val = self.y
                curr_y_min_val_no = sample_num

        y_sec_spike_samples.append((self.loc, self.y, is_spike))

        if y_sec_spike_count > ONE_SEC_SPIKES_COUNT_THRESHOLD:
            Y_1s_spikes += 1
            # Y_1s_spikes = True

            write_1s_spikes_log(y_sec_spike_samples, 'Y')
            y_sec_spike_samples = []
            y_sec_spike_count = 0
            curr_y_min_val = None
            curr_y_max_val = None
            # return
        else:
            if SAMPLES_PER_SECOND is not None and \
                    len(y_sec_spike_samples) == SAMPLES_PER_SECOND:
                ele = y_sec_spike_samples[0]
                if ele[1] == curr_y_min_val or ele[1] == curr_y_max_val:
                    y_sec_spike_samples = []
                    y_sec_spike_count = 0
                    curr_y_min_val = None
                    curr_y_max_val = None
                if len(y_sec_spike_samples) > 0:
                    if ele[2]:
                        y_sec_spike_count -= 1
                    y_sec_spike_samples.pop(0)

        # Z Axis

        if curr_z_min_val is None:
            curr_z_min_val = self.z
            curr_z_min_val_no = sample_num

        if curr_z_max_val is None:
            curr_z_max_val = self.z
            curr_z_max_val_no = sample_num

        is_spike = False

        if self.z < curr_z_min_val:
            curr_z_min_val = self.z
            curr_z_min_val_no = sample_num
            if abs(curr_z_max_val - curr_z_min_val) >= spike_threshold:
                if SAMPLES_PER_SECOND is not None and \
                        1 < abs(curr_z_max_val_no - curr_z_min_val_no) <= SAMPLES_PER_SECOND / 10:
                    is_spike = True
                    z_sec_spike_count += 1

                curr_z_max_val = self.z
                curr_z_max_val_no = sample_num

        if self.z > curr_z_max_val:
            curr_z_max_val = self.z
            curr_z_max_val_no = sample_num
            if abs(curr_z_max_val - curr_z_min_val) >= spike_threshold:
                if SAMPLES_PER_SECOND is not None and \
                        1 < abs(curr_z_max_val_no - curr_z_min_val_no) <= SAMPLES_PER_SECOND / 10:
                    is_spike = True
                    z_sec_spike_count += 1

                curr_z_min_val = self.z
                curr_z_min_val_no = sample_num

        z_sec_spike_samples.append((self.loc, self.z, is_spike))

        if z_sec_spike_count > ONE_SEC_SPIKES_COUNT_THRESHOLD:
            Z_1s_spikes += 1
            # Z_1s_spikes = True
            write_1s_spikes_log(z_sec_spike_samples, 'Z')
            z_sec_spike_samples = []
            z_sec_spike_count = 0
            curr_z_min_val = None
            curr_z_max_val = None
            # return
        else:
            if SAMPLES_PER_SECOND is not None and \
                    len(z_sec_spike_samples) == SAMPLES_PER_SECOND:
                ele = z_sec_spike_samples[0]
                if ele[1] == curr_z_min_val or ele[1] == curr_z_max_val:
                    z_sec_spike_samples = []
                    z_sec_spike_count = 0
                    curr_z_min_val = None
                    curr_z_max_val = None
                if len(z_sec_spike_samples) > 0:
                    if ele[2]:
                        z_sec_spike_count -= 1
                    z_sec_spike_samples.pop(0)

    def save_current_vals(self):
        global prev_x, prev_y, prev_z, prev_loc
        prev_x = self.x
        prev_y = self.y
        prev_z = self.z
        prev_loc = self.loc

    def update_params(self):
        self.update_zero_g_vals_for_all_axes()
        self.update_zero_g_vals_with_thresh_for_all_axes()
        self.update_max_g_vals_for_all_axes()
        self.update_min_g_vals_for_all_axes()
        self.update_spike_count_for_all_axes()
        self.update_impossible_g_vals_count()
        self.update_one_sec_spike_count_for_all_axes()
        self.update_all_zeroes_for_all_axes()
        self.update_identical_non_zeroes_for_all_axes()
        self.save_current_vals()


def write_1s_spikes_log(spike_samples, axis):
    global prev_x_1s_spike, prev_y_1s_spike, prev_z_1s_spike
    spike_samples = [t for t in spike_samples if t[2]]
    start_sample = spike_samples[0]
    end_sample = spike_samples[-1]

    sample_start_time = start_sample[0]
    sample_end_time = end_sample[0]

    if axis == "X":
        if not same_minute_timestamp(sample_start_time, sample_end_time):
            prev_x_1s_spike = True
        write_logs(sample_start_time, sample_end_time,
                   "COUNT_SPIKES_" + axis + "_1S", 1)
    elif axis == "Y":
        if not same_minute_timestamp(sample_start_time, sample_end_time):
            prev_y_1s_spike = True
        write_logs(sample_start_time, sample_end_time,
                   "COUNT_SPIKES_" + axis + "_1S", 1)
    elif axis == "Z":
        if not same_minute_timestamp(sample_start_time, sample_end_time):
            prev_z_1s_spike = True
        write_logs(sample_start_time, sample_end_time,
                   "COUNT_SPIKES_" + axis + "_1S", 1)


def process_line(line):
    if not line:
        print(("Could not read empty file. (Only header present",))
        return
    curr_line = Line(line)
    curr_line.update_params()


def read_variables_from_file(filename):
    with open(filename) as cache:
        var_array = cache.readlines()
    global prev_x
    prev_x = float(var_array[0].strip())
    global prev_y
    prev_y = float(var_array[1].strip())
    global prev_z
    prev_z = float(var_array[2].strip())

    global is_prev_x_max
    is_prev_x_max = (var_array[3].strip() == "True")
    global curr_x_max
    curr_x_max = int(var_array[4].strip())
    global x_max_temp_loc
    x_max_temp_loc = var_array[5].strip()
    if x_max_temp_loc is "None":
        x_max_temp_loc = None

    global is_prev_y_max
    is_prev_y_max = (var_array[6].strip() == "True")
    global curr_y_max
    curr_y_max = int(var_array[7].strip())
    global y_max_temp_loc
    y_max_temp_loc = var_array[8].strip()
    if y_max_temp_loc is "None":
        y_max_temp_loc = None

    global is_prev_z_max
    is_prev_z_max = (var_array[9].strip() == "True")
    global curr_z_max
    curr_z_max = int(var_array[10].strip())
    global z_max_temp_loc
    z_max_temp_loc = var_array[11].strip()
    if z_max_temp_loc is "None":
        z_max_temp_loc = None

    global is_prev_x_min
    is_prev_x_min = (var_array[12].strip() == "True")
    global curr_x_min
    curr_x_min = int(var_array[13].strip())
    global x_min_temp_loc
    x_min_temp_loc = var_array[14].strip()
    if x_min_temp_loc is "None":
        x_min_temp_loc = None

    global is_prev_y_min
    is_prev_y_min = (var_array[15].strip() == "True")
    global curr_y_min
    curr_y_min = int(var_array[16].strip())
    global y_min_temp_loc
    y_min_temp_loc = var_array[17].strip()
    if y_min_temp_loc is "None":
        y_min_temp_loc = None

    global is_prev_z_min
    is_prev_z_min = (var_array[18].strip() == "True")
    global curr_z_min
    curr_z_min = int(var_array[19].strip())
    global z_min_temp_loc
    z_min_temp_loc = var_array[20].strip()
    if z_min_temp_loc is "None":
        z_min_temp_loc = None

    global previous_day
    previous_day = var_array[21].strip()

    global day_number
    day_number = var_array[22].strip()

    global prev_loc
    prev_loc = var_array[23].strip()
    if prev_loc is "None":
        prev_loc = None

    global sample_num
    sample_num = int(var_array[24].strip())

    # Added on 1st August by Chandrika
    global is_prev_impossible
    is_prev_impossible = (var_array[25].strip() == "True")
    global curr_impossible
    curr_impossible = int(var_array[26].strip())
    global consecutive_impossible_temp_loc
    consecutive_impossible_temp_loc = var_array[27].strip()
    if consecutive_impossible_temp_loc is "None":
        consecutive_impossible_temp_loc = None

    global is_prev_all_zeroes
    is_prev_all_zeroes = (var_array[28].strip() == "True")
    global curr_all_zeroes
    curr_all_zeroes = int(var_array[29].strip())
    global consecutive_all_zeroes_temp_loc
    consecutive_all_zeroes_temp_loc = var_array[30].strip()
    if consecutive_all_zeroes_temp_loc is "None":
        consecutive_all_zeroes_temp_loc = None

    global is_prev_indentical_non_zeroes
    is_prev_indentical_non_zeroes = (var_array[31].strip() == "True")
    global curr_indentical_non_zeroes
    curr_indentical_non_zeroes = int(var_array[32].strip())
    global consecutive_indentical_non_zeroes_temp_loc
    consecutive_indentical_non_zeroes_temp_loc = var_array[33].strip()
    if consecutive_indentical_non_zeroes_temp_loc is "None":
        consecutive_indentical_non_zeroes_temp_loc = None

    global SAMPLES_PER_SECOND
    SAMPLES_PER_SECOND = int(var_array[34].strip())
    print_management_params()


def adjust_cons_values(cons_gs, curr_max):
    return cons_gs if cons_gs > curr_max else curr_max


def clear_parameters():
    # Gets called after every minute is processed:
    global X_max_g_vals, Y_max_g_vals, Z_max_g_vals, X_min_g_vals, Y_min_g_vals, Z_min_g_vals, X_zero_vals, \
        X_zero_vals_with_error_thresh, Y_zero_vals, Y_zero_vals_with_error_thresh, Z_zero_vals, \
        Z_zero_vals_with_error_thresh, XYZ_zero_vals, XYZ_zero_vals_loc, total_time, total_samples, \
        X_consecutive_max_gs, X_consecutive_max_gs_location, Y_consecutive_max_gs, Y_consecutive_max_gs_location, \
        Z_consecutive_max_gs, Z_consecutive_max_gs_location, X_consecutive_min_gs, X_consecutive_min_gs_location, \
        Y_consecutive_min_gs, Y_consecutive_min_gs_location, Z_consecutive_min_gs, Z_consecutive_min_gs_location, \
        consecutive_impossible_gs, data_quality_flag_count, x_spike_loc, y_spike_loc, \
        z_spike_loc, is_1s_flagged, X_1s_spikes, Y_1s_spikes, Z_1s_spikes, X_spikes, Y_spikes, Z_spikes, \
        flags_triggered, x_spike_start_loc, y_spike_start_loc, z_spike_start_loc, XYZ_zero_vals_start_loc, \
        x_max_start_loc, y_max_start_loc, z_max_start_loc, x_min_start_loc, y_min_start_loc, z_min_start_loc, \
        x_max_end_loc, y_max_end_loc, z_max_end_loc, x_min_end_loc, y_min_end_loc, z_min_end_loc, \
        prev_x_1s_spike, prev_y_1s_spike, prev_z_1s_spike, consecutive_all_zeroes_gs, \
        consecutive_identical_non_zeroes_gs, new_flag_impossible_gravity_values, interval_jump_x, interval_jump_y, interval_jump_z

    X_max_g_vals = 0
    Y_max_g_vals = 0
    Z_max_g_vals = 0
    X_min_g_vals = 0
    Y_min_g_vals = 0
    Z_min_g_vals = 0
    X_zero_vals = 0
    X_zero_vals_with_error_thresh = 0
    Y_zero_vals = 0
    Y_zero_vals_with_error_thresh = 0
    Z_zero_vals = 0
    Z_zero_vals_with_error_thresh = 0
    XYZ_zero_vals = 0
    XYZ_zero_vals_loc = None
    total_time = 0
    total_samples = 0
    X_consecutive_max_gs = 0
    Y_consecutive_max_gs = 0
    Z_consecutive_max_gs = 0
    X_consecutive_min_gs = 0
    Y_consecutive_min_gs = 0
    Z_consecutive_min_gs = 0
    consecutive_impossible_gs = 0
    new_flag_impossible_gravity_values = 0  # New Added
    consecutive_all_zeroes_gs = 0
    consecutive_identical_non_zeroes_gs = 0

    data_quality_flag_count = 0
    x_spike_loc = None
    y_spike_loc = None
    z_spike_loc = None

    x_spike_start_loc = None
    y_spike_start_loc = None
    z_spike_start_loc = None
    XYZ_zero_vals_start_loc = None
    is_1s_flagged = 0
    X_1s_spikes = 0
    Y_1s_spikes = 0
    Z_1s_spikes = 0
    X_spikes = 0
    Y_spikes = 0
    Z_spikes = 0
    flags_triggered = []
    x_max_start_loc = None
    y_max_start_loc = None
    z_max_start_loc = None
    x_min_start_loc = None
    y_min_start_loc = None
    z_min_start_loc = None
    x_max_end_loc = None
    y_max_end_loc = None
    z_max_end_loc = None
    x_min_end_loc = None
    y_min_end_loc = None
    z_min_end_loc = None
    prev_x_1s_spike = False
    prev_y_1s_spike = False
    prev_z_1s_spike = False
    interval_jump_x = 0
    interval_jump_y = 0
    interval_jump_z = 0


def not_header(prev_min_data):
    if prev_min_data[0] != 'DAY_OF_DATA':
        return True
    else:
        return False

def same_minute_datetime(timestamp, prev_min):
    if timestamp is None:
        return False
    if prev_min is None:
        return False
    min1 = prev_min.minute
    min2 = mhealth_timestamp_parser(timestamp).minute
    return min1 == min2

def same_minute(timestamp, prev_min):
    if timestamp is None:
        return False
    if prev_min is None:
        return False
    min1 = mhealth_time_parser_for_string(
        prev_min).minute
    min2 = mhealth_timestamp_parser(timestamp).minute
    return min1 == min2


def same_minute_timestamp(timestamp, prev_min):
    if timestamp is None:
        return False
    if prev_min is None:
        return False
    min1 = mhealth_timestamp_parser(prev_min).minute
    min2 = mhealth_timestamp_parser(timestamp).minute
    return min1 == min2


def addData():
    global temp_output_array, X_consecutive_max_gs, Y_consecutive_max_gs, Z_consecutive_max_gs, \
        X_consecutive_min_gs, Y_consecutive_min_gs, Z_consecutive_min_gs, \
        consecutive_impossible_gs, data_quality_flag_count, flags_triggered, \
        consecutive_all_zeroes_gs, consecutive_identical_non_zeroes_gs, new_flag_impossible_gravity_values, \
        sampling_rate, SAMPLES_PER_MINUTE, interval_jump_x, interval_jump_y, interval_jump_z

    SAMPLES_PER_MINUTE = sampling_rate * 60

    X_consecutive_max_gs = adjust_cons_values(X_consecutive_max_gs, curr_x_max)
    Y_consecutive_max_gs = adjust_cons_values(Y_consecutive_max_gs, curr_y_max)
    Z_consecutive_max_gs = adjust_cons_values(Z_consecutive_max_gs, curr_z_max)
    X_consecutive_min_gs = adjust_cons_values(X_consecutive_min_gs, curr_x_min)
    Y_consecutive_min_gs = adjust_cons_values(Y_consecutive_min_gs, curr_y_min)
    Z_consecutive_min_gs = adjust_cons_values(Z_consecutive_min_gs, curr_z_min)
    consecutive_impossible_gs = adjust_cons_values(
        consecutive_impossible_gs, curr_impossible)
    consecutive_all_zeroes_gs = adjust_cons_values(
        consecutive_all_zeroes_gs, curr_all_zeroes)
    consecutive_identical_non_zeroes_gs = adjust_cons_values(consecutive_identical_non_zeroes_gs,
                                                             curr_indentical_non_zeroes)

    if X_spikes > 0:
        data_quality_flag_count = (data_quality_flag_count + 1)
        # Added on 1st August by Chandrika
        flags_triggered.append("COUNT_SPIKES_X")
        write_logs(x_spike_start_loc, x_spike_loc, "COUNT_SPIKES_X", X_spikes)

    if Y_spikes > 0:
        data_quality_flag_count = (data_quality_flag_count + 1)
        # Added on 1st August by Chandrika
        flags_triggered.append("COUNT_SPIKES_Y")
        write_logs(y_spike_start_loc, y_spike_loc, "COUNT_SPIKES_Y", Y_spikes)

    if Z_spikes > 0:
        data_quality_flag_count = (data_quality_flag_count + 1)
        # Added on 1st August by Chandrika
        flags_triggered.append("COUNT_SPIKES_Z")
        write_logs(z_spike_start_loc, z_spike_loc, "COUNT_SPIKES_Z", Z_spikes)

    # if XYZ_zero_vals > 0:
    #     data_quality_flag_count = (data_quality_flag_count + 1)
    #     # Added on 1st August by Chandrika
    #     flags_triggered.append("COUNT_XYZ_ALL_ZEROS")
    #     write_logs(XYZ_zero_vals_start_loc, XYZ_zero_vals_loc, "COUNT_XYZ_ALL_ZEROS", XYZ_zero_vals)

    if X_max_g_vals >= MAX_G_COUNT_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        # Added on 1st August by Chandrika
        flags_triggered.append("COUNT_MAX_G_VALS_X")
        write_logs(x_max_start_loc, x_max_end_loc,
                   "COUNT_MAX_G_VALS_X", X_max_g_vals)

    if Y_max_g_vals >= MAX_G_COUNT_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        # Added on 1st August by Chandrika
        flags_triggered.append("COUNT_MAX_G_VALS_Y")
        write_logs(y_max_start_loc, y_max_end_loc,
                   "COUNT_MAX_G_VALS_Y", Y_max_g_vals)

    if Z_max_g_vals >= MAX_G_COUNT_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        # Added on 1st August by Chandrika
        flags_triggered.append("COUNT_MAX_G_VALS_Z")
        write_logs(z_max_start_loc, z_max_end_loc,
                   "COUNT_MAX_G_VALS_Z", Z_max_g_vals)

    if X_min_g_vals >= MAX_G_COUNT_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        # Added on 1st August by Chandrika
        flags_triggered.append("COUNT_MIN_G_VALS_X")
        write_logs(x_min_start_loc, x_min_end_loc,
                   "COUNT_MIN_G_VALS_X", X_min_g_vals),

    if Y_min_g_vals >= MAX_G_COUNT_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        # Added on 1st August by Chandrika
        flags_triggered.append("COUNT_MIN_G_VALS_Y")
        write_logs(y_min_start_loc, y_min_end_loc,
                   "COUNT_MIN_G_VALS_Y", Y_min_g_vals)

    if Z_min_g_vals >= MAX_G_COUNT_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        # Added on 1st August by Chandrika
        flags_triggered.append("COUNT_MIN_G_VALS_Z")
        write_logs(z_min_start_loc, z_min_end_loc,
                   "COUNT_MIN_G_VALS_Z", Z_min_g_vals)

    if X_consecutive_max_gs >= CONTINOUS_G_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("X_CONTIGUOUS_MAX_G")

    if Y_consecutive_max_gs >= CONTINOUS_G_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("Y_CONTIGUOUS_MAX_G")

    if Z_consecutive_max_gs >= CONTINOUS_G_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("Z_CONTIGUOUS_MAX_G")

    if X_consecutive_min_gs >= CONTINOUS_G_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("X_CONTIGUOUS_MIN_G")

    if Y_consecutive_min_gs >= CONTINOUS_G_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("Y_CONTIGUOUS_MIN_G")

    if Z_consecutive_min_gs >= CONTINOUS_G_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("Z_CONTIGUOUS_MIN_G")

    if consecutive_impossible_gs >= IMPOSSIBLE_CONTINOUS_G_THRESHOLD + 1:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("CONTIGUOUS_IMPOSSIBLE_GRAVITY")
        if consecutive_impossible_gs_location is None and curr_impossible >= IMPOSSIBLE_CONTINOUS_G_THRESHOLD:
            write_logs(start_time, stop_time, "CONTIGUOUS_IMPOSSIBLE_GRAVITY",
                       curr_impossible + 1)

    if consecutive_all_zeroes_gs >= CONTINOUS_ALL_ZEROES_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("CONTIGUOUS_ADJACENT_ZERO_VALS_XYZ")
        if consecutive_all_zeroes_gs_location is None and curr_all_zeroes >= 1:
            write_logs(start_time, stop_time, "CONTIGUOUS_ADJACENT_ZERO_VALS_XYZ",
                       curr_all_zeroes + 1)

    if consecutive_identical_non_zeroes_gs >= CONTINOUS_IDENTICAL_NON_ZEROES_THRESHOLD:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append(
            "CONTIGUOUS_ADJACENT_IDENTICAL_NON_ZERO_VALS_XYZ")
        if consecutive_identical_non_zeroes_gs_location is None and curr_indentical_non_zeroes >= 1:
            write_logs(start_time, stop_time, "CONTIGUOUS_ADJACENT_IDENTICAL_NON_ZERO_VALS_XYZ",
                       curr_indentical_non_zeroes + 1)

    if X_1s_spikes >= 1:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("COUNT_SPIKES_X_1S")
    if Y_1s_spikes >= 1:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("COUNT_SPIKES_Y_1S")
    if Z_1s_spikes >= 1:
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("COUNT_SPIKES_Z_1S")

    if (interval_jump_x >= 1):
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("INTERVALJUMP_X")

    if (interval_jump_y >= 1):
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("INTERVALJUMP_Y")

    if (interval_jump_z >= 1):
        data_quality_flag_count = (data_quality_flag_count + 1)
        flags_triggered.append("INTERVALJUMP_Z")

    if len(temp_output_array) > 0:
        prev_min_data = temp_output_array[-1]
        if not_header(prev_min_data) and data_quality_flag_count != 0:
            # prev_dq_flag_count = int(prev_min_data[36])
            prev_dq_flag_count = int(prev_min_data[34])
            # prev_dq_flags_triggered = prev_min_data[37]  # String seperated by commas
            # String seperated by commas
            prev_dq_flags_triggered = prev_min_data[35]

            prev_dq_flags_triggered = [
            ] if prev_dq_flags_triggered == '' else prev_dq_flags_triggered.split(",")

            # prev_x_consecutive_max_gs = int(prev_min_data[20])
            # prev_x_consecutive_max_gs = int(prev_min_data[22])
            # prev_x_consecutive_max_gs = int(prev_min_data[16])
            prev_x_consecutive_max_gs = int(prev_min_data[14])

            # prev_y_consecutive_max_gs = int(prev_min_data[21])
            # prev_y_consecutive_max_gs = int(prev_min_data[23])
            # prev_y_consecutive_max_gs = int(prev_min_data[17])
            prev_y_consecutive_max_gs = int(prev_min_data[15])

            # prev_z_consecutive_max_gs = int(prev_min_data[22])
            # prev_z_consecutive_max_gs = int(prev_min_data[24])
            # prev_z_consecutive_max_gs = int(prev_min_data[18])
            prev_z_consecutive_max_gs = int(prev_min_data[16])

            # prev_x_consecutive_min_gs = int(prev_min_data[23])
            # prev_x_consecutive_min_gs = int(prev_min_data[25])
            # prev_x_consecutive_min_gs = int(prev_min_data[19])
            prev_x_consecutive_min_gs = int(prev_min_data[17])

            # prev_y_consecutive_min_gs = int(prev_min_data[24])
            # prev_y_consecutive_min_gs = int(prev_min_data[26])
            # prev_y_consecutive_min_gs = int(prev_min_data[20])
            prev_y_consecutive_min_gs = int(prev_min_data[18])

            # prev_z_consecutive_min_gs = int(prev_min_data[25])
            # prev_z_consecutive_min_gs = int(prev_min_data[27])
            # prev_z_consecutive_min_gs = int(prev_min_data[21])
            prev_z_consecutive_min_gs = int(prev_min_data[19])

            # prev_consecutive_impossible_gs = int(prev_min_data[32])
            # prev_consecutive_impossible_gs = int(prev_min_data[34])
            # prev_consecutive_impossible_gs = int(prev_min_data[28])
            prev_consecutive_impossible_gs = int(prev_min_data[26])

            # prev_consecutive_all_zeroes_gs = int(prev_min_data[18])
            # prev_consecutive_all_zeroes_gs = int(prev_min_data[20])
            # prev_consecutive_all_zeroes_gs = int(prev_min_data[14])
            prev_consecutive_all_zeroes_gs = int(prev_min_data[12])

            # prev_consecutive_identical_non_zeroes_gs = int(prev_min_data[19])
            # prev_consecutive_identical_non_zeroes_gs = int(prev_min_data[21])
            # prev_consecutive_identical_non_zeroes_gs = int(prev_min_data[15])
            prev_consecutive_identical_non_zeroes_gs = int(prev_min_data[13])

            prev_min = prev_min_data[2]

            if (X_consecutive_max_gs >= CONTINOUS_G_THRESHOLD > prev_x_consecutive_max_gs) and \
                    (same_minute_datetime(X_consecutive_max_gs_location, prev_min) or X_consecutive_max_gs == SAMPLES_PER_MINUTE):
                prev_dq_flag_count += 1
                # Added on 1st Aug by Chandrika:
                prev_dq_flags_triggered.append("X_CONTIGUOUS_MAX_G")

            if (Y_consecutive_max_gs >= CONTINOUS_G_THRESHOLD > prev_y_consecutive_max_gs) and \
                    (same_minute_datetime(Y_consecutive_max_gs_location, prev_min) or Y_consecutive_max_gs == SAMPLES_PER_MINUTE):
                prev_dq_flag_count += 1
                # Added on 1st Aug by Chandrika:
                prev_dq_flags_triggered.append("Y_CONTIGUOUS_MAX_G")

            if (Z_consecutive_max_gs >= CONTINOUS_G_THRESHOLD > prev_z_consecutive_max_gs) and \
                    (same_minute_datetime(Z_consecutive_max_gs_location, prev_min) or Z_consecutive_max_gs == SAMPLES_PER_MINUTE):
                prev_dq_flag_count += 1
                # Added on 1st Aug by Chandrika:
                prev_dq_flags_triggered.append("Z_CONTIGUOUS_MAX_G")

            if (X_consecutive_min_gs >= CONTINOUS_G_THRESHOLD > prev_x_consecutive_min_gs) and \
                    (same_minute_datetime(X_consecutive_min_gs_location, prev_min) or X_consecutive_min_gs == SAMPLES_PER_MINUTE):
                prev_dq_flag_count += 1
                # Added on 1st Aug by Chandrika:
                prev_dq_flags_triggered.append("X_CONTIGUOUS_MIN_G")

            if (Y_consecutive_min_gs >= CONTINOUS_G_THRESHOLD > prev_y_consecutive_min_gs) and \
                    (same_minute_datetime(Y_consecutive_min_gs_location, prev_min) or Y_consecutive_min_gs == SAMPLES_PER_MINUTE):
                prev_dq_flag_count += 1
                # Added on 1st Aug by Chandrika:
                prev_dq_flags_triggered.append("Y_CONTIGUOUS_MIN_G")

            if (Z_consecutive_min_gs >= CONTINOUS_G_THRESHOLD > prev_z_consecutive_min_gs) and \
                    (same_minute_datetime(Z_consecutive_max_gs_location, prev_min) or Z_consecutive_min_gs == SAMPLES_PER_MINUTE):
                prev_dq_flag_count += 1
                # Added on 1st Aug by Chandrika:
                prev_dq_flags_triggered.append("Z_CONTIGUOUS_MIN_G")

            # Added on 1st Aug by Chandrika:
            if (consecutive_impossible_gs >= IMPOSSIBLE_CONTINOUS_G_THRESHOLD + 1 > prev_consecutive_impossible_gs) and \
                    (same_minute_datetime(consecutive_impossible_gs_location,
                                 prev_min) or consecutive_impossible_gs == SAMPLES_PER_MINUTE):
                prev_dq_flag_count += 1
                prev_dq_flags_triggered.append("CONTIGUOUS_IMPOSSIBLE_GRAVITY")

            if (consecutive_all_zeroes_gs >= CONTINOUS_ALL_ZEROES_THRESHOLD > prev_consecutive_all_zeroes_gs) and \
                    (same_minute_datetime(consecutive_all_zeroes_gs_location,
                                 prev_min) or consecutive_all_zeroes_gs == SAMPLES_PER_MINUTE):
                prev_dq_flag_count += 1
                prev_dq_flags_triggered.append(
                    "CONTIGUOUS_ADJACENT_ZERO_VALS_XYZ")

            if (consecutive_identical_non_zeroes_gs >= CONTINOUS_IDENTICAL_NON_ZEROES_THRESHOLD >
                prev_consecutive_identical_non_zeroes_gs) and \
                    (same_minute_datetime(consecutive_identical_non_zeroes_gs_location,
                                 prev_min) or consecutive_identical_non_zeroes_gs == SAMPLES_PER_MINUTE):
                prev_dq_flag_count += 1
                prev_dq_flags_triggered.append(
                    "CONTIGUOUS_ADJACENT_IDENTICAL_NON_ZERO_VALS_XYZ")

            if prev_x_1s_spike:
                prev_dq_flag_count += 1
                prev_dq_flags_triggered.append("COUNT_SPIKES_X_1S")

            if prev_y_1s_spike:
                prev_dq_flag_count += 1
                prev_dq_flags_triggered.append("COUNT_SPIKES_Y_1S")

            if prev_z_1s_spike:
                prev_dq_flag_count += 1
                prev_dq_flags_triggered.append("COUNT_SPIKES_Z_1S")

            # prev_min_data[36] = prev_dq_flag_count
            prev_min_data[34] = prev_dq_flag_count
            # prev_min_data[37] = ",".join(prev_dq_flags_triggered)
            prev_min_data[35] = ",".join(prev_dq_flags_triggered)

    start_timestamp = mhealth_timestamp_parser(start_time)
    stop_timestamp = mhealth_timestamp_parser(stop_time)

    formatted_start_time = mhealth_time_parser(start_timestamp)
    formatted_stop_time = mhealth_time_parser(stop_timestamp)

    temp_output_array.append([
        day_number,
        str(current_day),
        start_timestamp,
        stop_timestamp,
        sample_num_start,
        X_max_g_vals,
        Y_max_g_vals,
        Z_max_g_vals,
        # str(count_max_out_of_range_vals),  # Added by Chandrika on 14th August
        X_min_g_vals,
        Y_min_g_vals,
        Z_min_g_vals,
        # count_min_out_of_range_vals,  # Added by Chandrika on 14th August``
        XYZ_zero_vals,  # 13 11
        consecutive_all_zeroes_gs,  # 14 12
        consecutive_identical_non_zeroes_gs,  # 15 13
        X_consecutive_max_gs,  # 16 14
        Y_consecutive_max_gs,  # 17 15
        Z_consecutive_max_gs,  # 18 16
        X_consecutive_min_gs,  # 19 17
        Y_consecutive_min_gs,  # 20 18
        Z_consecutive_min_gs,  # 21 19
        X_spikes,  # 22 20
        Y_spikes,  # 23 21
        Z_spikes,  # 24 22
        X_1s_spikes,  # 25 23
        Y_1s_spikes,  # 26 24
        Z_1s_spikes,  # 27 25
        new_flag_impossible_gravity_values,  # 32 28 26
        percentage_time_in_idle_sleep_mode,  # 29 27
        num_samples_in_idle_sleep_mode,  # 30 28
        total_time,  # 31 29
        total_samples,  # 32 30
        interval_jump_x,  # 33 31
        interval_jump_y,  # 34 32
        interval_jump_z,  # 35 33
        data_quality_flag_count,  # 36 34
        ",".join(flags_triggered),  # 37 35
    ])


def to_dataframe(arr):
    return pd.DataFrame(data=arr, columns=QC_STAT_COLUMNS)


def write_logs(time_stamp_start, time_stamp_end, data_quality_flag_code, value):
    if time_stamp_start is None:
        return
    if time_stamp_end is None:
        return

    time_stamp_start = mhealth_timestamp_parser(
        time_stamp_start)
    time_stamp_end = mhealth_timestamp_parser(
        time_stamp_end)

    fp = open(logs_path, "a")

    fp.write(str(day_number) + "," +
             mhealth_time_parser(time_stamp_start) + "," +
             mhealth_time_parser(time_stamp_end) + "," +
             str(data_quality_flag_code) + "," +
             str(value) + "\n")

    fp.close()


def write_adjacent_logs(time_stamp_start, time_stamp_end, data_quality_flag_code, value):
    if time_stamp_start is None:
        return
    if time_stamp_end is None:
        return

    fp = open(logs_path, "a")

    fp.write(str(day_number) + "," +
             mhealth_time_parser(time_stamp_start) + "," +
             mhealth_time_parser(time_stamp_end) + "," +
             str(data_quality_flag_code) + "," +
             str(value) + "\n")

    fp.close()


def write_log_header():
    if not os.path.isfile(logs_path):
        with open(logs_path, "w") as fp:
            fp.write(
                "DAY_OF_DATA,"
                "START_TIME,"
                "END_TIME,"
                "DATA_QUALITY_FLAG_CODE,"
                "DATA_QUALITY_FLAG_VALUE\n"
            )
            fp.close()


def reconcile_adjacent_values():
    min_range = 60 if len(temp_output_array) > 60 else len(
        temp_output_array) - 1
    carry = False

    prev_min_data = temp_output_array[-min_range - 1]

    for i, item in enumerate(temp_output_array[-min_range:]):
        # if int(item[36]) != 0:
        if int(item[34]) != 0:
            # if not_header(prev_min_data) and int(prev_min_data[36]) == 0 and not carry:
            if not_header(prev_min_data) and int(prev_min_data[34]) == 0 and not carry:
                # prev_min_data[36] = '1'
                prev_min_data[34] = '1'
                # prev_min_data[37] = "ADJACENT_INVALID"
                prev_min_data[35] = "ADJACENT_INVALID"
                write_adjacent_logs(prev_min_data[2],
                                    prev_min_data[3],
                                    "ADJACENT_INVALID", 1)
            else:
                carry = False
        else:
            # if not_header(prev_min_data) and int(prev_min_data[36]) != 0 and not carry:
            if not_header(prev_min_data) and int(prev_min_data[34]) != 0 and not carry:
                # item[36] = '1'
                item[34] = '1'
                # item[37] = "ADJACENT_INVALID"  # Since the adjacent tagges samples will have no other flags
                # Since the adjacent tagges samples will have no other flags
                item[35] = "ADJACENT_INVALID"
                write_adjacent_logs(item[2],item[3],
                                    "ADJACENT_INVALID", 1)
                carry = True
            else:
                carry = False
        prev_min_data = item


def set_day_of_week(timestamp):
    global previous_day
    global current_day
    global day_number

    current_day = datetime.strftime(mhealth_timestamp_parser(timestamp), '%a')

    if not current_day == previous_day:
        previous_day = current_day
        day_number = int(day_number) + 1

# ---------------------------------------------------------Qu's code---------------------------------------------------------


def check_interval_jump(df, timestampstart):
    global interval_jump_x, interval_jump_y, interval_jump_z

    def interval_jump_criteria(value_counts):
        try:
            value_combs = itertools.combinations(value_counts.index[:3], 2)
            value_combs = np.array(list(value_combs))
            value_diffs = np.abs(value_combs[:, 1] - value_combs[:, 0])
            c1 = all(x > 10 for x in value_counts.tolist()[:3])
            c2 = np.all(value_diffs > 0.5)
        except IndexError:
            # print 'Except block:',value_counts.tolist()[:3]
            c1 = np.all(value_counts.tolist()[:1] > 10)
            c2 = False  # if only 1 record in the value_count series, difference will be zero always
        if c1 and c2:
            print(value_counts)
        return c1 and c2

    x_value_counts = df.iloc[:, 1].value_counts()
    y_value_counts = df.iloc[:, 2].value_counts()
    z_value_counts = df.iloc[:, 3].value_counts()

    # run against critiera

    x_interval_jump = interval_jump_criteria(x_value_counts)

    y_interval_jump = interval_jump_criteria(y_value_counts)

    z_interval_jump = interval_jump_criteria(z_value_counts)

    if x_interval_jump:
        # mark the epoch as interval jump x
        write_logs(timestampstart, timestampstart, 'INTERVAL_JUMP_X', 1)

        interval_jump_x += 1

    if y_interval_jump:
        # mark the epoch as interval jump y
        write_logs(timestampstart, timestampstart, 'INTERVAL_JUMP_Y', 1)
        interval_jump_y += 1

    if z_interval_jump:
        # mark the epoch as interval jump z
        write_logs(timestampstart, timestampstart, 'INTERVAL_JUMP_Z', 1)
        interval_jump_z += 1

# ---------------------------------------------------------------------------------------------------------------------------


def check_interval_jump1(x_vals, y_vals, z_vals, timestampstart):
    global interval_jump_x, interval_jump_y, interval_jump_z

    def check_continuous_in_samples(max_val_dict, all_samples):
        var = True
        continuous_val = 0
        max_cont = 0
        for max_val in max_val_dict:
            value = max_val[0]
            count = max_val[1]
            continuous_val = 0
            i = all_samples.index(value)
            for x in range(i+1, len(all_samples)):
                if all_samples[x] == value:
                    continuous_val += 1
                    max_cont = max(max_cont, continuous_val)
                    if continuous_val == count-1:
                        var = False
                        break
                else:
                    continuous_val = 0

        return var

    def interval_jump_criteria(value_counts, arr):
        sorted_d = []
        difference = []
        c1 = False
        c2 = False
        try:
            sorted_d = sorted(list(value_counts.items()),
                              key=lambda x: x[1], reverse=True)

            sorted_d = sorted_d[:3]
            for i in range(len(sorted_d)):
                for j in range(i+1, len(sorted_d)):
                    difference.append(abs(sorted_d[i][0]-sorted_d[j][0]))
            if all([b > 10 for (a, b) in sorted_d[:3]]):
                c1 = True
            else:
                c1 = False
            if len(difference) > 0:
                if all([i > 0.5 for i in difference]):
                    c2 = True
                else:
                    c2 = False

        except IndexError:
            # print 'Except block:',value_counts.tolist()[:3]
            c1 = False
            c2 = False  # if only 1 record in the value_count series, difference will be zero always
        if c1 == True and c2 == True:
            # check_continuous_in_samples(sorted_d, arr)
            return check_continuous_in_samples(sorted_d, arr)
        else:
            return False

    x_value_counts = Counter(x_vals)
    y_value_counts = Counter(y_vals)
    z_value_counts = Counter(z_vals)

    # run against critiera

    x_interval_jump = interval_jump_criteria(x_value_counts, x_vals)

    y_interval_jump = interval_jump_criteria(y_value_counts, y_vals)

    z_interval_jump = interval_jump_criteria(z_value_counts, z_vals)

    if x_interval_jump:
        # mark the epoch as interval jump x
        write_logs(timestampstart, timestampstart, 'INTERVAL_JUMP_X', 1)

        interval_jump_x += 1

    if y_interval_jump:
        # mark the epoch as interval jump y
        write_logs(timestampstart, timestampstart, 'INTERVAL_JUMP_Y', 1)
        interval_jump_y += 1

    if z_interval_jump:
        # mark the epoch as interval jump z
        write_logs(timestampstart, timestampstart, 'INTERVAL_JUMP_Z', 1)
        interval_jump_z += 1

# ---------------------------------------------------------------------------------------------------------------------------


def qc_single_file(filename, output_folder):
    global percentage_time_in_idle_sleep_mode, total_samples, total_time, num_samples_in_idle_sleep_mode, \
        start_time, stop_time, temp_output_array, logs_path, sample_num, sample_num_start, sampling_rate,\
        interval_jump_x, interval_jump_y, interval_jump_z
    sample_count_for_sampling_rate = 0
    split_file_path = filename.strip().split("/")
    file_name = split_file_path[-1]
    split_file_name = file_name.split(".")
    file_name = ".".join(split_file_name[:-2])
    one_second_samples = []

    logs_path, cache_filename = get_qc_output_filepaths(output_folder)
    one_second_samples_x = []
    one_second_samples_y = []
    one_second_samples_z = []
    write_log_header()

    if os.path.isfile(cache_filename):
        read_variables_from_file(cache_filename)
    if filename.endswith('gz'):
        use_open = gzip.open
    else:
        use_open = open
    with use_open(filename) as fp:
        if not next(fp):
            print(("Could not read empty file ", filename))
            fp.close()
            return
        line = fp.readline().strip()
        if not line:
            fp.close()
            return
        line = line.split(",")
        one_second_samples.append([line[0], float(line[1]), float(
            line[2]), float(line[3])])  # Interval Jump
        one_second_samples_x.append(float(line[1]))
        one_second_samples_y.append(float(line[2]))
        one_second_samples_z.append(float(line[3]))
        # Setting second to first second
        curr_second = line[0].split(" ")[1][:-4][6:]
        set_day_of_week(line[0])
        curr_minute = mhealth_timestamp_parser(line[0]).minute
        minute = curr_minute

        start = 0
        stop = 0
        count = 0
        pre_x = None
        pre_y = None
        pre_z = None
        line_counter = 0

        data = []
        contiguous_regions = []

        while line:
            sample_num_start = sample_num
            timestampstart = str(line[0])
            while curr_minute == minute:
                next_second = line[0].split(" ")[1][:-4][6:]
                # Incrementing sample count for sampling rate
                if curr_second == next_second:
                    one_second_samples.append(
                        [line[0], float(line[1]), float(line[2]), float(line[3])])
                    one_second_samples_x.append(float(line[1]))
                    one_second_samples_y.append(float(line[2]))
                    one_second_samples_z.append(float(line[3]))

                    if sample_count_for_sampling_rate >= 0:
                        sample_count_for_sampling_rate += 1
                        sampling_rate = sample_count_for_sampling_rate

                else:
                    #
                    curr_second = line[0].split(" ")[1][:-4][6:]
                    # one_second_samples_df=pd.DataFrame(one_second_samples)
                    # check_interval_jump(one_second_samples_df, timestampstart)
                    check_interval_jump1(
                        one_second_samples_x, one_second_samples_y, one_second_samples_z, timestampstart)
                    one_second_samples = []
                    one_second_samples_x = []
                    one_second_samples_y = []
                    one_second_samples_z = []

                    timestampstart = str(line[0])
                    one_second_samples.append(
                        [line[0], float(line[1]), float(line[2]), float(line[3])])
                    one_second_samples_x.append(float(line[1]))
                    one_second_samples_y.append(float(line[2]))
                    one_second_samples_z.append(float(line[3]))
                    sample_count_for_sampling_rate = -1

                sample_num += 1
                data.append(line)

                x = float(line[1])
                y = float(line[2])
                z = float(line[3])

                if x == pre_x and y == pre_y and z == pre_z and x != 0 and y != 0 and z != 0:
                    stop = stop + 1
                    count = count + 1
                else:
                    if start != stop and count > 0:
                        contiguous_regions.append((start, stop - 1))
                        start = stop
                        count = 0
                    else:
                        if total_samples != 0:
                            start = start + 1
                    stop = stop + 1
                pre_x = x
                pre_y = y
                pre_z = z

                total_samples = total_samples + 1

                process_line(line)

                line = fp.readline().strip()

                if line:
                    line = line.split(",")
                    curr_minute = mhealth_timestamp_parser(line[0]).minute
                else:
                    break

            if start != stop and count > 0:
                contiguous_regions.append((start, stop - 1))
            # sample_num_end = sample_num

            percentage_time_in_idle_sleep_mode, num_samples_in_idle_sleep_mode, total_time, start_time, \
                stop_time = check_idle_sleep_mode(contiguous_regions, data)

            addData()
            # sample_num_start = sample_num_end
            clear_parameters()
            data = []
            contiguous_regions = []
            minute = curr_minute
            start = 0
            stop = 0
            count = 0
            print('processed ' + str(line_counter) + ' lines\r')
            line_counter += 1
        reconcile_adjacent_values()
        fp.close()
        save_params(cache_filename)
        clear_parameters()
    result = to_dataframe(temp_output_array)
    temp_output_array = []
    return result

def get_qc_output_filepaths(output_path):
    intermediate_path = os.path.join(output_path, 'qc_intermediate')
    os.makedirs(intermediate_path, exist_ok=True)
    logs_path = os.path.join(intermediate_path, "QC_Logs.csv")
    cache_filename = os.path.join(intermediate_path, "QC_temp")
    return logs_path, cache_filename

def add_prediction_column(result):
    result['PREDICTION'] = result['DATA_QUALITY_FLAG_COUNT'] == 0
    result['PREDICTION'] = result['PREDICTION'].map(lambda x: 'Good' if x else 'Bad')
    return result

def main(input_folder, output_folder='.'):
    logs_path, cache_filename = get_qc_output_filepaths(output_folder)
    files = glob(os.path.join(input_folder,
                              'MasterSynced', '**', '*.sensor.csv'), recursive=True)
    result_dfs = list(map(lambda f: qc_single_file(f, output_folder), files))
    result = pd.concat(result_dfs, axis=0)
    result = result.sort_values(by=['START_TIME']).reset_index(drop=True)
    result = add_prediction_column(result)
    if os.path.exists(cache_filename):
        os.remove(cache_filename)
    return result


if __name__ == "__main__":
    print(main('D:/data/MDCAS', '.', pid='SPADES_17'))
