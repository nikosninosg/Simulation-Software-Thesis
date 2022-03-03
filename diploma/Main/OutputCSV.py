import pandas as pd
import os
import csv

headerList = ['Env_now', 'Machine', 'Description', 'Current_cans', 'Init_level', 'Capacity', 'Status', 'BrakeTF',
              'Brake_duration', 'Cause']


def check_csv():
    filesize = os.path.getsize("output/output.csv")
    # df = pd.read_csv("output/output.csv")

    if filesize != 0:
        print("Υπάρχουν δεδομένα στο csv.  Διαγραφή...")
        filename = "output/output.csv"
        # opening the file with w+ mode truncates the file
        f = open(filename, "w+")
        f.close()

    else:
        print("Δεν υπάρχουν δεδομένα στο csv.")
        with open('output/output.csv', 'w', encoding='UTF8') as file:
            wrt = csv.writer(file)
            wrt.writerow(headerList)
            file.close()


def write_row(row):
    # file = pd.read_csv("output/output.csv")
    df = pd.DataFrame(data=row, index=[None], columns=headerList)

    df.to_csv("output/output.csv", sep=',', mode='a', encoding='utf-8', header=False, index=False)


# check_csv()
'''
row1 = {'Env_now': 13, 'Machine': 'Depall', 'Init_level': 100, 'Capacity': 10000, 'Status': 'GREEN',
        'BrakeTF': True, 'Brake_duration': 13, 'Cause': 'Blocked door'}
write_row(row1)

row2 = {'Env_now': 25, 'Machine': 'Depall', 'Init_level': 100,  'Status': 'GREEN',
        'BrakeTF': True, 'Brake_duration': 200000}
write_row(row2)

row1 = {'Env_now': 13, 'Machine': 'Depall', 'Init_level': 100, 'Capacity': 10000, 'Status': 'GREEN',
        'BrakeTF': True, 'Brake_duration': 13, 'Cause': 'Blocked door'}
write_row({'Env_now': 13, 'Machine': 'Depall', 'Init_level': 100, 'Capacity': 10000, 'Status': 'GREEN',
        'BrakeTF': True, 'Brake_duration': 13, 'Cause': 'Blocked door'})
'''
