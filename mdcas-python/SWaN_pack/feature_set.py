import SWaN_pack.spectrum as spectrum
import SWaN_pack.orientation as orientation
import pandas as pd
import SWaN_pack.config as config

def compute_extra_features(X,sampling):
   
    feature_list = []

    ori_feature_extractor = orientation.OrientationFeature(X, subwins=config.winSize)
    ori_feature_extractor.estimate_orientation(unit='deg')

    feature_list.append(ori_feature_extractor.ori_x_median())
    feature_list.append(ori_feature_extractor.ori_y_median())
    feature_list.append(ori_feature_extractor.ori_z_median())
    
    spectrum_feature_extractor = spectrum.FrequencyFeature(X, sr=sampling)
    spectrum_feature_extractor.fft()
    spectrum_feature_extractor.peaks()

    feature_list.append(spectrum_feature_extractor.limited_band_total_power(low=0.15,high=0.41))
    feature_list.append(spectrum_feature_extractor.limited_band_total_power(low=1, high=1.7))
    feature_list.append(spectrum_feature_extractor.limited_band_total_power(low=0.42, high=2.6))
    feature_list.append(spectrum_feature_extractor.limited_band_total_power(low=2.7, high=5))

    # feature_list.append(spectrum_feature_extractor.dominant_frequency())
    # feature_list.append(spectrum_feature_extractor.dominant_frequency_power())
    feature_list.append(spectrum_feature_extractor.total_power())


    result = pd.concat(feature_list, axis=1)
    return result
