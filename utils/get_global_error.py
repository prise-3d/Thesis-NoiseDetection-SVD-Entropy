# main imports
import os, sys


results_folder = "results"


def main():

    files_dir = os.listdir(results_folder)
    csv_results_files = [ f for f in files_dir if '.csv' in f]

    min_error = 1000000
    min_model_found = None

    for csv_file in csv_results_files:

        global_error = 0
        csv_path = os.path.join(results_folder, csv_file)

        with open(csv_path, 'r') as f:
            for line in f.readlines():
                data = line.split(';')
                human_error = float(data[1])
                estimation_error = float(data[2])
                global_error = global_error + abs(human_error - estimation_error)

        if global_error < min_error:
            min_error = global_error
            min_model_found = csv_file

        print(csv_file, '=>', global_error)       

    print('------------------------')     
    print('Best found `' + min_model_found + '` => ' + str(min_error))

if __name__ == "__main__":
    main()