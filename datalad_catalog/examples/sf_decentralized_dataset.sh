#!/bin/zsh

# This script ...

# Example usage:
# >>

# ASSIGN VARIABLES FROM ARGUMENTS
BASEDIR=$(dirname "$0")
DATASET_PATH=$1
DATASET_NAME=$(basename "$DATASET_PATH")
OUTDIR=$2
OUTFILE="$OUTDIR/metadata_$DATASET_NAME.jsonl"
# CATALOG=$2
# TODO: flags to allow getting content or not

echo "Dataset:"
echo "      $DATASET_PATH"
echo "Dataset name:"
echo "      $DATASET_NAME"
echo "Outdir:"
echo "      $OUTDIR"
echo "Outfile:"
echo "      $OUTFILE"

# install necessary tools
# datalad
# datalad-metalad
# datalad-catalog
# datalad-neuroimaging

# datalad CLONE dataset
# datalad clone 

# extract metadata
echo "metalad_core:"
datalad --dbg meta-extract -d "$DATASET_PATH" metalad_core > $OUTFILE
# datalad meta-extract -d "$DATASET_PATH" metalad_studyminimeta >> $OUTFILE
echo "bids_dataset:"
datalad --dbg meta-extract -d "$DATASET_PATH" bids_dataset >> $OUTFILE
echo "datacite_gin:"
datalad --dbg meta-extract -d "$DATASET_PATH" datacite_gin >> $OUTFILE






# clone catalog (datalad or git clone)