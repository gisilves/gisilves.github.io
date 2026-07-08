import sys

filename, suffix = sys.argv[1], sys.argv[2]

with open(filename, 'r') as f:
    lines = f.readlines()

with open(filename, 'w') as f:
    for line in lines:
        f.write(line.rstrip('\n') + suffix + '\n')
