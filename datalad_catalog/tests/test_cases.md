# WIP

## Create

`catalog create -c path`:

|State|Behaviour|
|--|--|
| nothing exists at path | should create new catalog with assets |
| directory already exists at path, directory is random dir | should give warning and not create catalog |
| directory already exists at path, directory is an existing catalog | should give warning and tip to use `--force` if overwrite is required |
|||
|||
|||

## Add