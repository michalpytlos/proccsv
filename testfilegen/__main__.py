import pycountry
from random import randint
import time
import os
from testfilegen import settings


def test_file_gen(num, date_from, date_to, encoding, out_dir_path):
    """"Generate test file for proccsv

    Args:
        num (int): number of rows in test file
        date_from (str): date from (DD/MM/YYYY) for random date generator
        date_to (str): date to (DD/MM/YYYY) for random date generator
        encoding (str): test file's encoding
        out_dir_path (str): path to output directory
    """
    # Validate requested encoding
    if encoding not in ['utf-8', 'utf-16']:
        print('Invalid encoding!')
        return

    # Create descriptive file name
    file_name = 'test_{}_{}.csv'.format(num, encoding[4:])
    file_path = os.path.join(out_dir_path, file_name)

    # Get list of all state names in pycountry
    states = [subdiv.name for subdiv in pycountry.subdivisions]
    num_states = len(states)

    # Create test file
    with open(file_path, 'w', encoding=encoding) as f:
        for i in range(num):
            state = states[randint(0, num_states - 1)]
            clicks = randint(0, 2000)
            ctr = randint(0, 200) / 100  # percentage
            date = random_date(date_from, date_to)
            line = '{},{},{},{}%\n'.format(date, state, clicks, ctr)
            f.write(line)
    print('Test csv file created!')


def random_date(date_from='01/01/1970', date_to='01/01/2019'):
    """Generate random date between date_from and date_to"""
    try:
        time_from = time.mktime(time.strptime(date_from, '%d/%m/%Y'))
        time_to = time.mktime(time.strptime(date_to, '%d/%m/%Y'))
        assert time_from <= time_to
    except (ValueError, AssertionError) as e:
        print(e)
        return None
    timestamp = randint(time_from, time_to)
    return time.strftime('%m/%d/%Y', time.localtime(timestamp))


if __name__ == '__main__':
    test_file_gen(num=settings.FILE_ROWS,
                  date_from=settings.DATE_FROM,
                  date_to=settings.DATE_TO,
                  encoding=settings.ENCODING,
                  out_dir_path=settings.OUTPUT_DIR_PATH)
