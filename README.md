# Noise detection using 26 attributes

## Description

Noise detection on synthesis images using SVD entropy criteria.

Assumption: Entropy gives information about complexity of an image.

## Requirements

Recursive clone is required for `modules` git project.

or
```
git submodule update --init --recursive
```

Then, install python dependencies:
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

- **data/\***: folder which will contain all generated data files.


## How to use ?


**Note:** All generated output files are saved into `data` folder by default.


You can generate your own entropy data extracted from your dataset:
```bash
python estimate_entropy.py --output entropy_data.csv
```

You can compute the diff entropy using previous data file and get all estimated threshold from gradient criteria (obtained from human threshold):
```
python compute_diff_entropy.py --data data/entropy_data.py --output entropy_diff.csv
```

Then you can reconstruct image using estimated thresholds:
```
python reconstruct_image_estimated --data data/entropy_diff.csv --scene A --output data/images/A_scene_estimated.png
```

## TODO

- Create bash script to run all scenes

## License

[The MIT license](LICENSE)
