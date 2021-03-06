# main imports
import os, sys



# modules and config imports
sys.path.insert(0, '') # trick to enable import of main folder module

import custom_config as cfg


results_folder = os.path.join(cfg.output_data_folder, cfg.data_results)

std_file_results = results_folder + "/std_analysis.csv"


def main():

    min_error = 1000000
    min_model_found = None

    with open(std_file_results, 'r') as f:
        for line in f.readlines():
            data = line.split(';')

            current_method = data[0]
            current_std = float(data[1])

            if current_std < min_error:
                min_error = current_std
                min_model_found = data[0]

            print(current_method, '=>', current_std)       

    print('------------------------')     
    print('Best found `' + min_model_found + '` => ' + str(min_error))

if __name__ == "__main__":
    main()