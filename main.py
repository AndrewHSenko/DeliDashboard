import squirrel as sq
import qsr as qsr
import sys
from datetime import datetime
import time

dt = datetime.now()
dt_month = dt.month if dt.month >= 10 else f'0{dt.month}'
dt_day = dt.day if dt.day >= 10 else f'0{dt.day}'
DATE = f'{dt.year}{dt_month}{dt_day}' #%Y%m%d%H%M%S
completed_tickets = {}
pending_tickets = {} # Key: trans_num
last_start = ''

# Every x seconds...

def update_tickets(start: str, end: str) -> bool: # start is 900-1900ish (need to handle 959 -> 1000 kind of situations)
    try:
        check_start = f'{DATE}{start}00' # if start >= 1000 else f'{DATE}0{start}00'
        check_end = f'{DATE}{end}00'
        # Check No, Check Name, Check Qty, Total Qty, BL Sq Qty / PV Sq Qty,  Has___, BL Qty / PV Qty , BL items / PV items #
        print(check_start, check_end)
        all_checks_data = sq.get_check_data(check_start, check_end)
        # if check_start >= '20260614105500':
        #     print(all_checks_data)
        for sale_time, check_data in all_checks_data.items(): # sale time is the commonality between Squirrel and QSR
            if sale_time not in pending_tickets: # Initialize this ticket
                 pending_tickets[sale_time] = {
                    'Check No.' : check_data[0],
                    'Name': check_data[1],
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
        qsr.parse(completed_tickets, pending_tickets, start, end) # Updates completed and pending tickets
        return True
    except Exception as e:
        with open('main_errors.txt', 'a') as err_file:
                err_file.write(f'{datetime.now()}:\n   + update_tickets(): {e}\n')
        return False

def catch_up(start : str, end : str) -> bool:
    try:
        start_intvl = start
        while start_intvl <= end:
            if start_intvl[-2:] == '60':
                start_intvl = f'{int(start_intvl[:2]) + 1}00'
            end_intvl = start_intvl + 5 if int(start_intvl[-2:]) != 55 else start_intvl + 45
            update_tickets(str(start_intvl), end_intvl)
            start_intvl += 5
        return True
    except Exception as e:
        with open('main_errors.txt', 'a') as err_file:
                err_file.write(f'{datetime.now()}:\n   + update_tickets(): {e}\n')
        return False
    
if __name__ == '__main__':
    args = sys.argv # script_name, arg1, arg2, ...
    if len(args) > 1: # has args
        catch_up(args[1], args[2])
    with open('main_log.txt', 'a') as log_file:
        end = time.strftime('%H%M')
        start = f'{int(end[:2]) - 1}55' if end[-2:] == '00' else f'{end[:2]}{int(end[2:]) - 5}'
        update_tickets(start, end)
        log_file.write('Pending:\n')
        for sale_time, ticket_data in pending_tickets.items():
            log_file.write(f'{ticket_data['Name']} ({sale_time}): {ticket_data['HOT START']} | {ticket_data['HOT FINISH']} | {ticket_data['PLATESVILLE']} | {ticket_data['ANCHOR']}\n')
