import squirrel as sq
import qsr as qsr
from datetime import datetime

dt = datetime.now()
dt_month = dt.month if dt.month >= 10 else f'0{dt.month}'
DATE = f'{dt.year}{dt_month}{dt.day}' #%Y%m%d%H%M%S
completed_tickets = {}
pending_tickets = {} # Key: trans_num
last_start = ''

# Every x seconds...

def update_tickets(start: int, end: int) -> bool: # start is 900-1900ish (need to handle 959 -> 1000 kind of situations)
    try:
        check_start = f'{DATE}{start}00' if start >= 1000 else f'{DATE}0{start}00'
        check_end = f'{DATE}{end}00'if end >= 1000 else f'{DATE}0{end}00'

        # Check No, Check Name, Check Qty, Total Qty, BL Sq Qty / PV Sq Qty,  Has___, BL Qty / PV Qty , BL items / PV items #
        all_checks_data = sq.get_check_data(check_start, check_end)
        for sale_time, check_data in all_checks_data.items(): # sale time is the commonality between Squirrel and QSR
            if sale_time not in pending_tickets: # Initialize this ticket
                 pending_tickets[sale_time] = {
                    'Name': check_data[0],
                    'Qty': int(check_data[2]),
                    'Total Qty': int(check_data[3]),
                    'bl_sq_qty': int(check_data[4][0]),
                    'pv_sq_qty': int(check_data[4][1]),
                    'has_start': check_data[5][0],
                    'has_finish': check_data[5][1],
                    'has_pv': check_data[5][2],
                    'bl_qty': int(check_data[6][0]),
                    'pv_qty': int(check_data[6][1]),
                    'HOT START' : '',
                    'HOT FINISH' : '',
                    'PLATESVILLE': '',
                    'ANCHOR' : '',
                    'BL Items' : check_data[7][0],
                    'PV Items' : check_data[7][1],
                }
        qsr.parse(completed_tickets, pending_tickets) # Updates completed and pending tickets
        print('Pending:')
        for p in pending_tickets:
            print(p)
        print('Completed:')
        for c in completed_tickets:
             print(c)
        return True
    except Exception as e:
        with open('main_errors.txt', 'a') as err_file:
                err_file.write(f'{datetime.now()}:\n   + update_tickets(): {e}')
        return False
    
if __name__ == '__main__':
    update_tickets(1000, 1055)