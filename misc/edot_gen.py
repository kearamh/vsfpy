# https://stackoverflow.com/questions/27471980/f-readlines-wont-return-any-values

path = '/mnt/gs21/scratch/hayeskea/rerun_small_cluster/'

file_in = 'output_file_01.log'

count = 0

with open(path + file_in, 'r') as reading:

    with open(path + 'edot_out.txt', 'a') as writing:

        for line in reading:

            start_found = False
            end_found = False

            if line[0:12] == 'Heating rate':
                
                for c in range(len(line)):

                    if (line[c] == '(') and (start_found == False):
                        edot_start = c + 1   # retrieving the index in the line where the actual edot value starts
                        start_found = True

                    if (line[c] == ')') and (end_found == False):
                        edot_end = c - 6     # this isn't actually the character we want but instead set to make the exclusive end index work below
                        end_found = True

            if (start_found == True) and (end_found == True):       
                edot = line[edot_start:edot_end]

                writing.write(str(edot) + '\n')