import datetime as dt
import matplotlib.pyplot as plt

def get_datetime_from_line(line):
    l_field = line.split()
    nasa_id = l_field[2] # Get nasa id
    date = l_field[3].split(":")    # Get date
    time = l_field[4].split(":")    # Get time
    t = dt.datetime(int(date[0]), int(date[1]), int(date[2]),
                    int(time[0]), int(time[1]), int(time[2]))
    return nasa_id, t

cfile = "./Catalite/camera/ISS039/ISS039camera.txt"
f = open(cfile)

group = {}

id_last, t_last = get_datetime_from_line(f.readline())
print t_last
group_id = id_last

for l in f.readlines():
    id_curr, t_curr = get_datetime_from_line(l)
    time_diff = t_curr - t_last
    if time_diff < dt.timedelta(0,2):
        if group_id not in group.keys():
            group[group_id] = [group_id, id_curr]
        else:
            group[group_id].append(id_curr)
    else:
        group_id = id_curr
    id_last = id_curr
    t_last = t_curr

groups = group.keys()
print len(groups)
for g in groups:
    if len(group[g]) < 1:
        print g
