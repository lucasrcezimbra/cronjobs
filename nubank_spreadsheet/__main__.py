import sys
from datetime import datetime

from nubank_spreadsheet import main
from utils.log import logger

if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            initial_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
            main(initial_date)
        else:
            main()
    except Exception as e:
        logger.exception(e)
