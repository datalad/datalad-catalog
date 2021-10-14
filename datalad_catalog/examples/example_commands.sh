datalad meta-conduct pipelines/extract_metadata_auto \
traverser:/Users/jsheunis/Documents/psyinf/Data/sfdata_21sep/studyforrest-data/original/3T_multiresolution_fmri \
extractor:Dataset \
extractor:metalad_core_dataset



extractor:File \
extractor:file_info

```
datalad meta-conduct extract_metadata \
    traverser:/data/set1 \
    traverser:True # traverses down into subdatasets as well
    extractor1:Dataset \
    extractor1:metalad_studyminimeta \
    extractor2:Dataset \
    extractor2:metalad_core_dataset \
    adder:True # adds metadata to top-level dataset
```


datalad meta-conduct extract_metadata_pipeline_stephan \
    traverser:/Users/jsheunis/Documents/psyinf/Data/sfdata_21sep/studyforrest-data/original/3T_multiresolution_fmri \
    traverser:True # traverses down into subdatasets as well
    extractor1:Dataset \
    extractor1:metalad_studyminimeta \
    extractor2:Dataset \
    extractor2:metalad_core_dataset \
    extractor3:File \
    extractor3:file_info
    adder:True # adds metadata to top-level dataset

datalad meta-conduct datalad_metalad/pipelines/extract_metadata_pipeline_stephan.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/sfdata_21sep/studyforrest-data/original/3T_multiresolution_fmri \
    extractor1:Dataset \
    extractor1:metalad_studyminimeta \
    extractor2:Dataset \
    extractor2:metalad_core_dataset \
    extractor3:File \
    extractor3:metalad_core

datalad -f json meta-conduct datalad_metalad/pipelines/extract_metadata.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/sfdata_21sep/studyforrest-data/original/3T_multiresolution_fmri \
    extractor:Dataset \
    extractor:metalad_studyminimeta > data_3Tmulti_minimeta.json

datalad meta-conduct /Users/jsheunis/Documents/psyinf/datalad-metalad/datalad_metalad/pipelines/extract_metadata_pipeline.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/super \
    traverser:True \
    extractor:Dataset \
    extractor:metalad_core \
    adder:True


datalad meta-extract -d /Users/jsheunis/Documents/psyinf/Data/super/appliedml/scz_factors_subtypes_cla metalad_studyminimeta | datalad meta-add -d /Users/jsheunis/Documents/psyinf/Data/super/appliedml/scz_factors_subtypes_cla -


WORD1TOREMOVE="subdataset(ok): "
WORD2TOREMOVE=" (dataset)"
SUPER="/Users/jsheunis/Documents/psyinf/Data/super"
while read p; do
  koek="${p//$WORD1TOREMOVE/}"
  koek2="${koek//$WORD2TOREMOVE/}"
  koek3="/Users/jsheunis/Documents/psyinf/Data/super/$koek2"
  if [[ $koek3 == *":"* ]]; then
    echo "Skip line"
  else
    echo "$koek3"
    # datalad meta-extract -d "$koek3" metalad_core_dataset | datalad meta-add -d "$koek3" -
    datalad meta-aggregate -d "$super" "$koek3"
  fi
done <subds.txt

datalad meta-conduct /Users/jsheunis/Documents/psyinf/datalad-metalad/datalad_metalad/pipelines/extract_metadata_pipeline_stephan2.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/super \
    extractor1:Dataset \
    extractor1:metalad_core_dataset \
    adder1:True \
    extractor2:File \
    extractor2:metalad_core \
    adder2:True \
    extractor3:Dataset \
    extractor3:metalad_studyminimeta \
    adder3:True

datalad meta-conduct /Users/jsheunis/Documents/psyinf/datalad-metalad/datalad_metalad/pipelines/extract_metadata_pipeline.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/testsuper/super \
    traverser:dataset \
    traverser:True \
    extractor:Dataset \
    extractor:metalad_core \
    adder:True

datalad meta-aggregate -d /Users/jsheunis/Documents/psyinf/Data/super /Users/jsheunis/Documents/psyinf/Data/super/bneuro/connectome_network_CortexRev
datalad meta-dump -d /Users/jsheunis/Documents/psyinf/Data/super/bneuro/connectome_network_CortexRev -r "*"

datalad meta-extract -d original/3T_multiresolution_fmri metalad_core_dataset | datalad meta-add -d original/3T_multiresolution_fmri -
datalad meta-dump -d original/3T_multiresolution_fmri -r "*"
datalad meta-aggregate -d . original/3T_multiresolution_fmri

datalad meta-extract -d original/3T_multiresolution_fmri metalad_core participants.tsv | datalad meta-add -d original/3T_multiresolution_fmri -

datalad meta-conduct extract_metadata traverser:/dataset0 traverser:file traverser:True ...

datalad meta-conduct /Users/jsheunis/Documents/psyinf/datalad-metalad/datalad_metalad/pipelines/extract_metadata_pipeline.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/super \
    traverser:file \
    traverser:True \
    extractor:File \
    extractor:metalad_core \
    adder:True

datalad meta-conduct extract_add_metadata_pipeline.json \
    traverser:/data/set1 \
    traverser:dataset \
    traverser:True \
    extractor:Dataset \
    extractor:metalad_core \
    adder:True



datalad meta-conduct /Users/jsheunis/Documents/psyinf/datalad-catalog/datalad_catalog/examples/extract_file_metadata.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/super/simon/tahmasian_valk_2020 \
    traverser:file \
    traverser:True \
    extractor:File \
    extractor:metalad_core | jq .["pipeline_element"] | jq .['result']['metadata']

datalad -f json meta-conduct /Users/jsheunis/Documents/psyinf/datalad-catalog/datalad_catalog/examples/extract_file_metadata.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/super/bneuro/Masterthesis_Serbanescu \
    traverser:file \
    traverser:True \
    extractor:File \
    extractor:metalad_core | jq -c '.pipeline_element | fromjson' > testy.txt


datalad -f json meta-conduct /Users/jsheunis/Documents/psyinf/datalad-catalog/datalad_catalog/examples/extract_file_metadata.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/super/bneuro/Masterthesis_Serbanescu \
    traverser:file \
    traverser:True \
    extractor:File \
    extractor:metalad_core > testy.txt

datalad -f json meta-conduct /Users/jsheunis/Documents/psyinf/datalad-catalog/datalad_catalog/examples/extract_file_metadata.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/super/bneuro/Masterthesis_Serbanescu \
    traverser:file \
    traverser:True \
    extractor:File \
    extractor:metalad_core | sed "s/'/\"/g" | sed -e 's/^"//' -e 's/"$//' | jq -c '.pipeline_element | fromjson' > testy.txt


datalad -f json meta-extract -d /Users/jsheunis/Documents/psyinf/Data/super metalad_core
datalad -f json meta-extract -d /Users/jsheunis/Documents/psyinf/Data/super metalad_studyminimeta

datalad -f json meta-conduct /Users/jsheunis/Documents/psyinf/datalad-catalog/datalad_catalog/examples/extract_dataset_metadata.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/super/bneuro/Masterthesis_Serbanescu \
    traverser:dataset \
    extractor:Dataset \
    extractor:metalad_studyminimeta  > testmini.json


kaas=$(echo "{'type': 'PipelineElement', 'state': 'CONTINUE', 'result': {'path': PosixPath('/Users/jsheunis/Documents/psyinf/Data/super/bneuro/Masterthesis_Serbanescu/readme.docx'), 'dataset-traversal-record': [DatasetTraverseResult(state=<ResultState.SUCCESS: 'success'>, base_error=None, fs_base_path=PosixPath('/Users/jsheunis/Documents/psyinf/Data/super/bneuro/Masterthesis_Serbanescu'), type='File', dataset_path=PosixPath('.'), dataset_id='00e0c610-0f27-41bb-9626-157ec8815bfe', dataset_version='2648d3c53265c20cb790f44e677fbfc499ed1ca9', path=PosixPath('/Users/jsheunis/Documents/psyinf/Data/super/bneuro/Masterthesis_Serbanescu/readme.docx'), root_dataset_id=None, root_dataset_version=None, message='')], 'metadata': [MetadataExtractorResult(state=<ResultState.SUCCESS: 'success'>, base_error=None, path='/Users/jsheunis/Documents/psyinf/Data/super/bneuro/Masterthesis_Serbanescu/readme.docx', context=None, metadata_record={'type': 'file', 'dataset_id': UUID('00e0c610-0f27-41bb-9626-157ec8815bfe'), 'dataset_version': '2648d3c53265c20cb790f44e677fbfc499ed1ca9', 'path': MetadataPath('readme.docx'), 'extractor_name': 'metalad_core', 'extractor_version': '1', 'extraction_parameter': {}, 'extraction_time': 1634067078.255022, 'agent_name': 'Stephan Heunis', 'agent_email': 's.heunis@fz-juelich.de', 'extracted_metadata': {'@id': 'datalad:MD5E-s12060--9a9019561007e616e328cd15e87863a3.docx', 'contentbytesize': 12060}})]}}" | sed "s/'/\"/g" | sed -e 's/^"//' -e 's/"$//')


subds_path="bneuro/Masterthesis_Serbanescu"
datalad -f json meta-conduct /Users/jsheunis/Documents/psyinf/datalad-catalog/datalad_catalog/examples/extract_file_metadata.json \
    traverser:/Users/jsheunis/Documents/psyinf/Data/super/bneuro/Masterthesis_Serbanescu \
    traverser:file \
    traverser:True \
    extractor:File \
    extractor:metalad_core | jq '.["pipeline_element"]["result"]["metadata"][0]["metadata_record"]' | jq '. += {"dataset_path":"$subds_path", "root_dataset_id": "deabeb9b-7a37-4062-a1e0-8fcef7909609", "root_dataset_version": "0321dbde969d2f5d6b533e35b5c5c51ac0b15758"}'


{"root_dataset_id": "5df8eb3a-95c5-11ea-b4b9-a0369f287950", "root_dataset_version": "dae38cf901995aace0dde5346515a0134f919523", "dataset_path": "bneuro/Masterthesis_Serbanescu"

"root_dataset_id": "deabeb9b-7a37-4062-a1e0-8fcef7909609", "root_dataset_version": "0321dbde969d2f5d6b533e35b5c5c51ac0b15758", "dataset_path": "code/conversion_qa", "dataset_id": "0f66b1ba-e9a9-46fd-b9d9-2e64fe94d307", "dataset_version": "c74b66cf37c0d4ed8914296c6d7792b2d25696aa",