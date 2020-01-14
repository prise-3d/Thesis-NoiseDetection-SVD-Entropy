# Thesis common modules

## Description

Project which contains dependencies used in few developed projects:

- [Noise Detection CNN](https://github.com/prise-3d/Thesis-NoiseDetection-CNN.git)
- [Denoising autoencoder](https://github.com/prise-3d/Thesis-Denoising-autoencoder.git)
- [Noise Detection attributes](https://github.com/prise-3d/Thesis-NoiseDetection-attributes.git)
- [Noise Detection 26 attributes](https://github.com/prise-3d/Thesis-NoiseDetection-26-attributes.git)
- [Noise Analysis](https://github.com/prise-3d/Thesis-NoiseAnalysis.git)

## Configuration file

There is few configuration files (`config` folder):
- **global:** contains common variables of project
- **attributes:** extends from global and contains specific variables
- **cnn:** extends from global and contains specific variables for Deep Learning

## Add as dependency

```bash
git submodule add https://github.com/prise-3d/Thesis-CommonModules.git modules
```

## Dataset information

| ID | Name | Renderer | Number of Images |
|:---:|---:|---:|---:|
| A | Appart1opt02 | maxwell | 89 |
| B | Bureau1 | igloo | 200 |
| C | Cendrier | | 25 |
| D | Cuisine01 | maxwell | 116 |
| E | EchecsBas | cycle| 200 |
| F | PNDVuePlongeante | igloo | 800 |
| G | SdbCentre | maxwell | 94 |
| H | SdbDroite | maxwell | 94 |
| I | Selles | cycle | 62 |

## License

[The MIT License](LICENSE)