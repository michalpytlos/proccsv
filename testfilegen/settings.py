import os
from testfilegen import package_directory


# Number of lines to be generated in the output file
FILE_ROWS = 10000

# Encoding of the output file. Must be set to either utf-8 or utf-16
ENCODING = 'utf-8'

# Date_from and date_to for the random date generator. Required format DD/MM/YYYY
DATE_FROM = '01/01/2018'
DATE_TO = '01/02/2019'

# Path to the output directory 
OUTPUT_DIR_PATH = os.path.join(package_directory, 'output')
