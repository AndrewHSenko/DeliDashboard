from datetime import datetime

def parse_entry(raw_data: list) -> dict:
    category_indexes = {
        'trans_num' : 0,
        'entered' : (9, 10, 11, 13, 14, 15),
        'screen_time' : 22,
        'station_name' : 23,
        'check_num' : 25,
        'check_name' : 26,
        'bumped' : (28, 29, 30, 32, 33, 34),
        'day_of_week' : 31, # 0 - Sunday
        'server_name' : 36,
        'prep_time' : 45,
        'destination' : 46
    }
    sos_data = {}
    for category, index in category_indexes.items():
        if type(index) == tuple: # for dates
            t_time = ''
            for ind in index:
                t = raw_data[ind]
                t_time += '0' + t if len(t) == 1 else t # fixes single-digit entries
            sos_data[category] = t_time # YYYYMMDDhhmmss
        else:
            sos_data[category] = raw_data[index]
    return sos_data

# Handles updating completed and pending dicts by reading through QSR file #
def parse(completed_tickets: dict, pending_tickets: dict) -> bool:
    try:
        with open('c:/ProgramData/QSR Automations/ConnectSmart/BackOffice/SpeedofService/SpeedOfService.txt', 'r', encoding="utf-16") as qsr_file:
            for entry in qsr_file.readlines():
                line_data = parse_entry(entry.split(','))
                trans_num = line_data['trans_num']
                station_name = line_data['station_name']
                if trans_num in completed_tickets:
                    if completed_tickets[trans_num][station_name] == ''.join(line_data['bumped']): # Already seen this entry
                        continue
                    else:
                        completed_tickets[trans_num][station_name] = ''.join(line_data['bumped'])
                elif trans_num in pending_tickets:
                    pending_tickets[trans_num][station_name] = ''.join(line_data['bumped'])
                    if len(pending_tickets[trans_num]) == 4: # Has HOT START, HOT FINISH, PLATESVILLE, ANCHOR
                        completed_tickets[trans_num] = pending_tickets[trans_num] # Remove from pending checks
                        pending_tickets.pop(trans_num)
                else:
                    pending_tickets[trans_num] = {station_name : ''.join(line_data['bumped'])}
        return True
    except Exception as e:
        with open('qsr_errors.txt', 'a') as err_file:
                err_file.write(f'{datetime.now()}:\n   + parse(): {e}')
        return False