## Pseudocode for metadata entry

- User clicks to enter metadata for a given schema: addMetadata(schema)
- First resolve the schema to get any referenced schemas into a single object: resolveSchemaNew(schema)
- Then parse the 1st level:
    - form_config = parseSchema(name, resolved_schema, null, [])
