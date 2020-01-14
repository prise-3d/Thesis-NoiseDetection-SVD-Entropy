# Noise detection using 26 attributes

## Description

Noise detection on synthesis images using SVD entropy criteria.

Entropy gives information about complexity of an image.

## Requirements

```
pip install -r requirements.txt
```

## Project structure

### Link to your dataset

You have to create a symbolic link to your own database which respects this structure:

- dataset/
  - Scene1/
    - zone00/
    - ...
    - zone15/
      - seuilExpe (file which contains threshold samples of zone image perceived by human)
    - Scene1_00050.png
    - Scene1_00070.png
    - ...
    - Scene1_01180.png
    - Scene1_01200.png
  - Scene2/
    - ...
  - ...

Create your symbolic link:

```
ln -s /path/to/your/data dataset
```

### Code architecture description

- **modules/\***: contains all modules usefull for the whole project (such as configuration variable
- **custom_config.py**: override the main configuration project of `modules/config/global_config.py`

### Generated data directories:

- **data/\***: folder which will contain all generated *.train* & *.test* files in order to train model.
- **saved_models/\***: all scikit learn or keras models saved.
- **models_info/\***: all markdown files generated to get quick information about model performance and prediction obtained after running `run/runAll_*.sh` script.
- **results/**:  This folder contains `model_comparisons.csv` file used for store models performance.


## How to use ?

Explained later...

## License

[The MIT license](LICENSE)
