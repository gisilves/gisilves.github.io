import os

# Check if Targets_Y_Step1_XYAdjusted.csv exists

if os.path.isfile('Targets_Y_Step1_XYAdjusted.csv'):
    # Read lines in a list
    with open('Targets_Y_Step1_XYAdjusted.csv', 'r') as input_file:
        lines = input_file.readlines()
        # Change all occurrences of 20000 to 100000
        for i in range(len(lines)):
            lines[i] = lines[i].replace('20000', '100000')
    # Open output file for writing Targets_Y_Step0_XYAdjusted.csv
    with open('Targets_Y_Step0_XYAdjusted.csv', 'w') as output_file:
        # Extract Step 0 points from Step 1 points
        for i in range(111, 94, -1):
            output_file.write(lines[i])
            
        for i in range(264, 247, -1):
            output_file.write(lines[i])
            
else:
    print('Targets_Y_Step1_XYAdjusted.csv does not exist')