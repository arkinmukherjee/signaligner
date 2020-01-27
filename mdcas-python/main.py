import muss as muss_model
import SWaN
import QC
import os
import mhealth
from clize import run
import shutil

def create_output_folder(output_folder, pid):
    output_path = os.path.join(output_folder, pid)
    os.makedirs(output_path, exist_ok=True)
    return output_path

def remove_intermediate(*intermediate_folders):
    for f in intermediate_folders:
        print('removing {}'.format(f))
        shutil.rmtree(f, ignore_errors=True)
    

def main(input_file_or_folder, output_folder, sampling_rate, *, swan=True, muss=True, qc=True, parallel=False, debug=False, profiling=True):
    """Run SWaN, MUSS and QC on an actigraph csv file

    Examples:

        Run all models

            >> pipenv run python main.py ABCRAW.csv ./outputs/ 80

        Run only QC script

            >> pipenv run python main.py ABCRAW.csv ./outputs/ 80 --swan=False --muss=False

        Don't run QC script

            >> pipenv run python main.py ABCRAW.csv ./outputs/ 80 --qc=False

    :param input_file_or_folder: path of the input Actigraph raw csv file if a file, or an mhealth folder if a folder
    :param output_folder: relative or absolute path of an output folder. All algorithm outputs will be placed in a subfolder (with the same name as the input actigraph files (no extension)) of this output folder. So if you have multiple input actigraph files, you can always set this output folder to be the same as the master folder storing outputs for all of the input files.
    :param sampling_rate: sampling rate in Hz.
    :param swan: Run SWaN model
    :param muss: Run MUSS model
    :param qc: Run Quality check script
    :param parallel: if option is presented, muss will use multicore processing
    :param debug: if option is presented, all intermediate files and converted mhealth data files will be preserved otherwise, they will be deleted in the end. If error occurs during running algorithms, intermediate files and converted mhealth data files will always be preserved regardless of this option. Converted mhealth data files will be stored in `.temp` folder in the script root folder, algorithm intermediate files will be stored in the output folder corresponding to each input actigraph csv.
    :param profiling: Use profiling if available.
    """

    if os.path.isfile(input_file_or_folder):
        auto_id = os.path.basename(input_file_or_folder).split('.')[0]
        intermediate_folder = './.temp/'
        mhealth_folder = os.path.join(intermediate_folder, auto_id)
        mhealth.convert_to_mhealth(input_file_or_folder, mhealth_folder)
        output_path = create_output_folder(output_folder, auto_id)
    else:
        intermediate_folder = None
        mhealth_folder = input_file_or_folder
        output_path = output_folder

    sampling_rate = float(sampling_rate)
    if muss:
        print('Running MUSS model...')
        muss_intermediate_folder = os.path.join(output_path, 'muss_intermediate')
        os.makedirs(muss_intermediate_folder, exist_ok=True)
        muss_feature, muss_prediction = muss_model.main(mhealth_folder, sampling_rate=sampling_rate, parallel=parallel, profiling=profiling)
        muss_feature.to_csv(os.path.join(muss_intermediate_folder, 'muss_feature.csv'))
        muss_prediction.to_csv(os.path.join(output_path, 'muss_output.csv'), index=False, header=True)
    if swan:
        print('Running SWaN model...')
        SWaN.main(mhealth_folder, output_path, sampling_rate=sampling_rate)
    if qc:
        print('Running Quality check...')
        qc_result = QC.main(mhealth_folder, output_path)
        qc_result.to_csv(os.path.join(output_path, 'qc_output.csv'), index=False, header=True)

    if not debug:
        if intermediate_folder != None:
            remove_intermediate(intermediate_folder)
        remove_intermediate(os.path.join(output_path, 'intermediate'), os.path.join(output_path, 'qc_intermediate'), os.path.join(output_path, 'muss_intermediate'))

if __name__ == '__main__':
    run(main)
