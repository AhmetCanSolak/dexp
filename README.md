## DEXP
Dataset Exploration Tool


# Prerequisites:

Install Anaconda:
https://repo.anaconda.com/archive/Anaconda3-2019.03-MacOSX-x86_64.pkg

Update Anaconda:
```
conda update conda
conda update anaconda
```

# Installation:

Create conda environment:
```
conda create --name dexp python=3.7 
```

Activate environment:
```
source activate dexp
```

Install important packages:
```
conda install numpy mkl zarr dask click numcodecs
```

Clone dexp:
```
git clone https://github.com/royerlab/dexp.git
```

Install dexp:
```
cd dexp
pip install -e .
```

# Usage:

Always make sure that you are in the correct environment:
```
source activate dexp
```

There is currently 3 dexp commands: copy, info and view:

## info:
```
Usage: dexp info [OPTIONS] INPUT_PATH

Options:
  --help  Show this message and exit.
```

## copy:
```
Usage: dexp copy [OPTIONS] INPUT_PATH

Options:
  -o, --output_path TEXT
  -c, --channels TEXT     list of channels, all channels when ommited.
  -s, --slice TEXT        dataset slice (TZYX), e.g. [0:5] (first five stacks)
                          [:,0:100] (cropping in z)
  -z, --codec TEXT        compression codec: ‘zstd’, ‘blosclz’, ‘lz4’,
                          ‘lz4hc’, ‘zlib’ or ‘snappy’
  -w, --overwrite         to force overwrite of target
  -p, --project INTEGER   max projection over given axis (0->T, 1->Z, 2->Y,
                          3->X)
  --help                  Show this message and exit.
```

## view:
```
Usage: dexp view [OPTIONS] INPUT_PATH

Options:
  -c, --channels TEXT  list of channels, all channels when ommited.
  -s, --slice TEXT     dataset slice (TZYX), e.g. [0:5] (first five stacks)
                       [:,0:100] (cropping in z).
  --help               Show this message and exit.
```

# Examples:

The folowing examples can be test on the micro1 shared folder:

Gathers info on the dataset '2019-07-03-16-23-15-65-f2va.mch7' with napari: 
```
dexp info 2019-07-03-16-23-15-65-f2va.mch7
```

Copies a z-max-projection for the first 10n timepoints (-s [0:10]) from scope acquisition '2019-07-03-16-23-15-65-f2va.mch7' to Zarr folder '~/Downloads/local.zarr', and overwrites whatever is there (-w). 
```
dexp copy 2019-07-03-16-23-15-65-f2va.mch7 -o ~/Downloads/local.zarr -w -p 1 -s [0:10]
```

Views the first 100 times points '2019-07-03-16-23-15-65-f2va.mch7' with napari: 
```
dexp view 2019-07-03-16-23-15-65-f2va.mch7 -s [0:100]
```



