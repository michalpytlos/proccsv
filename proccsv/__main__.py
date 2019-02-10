import sys
import time
import os
import sqlite3
from collections import namedtuple
import pycountry
from proccsv import settings


# Container for processed report data items i.e. date, country code,
# number of impressions and number of clicks
Item = namedtuple('Item', ['val', 'msg'])


def get_date(raw_date):
    """Format date

    Args:
        raw_date (str): date in format MM/DD/YYYY

    Returns:
        namedtuple with the following fields:
            val (str): date in format YYYYY-MM-DD or None if input was invalid
            msg (str): information on input
    """
    try:
        structured_time = time.strptime(raw_date, '%m/%d/%Y')
        date = time.strftime('%Y-%m-%d', structured_time)
        msg = 'OK'
    except ValueError:
        date = None
        msg = 'invalid date format'
    return Item(date, msg)


def get_country(state, state_country):
    """Get three-letter code of the parent country of a given subdivision

    Args:
        state (str): name of the subdivision
        state_country (dict): subdivision to country code mapping

    Returns:
        namedtuple with the following fields:
            val (str): three-letter country code
            msg (str): information on input
    """
    country_code = state_country.get(state, 'XXX')
    msg = 'OK'
    return Item(country_code, msg)


def get_impressions(raw_impress):
    """Verify format of the input number of impressions

    Args:
        raw_impress(str): number of impressions

    Returns:
        namedtuple with the following fields:
            val (int): number of impressions or None if input was invalid
            msg (str): information on input
    """
    try:
        impress_count = int(raw_impress)
        assert impress_count >= 0
        msg = 'OK'
    except ValueError:
        impress_count = None
        msg = 'value of number of impressions is not an integer'
    except AssertionError:
        impress_count = None
        msg = 'value of number of impressions is negative'
    return Item(impress_count, msg)


def get_clicks(raw_impress, raw_ctr):
    """Calculate number of ad clicks

    Args:
        raw_impress (str): number of impressions
        raw_ctr (str): click to impression rate given as percentage

    Returns:
        namedtuple with the following fields:
            val (int): number of ad clicks or None if input was invalid
            msg (str): information on input
    """
    try:
        impress_count = int(raw_impress)
        ctr = float(raw_ctr[:raw_ctr.rindex('%')]) / 100
        assert 1 >= ctr >= 0
        click_count = round(ctr * impress_count)
        msg = 'OK'
    except ValueError:
        click_count = None
        msg = 'unable to compute number of clicks due to invalid format of ctr and/or number of impressions'
    except AssertionError:
        click_count = None
        msg = 'ctr percentage is outside [0, 100] interval'
    return Item(click_count, msg)


def create_db():
    """Create in-memory SQLite database

    Returns:
        sqlite3 cursor and connection
    """
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE metrics
             (date text, country text, impressions integer, clicks integer)''')
    conn.commit()
    return c, conn


def map_state_country():
    """Map pycountry subdivisions to country codes

    Returns:
        dictionary where key=subdivision name and
            value=three-letter country code
    """
    state_country = {}
    for state in pycountry.subdivisions:
        alpha_2 = state.country_code
        state_country[state.name] = pycountry.countries.get(alpha_2=alpha_2).alpha_3
    return state_country


def read_data(file_path, cur, encoding='utf-8'):
    """Read report data from input file and save to temp database after formatting

    Args:
        file_path (str): path to input csv file
        cur (Object): sqlite3 cursor
        encoding (str): encoding of input file
    """
    with open(file_path, 'r', encoding=encoding) as f:
        # Create subdivision to country code mapping for get_country()
        state_country = map_state_country()

        error_count = 0  # Invalid line counter

        # Read and process each row of input file
        for counter, line in enumerate(f, 1):
            raw_entry = line.split(',')
            try:
                # Process row data
                entry = {
                    'date': get_date(raw_entry[0]),
                    'country': get_country(raw_entry[1], state_country),
                    'impressions': get_impressions(raw_entry[2]),
                    'clicks': get_clicks(raw_entry[2], raw_entry[3])
                }
            except IndexError:
                print('Error in line {}: missing column'.format(counter),
                      file=sys.stderr)
                error_count += 1
                continue

            # Validate row data; if valid save to database
            if None in ([item.val for item in entry.values()]):
                # Row data is invalid: print error message to stderr
                err_msg = ' & '.join([item.msg for item in entry.values() if not item.val])
                print('Error in line {}: {}'.format(counter, err_msg),
                      file=sys.stderr)
                error_count += 1
            else:
                # Row data is valid: insert entry into metrics table
                cur.execute('INSERT INTO metrics VALUES (?, ?, ?, ?)',
                            (entry['date'].val, entry['country'].val,
                             entry['impressions'].val, entry['clicks'].val))
    return 'Total number of invalid lines in the input file: {}'.format(error_count)


def process_data(cur):
    """Aggregate report data held in database by date and country

    Args:
         cur (Object): sqlite3 cursor

    Returns:
          list with aggregated and sorted report entries
    """
    output = cur.execute('''SELECT  date, country, SUM(impressions), SUM(clicks)
                            FROM metrics
                            GROUP BY date, country
                            ORDER BY date, country''').fetchall()
    return output


def write_data(data, file_path):
    """Write processed report data to output file

    Args:
        data (list): list with aggregated and sorted report entries
        file_path (str): path to output file

    """
    with open(file_path, 'w', encoding='utf-8') as f:
        for entry in data:
            line = '{},{},{},{}\n'.format(*entry)
            f.write(line)


def get_file_paths():
    """Returns paths to input and output files"""
    # Gather information on files in input directory
    files = os.listdir(settings.INPUT_DIR_PATH)
    file_nums = [str(i) for i in range(len(files))]

    # Ask user to select file for processing
    print('List of files in the input directory:')
    for num, file_name in enumerate(files):
        print('[{}] {}'. format(num, file_name))
    while True:
        user_input = input('Select csv file to be processed by specifying its number or press q to exit: ')
        if user_input in file_nums:
            file_no = int(user_input)
            break
        elif user_input == 'q':
            sys.exit()

    # Construct path to input file
    in_filename = os.listdir(settings.INPUT_DIR_PATH)[file_no]
    input_path = os.path.join(settings.INPUT_DIR_PATH, in_filename)

    # Construct path to output file
    ext_pos = in_filename.rfind('.')
    if ext_pos == -1:
        out_filename = in_filename + settings.OUTPUT_FILE_NAME_SUFFIX
    else:
        out_filename = in_filename[:ext_pos] + \
                       settings.OUTPUT_FILE_NAME_SUFFIX + in_filename[ext_pos:]
    output_path = os.path.join(settings.OUTPUT_DIR_PATH, out_filename)
    return input_path, output_path


def main():
    """Process csv file with report data on ad campaign"""
    # Generate paths to input and output files
    input_path, output_path = get_file_paths()

    # Create in-memory database
    cur, conn = create_db()

    # Read report data from input file and save to temp database after formatting
    try:
        error_msg = read_data(input_path, cur, 'utf-8')
    except UnicodeError:
        try:
            error_msg = read_data(input_path, cur, 'utf-16')
        except UnicodeError:
            print('Invalid encoding of the input file. Valid encodings: utf-8 and utf-16')
            conn.close()
            sys.exit()

    # Aggregate report data by data and country
    data = process_data(cur)

    # Write processed report data to output file
    write_data(data, output_path)

    # Close database connection and delete database
    conn.close()
    print(error_msg)
    print('File processed!')


if __name__ == '__main__':
    main()
