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
    if not name.isnumeric():
        new_name = ''
        if not name.split()[-1].isalpha():
            new_name = ' '.join(name.split()[:-1])
        else: # Handles if FoH enters Josh1/2 instead of Josh 1/2
            new_name = ' '.join(name.split()[:-1]) + ' '
            for c in name.split()[-1]:
                if c.isalpha():
                    new_name += c
        return new_name
    return name

def find_entry(pending_sq_data, saletime, check_name):
    try:
        for st, d in pending_sq_data.items():
            new_saletime = '' # For QSR entry (Squirrel_saletime = QSR_saletime - 1 sometimes)
            new_hour = int(st[-6:-4])
            new_min = int(st[-4:-2])
            new_sec = int(st[-2:]) + 1
            if new_sec > 59:
                new_sec = 0
                new_min += 1
                if new_min > 59:
                    new_min = 0
                    new_hour += 1
            # Converts single digit times to double digit if needed
            if len(str(new_hour)) == 1:
                new_hour = '0' + str(new_hour)
            if len(str(new_min)) == 1:
                new_min = '0' + str(new_min)
            if len(str(new_sec)) == 1:
                new_sec = '0' + str(new_sec)
            new_saletime = saletime[:8] + str(new_hour) + str(new_min) + str(new_sec)
            new_sq_name = reformat_name(check_name)
            new_qsr_name = reformat_name(d['Name'])
            if saletime == new_saletime and new_sq_name == new_qsr_name:
                return saletime[:8] + st[-6:]
    except Exception as e:
        with open('bad.txt', 'a') as tf:
            tf.write(f'{check_name}: {e}\n')

def ticket_completed(ticket):
    if ticket['HOT START'] and ticket['HOT FINISH'] and ticket['PLATESVILLE'] and ticket['ANCHOR']:
        return True
    elif 'STAFF' in ticket['Name'].upper():
        if ticket['ANCHOR']:
            return True
    return False

# Handles updating completed and pending dicts by reading through QSR file #
def parse(completed_tickets: dict, pending_tickets: dict, start: int, end: int) -> bool:
    # try:
        with open('c:/ProgramData/QSR Automations/ConnectSmart/BackOffice/SpeedofService/SpeedOfService.txt', 'r', encoding="utf-16") as qsr_file:
            for entry in qsr_file.readlines():
                line_data = parse_entry(entry.split(','))
                sale_time = ''.join(line_data['entered'])
                station_name = line_data['station_name']
                if int(sale_time[-6:-2]) < start or station_name in ('COFFEE', 'COLD') or int(sale_time[-6:-2]) >= end: # Ignores irrelevant QSR entries stations
                    continue
                if sale_time in completed_tickets:
                    if completed_tickets[sale_time][station_name] == ''.join(line_data['bumped']): # Already seen this entry
                        continue
                    else: # Rebumped
                        completed_tickets[sale_time][station_name] = ''.join(line_data['bumped'])
                elif sale_time in pending_tickets:
                    pending_tickets[sale_time][station_name] = ''.join(line_data['bumped'])
                    if ticket_completed(pending_tickets[sale_time]): # Has HOT START, HOT FINISH, PLATESVILLE, ANCHOR
                        completed_tickets[sale_time] = pending_tickets[sale_time] # Remove from pending checks
                        pending_tickets.pop(sale_time)
                else: # Cannot find sale time in Squirrel-entered tickets
                    if pending_tickets:
                        new_time = find_entry(pending_tickets, sale_time, line_data['check_name'])
                        if new_time in pending_tickets:
                            pending_tickets[new_time][station_name] = ''.join(line_data['bumped'])
                            if ticket_completed(pending_tickets[new_time]): # Has HOT START, HOT FINISH, PLATESVILLE, ANCHOR
                                completed_tickets[new_time] = pending_tickets[new_time] # Remove from pending checks
                                pending_tickets.pop(new_time)
                        else:
                            with open('mystery_bumps', 'a') as mb:
                                mb.write(f'{sale_time} ({line_data['check_name']}) | {station_name}: {line_data['bumped']}\n')
        return True
    # except Exception as e:
    #     with open('qsr_errors.txt', 'a') as err_file:
    #             err_file.write(f'{datetime.now()}:\n   + parse(): {e}\n')
    #     return False
    
    