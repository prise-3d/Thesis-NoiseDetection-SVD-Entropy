from modules.config.attributes_config import *

# store all variables from global config
context_vars = vars()

# folders
logs_folder                             = 'logs'
backup_folder                           = 'backups'
references_folder                       = 'references'

data_generated                          = 'generated'
data_thresholds                         = 'thresholds'
data_results                            = 'results'
data_fig_folder                         = 'tmp_images'

## min_max_custom_folder           = 'custom_norm'
## correlation_indices_folder      = 'corr_indices'

# variables
features_choices_labels                 = ['svd_entropy']

filter_reduction_choices                = ['attributes', 'filters']
models_names_list                       = ["svm_model"]

references_scenes                       = ['A_00900.png', 'B_10000.png', 'C_01480.png', 'D_01200.png', 'E_10000.png', 'F_40000.png', 'G_00950.png', 'H_00950.png', 'I_03100.png']

# parameters
## keras_epochs                    = 500
## keras_batch                     = 32
## val_dataset_size                = 0.2