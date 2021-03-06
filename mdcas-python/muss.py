import numpy as np
import os
from glob import glob
import pandas as pd
from padar_converter.mhealth import dataset, fileio, dataframe
from padar_parallel.groupby import GroupBy, GroupByWindowing
from padar_parallel.grouper import MHealthGrouper
from padar_parallel.windowing import MhealthWindowing
from padar_parallel.join import join_as_dataframe
from padar_parallel.sort import sort_by_file_timestamp
from padar_features.feature_extractor import FeatureExtractor
from padar_features.feature_set import FeatureSet
from padar_features.transformations.accelerometer import orientation
from padar_features.libs.data_formatting.decorator import apply_on_accelerometer_dataframe
from dask import delayed
from functools import partial
import pickle


MODEL_FILE = "DW.MO.mdcas_model.pkl"



def find_sensor_files(input_folder):
    return glob(
        os.path.join(input_folder, 'MasterSynced', '**',
                     '*.sensor.csv*'),
        recursive=True)


def load_data(item, all_items, **kwargs):
    # get session boundaries
    metas = GroupBy.get_meta(item)

    # load data
    data_loader = delayed(fileio.load_sensor)
    loaded_data = data_loader(GroupBy.get_data(item))

    return GroupBy.bundle(loaded_data, **metas)


@delayed
@MhealthWindowing.groupby_windowing('sensor')
def compute_features(df, **kwargs):
    return FeatureSet.location_matters(df.values[:, 1:], **kwargs)


def get_feature_set(sensor_files, sampling_rate=80, parallel=False, profiling=True):
    if parallel:
        scheduler = 'processes'
    else:
        scheduler = 'sync'
    groupby = GroupBy(sensor_files,
                      **MhealthWindowing.make_metas(sensor_files))
    grouper = MHealthGrouper(sensor_files)
    groups = [
        grouper.pid_group()
    ]

    groupby.split(
        *groups,
        group_types=['PID'],
        ingroup_sortkey_func=sort_by_file_timestamp,
        descending=False)

    groupby.apply(load_data)
    groupby.apply(compute_features, interval=12.8, step=12.8, sr=sampling_rate)
    groupby.final_join(delayed(join_as_dataframe))
    feature_set = groupby.compute(scheduler=scheduler,profiling=profiling).get_result()
    feature_columns = feature_set.columns
    feature_columns = [col + '_' + 'DW' for col in feature_columns]
    feature_set.columns = feature_columns
    feature_set = feature_set.reset_index()
    return feature_set


def make_input_matrix(feature_df, model_bundle):
    feature_order = model_bundle['feature_order']
    ordered_df = feature_df.loc[:, feature_order]
    X = ordered_df.values
    scaled_X = model_bundle['scaler'].transform(X)
    return scaled_X


def get_train_target(target):
    if target == 'ACTIVITY' or target == 'POSTURE' or target == 'MDCAS':
        return target
    else:
        return 'ACTIVITY'


def group_predictions(predicted_labels, target, class_mapping):
    train_target = get_train_target(target)
    def map_prediction(p):
        result = class_mapping.loc[class_mapping[train_target] == p, target].values[0]
        return result
    return list(map(map_prediction, predicted_labels))


def get_prediction_set(feature_set):
    feature_set = feature_set.dropna()
    indexed_feature_df = feature_set.set_index([
        'START_TIME', 'STOP_TIME', 'PID'
    ])
    p_df = feature_set
    with open(MODEL_FILE, 'rb') as mf:
        model_bundle = pickle.load(mf)
        X = make_input_matrix(indexed_feature_df, model_bundle)
        try:
            predicted_labels = model_bundle['model'].predict(X)
            class_mapping = model_bundle['class_mapping']
            target = model_bundle['name']
            predicted_labels = group_predictions(predicted_labels, target, class_mapping)
        except:
            predicted_labels = X.shape[0] * [np.nan]
        p_df['PREDICTION'] = predicted_labels
    p_df = p_df.loc[(p_df['PREDICTION'] != 'Unknown') & (p_df['PREDICTION'] != 'Transition'),:]
    return p_df


def main(input_folder, sampling_rate=80, parallel=False, profiling=True):
    sensor_files = find_sensor_files(input_folder)
    feature_set = get_feature_set(sensor_files, sampling_rate=sampling_rate, parallel=parallel, profiling=profiling)
    prediction_set = get_prediction_set(feature_set)
    return feature_set, prediction_set


if __name__ == '__main__':
    main('D:/data/MDCAS/EIGHT_DAY/', sampling_rate=80)
