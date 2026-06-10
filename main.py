import squirrel as sq
import qsr as qsr
from datetime import datetime

dt = datetime.now()
dt_month = dt.month if dt.month >= 10 else f'0{dt.month}'
dt_day = dt.day if dt.day >= 10 else f'0{dt.day}'
DATE = f'{dt.year}{dt_month}{dt_day}' #%Y%m%d%H%M%S
completed_tickets = {}
pending_tickets = {} # Key: trans_num
last_start = ''

# Every x seconds...

def update_tickets(start: int, end: int) -> bool: # start is 900-1900ish (need to handle 959 -> 1000 kind of situations)
    # try:
        check_start = f'{DATE}{start}00' if start >= 1000 else f'{DATE}0{start}00'
        check_end = f'{DATE}{end}00'if end >= 1000 else f'{DATE}0{end}00'
        # Check No, Check Name, Check Qty, Total Qty, BL Sq Qty / PV Sq Qty,  Has___, BL Qty / PV Qty , BL items / PV items #
        all_checks_data = sq.get_check_data(check_start, check_end)
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
        qsr.parse(completed_tickets, pending_tickets, start) # Updates completed and pending tickets
        return True
    # except Exception as e:
    #     with open('main_errors.txt', 'a') as err_file:
    #             err_file.write(f'{datetime.now()}:\n   + update_tickets(): {e}\n')
    #     return False
    
if __name__ == '__main__':
    with open('main_log.txt', 'a') as log_file:
        for i in range(1000, 1050, 5):
            update_tickets(i, i + 5)
            log_file.write('Pending:\n')
            for sale_time, ticket_data in pending_tickets.items():
                log_file.write(f'{ticket_data['Name']} ({sale_time}): {ticket_data['HOT START']} | {ticket_data['HOT FINISH']} | {ticket_data['PLATESVILLE']} | {ticket_data['ANCHOR']}\n')
            log_file.write('Completed:\n')
            for sale_time, ticket_data in completed_tickets.items():
                log_file.write(f'{ticket_data['Name']} ({sale_time}): {ticket_data['HOT START']} | {ticket_data['HOT FINISH']} | {ticket_data['PLATESVILLE']} | {ticket_data['ANCHOR']}\n')
        # update_tickets(1055, 1100)
        # update_tickets(1100, 1155)