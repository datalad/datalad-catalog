#!/bin/zsh
# This script ...
# Example usage:
# >>
# ASSIGN CORE VARIABLES FROM ARGUMENTS
BASEDIR=$(dirname "$0")
INPUT_META=$1

# EXTRACT TOP-LEVEL VARIABLES USING JQ
METADATA=$(cat $INPUT_META | jq .)
# echo "$METADATA"
EXTRACTED=$(cat $INPUT_META | jq '.extracted_metadata')

# EXTRACT PROPERTIES USING JQ
# type
type=$(echo "$METADATA" | jq .type )
# dataset_id
dataset_id=$(echo "$METADATA" | jq .dataset_id )
# dataset_version
dataset_version=$(echo "$METADATA" | jq .dataset_version )
# name
name=$(echo "$EXTRACTED" | jq .Name )
# short_name
short_name=""
# description(.tags | join(","))
description=$(echo "$EXTRACTED" | jq '.description | join("\n\n")' )
# doi
doi=""
# url
url=""
# license
license=$(echo "$EXTRACTED" | jq '{ "name": .License, "url": ""}' )
# authors
authors=$(echo "$EXTRACTED" | jq '[.Authors[] as $auth | {"name": $auth, "givenName":"", "familyName":"", "email":"", "honorificSuffix":"", "identifiers":[]}]' )
# keywords
keywords=$(echo "$EXTRACTED" | jq '. as $parent | .entities.task + .variables.dataset')
# funding
funding=$(echo "$EXTRACTED" | jq '[.Funding[] as $fund | {"name": "", "grant":"", "description":$fund}]' )
# publications
publications="[]"
# subdatasets
subdatasets="[]"
# children
children="[]"
# extractors_used
extractors_used=$(echo "$METADATA" | jq '[{"extractor_name": .extractor_name, "extractor_version": .extractor_version, "extraction_parameter": .extraction_parameter, "extraction_time": .extraction_time, "agent_name": .agent_name, "agent_email": .agent_email}]')
# additional_display
additional_display=$(echo "$EXTRACTED" | jq '[{"name": "BIDS", "content": .entities}]' )
# top_content
top_display=$(echo "$EXTRACTED" | jq '[{"name": "Subjects", "value": (.entities.subject | length)}, {"name": "Sessions", "value": (.entities.session | length)}, {"name": "Tasks", "value": (.entities.task | length)}, {"name": "Runs", "value": (.entities.run | length)}]' )


# ADD EXTRACTED PROPERTIES TO A SINGLE OUTPUT OBJECT, WRITE TO FILE
final=$(jq -n --argjson type "$type" \
--argjson dataset_id $dataset_id \
--argjson dataset_version "$dataset_version" \
--argjson name "$name" \
--arg short_name "$short_name" \
--argjson description "$description" \
--arg doi "$doi" \
--arg url "$url" \
--argjson license "$license" \
--argjson authors "$authors" \
--argjson keywords "$keywords" \
--argjson funding "$funding" \
--argjson publications $publications \
--argjson subdatasets $subdatasets \
--argjson children $children \
--argjson extractors_used $extractors_used \
--argjson additional_display $additional_display \
--argjson top_display $top_display \
'$ARGS.named'
)
echo $final > testy.json