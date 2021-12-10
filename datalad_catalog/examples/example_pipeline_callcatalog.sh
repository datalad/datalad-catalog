#!/bin/zsh

# This script ...
catalog_dir="/Users/jsheunis/Documents/archived-catalog"
meta_source="/Users/jsheunis/Documents/psyinf/datalad-catalog/super_metadata"
filedir="$meta_source/files"
for filename in $filedir/*.json; do
    echo "$filename"
    filebase=$(basename -- "$filename")
    dataset_meta="$meta_source/dataset/submeta_$filebase"

    sed '$d' $filename | sed '$s/$/,/' > temp_meta.json
    while read p; do
      echo $p | sed 's/$/,/' >> temp_meta.json
    done <$dataset_meta
    # Remove last comma
    sed -i '' '$ s/.$//' temp_meta.json
    # Add closing array bracket
    echo "]" >> temp_meta.json
    datalad catalog -f temp_meta.json -o $catalog_dir
    rm -rf temp_meta.json
done
super_meta="$meta_source/dataset/supermeta.json"
datalad catalog -f $super_meta -o $catalog_dir -s
# datalad catalog -f /Users/jsheunis/Documents/psyinf/datalad-catalog/super_metadata/dataset/supermeta.json -o /Users/jsheunis/Documents/archived-catalog -s 

# "5df8eb3a-95c5-11ea-b4b9-a0369f287950-dae38cf901995aace0dde5346515a0134f919523"

# SUBDS_NAME="Masterthesis_Barisch"

# file_meta="$meta_source/files/$SUBDS_NAME.json"
# dataset_meta="$meta_source/dataset/submeta_$SUBDS_NAME.json"
# arr=$(tail -n +2 $file_meta | sed '$d' | sed 's/.$//')
# new_arr=$(cat $dataset_meta $arr)
# datalad catalog -o "/Users/jsheunis/Documents/archived_catalog" -a $new_arr


# sed '$d' $file_meta | sed '$s/$/,/' > temp_meta.json
# while read p; do
#   echo $p | sed 's/$/,/' >> temp_meta.json
# done <$dataset_meta
# # Remove last comma
# sed -i '' '$ s/.$//' temp_meta.json
# # Add closing array bracket
# echo "]" >> temp_meta.json


# arr=$(tail -n +2 /Users/jsheunis/Documents/psyinf/datalad-catalog/super_metadata/file_test_operations.json | sed '$d' | sed 's/.$//')
# new_arr=$(cat /Users/jsheunis/Documents/psyinf/datalad-catalog/super_metadata/submeta_SCZ_Network_Pred.json $arr)


# datalad -f json meta-conduct "/Users/jsheunis/Documents/psyinf/datalad-catalog/datalad_catalog/examples/extract_file_metadata.json" \
#         traverser:"/Users/jsheunis/Documents/psyinf/Data/super" \
#         traverser:file \
#         traverser:False \
#         extractor:File \
#         extractor:metalad_core \
#         | jq '.["pipeline_element"]["result"]["metadata"][0]["metadata_record"]' \
#         | jq -c . | sed 's/$/,/' >> "supermeta_files.json"