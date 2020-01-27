## About this repository
This repository is a collection of algorithms and scripts useful to prepare data when annotating using Signaligner Pro: https://github.com/crowdgames/signaligner

#### This repo includes
1. Scripts to run multi-sensor physical activity algorithm MUSS
2. Scripts for single sensor Sleep, Wear, and Non-Wear detection algorithm SWaN
3. Scripts to check and detect the quality issues related to raw accelerometer data QC
4. Scripts to convert a raw Actigraph CSV file into mHealth folder format to be used by the algorithms

## System requirements
1. Python 3.6+. To install and set up Python, please visit: https://www.python.org/downloads/release/python-356/. Verify installation,

    ```bash
    >> python --version
    ```

2. Java 8+ Runtime environment. To install and set up Java, please visit: https://www.java.com/en/download/. Verify installation,

    ```bash
    >> java --version
    ```

## Installing dependencies

1. Install package manager `pipenv`.

    ```bash
    >> pip install pipenv
    ```

2. Run `pipenv install` at the root of the repository to install all dependencies.

    ```bash
    >> pipenv install
    ```

## Running algorithms
use the 'main.py' script to run all the algorithms at once. You may run the following command to see the help information with descriptions for all available parameters.

```bash
>> pipenv run python main.py --help
```

Assuming you have an Actigraph csv file called "ABCRAW.csv", with data sampled at 80 Hz. And you want to store all algorithm outputs into a subfolder `outputs` in the current folder.

1. To run all the models

    ```bash
    >> pipenv run python main.py ABCRAW.csv ./outputs/ 80
    ```

2. To run only quality check script

    ```bash
    >> pipenv run python main.py ABCRAW.csv ./outputs/ 80 --swan=False --muss=False
    ```

3. if you don't want to run quality check but everything else

    ```bash
    >> pipenv run python main.py ABCRAW.csv ./outputs/ 80 --qc=False
    ```