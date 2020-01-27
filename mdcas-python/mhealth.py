import os
import subprocess
from clize import run

def convert_to_mhealth(actigraph_file, output_folder):
    if os.path.exists(actigraph_file):
        output_folder = os.path.join(output_folder, 'MasterSynced')
        os.makedirs(output_folder, exist_ok=True)
        subprocess.run(' '.join(['java', '-jar', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mhealthformat-actigraph-converter-latest.jar'), 'MHEALTH_STRUCTURE', actigraph_file, output_folder]), check=True, shell=True)
    else:
        raise FileNotFoundError('Input file {} is not found'.format(actigraph_file))

if __name__ == "__main__":
    run(convert_to_mhealth)