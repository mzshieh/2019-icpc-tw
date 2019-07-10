# input: domjudge standing.tsv
# output: baylor standings.csv
# example.csv: download from baylor

from sys import stdin

res = {}
lines = [line.strip('\n').split('\t') for line in stdin.readlines()]
n_teams = len(lines)-1
for line in lines:
     if len(line) != 2:
         tid = line[1]
         rank = int(line[2])
         solved = line[3]
         penalty = line[4]
         last = line[5]
         if rank <= n_teams/10:
             medal = '"Gold Prize"'
         elif rank <= n_teams*3/10:
             medal = '"Silver Prize"'
         elif rank <= n_teams*6/10:
             medal = '"Bronze Prize"'
         else:
             medal = '"Honorable Mention"'
         site = ''
         cite = ''
         output = [tid,rank,medal,solved,penalty,last,site,cite]
         res[tid] = output

with open('example.csv') as FILE:
    for line in FILE:
        tid = line.split(',')[0]
        if tid.isdecimal():
            print(*res[tid],sep=',')
        else:
            print(line.strip())
