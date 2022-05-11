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


def machine_duration_conv_to_perc(DURATION, SIM_TIME):
    print(type(DURATION))
    if type(DURATION) is dict:
        # if dict is empty
        if not DURATION:
            total_sum = 0
        elif isinstance(DURATION.values(), float):
            total_sum = DURATION.values()
        else:
            total_sum = sum(DURATION.values())

    else:
        # if list is empty
        if not DURATION:
            total_sum = 0
            # if list has one number
        elif isinstance(DURATION, float):
            total_sum = DURATION
        else:
            total_sum = sum(DURATION)

    # print(round(total_sum * 100 / SIM_TIME, 2))
    return round(total_sum*100/SIM_TIME, 2)


# print(machine_duration_conv_to_perc({1: 5000, 2: 5000, 4: 10000, 5: 10000}, 60000))
# print(machine_duration_conv_to_perc([5000.887959562, 5000.6456645654, 10990.099931239, 10000], 60000))


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
