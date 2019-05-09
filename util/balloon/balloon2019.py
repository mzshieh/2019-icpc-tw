#!/usr/bin/env python3
import sys, os, argparse, re, json
from time import sleep
from subprocess import run

### Setup argument parser
parser = argparse.ArgumentParser(description="Balloon Sheet Printer")
parser.add_argument('-l','--log',default='delivered.log',
                    help='Store delivered balloons (default: delivered.log)')
parser.add_argument('-c','--cont',default=True,type=eval,
                    help='Continue to deliver (default: True)')

args = parser.parse_args()

os.makedirs('printed',exist_ok=True)

with open(args.log,'at'):
    pass

delivered = {}
if args.cont:
    with open(args.log) as FILE:
        for line in FILE:
            try:
                teamID, probID, runID, penalty = line.strip().split()
                delivered[(teamID,probID)]={'run': runID, 'time': penalty}
            except:
                print('failed to parse old log:',line.strip(),file=sys.stderr)

# Main loop
acceptable = set()
pid, jid = {}, {}
submission = {}
for line in sys.stdin:
    line = line.strip()
    try: obj = json.loads(line)
    except: continue

    data_type = obj.get('type')
    data = obj.get('data')
    if data == None: continue
    if data_type == 'judgement-types': 
        if data.get('solved'):
            acceptable.add(data.get('id'))
    elif data_type == 'problems':
        pid[data.get('id')]=chr(ord('A')+data.get('ordinal'))
    elif data_type == 'submissions':
        submission[data.get('id')]={'pid':pid.get(data.get('problem_id')),
                'tid':data.get('team_id')}
    elif data_type == 'judgements':
        jid[data.get('id')]=submission[data.get('submission_id')]
    elif data_type == 'runs' and data.get('judgement_type_id') in acceptable:
        runID = data.get('judgement_id')
        probID = jid[data.get('judgement_id')].get('pid')
        teamID = jid[data.get('judgement_id')].get('tid')
        penalty = data.get('contest_time').split(':')
        penalty = int(penalty[0])*60 + int(penalty[1])
    if data_type != 'runs': continue
    if (teamID,probID) not in delivered:
        filename = 'printed/T{}_P{}_R{}'.format(teamID,probID,runID)
        with open(filename,'wt') as FILE:
            print('''

   Balloon Delivery Sheet





  Team {} solved Problem {}
  Run {} at {} minutes





      Delivered by:
'''.format(teamID,probID,runID,penalty),file=FILE)
        # run(['lp','-o','lpi=1.9','-o','cpi=3.5',filename])
        print('Run {}: Team'.format(runID),teamID,'solved',probID,'at',penalty)
        with open(args.log,'at') as FILE:
            print(teamID,probID,runID,penalty,file=FILE)
            sleep(1) # prevent to flood the printer
        delivered[(teamID,probID)]={'run': runID, 'time': penalty}

print('The connection to the event feeder is closed.')
