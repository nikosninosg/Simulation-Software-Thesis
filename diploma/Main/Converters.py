# get_ipython().run_line_magic('matplotlib', 'qt')

def duration_converter(total_ptime):
    if type(total_ptime) is dict:
        total_proc_time = sum(total_ptime.values())
    elif type(total_ptime) is list:
        total_proc_time = sum(total_ptime)
    else:
        total_proc_time = total_ptime

    days = int(total_proc_time / 86400)
    hours = int((total_proc_time - (days * 86400)) // 3600)
    minutes = int(total_proc_time % 3600 / 60)
    seconds = int((total_proc_time % 3600) % 60)
    return '{:02d}d {:02d}h {:02d}m {:02d}s'.format(days, hours, minutes, seconds)
    # return '{:02d}:{:02d}:{:02d}:{:02d}'.format(days, hours, minutes, seconds)


def double_time_print(stop_times):
    if stop_times <= 9:
        return '0' + str(stop_times)
    else:
        return str(stop_times)


'''
TOTAL_PTIME = [10000, 18000]
SHIFTS = 1
depall_env_time = [10000, 18000]
processTimeConv("Depall", TOTAL_PTIME, SHIFTS)
# ((sum(depall_total_ptime) * 24) % SIM_TIME)*60)

plt.figure()
plt.step(depall_env_time, TOTAL_PTIME, where='post')
plt.xlabel('Time (minutes)')
plt.ylabel('Depall Process Time')
# get_ipython().run_line_magic('matplotlib', 'qt')
plt.show()
'''