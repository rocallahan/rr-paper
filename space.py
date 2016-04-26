import re;
import sys;
import os;
import glob;
import subprocess;

dump = re.compile("// Uncompressed bytes (\d+), compressed bytes (\d+),.*")

def geomean(array):
    prod = 1
    for a in array:
        prod = prod*a
    return pow(prod, 1.0/len(array))

def file_size(path):
    return os.stat(path).st_size

for name in ['samba']:
    cloned_blocks_sizes = []
    compressed_sizes = []
    uncompressed_sizes = []
    
    for i in range(1,6):
         cloned_blocks = 0
         for p in glob.iglob("traces/%s-%d/cloned_data_*"%(name,i)):
             cloned_blocks = cloned_blocks + file_size(p)
         cloned_blocks_sizes.append(cloned_blocks)
         line = subprocess.check_output("rr dump -s traces/%s-%d/|grep ^//"%(name,i), shell=True)
         m = dump.match(line)
         compressed_sizes.append(int(m.group(1)))
         uncompressed_sizes.append(int(m.group(2)))

    print "%s\t%f\t%f\t%f"%(name,geomean(cloned_blocks_sizes),geomean(compressed_sizes),geomean(uncompressed_sizes))

