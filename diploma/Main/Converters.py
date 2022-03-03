# get_ipython().run_line_magic('matplotlib', 'qt')

def runTimeConv(machine, total_ptime, shift):
    total_proc_time = sum(total_ptime)

    # Total Time
    # p_total_time_m = total_proc_time / 60
    p_total_time_h = total_proc_time / (60 * 60)

    # In a shift
    time_per_shift = total_proc_time / shift  # time per shift
    # print(m_per_day)
    p_in_h = time_per_shift // (60*60)
    p_in_mod_m = (time_per_shift % (60*60))

    # print((total_proc_time * 24) % sim_time)
    # print(machine + ' Process Time in a shift: %d ' % round(p_in_h) + 'hours and %d minutes.' % round(p_in_mod_m))
    # print( machine + ' Total Process Time in %d shifts ' % shift + 'in H: %d hours ' % round(p_total_time_h) + 'and in S: %d seconds' % total_proc_time)
    return str(round(p_in_h)) + 'h ' + str(round(p_in_mod_m)) + 'm'


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