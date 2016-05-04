import re
import sys
import os;
import glob;
import subprocess;
from math import log, exp, sqrt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

header = re.compile("\^\^\^\^ ([A-Z-]+)")
real = re.compile("real ([0-9.]+)")
pss = re.compile("PeakPss ([0-9]+)kB")
octane_score = re.compile("Score [^:]+: (\d+)")

workloads = ['cp', 'make', 'octane', 'htmltest', 'sambatest']
configs = ['NORMAL','RECORD','REPLAY','SINGLE-CORE','RECORD-NO-SYSCALLBUF',
           'REPLAY-NO-SYSCALLBUF','RECORD-NO-CLONING','DYNAMORIO']

baseline_seconds = []
overheads = {}
mem_pss = {}
mem_pss_err_min = {}
mem_pss_err_max = {}
overhead_err_min = {}
overhead_err_max = {}
for c in configs:
    overheads[c] = []
    overhead_err_min[c] = []
    overhead_err_max[c] = []
    mem_pss[c] = []
    mem_pss_err_min[c] = []
    mem_pss_err_max[c] = []

baseline_scores = []
record_scores = []
record_time_scores = []

z = 1.96

def geomean(array):
    prod = 1
    for a in array:
        prod = prod*a
    return pow(prod, 1.0/len(array))

def mean(array):
    s = 0
    for a in array:
        s = s + a
    return s/len(array)

def variance(array):
    s = 0
    m = mean(array)
    for a in array:
        s = s + (a - m)*(a - m)
    return s/len(array)

def flush_header(name, h, times, octane_scores):
    global baseline_scores
    global record_scores
    global record_time_scores
    times.pop(0)
    if len(octane_scores) > 0:
        octane_scores.pop(0)

    scores = []
    for i in xrange(0, len(times)):
        if len(octane_scores) > 0:
            s = -log(octane_scores[i])
        elif h == "DYNAMORIO" and name == "octane":
            s = -1000
        else:
            s = log(times[i])
        scores.append(s)

    if h == "NORMAL":
        baseline_seconds.append(geomean(times))
        baseline_scores = scores
    else:
        if h[0:6] == "REPLAY" and name == "octane":
            replay_time_scores = []
            for i in xrange(0, len(times)):
                replay_time_scores.append(log(times[i]))
            m = mean(replay_time_scores) - mean(record_time_scores) + mean(record_scores) - mean(baseline_scores)
            v = variance(replay_time_scores) + variance(record_time_scores) + variance(record_scores) + variance(baseline_scores)
        else:
            m = mean(scores) - mean(baseline_scores)
            v = variance(scores) + variance(baseline_scores)
        overheads[h].append(exp(m))
        overhead_err_min[h].append(exp(m) - exp(m - z*sqrt(v/len(scores))))
        overhead_err_max[h].append(exp(m + z*sqrt(v/len(scores))) - exp(m))

    if h[0:6] == "RECORD":
        record_time_scores = []
        for i in xrange(0, len(times)):
            record_time_scores.append(log(times[i]))
        record_scores = scores

def process(name, f):
    h = None
    times = []
    octane_scores = []
    for line in f:
        m = header.match(line)
        if m:
            if h != None:
                flush_header(name, h, times, octane_scores)
            h = m.group(1)
            times = []
            octane_scores = []
        m = real.match(line)
        if m:
            times.append(float(m.group(1)))
        m = octane_score.match(line)
        if m:
            octane_scores.append(int(m.group(1)))
    flush_header(name, h, times, octane_scores)

def sample(ws, os):
    result = []
    for w in ws:
        for i in xrange(len(workloads)):
            if workloads[i] == w:
                result.append(os[i])
    return result

for name in workloads:
    f = open("output-%s"%name, 'r')
    process(name, f)

for i in xrange(0,len(workloads)):
    print "%s & %.2fs & %.2f$\\times$ & %.2f$\\times$ & %.2f$\\times$ & %.2f$\\times$ & %.2f$\\times$ & %.2f$\\times$ & %.2f$\\times$ \\\\"%(workloads[i], baseline_seconds[i], overheads['RECORD'][i],
          overheads['REPLAY'][i], overheads['SINGLE-CORE'][i],
          overheads['RECORD-NO-SYSCALLBUF'][i], overheads['REPLAY-NO-SYSCALLBUF'][i],
          overheads['RECORD-NO-CLONING'][i], overheads['DYNAMORIO'][i])

print

def flush_header_mem(name, h, peak_pss):
    peak_pss.pop(0)

    m = geomean(peak_pss)
    v = variance(peak_pss)
    mem_pss[h].append(m/1024.0)
    mem_pss_err_min[h].append(z*sqrt(v/len(peak_pss))/1024.0)
    mem_pss_err_max[h].append(z*sqrt(v/len(peak_pss))/1024.0)

def process_mem(name, f):
    h = None
    peak_pss = []
    for line in f:
        m = header.match(line)
        if m:
            if h != None:
                flush_header_mem(name, h, peak_pss)
            h = m.group(1)
            peak_pss = []
        m = pss.match(line)
        if m:
            peak_pss.append(float(m.group(1)))
    flush_header_mem(name, h, peak_pss)

for name in workloads:
    f = open("mem-%s"%name, 'r')
    process_mem(name, f)

for i in xrange(0,len(workloads)):
    print "%s & %.2f & %.2f & %.2f & %.2f \\\\"%(workloads[i], mem_pss['NORMAL'][i], mem_pss['RECORD'][i],
          mem_pss['REPLAY'][i], mem_pss['SINGLE-CORE'][i], )

def offset(array, delta):
    return map(lambda x:x + delta, array)

plot_workloads = ["cp", "octane", "htmltest", "sambatest"]
plt.figure(1)
fig, ax = plt.subplots()
width = 1.0/3
spacing = width/2
ind = range(len(plot_workloads))
plt.rcParams.update({'font.size': 16})
record_rects = ax.bar(offset(ind, spacing), sample(plot_workloads, overheads['RECORD']), width, color="r",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, overhead_err_min['RECORD']),
        sample(plot_workloads, overhead_err_max['RECORD'])])
replay_rects = ax.bar(offset(ind, spacing + width), sample(plot_workloads, overheads['REPLAY']), width, color="y",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, overhead_err_min['REPLAY']),
        sample(plot_workloads, overhead_err_max['REPLAY'])])
ax.set_ylabel('Overhead relative to baseline')
ax.set_xlabel('Workload',labelpad=10)
ax.xaxis.set_major_formatter(ticker.NullFormatter())
ax.xaxis.set_minor_formatter(ticker.NullFormatter())
ax.set_xticks(offset(ind, 0.5),minor=True)
ax.set_xticklabels(plot_workloads,minor=True)
ax.set_axisbelow(True)
ax.yaxis.grid()
ax.set_ylim([0,2.5])
ax.legend([record_rects[0], replay_rects[0]], ['Record', 'Replay'])
plt.savefig('RecordReplay.pdf')

def autolabel_over_limit(rects, values, lim):
    i = 0
    for rect in rects:
        height = rect.get_height()
        if lim < values[i]:
            ax.text(rect.get_x() + rect.get_width()/2., lim,
                '%.2f' % values[i],
                ha='center', va='bottom')
        i = i + 1

plot_workloads = workloads
plt.figure(2)
fig, ax = plt.subplots()
width = 1.0/4
spacing = width/2
ind = range(len(plot_workloads))
plt.rcParams.update({'font.size': 16})
record_rects = ax.bar(offset(ind, spacing), sample(plot_workloads, overheads['RECORD']), width, color="r",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, overhead_err_min['RECORD']),
        sample(plot_workloads, overhead_err_max['RECORD'])])
values = sample(plot_workloads, overheads['RECORD-NO-SYSCALLBUF'])
record_no_syscallbuf_rects = ax.bar(offset(ind, spacing + width), values, width, color="lime",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, overhead_err_min['RECORD-NO-SYSCALLBUF']),
        sample(plot_workloads, overhead_err_max['RECORD-NO-SYSCALLBUF'])])
autolabel_over_limit(record_no_syscallbuf_rects, values, 14)
record_no_cloning_rects = ax.bar(offset(ind, spacing + width*2), sample(plot_workloads, overheads['RECORD-NO-CLONING']), width, color="navy",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, overhead_err_min['RECORD-NO-CLONING']),
        sample(plot_workloads, overhead_err_max['RECORD-NO-CLONING'])])
ax.set_ylabel('Overhead relative to baseline')
ax.set_xlabel('Workload',labelpad=10)
ax.xaxis.set_major_formatter(ticker.NullFormatter())
ax.xaxis.set_minor_formatter(ticker.NullFormatter())
ax.set_xticks(offset(ind, 0.5),minor=True)
ax.set_xticklabels(plot_workloads,minor=True)
ax.set_axisbelow(True)
ax.yaxis.grid()
ax.set_ylim([0,14])
ax.legend([record_rects[0], record_no_syscallbuf_rects[0], record_no_cloning_rects[0]], ['Record', 'Record-no-syscallbuf', 'Record-no-cloning'])
plt.savefig('Optimizations.pdf')

plot_workloads = ["cp", "make", "htmltest", "sambatest"]
plt.figure(3)
fig, ax = plt.subplots()
width = 1.0/3
spacing = width/2
ind = range(len(plot_workloads))
plt.rcParams.update({'font.size': 16})
record_rects = ax.bar(offset(ind, spacing), sample(plot_workloads, overheads['RECORD']), width, color="r",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, overhead_err_min['RECORD']),
        sample(plot_workloads, overhead_err_max['RECORD'])])
dynamorio_rects = ax.bar(offset(ind, spacing + width), sample(plot_workloads, overheads['DYNAMORIO']), width, color="purple",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, overhead_err_min['DYNAMORIO']),
        sample(plot_workloads, overhead_err_max['DYNAMORIO'])])
ax.set_ylabel('Overhead relative to baseline')
ax.set_xlabel('Workload',labelpad=10)
ax.xaxis.set_major_formatter(ticker.NullFormatter())
ax.xaxis.set_minor_formatter(ticker.NullFormatter())
ax.set_xticks(offset(ind, 0.5),minor=True)
ax.set_xticklabels(plot_workloads,minor=True)
ax.set_axisbelow(True)
ax.yaxis.grid()
ax.legend([record_rects[0], dynamorio_rects[0]], ['Record', 'DynamoRio-null'], loc = 'right')
plt.savefig('DynamoRio.pdf')

plot_workloads = workloads
plt.figure(4)
fig, ax = plt.subplots()
width = 1.0/5
spacing = width/2
ind = range(len(plot_workloads))
plt.rcParams.update({'font.size': 16})
normal_rects = ax.bar(offset(ind, spacing), sample(plot_workloads, mem_pss['NORMAL']), width, color="black",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, mem_pss_err_min['NORMAL']),
        sample(plot_workloads, mem_pss_err_max['NORMAL'])])
record_rects = ax.bar(offset(ind, spacing + width), sample(plot_workloads, mem_pss['RECORD']), width, color="r",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, mem_pss_err_min['RECORD']),
        sample(plot_workloads, mem_pss_err_max['RECORD'])])
replay_rects = ax.bar(offset(ind, spacing + 2*width), sample(plot_workloads, mem_pss['REPLAY']), width, color="y",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, mem_pss_err_min['REPLAY']),
        sample(plot_workloads, mem_pss_err_max['REPLAY'])])
single_core_rects = ax.bar(offset(ind, spacing + width*3), sample(plot_workloads, mem_pss['SINGLE-CORE']), width, color="magenta",
  error_kw=dict(elinewidth=2),yerr=[sample(plot_workloads, mem_pss_err_min['SINGLE-CORE']),
        sample(plot_workloads, mem_pss_err_max['SINGLE-CORE'])])
ax.set_ylabel('Peak PSS (MB)')
ax.set_xlabel('Workload',labelpad=10)
ax.xaxis.set_major_formatter(ticker.NullFormatter())
ax.xaxis.set_minor_formatter(ticker.NullFormatter())
ax.set_xticks(offset(ind, 0.5),minor=True)
ax.set_xticklabels(plot_workloads,minor=True)
ax.set_axisbelow(True)
ax.yaxis.grid()
ax.set_ylim([0,1200])
ax.legend([normal_rects[0], record_rects[0], replay_rects[0], single_core_rects[0]], ['Baseline', 'Record', 'Replay', 'Single Core'])
plt.savefig('MemUsage.pdf')

dump = re.compile("// Uncompressed bytes (\d+), compressed bytes (\d+),.*")

def file_size(path):
    return os.stat(path).st_size

print

index = 0
for name in workloads:
    cloned_blocks_sizes = []
    compressed_sizes = []
    uncompressed_sizes = []
    trace_name = name
    if name == "sambatest":
        trace_name = "samba"
    for i in range(1,6):
         cloned_blocks = 0
         for p in glob.iglob("traces/%s-%d/cloned_data_*"%(name,i)):
             cloned_blocks = cloned_blocks + file_size(p)
         cloned_blocks_sizes.append(cloned_blocks)
         line = subprocess.check_output("rr dump -s traces/%s-%d/|grep ^//"%(trace_name,i), shell=True)
         m = dump.match(line)
         uncompressed_sizes.append(int(m.group(1)))
         compressed_sizes.append(int(m.group(2)))

    print "%s & %.2f & %.2f$\\times$ & %.2f \\\\"%(name,geomean(compressed_sizes)/(1024*1024)/baseline_seconds[index],geomean(uncompressed_sizes)/geomean(compressed_sizes),geomean(cloned_blocks_sizes)/(1024*1024)/baseline_seconds[index])
    index = index + 1

