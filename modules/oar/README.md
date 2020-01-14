# Run on Calculco

## Preparation of project

```
cd ~/projects
git clone https://%PROJET_NAME%.git %PROJET_NAME%
```

Push you `dataset` into the /scratch/orvalXX/lisic/user/data
```
cp -r %PROJET_NAME% /scratch/orvalXX/lisic/user/%PROJET_NAME%
```

## Link data

Create symbolic links to `dataset` of project:
```
ln -s /scracth/orvalXX/lisic/user/data/%PROJET_NAME% dataset
```

Create all usefull symbolic links to for project:
```
bash modules/oar/generate_symlinks orvalXX lisic/user/projects/%PROJET_NAME%
```

**Note:** `modules` is the submodule name of this project into your own project.

## Run script

Create your `oar.sh` script based on `oar.example.sh` and run it:
```
oarsub -S oar.sh
```