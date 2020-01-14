from modules.config.attributes_config import *

# store all variables from global config
context_vars = vars()

# folders
logs_folder                             = 'logs'
backup_folder                           = 'backups'

## min_max_custom_folder           = 'custom_norm'
## correlation_indices_folder      = 'corr_indices'

# variables
features_choices_labels                 = ['svd_entropy']

filter_reduction_choices                = ['attributes', 'filters']
models_names_list                       = ["svm_model"]

# parameters
## keras_epochs                    = 500
## keras_batch                     = 32
## val_dataset_size                = 0.2