#!/usr/bin/env python3
import sys, os, argparse, re, json
from time import sleep
from subprocess import run
import requests

### Setup argument parser
parser = argparse.ArgumentParser(description="Balloon Sheet Printer")
parser.add_argument('-a','--account',default='balloon',
                    help='DOMjudge API reader account (default: balloon)')
parser.add_argument('-p','--password',default='balloon',
                    help='Password (default: balloon)')
parser.add_argument('-u','--url',default='localhost',
                    help='DOMjudge url')
parser.add_argument('-i','--id',default=4,
                    help='Contest ID')
parser.add_argument('-l','--log',default='delivered.log',
                    help='Store delivered balloons (default: delivered.log)')
parser.add_argument('-c','--cont',default=True,type=eval,
                    help='Continue to deliver (default: True)')

args = parser.parse_args()

os.makedirs('printed',exist_ok=True)

with open(args.log,'at'): pass

delivered = {}
if args.cont:
    with open(args.log) as FILE:
        for line in FILE:
            try:
                teamID, probID, runID, penalty = line.strip().split()
                delivered[(teamID,probID)]={'run': runID, 'time': penalty}
            except:
                print('failed to parse old log:',line.strip(),file=sys.stderr)

api_base = 'http://{}:{}@{}/domjudge/api/v4/contests/{}/'.format(
                        args.account,args.password,args.url,args.id)+'{}'

problems = None
while not problems:
    res = requests.get(api_base.format('problems'))
    if res.status_code != 200:
        print('problems:',res.status_code)
        continue
    problems = json.loads(res.text)
problems = {p['id']:p for p in problems}

# Main loop
submissions = {}
judgements = {}
while True:
    # print('Working')
    res = requests.get(api_base.format('judgements'))
    if res.status_code != 200:
        print('judgements:',res.status_code)
        continue
    new_judge = json.loads(res.text)
    res = requests.get(api_base.format('submissions'))
    if res.status_code != 200:
        print('submissions:',res.status_code)
        continue
    new_sub = json.loads(res.text)
    for sub in new_sub:
        if not sub.get('id'): continue
        submissions[sub['id']] = sub
    for judge in new_judge:
        if not judge.get('id') or judge['id'] in judgements: continue
        if not judge['judgement_type_id'] or not judge['valid']: continue
        judgements[judge['id']] = judge
        if judge['submission_id'] not in submissions: continue
        sub = submissions[judge['submission_id']]
        runID = sub['id']
        probID = problems[sub['problem_id']]['short_name']
        teamID = sub['team_id']
        penalty = sub['contest_time'].split(':')
        penalty = int(penalty[0])*60 + int(penalty[1])
        if judge['judgement_type_id'] != 'AC': continue
        if (teamID,probID) not in delivered:
            filename = 'printed/T{}_P{}_R{}'.format(teamID,probID,runID)
            with open(filename,'wt') as FILE:
                print('''

   Balloon Delivery Sheet





  team{} solved problem {}
  ID s{} at {} minutes





      Delivered by:
'''.format(teamID,probID[-1],runID,penalty),file=FILE)
            run(['lp','-o','lpi=1.9','-o','cpi=3.6',filename])
            print('Run {}: Team'.format(runID),teamID,'solved',probID,'at',penalty)
            with open(args.log,'at') as FILE:
                print(teamID,probID,runID,penalty,file=FILE)
                sleep(1) # prevent to flood the printer
            delivered[(teamID,probID)]={'run': runID, 'time': penalty}
    # print('sleep for a while')
    sleep(10)
