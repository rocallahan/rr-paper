import re;
import sys;

header = re.compile("\^\^\^\^ ([A-Z-]+)")
real = re.compile("real\s+(\d+)m([0-9.]+)s")
octane_score = re.compile("Score [^:]+: (\d+)")

results = []
baseline_score = 0
record_time = 0

def geomean(array):
    prod = 1
    for a in array:
        prod = prod*a
    return pow(prod, 1.0/len(array))

def flush_header(name, h, times, octane_scores):
    global baseline_score
    global record_time
    times.pop(0)
    if len(octane_scores) > 0:
        octane_scores.pop(0)

    scores = []
    for i in xrange(0, len(times)):
        if len(octane_scores) > 0:
            s = 1.0/octane_scores[i]
        else:
            s = times[i]
        scores.append(s)

    if h == "DYNAMORIO" and name == "octane":
        results.append(0)
    elif h == "NORMAL":
        results.append(geomean(times))
        baseline_score = geomean(scores)
    elif h[0:6] == "REPLAY" and name == "octane":
        results.append((geomean(scores)/baseline_score)*geomean(times)/record_time)
    else:
        results.append(geomean(scores)/baseline_score)

    if h[0:6] == "RECORD":
        record_time = geomean(times)

def process(name, f):
    have_header = False
    h = ""
    times = []
    octane_scores = []
    for line in f:
        m = real.match(line)
        if m:
            times.append(int(m.group(1))*60 + float(m.group(2)))
        m = octane_score.match(line)
        if m:
            octane_scores.append(int(m.group(1)))
        m = header.match(line)
        if m:
            if have_header:
                flush_header(name, h, times, octane_scores)
            h = m.group(1)
            times = []
            octane_scores = []
            have_header = True
    flush_header(name, h, times, octane_scores)

print "\tNORMAL\tRECORD\tREPLAY\tSINGLE-CORE\tRECORD-NO-SYSCALLBUF\tREPLAY-NO-SYSCALLBUF\tRECORD-NO-CLONING\tDYNAMORIO"

for name in ['cp', 'make', 'octane', 'htmltest', 'sambatest']:
    f = open("output-%s"%name, 'r')
    process(name, f)
    print "%s\t%f\t%f\t%f\t%f\t%f\t%f\t%f\t%f"%(name,results[0],results[5],results[6],results[1],results[2],results[3],results[4],results[7])
    results = []

