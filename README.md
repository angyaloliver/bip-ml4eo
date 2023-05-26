# bip-ml4eo
Repository for the Machine Learning for Earth Observation Summer School in Pavia, Italy

## Setup environment

TBD...

## Download the data

The Sentinel-2 data has been uploaded to Kaggle: see [sentinel-2-cremona](https://www.kaggle.com/datasets/olivrangyal/sentinel-2-cremona) dataset.
The ancillary data (hydrometric levels) is on Google Drive [here](https://drive.google.com/file/d/1m3oRkElw3WGTwfrHbnD2iQKXz-FlfIga/view?usp=drive_link).

The data should be downloaded at `data/Water/` with the folder tree as below:
```
data/Water
├── Cremona SIAP - Livello Idrometrico - 2023-01-12.csv
└── sentinel-2-cremona
    ├── images
    │   ├── S2A_MSIL2A_20220309T100841_N0400_R022_T32TNQ_20220309T134626.tif
    │   ├── S2A_MSIL2A_20220309T100841_N0400_R022_T32TNR_20220309T134626.tif
    │   ├── S2A_MSIL2A_20220322T101711_N0400_R065_T32TNQ_20220322T141030.tif
    │   ├── S2A_MSIL2A_20220322T101711_N0400_R065_T32TNR_20220322T141030.tif
    │   ├── ...
    └── S2_Cremona_DESCENDING_info.csv

```


## Merge Sentinel-2 raster tiles

Merge the Sentinel-2 raster tiles with:
```sh
python src/merge_s2_tiles.py
```
This should take approx. 3-4 min to complete.
This should create 31 merged images in total. The merge dataset will be in the output directory `data/Water/sentinel-2-cremona/merged-images`.


## Notebook of analyses

This [notebook](./src/bip-ml4eo.ipynb) contains Olivèr's work.
