import squirrel as sq
import qsr as qsr
from datetime import datetime, timezone, timedelta
import time
import re

DATE = datetime.now()
completed_tickets = {}
pending_tickets = {} # Key: trans_num
last_start = ''

# Every x seconds...

def update_tickets(start: str, end: str) -> bool:
    try:
        qsr.parse(completed_tickets, pending_tickets)
        


        check_start = f'{DATE}{start_time}00' if start_time >= 1000 else f'{DATE}0{start_time}00'
        check_end = f'{DATE}{end_time}00'if end_time >= 1000 else f'{DATE}0{end_time}00'

        sq.get_check_data(start, end)
        return True
    except Exception as e:
        with open('main_errors.txt', 'a') as err_file:
                err_file.write(f'{datetime.now()}:\n   + update_tickets(): {e}')
        return False

