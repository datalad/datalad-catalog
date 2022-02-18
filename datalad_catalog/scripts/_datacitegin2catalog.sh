#!/bin/zsh
# This script ...
# Example usage:
# >>
# ASSIGN CORE VARIABLES FROM ARGUMENTS
BASEDIR=$(dirname "$0")
INPUT_META=$1

# EXTRACT TOP-LEVEL VARIABLES USING JQ
METADATA=$(cat $INPUT_META | jq .)
GRAPH=$(cat $INPUT_META | jq '.extracted_metadata["@graph"]')

# EXTRACT PROPERTIES USING JQ
# type
type=$(echo "$METADATA" | jq .type )
# dataset_id
dataset_id=$(echo "$METADATA" | jq .dataset_id )
# dataset_version
dataset_version=$(echo "$METADATA" | jq .dataset_version )
# name
name=""
# short_name
short_name=""
# description
description=""
# doi
doi=""
# url
url=$(echo "$GRAPH" | jq '.[] | select(.["@type"] == "Dataset") | .distribution[] | select(has("url")) | .url' )
# license
license="{}"
# authors
authors=$(echo  "$GRAPH" | jq '[.[] | select(.["@type"]=="agent")] | map(del(.["@id"], .["@type"]))' )
# keywords
keywords="[]"
# funding
funding="[]"
# publications
publications="[]"
# subdatasets
subdatasets=$(echo "$GRAPH" | jq '.[] | select(.["@type"] == "Dataset") | [.hasPart[] | {"dataset_id": (.identifier | sub("^datalad:"; "")), "dataset_version": (.["@id"] | sub("^datalad:"; "")), "dataset_path": .name, "dirs_from_path": "[]"}]' )
# children
children="[]"
# extractors_used
extractors_used=$(echo "$METADATA" | jq '[{"extractor_name": .extractor_name, "extractor_version": .extractor_version, "extraction_parameter": .extraction_parameter, "extraction_time": .extraction_time, "agent_name": .agent_name, "agent_email": .agent_email,}]')

# ADD EXTRACTED PROPERTIES TO A SINGLE OUTPUT OBJECT, WRITE TO FILE
final=$(jq -n --argjson type "$type" \
--argjson dataset_id $dataset_id \
--argjson dataset_version "$dataset_version" \
--arg name "$name" \
--arg short_name "$short_name" \
--arg description "$description" \
--arg doi "$doi" \
--argjson url "$url" \
--argjson license "$license" \
--argjson authors "$authors" \
--argjson keywords "$keywords" \
--argjson funding "$funding" \
--argjson publications $publications \
--argjson subdatasets $subdatasets \
--argjson children $children \
--argjson extractors_used $extractors_used \
'$ARGS.named'
)
echo $final > testy.json