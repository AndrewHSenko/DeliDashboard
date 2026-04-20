import squirrel as sq

def parse_entry(raw_data):
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

# PENDING CLEAN: Cleanup completed_tickets once their latest bump is 20 minutes after start_time #
# start_time = '1000'

completed_tickets = {}
pending_tickets = {} # Key: trans_num

# Every x seconds...
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
        if trans_num in pending_tickets:
            pending_tickets[trans_num][station_name] = ''.join(line_data['bumped'])
            if len(pending_tickets[trans_num]) == 4: # Has HOT START, HOT FINISH, PLATESVILLE, ANCHOR
                completed_tickets[trans_num] = pending_tickets[trans_num] # Remove from pending checks
                pending_tickets.pop(trans_num)
        else:
            pending_tickets[trans_num] = {station_name : ''.join(line_data['bumped'])}


sq.get_check_data('1005', '1010')
