# -*- coding: utf-8 -*-
######################################################################
# Copyright 2020 Yusen Su. All Rights Reserved.
# Email address: y256su@uwaterloo.ca
######################################################################
import sys, os
import re
import csv
import argparse
import subprocess

# parser = argparse.ArgumentParser()
# parser.add_argument('-csv', type=str, help='give an output csv name', required=True)
# args = parser.parse_args()

benchdir = '../'
benchdirabspath = os.path.abspath(benchdir)
table_file = 'aws-cbmc.csv'
pattern = re.compile(".*log$")
attrs = ['bench name', 'total timing (seconds)', 'iterations', 'total decision procedure timing (seconds)', 'result (success/fail)']
benchsubdirs = []

def convert_time_to_seconds(str_time):
    m, s = str_time.split("m")
    _, m = m.split("r")
    s = s[:-1]
    m,s = int(m), float(s)
    result = m * 60 + s
    return result

def manipulate_input_data(data):
    res_data = []
    for x in data:
        if x == '\n':
            continue
        else:
            res_data.append(x)
    return res_data

def read_output_from_file(benchsubdir, file_name):
    try:
        file = open(file_name, 'r')
    except:
        sys.exit("log file does not exits. Exit!")
    data = file.readlines()
    res_data = []
    for i in range(len(attrs)):
        res_data.append('')
    res_data[3] = 0.0
    plain_data = manipulate_input_data(data)
    plain_data = [d.replace("\t", "").replace("\n", "") for d in plain_data]
    # 1. Add benchname
    res_data[0] = benchsubdir
    # 2. Add total timing
    total_timing = round(convert_time_to_seconds(plain_data[-2]), 3)
    format_total_timing = "{:0.3f}".format(total_timing)
    res_data[1] = format_total_timing
    success_regexp = re.compile(r'SUCCESSFUL')
    failed_regexp = re.compile(r'FAILED')
    decision_regexp = re.compile(r'Runtime')
    iterations_regexp = re.compile(r'iterations')
    for plain_d in plain_data:
        if success_regexp.search(plain_d):
            res_data[4] = "success"
        if failed_regexp.search(plain_d):
            res_data[4] = "fail"
        if iterations_regexp.search(plain_d):
            # 3. Add iterations
            _, rawd = plain_data[-5].split('(')
            iters, _ = rawd.split(' ')
            res_data[2] = iters
        if decision_regexp.search(plain_d):
            # 4. Add the decision procedure times (iterations)
            _, raw_procedure_time = plain_d.replace(" ", "").split(":")
            res_data[3] += float(raw_procedure_time[:-1])
    if res_data[4] == '':
         res_data[4] = "undefined"
    if res_data[3] != '':
        procedure_timing = "{:0.3f}".format(round(float(res_data[3]), 3))
        res_data[3] = procedure_timing
    if res_data[3] != '' and float(res_data[1]) < float(res_data[3]):
        # print(res_data[1], res_data[3])
        print(f'Bench {benchsubdir} recording error! Please check log file on that folder.')
    file.close()
    return res_data

def get_all_res_from_log_file(table_lst):
    idx_output = 0
    for benchsubdir in benchsubdirs:
        log_path = "../"+benchsubdir+"/log"
        res_data = read_output_from_file(benchsubdir, log_path)
        table_lst.append(res_data)
    # for root, dirs, files in os.walk(benchdir+'/'+subdir):
    #     dict[subdir] = [(os.path.join(root, file), file, root) for file in files if pattern.match(file)]
    # for file_path in dict[subdir]:
    #     _, dir = file_path[2].split('../outputs/DRIFT2/')
    #     if dir == "negative":
    #         res_data = read_false_info_from_file(file_path[0])
    #         res_data.append("Neg")
    #     else:
    #         res_data = read_info_from_file(file_path[0])
    #         res_data.append("Pos")
    #     test_case = file_path[1][4:-3]
    #     res_data.append(test_case)
    #     res_data.append(subdir)
    #     res_data.reverse()
    #     dict[subdir][dict[subdir].index(file_path)] = res_data

def search_get_all_subdirse():
    global benchsubdirs
    benchsubdirs = sorted(next(os.walk(benchdir))[1])[:-1]
    # benchsubdirs = benchsubdirs[:1]
    # print(os.getcwd())

def run_benchs_cbmc():
    command_lst = ["rm -rf gotos", "(time make result) &> log"]
    print("Start making results ...")
    for benchsubdir in benchsubdirs:
        benchsubdirabspath = benchdirabspath + '/' + benchsubdir
        cddir = "cd ../"+benchsubdir
        for strcmd in command_lst:
            cddir += " ; " + strcmd
        print(cddir)
        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        _ = process.communicate(cddir.encode())
    print("Benchmark end-of-run. Start gathering info...")

def write_info_into_csv(table_lst):
    print(f'Writing data into {table_file} at current directory...')
    try:
        file = open(table_file, 'w')
    except:
        sys.exit("output table file does not exits. Exit!")
    strs = ','.join(attrs)
    file.write(strs+'\n')
    file.close()
    with open(table_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for out_data in table_lst:
            writer.writerow(out_data)

def main():
    table_list = []
    search_get_all_subdirse()
    run_benchs_cbmc()
    get_all_res_from_log_file(table_list)
    write_info_into_csv(table_list)

if __name__ == '__main__':
	main()
