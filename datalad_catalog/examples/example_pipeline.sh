#!/bin/zsh

# This script runs on a datalad superdataset which has all subdatasets installed locally.
# Only recursive installation/cloning is required, obtaining files via `datalad get` is NOT necessary.
# The script requires a single parameter: absolute path to super-dataset
# Output files are written to current working directory (subds.txt, supersubmeta.json, and a json file per subdataset)
# Output files are in a format that's ingested by python scripts in datalad-catalog
# Example usage:
# >> cd /path/to/datalad-catalog
# >> datalad_catalog/examples/example_pipeline.sh /path/to/super-dataset

BASEDIR=$(dirname "$0")
SUPER=$1
echo "Super dataset:"
echo "      $SUPER"

# Get subdatsets, write to file, count
# TODO: this could possibly be replaced by a smarter git- or datalad-specific method
# TODO: write dataset paths to array
datalad subdatasets -d $SUPER > subds.txt
echo "Number of subdatasets:"
grep "subdataset(ok)" subds.txt | wc -l

# Get superdataset id and version (to add to file metadata for context in hierarchy)
# TODO: this could probably be replaced by: git config -f ${SUPER}/.datalad/config datalad.dataset.<id/version>
echo "Get superdataset metadata:"

SUPER_ID=$(datalad -f json meta-extract -d "$SUPER" metalad_core | jq -r '.["metadata_record"]["dataset_id"]')
SUPER_VERSION=$(datalad -f json meta-extract -d "$SUPER" metalad_core | jq -r '.["metadata_record"]["dataset_version"]')
echo "id: $SUPER_ID"
echo "version: $SUPER_VERSION"

# Use meta-conduct to traverse all datasets and extract+add+aggregate dataset-level metadata using 2 extractors
# TODO: in keeping with "not adding metadata to subdatasets", these could also just be written to file
# without adding to subdataset metadatastores.
echo "Extracting and adding all dataset-level metadata:"
datalad meta-conduct "$BASEDIR/extract_add_metadata.json" \
    traverser:"$SUPER" \
    traverser:dataset \
    traverser:True \
    extractor1:Dataset \
    extractor1:metalad_core \
    extractor2:Dataset \
    extractor2:metalad_studyminimeta \
    adder:True

# Write all dataset-level metadata to file
# TODO: add operations to turn this into a json array
echo "Dump dataset-level metadata:"
datalad meta-dump -d "$SUPER" -r "*" > supersubmeta.json

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
    echo "[" > "$SUBDS_NAME.json"
    # Extract file-level metadata, add context, add comma
    datalad -f json meta-conduct "$BASEDIR/extract_file_metadata.json" \
        traverser:"$LINE" \
        traverser:file \
        traverser:True \
        extractor:File \
        extractor:metalad_core \
        | jq '.["pipeline_element"]["result"]["metadata"][0]["metadata_record"]' \
        | jq --arg SUBDS_PATH "$SUBDS_PATH" --arg SUPER_ID $SUPER_ID --arg SUPER_VERSION $SUPER_VERSION \
        '. += {"dataset_path": $SUBDS_PATH, "root_dataset_id": $SUPER_ID, "root_dataset_version": $SUPER_VERSION}' | jq -c . | sed 's/$/,/' >> "$SUBDS_NAME.json"
    # Remove last comma
    sed -i '' '$ s/.$//' "$SUBDS_NAME.json"
    # Add closing array bracket
    echo "]" >> "$SUBDS_NAME.json"
    # TODO: perhaps filename should be hash of id and version, or related
  fi
done <subds.txt