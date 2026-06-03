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

# Removes part (ex 1/2 or 2/2) from check name
def reformat_name(name): 
    new_name = ''
    if not name.split()[-1].isalpha():
        new_name = ' '.join(name.split()[:-1])
    else: # Handles if FoH enters Josh1/2 instead of Josh 1/2
        new_name = ' '.join(name.split()[:-1]) + ' '
        for c in name.split()[-1]:
            if c.isalpha():
                new_name += c
    return new_name

def find_entry(qsr_data, saletime, check_name):
    for d in qsr_data.values():
        new_saletime = '' # For QSR entry
        new_hour = int(d['entered'][-6:-4])
        new_min = int(d['entered'][-4:-2])
        new_sec = int(d['entered'][-2:]) - 1
        if new_sec < 0:
            new_sec = 59
            new_min -= 1
            if new_min < 0:
                new_min = 59
                new_hour -= 1
        # Converts single digit times to double digit if needed
        if len(str(new_hour)) == 1:
            new_hour = '0' + str(new_hour)
        if len(str(new_min)) == 1:
            new_min = '0' + str(new_min)
        if len(str(new_sec)) == 1:
            new_sec = '0' + str(new_sec)
        new_saletime = saletime[:8] + str(new_hour) + str(new_min) + str(new_sec)
        new_sq_name = reformat_name(check_name)
        new_qsr_name = reformat_name(d['check_name'])
        if saletime == new_saletime and new_sq_name == new_qsr_name:
            return saletime[:8] + d['entered'][-6:]

# Handles updating completed and pending dicts by reading through QSR file #
def parse(completed_tickets: dict, pending_tickets: dict) -> bool:
    # try:
        with open('c:/ProgramData/QSR Automations/ConnectSmart/BackOffice/SpeedofService/SpeedOfService.txt', 'r', encoding="utf-16") as qsr_file:
            for entry in qsr_file.readlines():
                line_data = parse_entry(entry.split(','))
                sale_time = ''.join(line_data['entered'])
                station_name = line_data['station_name']
                if sale_time in completed_tickets:
                    if completed_tickets[sale_time][station_name] == ''.join(line_data['bumped']): # Already seen this entry
                        continue
                    else: # Rebumped
                        completed_tickets[sale_time][station_name] = ''.join(line_data['bumped'])
                elif sale_time in pending_tickets:
                    pending_tickets[sale_time][station_name] = ''.join(line_data['bumped'])
                    if len(pending_tickets[sale_time]) == 4: # Has HOT START, HOT FINISH, PLATESVILLE, ANCHOR
                        completed_tickets[sale_time] = pending_tickets[sale_time] # Remove from pending checks
                        pending_tickets.pop(sale_time)
                else: # Cannot find sale time in Squirrel-entered tickets
                    new_time = find_entry(pending_tickets, sale_time, line_data['check_name'])
                    if new_time in pending_tickets:
                        pending_tickets[sale_time][station_name] = ''.join(line_data['bumped'])
                        if len(pending_tickets[sale_time]) == 4: # Has HOT START, HOT FINISH, PLATESVILLE, ANCHOR
                            completed_tickets[sale_time] = pending_tickets[sale_time] # Remove from pending checks
                            pending_tickets.pop(sale_time)
                    else:
                        pending_tickets[sale_time] = {station_name : ''.join(line_data['bumped'])}
        return True
    # except Exception as e:
    #     with open('qsr_errors.txt', 'a') as err_file:
    #             err_file.write(f'{datetime.now()}:\n   + parse(): {e}\n')
    #     return False
    
    