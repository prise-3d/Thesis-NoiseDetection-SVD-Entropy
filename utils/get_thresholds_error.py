# main imports
import os, sys
import argparse


# modules and config imports
sys.path.insert(0, '') # trick to enable import of main folder module

import custom_config as cfg


def main():

    thresholds_folder = os.path.join(cfg.output_data_folder, cfg.data_thresholds)
    files_dir = os.listdir(thresholds_folder)
    csv_results_files = [ f for f in files_dir if '.csv' in f and 'analysis' not in f]

    min_error = 100000000
    min_model_found = None

    for csv_file in csv_results_files:

        global_error = 0
        csv_path = os.path.join(thresholds_folder, csv_file)

        with open(csv_path, 'r') as f:

            for line in f.readlines():
                data = line.split(';')

                human_threshold = float(data[3])
                estimated_threshold = float(data[4])
                global_error = global_error + abs(human_threshold - estimated_threshold)


        if global_error < min_error:
            min_error = global_error
            min_model_found = csv_file


        print(csv_file, '=>', global_error)       

    print('------------------------')     
    print('Best found `' + min_model_found + '` => ' + str(min_error))

if __name__ == "__main__":
    main()