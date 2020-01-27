winSize = 30
samplingRate = 80
scalePath = 'SWaN_pack/model/StandardScalar_all_data.sav'
modelPath = 'SWaN_pack/model/LogisticRegression_all_data_F1score_0.51.sav'
# modelPath = 'SWaN_pack/model/RandomForest_all_data_2isto1000_F1score_1.00.sav'

oriChangePath = 'SWaN_pack/model/ori_change_use.csv'
timeString = 'HEADER_TIME_STAMP'

feature_lis = ['X_TOTAL_POWER_BETWEEN_0.15_0.41','X_TOTAL_POWER_BETWEEN_0.42_2.6','X_TOTAL_POWER_BETWEEN_1_1.7',
               'X_TOTAL_POWER_BETWEEN_2.7_5','X_TOTPOW','Y_TOTAL_POWER_BETWEEN_0.15_0.41','Y_TOTAL_POWER_BETWEEN_0.42_2.6',
               'Y_TOTAL_POWER_BETWEEN_1_1.7','Y_TOTAL_POWER_BETWEEN_2.7_5','Y_TOTPOW','Z_TOTAL_POWER_BETWEEN_0.15_0.41',
               'Z_TOTAL_POWER_BETWEEN_0.42_2.6','Z_TOTAL_POWER_BETWEEN_1_1.7','Z_TOTAL_POWER_BETWEEN_2.7_5','Z_TOTPOW']

MHEALTH_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"