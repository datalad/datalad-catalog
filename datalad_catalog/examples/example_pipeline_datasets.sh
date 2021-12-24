#!/bin/zsh

# This script runs on a datalad superdataset which has all subdatasets installed locally.
# Only recursive installation/cloning is required, obtaining files via `datalad get` is NOT necessary.
# The script requires a single parameter: absolute path to super-dataset
# Output files are written to current working directory (subds.txt, supersubmeta.json, and a json file per subdataset)
# Output files are in a format that's ingested by python scripts in datalad-catalog
# Example usage:
# >> cd /path/to/datalad-catalog
# >> datalad_catalog/examples/example_pipeline_datasets.sh /path/to/super-dataset

BASEDIR=$(dirname "$0")
SUPER=$1
echo "Super dataset:"
echo "      $SUPER"

# Get subdatsets, write to file, count
# TODO: this could possibly be replaced by a smarter git- or datalad-specific method. e.g. subdatasets also available from .gitmodules
# TODO: write dataset paths to array
datalad subdatasets -d $SUPER > subds.txt
echo "Number of subdatasets:"
grep "subdataset(ok)" subds.txt | wc -l

datalad meta-extract -d "$SUPER" metalad_core > supermeta.json
datalad meta-extract -d "$SUPER" metalad_studyminimeta >> supermeta.json
# Get superdataset id and version (to add to file metadata for context in hierarchy)
# TODO: this could probably be replaced by: git config -f ${SUPER}/.datalad/config datalad.dataset.<id/version>
echo "Get superdataset metadata:"
SUPER_ID=$(datalad -f json meta-extract -d "$SUPER" metalad_core | jq -r '.["metadata_record"]["dataset_id"]')
SUPER_VERSION=$(datalad -f json meta-extract -d "$SUPER" metalad_core | jq -r '.["metadata_record"]["dataset_version"]')
echo "id: $SUPER_ID"
echo "version: $SUPER_VERSION"

# For each subdataset, extract file-level metadata, write to disk
echo "Extracting file-level metadata:"
WORD1TOREMOVE="subdataset(ok): "
WORD2TOREMOVE=" (dataset)"
i=0
while read p; do
  SUBDS_PATH="${${p//$WORD1TOREMOVE/}//$WORD2TOREMOVE/}"
  SUBDS_NAME="${SUBDS_PATH##*/}"
  LINE="$SUPER/$SUBDS_PATH"
  if ! [[ $LINE == *":"* ]]; then
    i=$((i+1))
    echo "$i: $LINE"
    # Add starting array bracket
    datalad meta-extract -d "$LINE" metalad_core > "submeta_$SUBDS_NAME.json"
    datalad meta-extract -d "$LINE" metalad_studyminimeta >> "submeta_$SUBDS_NAME.json"
    # Remove last comma
    # sed -i '' '$ s/.$//' "$SUBDS_NAME.json"
  fi
done <subds.txt

SUBDS_NAME="Masterthesis_Barisch"
meta_source="/Users/jsheunis/Documents/psyinf/datalad-catalog/super_metadata"
file_meta="$meta_source/files/$SUBDS_NAME.json"
dataset_meta="$meta_source/dataset/submeta_$SUBDS_NAME.json"
arr=$(tail -n +2 $file_meta | sed '$d' | sed 's/.$//')
new_arr=$(cat $dataset_meta $arr)
datalad catalog -o "/Users/jsheunis/Documents/archived_catalog" -a $new_arr