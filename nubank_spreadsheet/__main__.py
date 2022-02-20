import sys
from datetime import datetime

from nubank_spreadsheet import main

if __name__ == '__main__':
    if len(sys.argv) > 1:
        initial_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
        main(initial_date)
    else:
        main()
