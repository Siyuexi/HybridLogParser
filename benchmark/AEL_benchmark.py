#!/usr/bin/env python

import sys
sys.path.append('')
from logparser import AEL, evaluator
import os
import pandas as pd

import warnings
warnings.filterwarnings("ignore")


input_dir = 'logs/' # The input directory of log file
output_dir = 'results/AEL_result/' # The output directory of parsing results

benchmark_settings = {
    'HDFS': {
        'log_file': 'HDFS/HDFS_2k.log',
        'log_format': '<Date> <Time> <Pid> <Level> <Component>: <Content>',
        'regex': [r'blk_-?\d+', r'(\d+\.){3}\d+(:\d+)?'],
        'minEventCount': 2,
        'merge_percent' : 0.5
        },

    'Hadoop': {
        'log_file': 'Hadoop/Hadoop_2k.log',
        'log_format': '<Date> <Time> <Level> \[<Process>\] <Component>: <Content>', 
        'regex': [r'(\d+\.){3}\d+'],
        'minEventCount': 2,
        'merge_percent' : 0.4
        },

    'Spark': {
        'log_file': 'Spark/Spark_2k.log',
        'log_format': '<Date> <Time> <Level> <Component>: <Content>', 
        'regex': [r'(\d+\.){3}\d+', r'\b[KGTM]?B\b', r'([\w-]+\.){2,}[\w-]+'],
        'minEventCount': 2,
        'merge_percent' : 0.4
        },

    'Zookeeper': {
        'log_file': 'Zookeeper/Zookeeper_2k.log',
        'log_format': '<Date> <Time> - <Level>  \[<Node>:<Component>@<Id>\] - <Content>',
        'regex': [r'(/|)(\d+\.){3}\d+(:\d+)?'],
        'minEventCount': 2,
        'merge_percent' : 0.4
        },

    'BGL': {
        'log_file': 'BGL/BGL_2k.log',
        'log_format': '<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>',
        'regex': [r'core\.\d+'],
        'minEventCount': 2,
        'merge_percent' : 0.5
        },

    'HPC': {
        'log_file': 'HPC/HPC_2k.log',
        'log_format': '<LogId> <Node> <Component> <State> <Time> <Flag> <Content>',
        'regex': [r'=\d+'],
        'minEventCount': 5,
        'merge_percent' : 0.4
        },

    'Thunderbird': {
        'log_file': 'Thunderbird/Thunderbird_2k.log',
        'log_format': '<Label> <Timestamp> <Date> <User> <Month> <Day> <Time> <Location> <Component>(\[<PID>\])?: <Content>',
        'regex': [r'(\d+\.){3}\d+'],
        'minEventCount': 2,
        'merge_percent' : 0.4
        },

    'Windows': {
        'log_file': 'Windows/Windows_2k.log',
        'log_format': '<Date> <Time>, <Level>                  <Component>    <Content>',
        'regex': [r'0x.*?\s'],
        'minEventCount': 2,
        'merge_percent' : 0.4
        },

    'Linux': {
        'log_file': 'Linux/Linux_2k.log',
        'log_format': '<Month> <Date> <Time> <Level> <Component>(\[<PID>\])?: <Content>',
        'regex': [r'(\d+\.){3}\d+', r'\d{2}:\d{2}:\d{2}'],
        'minEventCount': 2,
        'merge_percent' : 0.6
        },

    'Andriod': {
        'log_file': 'Andriod/Andriod_2k.log',
        'log_format': '<Date> <Time>  <Pid>  <Tid> <Level> <Component>: <Content>',
        'regex': [r'(/[\w-]+)+', r'([\w-]+\.){2,}[\w-]+', r'\b(\-?\+?\d+)\b|\b0[Xx][a-fA-F\d]+\b|\b[a-fA-F\d]{4,}\b'],
        'minEventCount': 2,
        'merge_percent' : 0.6
        },

    'HealthApp': {
        'log_file': 'HealthApp/HealthApp_2k.log',
        'log_format': '<Time>\|<Component>\|<Pid>\|<Content>',
        'regex': [],
        'minEventCount': 2,
        'merge_percent' : 0.6
        },

    'Apache': {
        'log_file': 'Apache/Apache_2k.log',
        'log_format': '\[<Time>\] \[<Level>\] <Content>',
        'regex': [r'(\d+\.){3}\d+'],
        'minEventCount': 2,
        'merge_percent' : 0.4
        },

    'Proxifier': {
        'log_file': 'Proxifier/Proxifier_2k.log',
        'log_format': '\[<Time>\] <Program> - <Content>',
        'regex': [r'<\d+\s?sec', r'([\w-]+\.)+[\w-]+(:\d+)?', r'\d{2}:\d{2}(:\d{2})*', r'[KGTM]B'],
        'minEventCount': 2,
        'merge_percent' : 0.4
        },

    'OpenSSH': {
        'log_file': 'OpenSSH/OpenSSH_2k.log',
        'log_format': '<Date> <Day> <Time> <Component> sshd\[<Pid>\]: <Content>',
        'regex': [r'(\d+\.){3}\d+', r'([\w-]+\.){2,}[\w-]+'],
        'minEventCount': 10,
        'merge_percent' : 0.7
        },

    'OpenStack': {
        'log_file': 'OpenStack/OpenStack_2k.log',
        'log_format': '<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>',
        'regex': [r'((\d+\.){3}\d+,?)+', r'/.+?\s', r'\d+'],
        'minEventCount': 6,
        'merge_percent' : 0.5
        },

    'Mac': {
        'log_file': 'Mac/Mac_2k.log',
        'log_format': '<Month>  <Date> <Time> <User> <Component>\[<PID>\]( \(<Address>\))?: <Content>',
        'regex': [r'([\w-]+\.){2,}[\w-]+'],
        'minEventCount': 2,
        'merge_percent' : 0.6
        },

    'HiBench': {
        'log_file': 'HiBench/HiBench_4k.log',
        'log_format': '\[<Time>\] <Content>', 
        'regex': [r'(([A-Z]:)|)(/\S+)+', r'(\S+\.\S+(\.\S+)+(:\d+)?)|(\w+-\w+(-\w+)+)', r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', r'(0x.*?\s)|(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', r'(=*|)(True)|(False)|(true)|(false)', r'[-\+\=\|]+'],
        'minEventCount': 2,
        'merge_percent' : 0.35
        },

    'CTS': {
        'log_file': 'CTS/CTS_4k.log',
        'log_format': '\[<ThreadID>\]\[<User>\] <Content>', 
        'regex': [r'(([A-Z]:)|)(/\S+)+', r'(\S+\.\S+(\.\S+)+(:\d+)?)|(\w+-\w+(-\w+)+)', r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', r'(0x.*?\s)|(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', r'(=*|)(True)|(False)|(true)|(false)', r'[-\+\=\|]+'],
        'minEventCount': 2,
        'merge_percent' : 0.2
        },
}

meanacc = 0
meanf1 = 0
bechmark_result = []
import time
begintime = time.time()
for dataset, setting in benchmark_settings.items():
    print('\n=== Evaluation on %s ==='%dataset)
    indir = os.path.join(input_dir, os.path.dirname(setting['log_file']))
    log_file = os.path.basename(setting['log_file'])

    parser = AEL.LogParser(log_format=setting['log_format'], indir=indir, outdir=output_dir,
                             minEventCount=setting['minEventCount'], merge_percent=setting['merge_percent'], rex=setting['regex'])
    parser.parse(log_file)
    
    accuracy, precision, recall, F1_measure,  = evaluator.evaluate(
                           groundtruth=os.path.join(indir, log_file + '_structured.csv'),
                           parsedresult=os.path.join(output_dir, log_file + '_structured.csv')
                           )
    bechmark_result.append([dataset, accuracy, precision, recall, F1_measure])
    meanacc += accuracy
    meanf1 += F1_measure

endtime = time.time()
print("total time = {}s".format(endtime-begintime))

print('\n=== Overall evaluation results ===')
df_result = pd.DataFrame(bechmark_result, columns=['Dataset', 'Accuracy', 'Precision', 'Recall', 'F1_measure'])
df_result.set_index('Dataset', inplace=True)
print(df_result)
# df_result.T.to_csv('AEL_bechmark_result.csv')
# print("AVERAGE ACCURACY:{}".format(meanacc/len(benchmark_settings)))
# print("AVERAGE F1-SCORE:{}".format(meanf1/len(benchmark_settings)))
