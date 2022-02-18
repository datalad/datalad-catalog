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
type="dataset"
# dataset_id
dataset_id=$(echo "$METADATA" | jq .dataset_id )
# dataset_version
dataset_version=$(echo "$METADATA" | jq .dataset_version )
# name
name=$(echo "$GRAPH" | jq '.[] | select(.["@type"] == "Dataset") | .name' )
# short_name
short_name=""
# description
description=$(echo "$GRAPH" | jq '.[] | select(.["@type"] == "Dataset") | .description' )
# doi
doi=""
# url
url=$(echo "$GRAPH" | jq '.[] | select(.["@type"] == "Dataset") | .url' )
# license
license="{}"
# authors
combinedpersonsids=$(echo "$GRAPH" | jq '{"authordetails": .[] | select(.["@id"] == "#personList") | .["@list"], "authorids": .[] | select(.["@type"] == "Dataset") | .author}' )
authors=$(echo "$combinedpersonsids" | jq '. as $parent | [.authorids[]["@id"] as $idin | ($parent.authordetails[] | select(.["@id"] == $idin))]' )
# keywords
keywords=$(echo "$GRAPH" | jq '.[] | select(.["@type"] == "Dataset") | .keywords' )
# funding
funding=$(echo "$GRAPH" | jq '.[] | select(.["@type"] == "Dataset") | [.funder[] | {"name": .name, "identifier": "", "description": ""}]' )
# publications
combinedpersonspubs=$(echo "$GRAPH" | jq '{"authordetails": .[] | select(.["@id"] == "#personList") | .["@list"], "publications": .[] | select(.["@id"] == "#publicationList") | .["@list"]}' )
publications=$(echo "$combinedpersonspubs" | jq '. as $parent | [.publications[] as $pubin | {"type":$pubin["@type"], "title":$pubin["headline"], "doi":$pubin["sameAs"], "datePublished":$pubin["datePublished"], "publicationOutlet":$pubin["publication"]["name"], "authors": ([$pubin.author[]["@id"] as $idin | ($parent.authordetails[] | select(.["@id"] == $idin))])}]')
# subdatasets
subdatasets="[]"
# children
children="[]"
# extractors_used
extractors_used=$(echo "$METADATA" | jq '[{"extractor_name": .extractor_name, "extractor_version": .extractor_version, "extraction_parameter": .extraction_parameter, "extraction_time": .extraction_time, "agent_name": .agent_name, "agent_email": .agent_email,}]')

# ADD EXTRACTED PROPERTIES TO A SINGLE OUTPUT OBJECT, WRITE TO FILE
final=$(jq -n --arg type "$type" \
--argjson dataset_id $dataset_id \
--argjson dataset_version "$dataset_version" \
--argjson name "$name" \
--arg short_name "$short_name" \
--argjson description "$description" \
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