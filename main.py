import difflib

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

new_lines = []
new_lines_data = []
with open('c:/ProgramData/QSR Automations/ConnectSmart/BackOffice/SpeedofService/SpeedOfService.txt', 'r', encoding="utf-16") as has_more:
    with open('c:/ProgramData/QSR Automations/ConnectSmart/BackOffice/SpeedofService/acSpeedOfService.txt', 'r', encoding="utf-16") as has_less:
        diff_lines = difflib.unified_diff(has_more.readlines(), has_less.readlines())
        for entry in diff_lines:
            new_lines.append(entry)
for line in new_lines:
    if line[0] == '-' and line[1] != '-':
        line_data = parse_entry(line.split(','))
        new_lines_data.append(line_data)
    elif line[0] == '+':
        print('Random entry:', line)