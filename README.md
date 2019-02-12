# proccsv
proccsv is a tool for processing csv ad reports

Input: UTF-8 or UTF-16 file with the following comma separated columns:
+ date (MM/DD/YYYY)
+ state name (only names of subdivisions from pycountry are recognized)
+ number of impressions
+ CTR percentage (number followed by %)

Output: UTF-8 CSV file with the following columns:
+ date (YYYY-MM-DD)
+ three-letter country code (XXX for unknown)
+ number of impressions
+ number of clicks

Rows in the output file are aggregated by date and country.

## Prerequisites
* Python 3.7 (available from [python.org](https://www.python.org/downloads/))
* pycountry package. Install using the provided requirements.txt file: `pip install -r requirements.txt`

## Usage
To run the program from the Python interpreter
1. Copy the files to be processed to the input directory
2. Navigate to the directory containing the **proccsv** package
3. Run `python -m proccsv` (for virtualenv with python3.7)
4. Follow the on-screen instructions to select the file for processing from the input directory
5. proccsv will save the output file in the output directory under the input filename with a suffix.

The location of the input and output directories as well as the suffix can be modified by editing **settings.py** located inside the package directory. The default settings are as follows:
```
INPUT_DIR_PATH = os.path.join(package_directory, 'input')
OUTPUT_DIR_PATH = os.path.join(package_directory, 'output')
OUTPUT_FILE_NAME_SUFFIX = '_out'
```

## How it works
1. Create in-memory sqlite database
2. Create mapping between state name and three-letter country codes in form of a dictionary
3. Validate and process each field of the first line from the input file to the required format
4. If the operation in step 3 is successful for all four fields, insert the processed data into a table in the in-memory database. Otherwise print the appropriate error message to stderr.
5. Repeat Steps 3-4 for all the remaining lines of the input file
6. Using SQL, aggregate and sort the data in the in-memory database
7. Save the aggregated data to the output file and destroy the in-memory database

## testfilegen
testfilegen is a program for generation of test files for proccsv. It has the same prerequisites as proccsv. Program settings are specified in **settings.py** located inside the testfilegen package directory.

To run testfilegen from the Python interpreter:
1. Navigate to the directory containing the **testfilegen** package
2. Run `python -m testfilegen` (for virtualenv with python3.7)
