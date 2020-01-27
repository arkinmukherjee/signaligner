import os,gzip,pickle
from glob import glob
import datetime
import pandas as pd
import numpy as np
from scipy import optimize

from SWaN_pack import config
from SWaN_pack import utils
from SWaN_pack import feature_set
from clize import run


def mhealth_timestamp_parser(val):
    MHEALTH_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
    return datetime.datetime.strptime(val, MHEALTH_TIMESTAMP_FORMAT)

def find_sensor_files(input_folder):
    return glob(os.path.join(input_folder, 'MasterSynced', '**','*.sensor.csv*'),recursive=True)

def convertToGT3Xplus(files,out_fold):
    for file in files:
        print('Standarizing to GT3Xplus for :'+file)
        outfilename = os.path.basename(file)[:-4]+'.GT3Xplus.csv.gz'
        outfilePath = os.path.join(out_fold,outfilename)

        ori_df = pd.read_csv(file, header=0, skiprows=0, sep=',', compression="infer", quotechar='"', parse_dates=[0],
                         date_parser=mhealth_timestamp_parser)
        ori_col = ori_df.columns
        ori_df.columns = ["HEADER_TIME_STAMP", 'X', 'Y', 'Z']
        df = ori_df[["HEADER_TIME_STAMP", 'Y', 'X', 'Z']]
        df['Z'] = -1 * df['Z']
        df.columns = ori_col
        df.to_csv(outfilePath, index=False, float_format='%.3f', compression='gzip')
        print("Wrote :"+outfilePath)

def get_feature_sleep(tdf,sampling):
    X_axes = utils.as_float64(tdf.values[:, 1:])
    result_axes = feature_set.compute_extra_features(X_axes,sampling)
    return result_axes

def get_feature_set(folder,sampling_rate = 80):
    for file in sorted(glob(os.path.join(folder,'*.sensor.GT3Xplus.csv.gz'))):
        print('Computing feature set for :'+file)
        outfilePath = file[:-7]+'.feature.csv'
        with gzip.open(file) as fp:
            df = pd.read_csv(fp, header=0, sep=',', compression="infer", quotechar='"', parse_dates=[0])
            df.columns = ['HEADER_TIME_STAMP', 'X', 'Y', 'Z']
            time_grouper = pd.TimeGrouper(key='HEADER_TIME_STAMP', freq='30s')
            feature_df = df.groupby(time_grouper).apply(get_feature_sleep,sampling_rate)
            feature_df = feature_df.reset_index(level=['HEADER_TIME_STAMP'])
            final_feature_df = feature_df.dropna(how='any',axis=0,inplace=False)
            final_feature_df.rename(columns={'HEADER_TIME_STAMP':'START_TIME'},inplace=True)
            final_feature_df['HEADER_TIME_STAMP'] = final_feature_df['START_TIME']
            final_feature_df['STOP_TIME'] = final_feature_df['START_TIME'] + pd.Timedelta(seconds=30)
            final_feature_df.to_csv(outfilePath,index=False,float_format='%.3f')
            print('Done writing:'+outfilePath)
            fp.close()

def get_prediction_set(folder):
    trainedModel = pickle.load(open(config.modelPath, "rb"))
    standardScalar = pickle.load(open(config.scalePath, "rb"))
    for file in sorted(glob(os.path.join(folder, '*.feature.csv'))):
        print('Working on:' + file)
        filename = os.path.basename(file)[:-12]
        fdata = pd.read_csv(file)
        fdata = fdata.dropna()
        subfdata = fdata[config.feature_lis]
        if subfdata.empty:
            print(filename + ' is empty, likely raw data is invalid, skip making predictions on this file')
            return
        sfdata = standardScalar.transform(subfdata)
        prediction_prob = trainedModel.predict_proba(sfdata)
        prediction = np.argmax(prediction_prob, axis=1)
        p = prediction.reshape((-1, 1))
        test = fdata[['START_TIME']]
        test["PREDICTED"] = p
        test['PROB_WEAR'] = prediction_prob[:, 0]
        test['PROB_SLEEP'] = prediction_prob[:, 1]
        test['PROB_NWEAR'] = prediction_prob[:, 2]
        test['ORI_X_MEDIAN'] = fdata['ORI_X_MEDIAN'].values
        test['ORI_Y_MEDIAN'] = fdata['ORI_Y_MEDIAN'].values
        test['ORI_Z_MEDIAN'] = fdata['ORI_Z_MEDIAN'].values
        test.rename(columns={'START_TIME': 'HEADER_TIME_STAMP'}, inplace=True)
        test = test[
            ['HEADER_TIME_STAMP', 'PREDICTED', 'ORI_X_MEDIAN', 'ORI_Y_MEDIAN', 'ORI_Z_MEDIAN', 'PROB_WEAR', 'PROB_SLEEP',
             'PROB_NWEAR']]
        outFilePath = os.path.join(folder, filename + ".prediction.csv")
        print(outFilePath)
        test.to_csv(outFilePath, index=False, float_format="%.3f")
        print("Created prediction file:" + outFilePath)

def combine_prediction_set(folder):
    first = True
    for file in sorted(glob(os.path.join(folder, '*.prediction.csv'))):
        print('Working on:' + file)

        df = pd.read_csv(file, parse_dates=[0])
        if first:
            firstName = os.path.basename(file).split('.')[2]
            final_df = df
            first = False
        else:
            final_df = pd.concat([final_df, df], ignore_index=True)

    final_df.sort_values(by=config.timeString, inplace=True)

    lastName = os.path.basename(file).split('.')[2]
    PID = os.path.basename(os.path.dirname(folder))
    outFileName = 'SWaN.'+str(PID)+'.' + firstName + '.to.' + lastName + '.predictionCombined.csv'
    outFilePath = os.path.join(folder, outFileName)

    final_df.to_csv(outFilePath, index=False, float_format="%.3f")
    print("Cobined prediction file:" + outFilePath)


def mhealth_timestamp_parser_second(val):
    MHEALTH_TIMESTAMP_FORMAT_SEC = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.strptime(val, MHEALTH_TIMESTAMP_FORMAT_SEC)

def contigous_regions(condition):
    d = np.diff(condition)
    idx, = d.nonzero()
    idx += 1
    idx = np.r_[0, idx - 1]
    idx = np.r_[idx, condition.size - 1]

    bout_lis = []
    for i in range(len(idx) - 1):
        if (i == 0):
            first = idx[i]
        else:
            first = idx[i] + 1
        second = idx[i + 1]
        bout_lis = bout_lis + [[first, second]]

    this_ar = np.asarray(bout_lis)

    return this_ar


def perform_prediction_filtering(tdf):
    WIN_IN_MIN = 2
    WEAR_MIN = 3 * WIN_IN_MIN
    SLEEP_MIN = 10 * WIN_IN_MIN
    SLEEP_CERTAIN = 38 * WIN_IN_MIN
    NWEAR_MIN = 10 * WIN_IN_MIN
    NWEAR_CERTAIN = 38 * WIN_IN_MIN
    BEFORE_AFTER_MIN = 5

    PROB_WEAR = 'PROB_WEAR'
    PROB_SLEEP = 'PROB_SLEEP'
    PROB_NWEAR = 'PROB_NWEAR'

    ar = tdf['PREDICTED'].values
    bout_array = contigous_regions(ar)

    if((bout_array.shape[0]==1) & (tdf.iloc[0]['PREDICTED']==1)):
        tdf['PREDICTED_SMOOTH'] = 2
        tdf['PROB_WEAR_SMOOTH'] = tdf[PROB_WEAR]
        tdf['PROB_SLEEP_SMOOTH'] = tdf[PROB_NWEAR]
        tdf['PROB_NWEAR_SMOOTH'] = tdf[PROB_SLEEP]
        return tdf
    elif((bout_array.shape[0]==1) & (tdf.iloc[0]['PREDICTED']==2)):
        tdf['PREDICTED_SMOOTH'] = 2
        tdf['PROB_WEAR_SMOOTH'] = tdf[PROB_WEAR]
        tdf['PROB_SLEEP_SMOOTH'] = tdf[PROB_SLEEP]
        tdf['PROB_NWEAR_SMOOTH'] = tdf[PROB_NWEAR]
        return tdf
    elif((bout_array.shape[0]==1) & (tdf.iloc[0]['PREDICTED']==0)):
        tdf['PREDICTED_SMOOTH'] = 0
        tdf['PROB_WEAR_SMOOTH'] = tdf[PROB_WEAR]
        tdf['PROB_SLEEP_SMOOTH'] = tdf[PROB_SLEEP]
        tdf['PROB_NWEAR_SMOOTH'] = tdf[PROB_NWEAR]
        return tdf
    else:
        bout_df = pd.DataFrame(bout_array, columns=['START_IND', 'STOP_IND'])
        bout_df['WEAR_ENERGY'] = -1
        bout_df['SLEEP_ENERGY'] = -1
        bout_df['NWEAR_ENERGY'] = -1
        bout_df['CONFIDENCE_DIFF'] = -1
        bout_df['LENGTH'] = -1
        bout_df['PREDICTED'] = -1

        for bout_ind, bout_row in bout_df.iterrows():
            tmp_df = tdf.loc[bout_row['START_IND']:bout_row['STOP_IND']]
            tmp_df.reset_index(inplace=True)
            bout_df['LENGTH'].iloc[bout_ind] = len(tmp_df.index)
            bout_df['PREDICTED'].iloc[bout_ind] = tmp_df.loc[0]['PREDICTED']
            bout_df['WEAR_ENERGY'].iloc[bout_ind] = tmp_df[PROB_WEAR].sum()
            bout_df['SLEEP_ENERGY'].iloc[bout_ind] = tmp_df[PROB_SLEEP].sum()
            bout_df['NWEAR_ENERGY'].iloc[bout_ind] = tmp_df[PROB_NWEAR].sum()
            bout_df['CONFIDENCE_DIFF'].iloc[bout_ind] = min(np.sum(np.absolute(np.diff(tmp_df[[PROB_WEAR, PROB_SLEEP, PROB_NWEAR]], axis=1)), axis=0) / len(tmp_df.index))

        start_ind = bout_df.iloc[0]['START_IND']
        stop_ind = bout_df.iloc[-1]['STOP_IND']
        new_df = pd.DataFrame(columns=list(tdf.columns) + ['PROB_WEAR_SMOOTH', 'PROB_SLEEP_SMOOTH', 'PROB_NWEAR_SMOOTH',
                                                              'PREDICTED_SMOOTH'])
        for bout_ind, bout_row in bout_df.iterrows():
            this_df = tdf.loc[bout_row['START_IND']:bout_row['STOP_IND']]
            this_df_ori = this_df[['ORI_X_MEDIAN','ORI_Y_MEDIAN','ORI_Z_MEDIAN']]
            bout_len_min = (bout_row['STOP_IND'] - bout_row['START_IND'] + 1) / 2.0

            this_ind_start = bout_row['START_IND']
            this_ind_stop = bout_row['STOP_IND']
            ref_before = this_ind_start - (BEFORE_AFTER_MIN * WIN_IN_MIN)
            ref_after = this_ind_stop + (BEFORE_AFTER_MIN * WIN_IN_MIN)
            if (ref_before <= start_ind):
                ref_before = start_ind
            if (ref_after >= stop_ind):
                ref_after = stop_ind

            before_period = bout_df[(bout_df['STOP_IND'] >= ref_before) & (bout_df['STOP_IND'] < this_ind_start)]
            after_period = bout_df[(bout_df['START_IND'] <= ref_after) & (bout_df['START_IND'] > this_ind_stop)]

            if (not (before_period.empty | after_period.empty)):
                before_period_max_len = before_period.ix[before_period['LENGTH'].argmax()]
                before_class = before_period_max_len['PREDICTED']
                before_energy = max(before_period_max_len['WEAR_ENERGY'], before_period_max_len['SLEEP_ENERGY'],before_period_max_len['NWEAR_ENERGY'])
                after_period_max_len = after_period.ix[after_period['LENGTH'].argmax()]
                after_class = after_period_max_len['PREDICTED']
                after_energy = max(after_period_max_len['WEAR_ENERGY'], after_period_max_len['SLEEP_ENERGY'],after_period_max_len['NWEAR_ENERGY'])
                if (before_class == after_class):
                    potential_class = before_class
                    check_energy = (0.5) * (before_energy + after_energy)
                else:
                    potential_class = before_class
                    check_energy = before_energy
                    potential_class_next = before_class
                    if (after_energy > before_energy):
                        potential_class = after_class
                        potential_class_next = before_class
                        check_energy = after_energy

            if (after_period.empty):
                before_period_max_len = before_period.ix[before_period['LENGTH'].argmax()]
                before_class = before_period_max_len['PREDICTED']
                before_energy = max(before_period_max_len['WEAR_ENERGY'], before_period_max_len['SLEEP_ENERGY'],before_period_max_len['NWEAR_ENERGY'])
                potential_class = before_class
                check_energy = before_energy
                potential_class_next = before_class

            if (before_period.empty):
                after_period_max_len = after_period.ix[after_period['LENGTH'].argmax()]
                after_class = after_period_max_len['PREDICTED']
                after_energy = max(after_period_max_len['WEAR_ENERGY'], after_period_max_len['SLEEP_ENERGY'],after_period_max_len['NWEAR_ENERGY'])

                potential_class = after_class
                check_energy = after_energy
                potential_class_next = after_class

            if (bout_row['PREDICTED'] == 0):
                if (bout_row['LENGTH'] < WEAR_MIN):
                    if (check_energy >= bout_row['WEAR_ENERGY']):
                        if (potential_class == 1):
                            this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_SLEEP]
                            this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_WEAR]
                            this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_NWEAR]
                        elif (potential_class == 2):
                            this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_NWEAR]
                            this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_SLEEP]
                            this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_WEAR]
                        else:
                            this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_WEAR]
                            this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_SLEEP]
                            this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_NWEAR]

                        this_df['PREDICTED_SMOOTH'] = potential_class
                    else:
                        this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_WEAR]
                        this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_SLEEP]
                        this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_NWEAR]
                        this_df['PREDICTED_SMOOTH'] = this_df['PREDICTED']

                else:
                    this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_WEAR]
                    this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_SLEEP]
                    this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_NWEAR]
                    this_df['PREDICTED_SMOOTH'] = this_df['PREDICTED']

            if (bout_row['PREDICTED'] == 1):
                if (bout_row['LENGTH'] < SLEEP_MIN):
                    if (check_energy > bout_row['SLEEP_ENERGY']):
                        if (potential_class == 1):
                            this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_WEAR]
                            this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_SLEEP]
                            this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_NWEAR]
                        elif (potential_class == 2):
                            this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_WEAR]
                            this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_NWEAR]
                            this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_SLEEP]
                        else:
                            this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_SLEEP]
                            this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_WEAR]
                            this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_NWEAR]
                        this_df['PREDICTED_SMOOTH'] = potential_class
                    else:
                        this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_SLEEP]
                        this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_WEAR]
                        this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_NWEAR]
                        this_df['PREDICTED_SMOOTH'] = 0
                else:
                    this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_WEAR]
                    this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_SLEEP]
                    this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_NWEAR]
                    this_df['PREDICTED_SMOOTH'] = 1

            if (bout_row['PREDICTED'] == 2):
                if (bout_row['LENGTH'] < NWEAR_MIN):
                    if (check_energy > bout_row['NWEAR_ENERGY']):
                        if (potential_class == 2):
                            this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_WEAR]
                            this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_SLEEP]
                            this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_NWEAR]
                        elif (potential_class == 1):
                            this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_WEAR]
                            this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_NWEAR]
                            this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_SLEEP]
                        else:
                            this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_NWEAR]
                            this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_SLEEP]
                            this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_WEAR]
                        this_df['PREDICTED_SMOOTH'] = potential_class
                    else:
                        this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_NWEAR]
                        this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_SLEEP]
                        this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_WEAR]
                        this_df['PREDICTED_SMOOTH'] = 0
                else:
                    this_df['PROB_WEAR_SMOOTH'] = this_df[PROB_WEAR]
                    this_df['PROB_SLEEP_SMOOTH'] = this_df[PROB_SLEEP]
                    this_df['PROB_NWEAR_SMOOTH'] = this_df[PROB_NWEAR]
                    this_df['PREDICTED_SMOOTH'] = 2

            new_df = pd.concat([new_df, this_df], ignore_index=True)
        return new_df

def perform_smoothing_initial(folder):
    for file in sorted(glob(os.path.join(folder, '*.predictionCombined.csv'))):
        print('Working on:' + file)
        filename = os.path.basename(file)[:-4]
        outFilePath = os.path.join(folder, filename + '.CommonsenseRules.csv')
        df = pd.read_csv(file, header=0, skiprows=0, sep=',', compression="infer", quotechar='"',
                         parse_dates=[0], date_parser=mhealth_timestamp_parser_second)
        filtered_df = perform_prediction_filtering(df)
        filtered_df = filtered_df[['HEADER_TIME_STAMP', 'PREDICTED', 'PREDICTED_SMOOTH',
                                   'ORI_X_MEDIAN', 'ORI_Y_MEDIAN', 'ORI_Z_MEDIAN', 'PROB_WEAR',
                                   'PROB_SLEEP', 'PROB_NWEAR',
                                   'PROB_WEAR_SMOOTH', 'PROB_SLEEP_SMOOTH', 'PROB_NWEAR_SMOOTH']]
        filtered_df.to_csv(outFilePath, index=False, float_format='%.3f')
        print("Done filtering predictions for:" + file)

def piecewise_linear(x, x0, y0, k1, k2):
    return np.piecewise(x, [x <= 30, x > 30 ], [lambda x:0, lambda x:k2*x+ k2*x0])

def same_ori_region(condition):
    d = np.absolute(np.diff(condition,axis=0))
    idx = np.argwhere((d[:,0]>=1) | (d[:,1]>=1) | (d[:,2]>=1)).flatten()
    return len(idx)

def perform_prediction_filtering_final(tdf):

    ori_change_dist = pd.read_csv(config.oriChangePath)
    x_g = ori_change_dist['DURATION(MIN)'].values
    y_g = ori_change_dist['NUM_ORIENT_CHANGE'].values
    p, e = optimize.curve_fit(piecewise_linear, x_g, y_g)

    PROB_WEAR = 'PROB_WEAR_SMOOTH'
    PROB_SLEEP = 'PROB_SLEEP_SMOOTH'
    PROB_NWEAR = 'PROB_NWEAR_SMOOTH'

    ori_header = ['ORI_X_MEDIAN', 'ORI_Y_MEDIAN', 'ORI_Z_MEDIAN']

    WIN_IN_MIN = 2
    WEAR_MIN = 3 * WIN_IN_MIN
    SLEEP_MIN = 10 * WIN_IN_MIN
    SLEEP_CERTAIN = 38 * WIN_IN_MIN
    NWEAR_MIN = 10 * WIN_IN_MIN
    NWEAR_CERTAIN = 38 * WIN_IN_MIN
    BEFORE_AFTER_MIN = 5
    CONFIDENCE_DIFF_THRESH = 0.2
    DOUBLE_CHECK = 180 * WIN_IN_MIN

    ar = tdf['PREDICTED_SMOOTH'].values
    bout_array = contigous_regions(ar)

    if((bout_array.shape[0]==1) & (tdf.iloc[0]['PREDICTED_SMOOTH']==1)):
        tdf['PREDICTED_SMOOTH_2'] = 2
        tdf['PROB_WEAR_SMOOTH_2'] = tdf['PROB_WEAR_SMOOTH']
        tdf['PROB_SLEEP_SMOOTH_2'] = tdf['PROB_NWEAR_SMOOTH']
        tdf['PROB_NWEAR_SMOOTH_2'] = tdf['PROB_SLEEP_SMOOTH']
        return tdf
    elif((bout_array.shape[0]==1) & (tdf.iloc[0]['PREDICTED_SMOOTH']==2)):
        tdf['PREDICTED_SMOOTH_2'] = 2
        tdf['PROB_WEAR_SMOOTH_2'] = tdf['PROB_WEAR_SMOOTH']
        tdf['PROB_SLEEP_SMOOTH_2'] = tdf['PROB_SLEEP_SMOOTH']
        tdf['PROB_NWEAR_SMOOTH_2'] = tdf['PROB_NWEAR_SMOOTH']
        return tdf
    elif((bout_array.shape[0]==1) & (tdf.iloc[0]['PREDICTED_SMOOTH']==0)):
        tdf['PREDICTED_SMOOTH_2'] = 0
        tdf['PROB_WEAR_SMOOTH_2'] = tdf['PROB_WEAR_SMOOTH']
        tdf['PROB_SLEEP_SMOOTH_2'] = tdf['PROB_SLEEP_SMOOTH']
        tdf['PROB_NWEAR_SMOOTH_2'] = tdf['PROB_NWEAR_SMOOTH']
        return tdf

    else:

        bout_df = pd.DataFrame(bout_array,columns=['START_IND','STOP_IND'])
        bout_df['WEAR_ENERGY'] = -1
        bout_df['SLEEP_ENERGY'] = -1
        bout_df['NWEAR_ENERGY'] = -1
        bout_df['CONFIDENCE_DIFF'] = -1
        bout_df['LENGTH'] = -1
        bout_df['PREDICTED_SMOOTH'] = -1

        for bout_ind,bout_row in bout_df.iterrows():
            tmp_df = tdf.loc[bout_row['START_IND']:bout_row['STOP_IND']]
            tmp_df.reset_index(inplace=True)
            bout_df['LENGTH'].iloc[bout_ind] = len(tmp_df.index)
            bout_df['PREDICTED_SMOOTH'].iloc[bout_ind] = tmp_df.loc[0]['PREDICTED_SMOOTH']
            bout_df['WEAR_ENERGY'].iloc[bout_ind] = tmp_df[PROB_WEAR].sum()
            bout_df['SLEEP_ENERGY'].iloc[bout_ind] = tmp_df[PROB_SLEEP].sum()
            bout_df['NWEAR_ENERGY'].iloc[bout_ind] = tmp_df[PROB_NWEAR].sum()
            bout_df['CONFIDENCE_DIFF'].iloc[bout_ind] = min(np.sum(np.absolute(np.diff(tmp_df[[PROB_WEAR,PROB_SLEEP,PROB_NWEAR]],axis=1)),axis=0)/len(tmp_df.index))

        start_ind = bout_df.iloc[0]['START_IND']
        stop_ind = bout_df.iloc[-1]['STOP_IND']
        new_df = pd.DataFrame(columns = list(tdf.columns)+['PROB_WEAR_SMOOTH_2','PROB_SLEEP_SMOOTH_2','PROB_NWEAR_SMOOTH_2',
                                                          'PREDICTED_SMOOTH_2'])
        for bout_ind,bout_row in bout_df.iterrows():

            this_df = tdf.loc[bout_row['START_IND']:bout_row['STOP_IND']]
            this_df_ori = this_df[ori_header]
            num_orient_change = same_ori_region(this_df_ori.values)
            bout_len_min = (bout_row['STOP_IND'] - bout_row['START_IND'] + 1)/2.0
            compare_ori_change = piecewise_linear(bout_len_min, *p)

            this_ind_start = bout_row['START_IND']
            this_ind_stop = bout_row['STOP_IND']
            ref_before = this_ind_start-(BEFORE_AFTER_MIN*WIN_IN_MIN)
            ref_after = this_ind_stop+(BEFORE_AFTER_MIN*WIN_IN_MIN)
            if(ref_before <= start_ind):
                ref_before = start_ind
            if(ref_after >= stop_ind):
                ref_after = stop_ind

            before_period = bout_df[(bout_df['STOP_IND']>=ref_before)&
                                    (bout_df['STOP_IND']<this_ind_start)]
            after_period = bout_df[(bout_df['START_IND']<=ref_after)&
                                   (bout_df['START_IND']>this_ind_stop)]

            if(not(before_period.empty | after_period.empty)):
                before_period_max_len = before_period.ix[before_period['LENGTH'].argmax()]
                before_class = before_period_max_len['PREDICTED_SMOOTH']
                before_energy = max(before_period_max_len['WEAR_ENERGY'],before_period_max_len['SLEEP_ENERGY'],
                                    before_period_max_len['NWEAR_ENERGY'])
                after_period_max_len = after_period.ix[after_period['LENGTH'].argmax()]
                after_class = after_period_max_len['PREDICTED_SMOOTH']
                after_energy = max(after_period_max_len['WEAR_ENERGY'],after_period_max_len['SLEEP_ENERGY'],
                                   after_period_max_len['NWEAR_ENERGY'])
                if(before_class==after_class):
                    potential_class = before_class
                    check_energy = (0.5) * (before_energy+after_energy)
                else:
                    potential_class = before_class
                    check_energy = before_energy
                    potential_class_next = before_class
                    if(after_energy>before_energy):
                        potential_class = after_class
                        potential_class_next = before_class
                        check_energy = after_energy

            if(after_period.empty):
                before_period_max_len = before_period.ix[before_period['LENGTH'].argmax()]
                before_class = before_period_max_len['PREDICTED_SMOOTH']
                before_energy = max(before_period_max_len['WEAR_ENERGY'],before_period_max_len['SLEEP_ENERGY'],
                                    before_period_max_len['NWEAR_ENERGY'])

                potential_class = before_class
                check_energy = before_energy
                potential_class_next = before_class

            if(before_period.empty):
                after_period_max_len = after_period.ix[after_period['LENGTH'].argmax()]
                after_class = after_period_max_len['PREDICTED_SMOOTH']
                after_energy = max(after_period_max_len['WEAR_ENERGY'],after_period_max_len['SLEEP_ENERGY'],
                                   after_period_max_len['NWEAR_ENERGY'])

                potential_class = after_class
                check_energy = after_energy
                potential_class_next = after_class


            if(bout_row['PREDICTED_SMOOTH'] in [0]):
                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                this_df['PREDICTED_SMOOTH_2'] = this_df['PREDICTED_SMOOTH']


            if(bout_row['PREDICTED_SMOOTH']==1):
                if(bout_row['STOP_IND']==len(tdf.index)-1):
                    this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                    this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                    this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                    this_df['PREDICTED_SMOOTH_2'] = 1
                else:
                    if(bout_row['LENGTH']<SLEEP_MIN):
                        if(check_energy>bout_row['SLEEP_ENERGY']):
                            if(potential_class==1):
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                            elif(potential_class==2):
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                            else:
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                            this_df['PREDICTED_SMOOTH_2'] = potential_class
                        else:
                            this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                            this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                            this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                            this_df['PREDICTED_SMOOTH_2'] = 0

                    else:
                        if(bout_row['LENGTH']<=SLEEP_CERTAIN):
                            if(num_orient_change>=1):
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                this_df['PREDICTED_SMOOTH_2'] = 1
                            else:
                                if(check_energy>bout_row['SLEEP_ENERGY']):
                                    if(potential_class==1):
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                    elif(potential_class==2):
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                    else:
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                    this_df['PREDICTED_SMOOTH_2'] = potential_class
                                else:
                                    # adjust probabilities
                                    portion = (bout_row['LENGTH']-SLEEP_MIN)/(SLEEP_CERTAIN-SLEEP_MIN)
                                    if(bout_row['WEAR_ENERGY'] > bout_row['NWEAR_ENERGY']):
                                        di = this_df['PROB_SLEEP_SMOOTH'] - this_df['PROB_WEAR_SMOOTH']
                                        print(len(di.index))
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH'] + (portion*di)
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH'] - (portion*di)
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                    else:
                                        di = this_df['PROB_SLEEP_SMOOTH'] - this_df['PROB_NWEAR_SMOOTH']
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH'] + (portion*di)
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH'] - (portion*di)
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                    this_df['PREDICTED_SMOOTH_2'] = this_df['PREDICTED_SMOOTH']

                        elif((bout_row['LENGTH']>SLEEP_CERTAIN) & (bout_row['LENGTH']<=DOUBLE_CHECK)):
                            if(1 in [potential_class,potential_class_next]):
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                this_df['PREDICTED_SMOOTH_2'] = 1
                            else:
                                if(num_orient_change==0):
                                    this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                    this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                    this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                    this_df['PREDICTED_SMOOTH_2'] = 2
                                else:
                                    if(num_orient_change>=compare_ori_change):
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                        this_df['PREDICTED_SMOOTH_2'] = 1
                                    else:
                                        if(check_energy>bout_row['SLEEP_ENERGY']):
                                            if(potential_class==1):
                                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                                this_df['PREDICTED_SMOOTH_2'] = potential_class
                                            elif(potential_class==2):
                                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                                this_df['PREDICTED_SMOOTH_2'] = potential_class
                                            else:
                                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                                this_df['PREDICTED_SMOOTH_2'] = 1
                                        else:
                                            this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                            this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                            this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                            this_df['PREDICTED_SMOOTH_2'] = 1

                        elif (bout_row['LENGTH']>DOUBLE_CHECK):
                            if(num_orient_change==0):
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                this_df['PREDICTED_SMOOTH_2'] = 2
                            else:
                                if(num_orient_change>=compare_ori_change):
                                    this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                    this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                    this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                    this_df['PREDICTED_SMOOTH_2'] = 1
                                else:
                                    this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                    this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                    this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                    this_df['PREDICTED_SMOOTH_2'] = 2


            if(bout_row['PREDICTED_SMOOTH']==2):
                if(bout_row['STOP_IND']==len(tdf.index)-1):
                    this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                    this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                    this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                    this_df['PREDICTED_SMOOTH_2'] = 2
                else:
                    if(bout_row['LENGTH']<NWEAR_MIN):
                        if(check_energy>bout_row['NWEAR_ENERGY']):
                            if(potential_class==2):
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                            elif(potential_class==1):
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                            else:
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                            this_df['PREDICTED_SMOOTH_2'] = potential_class
                        else:
                            this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                            this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                            this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                            this_df['PREDICTED_SMOOTH_2'] = 0

                    else:
                        if(bout_row['LENGTH']<=NWEAR_CERTAIN):
                            if(num_orient_change>=1):
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                this_df['PREDICTED_SMOOTH_2'] = 1
                            else:
                                if(check_energy>bout_row['NWEAR_ENERGY']):
                                    if(potential_class==2):
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                    elif(potential_class==1):
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                    else:
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                    this_df['PREDICTED_SMOOTH_2'] = potential_class
                                else:
                                    # adjust probabilities
                                    portion = (bout_row['LENGTH']-NWEAR_MIN)/(NWEAR_CERTAIN-NWEAR_MIN)
                                    if(bout_row['WEAR_ENERGY'] > bout_row['SLEEP_ENERGY']):
                                        di = this_df['PROB_NWEAR_SMOOTH'] - this_df['PROB_WEAR_SMOOTH']
                                        print(len(di.index))
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH'] + (portion*di)
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH'] - (portion*di)
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                    else:
                                        di = this_df['PROB_NWEAR_SMOOTH'] - this_df['PROB_SLEEP_SMOOTH']
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH'] + (portion*di)
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH'] - (portion*di)
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                    this_df['PREDICTED_SMOOTH_2'] = this_df['PREDICTED_SMOOTH']

                        elif((bout_row['LENGTH']>NWEAR_CERTAIN) & (bout_row['LENGTH']<=DOUBLE_CHECK)):
                            if(1 in [potential_class,potential_class_next]):
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                this_df['PREDICTED_SMOOTH_2'] = 1
                            else:
                                if(num_orient_change==0):
                                    this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                    this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                    this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                    this_df['PREDICTED_SMOOTH_2'] = 2
                                else:
                                    if(num_orient_change>=compare_ori_change):
                                        this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                        this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                        this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                        this_df['PREDICTED_SMOOTH_2'] = 1
                                    else:
                                        if(check_energy>bout_row['NWEAR_ENERGY']):
                                            if(potential_class==2):
                                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                                this_df['PREDICTED_SMOOTH_2'] = potential_class
                                            elif(potential_class==1):
                                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                                this_df['PREDICTED_SMOOTH_2'] = potential_class
                                            else:
                                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                                this_df['PREDICTED_SMOOTH_2'] = 0
                                        else:
                                            this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                            this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                            this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                            this_df['PREDICTED_SMOOTH_2'] = 2

                        elif (bout_row['LENGTH']>DOUBLE_CHECK):
                            if(num_orient_change==0):
                                this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                this_df['PREDICTED_SMOOTH_2'] = 2
                            else:
                                if(num_orient_change>=compare_ori_change):
                                    this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                    this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                    this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                    this_df['PREDICTED_SMOOTH_2'] = 1
                                else:
                                    this_df['PROB_WEAR_SMOOTH_2'] = this_df['PROB_WEAR_SMOOTH']
                                    this_df['PROB_SLEEP_SMOOTH_2'] = this_df['PROB_SLEEP_SMOOTH']
                                    this_df['PROB_NWEAR_SMOOTH_2'] = this_df['PROB_NWEAR_SMOOTH']
                                    this_df['PREDICTED_SMOOTH_2'] = 2
            new_df = pd.concat([new_df,this_df],ignore_index=True)

        return new_df


def perform_smoothing_final(folder, outfolder):
    for file in sorted(glob(os.path.join(folder, '*CommonsenseRules.csv'))):
        print('Working on:' + file)
        outFilePath = os.path.join(outfolder,'SWaN_output.csv')
        df = pd.read_csv(file, header=0, skiprows=0, sep=',', compression="infer", quotechar='"',
                         parse_dates=[0], date_parser=mhealth_timestamp_parser_second)
        filtered_df = perform_prediction_filtering_final(df)
        filtered_df = filtered_df[[config.timeString,'PREDICTED_SMOOTH_2','PROB_WEAR_SMOOTH_2', 'PROB_SLEEP_SMOOTH_2', 'PROB_NWEAR_SMOOTH_2']]
        filtered_df.columns = ['HEADER_START_TIME','LABEL','PROB_WEAR','PROB_SLEEP','PROB_NWEAR']
        filtered_df['HEADER_STOP_TIME'] = filtered_df['HEADER_START_TIME'] + pd.Timedelta(seconds=30)
        filtered_df = filtered_df[['HEADER_START_TIME','HEADER_STOP_TIME','LABEL','PROB_WEAR','PROB_SLEEP','PROB_NWEAR']]

        filtered_df.rename(columns={'HEADER_START_TIME': 'START_TIME', 'HEADER_STOP_TIME':'STOP_TIME','LABEL':'PREDICTION'}, inplace=True)
        filtered_df['PREDICTION'] = filtered_df['PREDICTION'].map({0:'Wear',1:'Sleep',2:'Nonwear'})
        filtered_df.to_csv(outFilePath, index=False, float_format='%.3f',date_format="%Y-%m-%d %H:%M:%S.000")
        print("Done second-pass filtering predictions :" + file)


def main(input_folder, output_folder, sampling_rate=80):
    final_output_folder = output_folder
    intermediate_folder = os.path.join(final_output_folder,'intermediate')
    os.makedirs(intermediate_folder, exist_ok=True)
    sensor_files = find_sensor_files(input_folder)
    convertToGT3Xplus(sensor_files, intermediate_folder)
    get_feature_set(intermediate_folder, sampling_rate=sampling_rate)
    get_prediction_set(intermediate_folder)
    combine_prediction_set(intermediate_folder)
    perform_smoothing_initial(intermediate_folder)
    perform_smoothing_final(intermediate_folder, final_output_folder)
    print('SWaN has completed processing.')



if __name__ == '__main__':
    main('D:/data/MDCAS/SWAN_DEBUG','./outputs/', sampling_rate=80)