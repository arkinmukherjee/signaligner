# Signaligner

Signaligner, the signal aligner tool, is a web-based utility for annotating multi-day raw accelerometer data for activity recognition.



## Getting Started

### Installation

You will need [Python 3](https://www.python.org/downloads/). If you have Python 2, you can switch to Python 3 with [this guide](https://docs.anaconda.com/anaconda/user-guide/tasks/switch-environment/).

To run properly on large (multi-day) datasets, the 64-bit version of Python3 is required. The 32-bit version can run out of memory. 



### Overview and Usage

Signaligner runs on a local server. You can set up this server by running this command from a terminal in the Signaligner directory:
`python3 scripts/signaserver.py`
Then direct your web browser to: http://localhost:3007/signaligner.html
You should see an example signal loaded into the tool. To load in your own dataset, see Importing Data.



### Useful Files and Folders

As a user, the most important files and folders to know about are:

- `scripts/`: the folder containing scripts to process your data
    - `signaserver.py`: the script you run to boot up the server program
    - `signalauncher.py`: opens a GUI for running script functionality
- `signaligner/`: folder for the main Signaligner web files
    - `signaligner.html`: the main HTML file (the displayed webpage)
    - `signaligner.js`: the main JavaScript code file
- `data/`: folder for data (this may be somewhere else depending on your setup)
    - `datasets/`: the folder containing your Signaligner-formatted signal data
    - `labels/`: the folder containing the Signaligner labels of your data
- `common/`: includes useful templates and example files
- `static/`: folder for static HTML pages and related



## Example workflow

Examples of useful scripts for data processing are given below.

**After running each of the example commands, you can check the dataset, while running the server, at: http://localhost:3007/signaligner.html?dataset=example_sin30min**

**You must import a dataset before importing and exporting labels to for that dataset will work.***



### Importing Datasets

The dataset import script processes your raw accelerometer data into a Signaligner-ready dataset.

For usage information, run `python3 scripts/import_dataset.py --help`.

You will likely want to specify what labels the dataset will need (such as Ambulation/Sedenary or Wear/Non-wear/Sleep).
The `common/` folder has several files that start with `labels_` as example files for this purpose.

If the import was successful, there will be a new dataset in your `datasets/` folder. Each dataset contains a `config.json` file which has the meta-data of your dataset, and a `tiles/` folder which contains all of your data in a format Signaligner can read.

**To test dataset import, you can run `python3 scripts/import_dataset.py common/example_sin30min.csv`.**



### Importing Algorithm Output to Signaligner Labels

If you have the output of a prediction algorithm and you'd like to convert its output into Signaligner labels, use the algorithm label import script.

For usage information, run `python3 scripts/import_labels.py --help`.

**To test algorithm label import, you can run `python3 scripts/import_labels.py example_sin30min common/example_sin30min_algo.csv --source Algo --session ALGO`.**



### Exporting Signaligner Labels to CSV

To convert the Signaligner labels to a CSV, use the CSV export script. They will be written to the `export` folder.

For usage information, run `python3 scripts/export_labels.py --help`.

**To test label csv export, you can run `python3 scripts/export_labels.py example_sin30min`.**



## Signalauncher

### Getting the code

This repository uses `mdcas-python` as a submodule. To clone, use: `git clone --recurse-submodules`.

If cloned without recursing submodules, you can use `git submodule init` then `git submodule update` to get the submodules.

### Installing dependencies

To run the algorithms in `mdcas-python`, install the following Python packages:

`pip3 install numpy` \
`pip3 install pandas` \
`pip3 install scikit-learn` \
`pip3 install padar-converter` \
`pip3 install padar-parallel` \
`pip3 install padar-features` \
`pip3 install clize` \
`pip3 install pyinstaller`

On Linux, also install:

`apt-get install python3-tk`

### Running

Run `python3 scripts/signalauncher.py` to start.



## For Developers

### How to set up with Vagrant

If you would like to develop in a virtual environment, Vagrant can be used. Vagrant is a virtual machine manager that can set up a standard development environment.

Install a [VM provider](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/), if needed.

In a terminal, run `vagrant up` then `vagrant ssh`.

On the guest machine, go to `cd /vagrant`.

Follow the instructions on how to run.
