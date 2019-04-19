"""
Wrapper module to run the whole project
"""
import sys
from csv_reader import process_csv
# TODO: at some point add logic to check for correct argument

if __name__ == '__main__':
    process_csv(sys.argv[2])
