#!/bin/zsh

echo "type"
echo "dataset" | jq .

echo "dataset_id"
cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '.dataset_id'

echo "dataset_version"
cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '.dataset_version'

echo "name"
cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '.extracted_metadata["@graph"][] | select(.["@type"] == "Dataset") | .name'

echo "description"
cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '.extracted_metadata["@graph"][] | select(.["@type"] == "Dataset") | .description'

echo "url"
cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '.extracted_metadata["@graph"][] | select(.["@type"] == "Dataset") | .url'

echo "authoridlist"
authoridlist=$(cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '.extracted_metadata["@graph"][] | select(.["@type"] == "Dataset") | .author')
echo "$authoridlist" | jq .

echo "authorlist"
authorlist=$(cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '.extracted_metadata["@graph"][] | select(.["@id"] == "#personList") | .["@list"]')
echo "$authorlist" | jq .

echo "combinedauthorlist"
newthing=$(cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '{"deets": .extracted_metadata["@graph"][] | select(.["@id"] == "#personList") | .["@list"], "ids": .extracted_metadata["@graph"][] | select(.["@type"] == "Dataset") | .author}')
echo "$newthing" | jq .

echo "authors"
echo "$newthing" | jq '. as $parent | [.ids[]["@id"] as $idin | ($parent.deets[] | select(.["@id"] == $idin))]'
# echo "$newthing" | jq '. as $parent | .deets[] | select(.["@id"] == ($parent.ids[]["@id"]))'

echo "keywords"
cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '.extracted_metadata["@graph"][] | select(.["@type"] == "Dataset") | .keywords'

echo "funding"
cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '.extracted_metadata["@graph"][] | select(.["@type"] == "Dataset") | [.funder[] | {"name": .name, "identifier": "", "description": ""}]'


echo "pubslist"
pubslist=$(cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '.extracted_metadata["@graph"][] | select(.["@id"] == "#publicationList") | .["@list"]')
echo "$pubslist" | jq .

echo "pubsanddeets"
pubsanddeets=$(cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '{"deets": .extracted_metadata["@graph"][] | select(.["@id"] == "#personList") | .["@list"], "pubs": .extracted_metadata["@graph"][] | select(.["@id"] == "#publicationList") | .["@list"]}')
echo "$pubsanddeets" | jq .

echo "publications"
echo "$pubsanddeets" | jq '. as $parent | [.pubs[] as $pubin | {"type":$pubin["@type"], "title":$pubin["headline"], "doi":$pubin["sameAs"], "datePublished":$pubin["datePublished"], "publicationOutlet":$pubin["publication"]["name"], "authors": ([$pubin.author[]["@id"] as $idin | ($parent.deets[] | select(.["@id"] == $idin))])}]                                                           '


echo "extractors_used"
cat datalad_catalog/tests/data/metadata_studyminimeta.json | \
jq '[{"extractor_name": .extractor_name, "extractor_version": .extractor_version, "extraction_parameter": .extraction_parameter, "extraction_time": .extraction_time, "agent_name": .agent_name, "agent_email": .agent_email,}]'

# {
#     "type": "dataset",
#     "dataset_id":"",
#     "dataset_version":"",
#     "name": "",
#     "short_name": "",
#     "description": "",
#     "doi": "",
#     "url": "",
#     "license": {
#       "name": "",
#       "url": ""
#     },
#     "authors": [
#         {
#             "name":"",
#             "givenName":"",
#             "familyName":"",
#             "email":"",
#             "honorificSuffix":"",
#             "identifiers":[
#                 "type": "",
#                 "identifier": ""
#             ],
#         }
#     ],
#     "keywords": [""],
#     "funding": [
#         {
#             "name":"",
#             "grant":"",
#             "description":""
#         }
#     ],
#     "publications": [
#         {
#             "type":"",
#             "title":"",
#             "doi":"",
#             "datePublished":"",
#             "publicationOutlet":"",
#             "authors":[
#                 {
#                     "name":"",
#                     "givenName":"",
#                     "familyName":"",
#                     "email":"",
#                     "honorificSuffix":"",
#                     "identifiers":[
#                         "type": "",
#                         "identifier": ""
#                     ],
#                 }
#             ],
#         }
#     ],
#     "subdatasets": [
#         {
            # "dataset_id":"",
            # "dataset_version":"",
            # "dataset_path": "",
            # "dirs_from_path": []
#         }
#     ],
#     "children": [
#         {

#         }
#     ],
#     "extractors_used": [
#         {
#             "extractor_name": "",
#             "extractor_version": "",
#             "extraction_parameter": {},
#             "extraction_time": 0,
#             "agent_name": "",
#             "agent_email": "",
#         }
#     ]
# }