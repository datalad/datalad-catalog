/**************/
// Components //
/**************/

const dataset_schema_file = "./assets/jsonschema_dataset.json";
const authors_schema_file = "./assets/jsonschema_authors.json";
const file_schema_file = "./assets/jsonschema_file.json";
const sources_schema_file = "./assets/jsonschema__metadata_sources.json";
const catalog_schema_file = "./assets/jsonschema_catalog.json";

const TYPES =  [
  "string",
  "number",
  "integer",
  "object",
  "array",
  "boolean",
  "null",
]

const ARRAY = 'array'
const ID = '$id'
const ITEMS = 'items'
const NULL = null
const OBJECT = 'object'
const PROPERTIES = 'properties'
const REF = '$ref'
const REQUIRED = 'required'
const SCHEMA = '$schema'
const TYPE = 'type'


schema_files = {
  // "jsonschema_catalog": catalog_schema_file,
  "jsonschema_dataset": dataset_schema_file,
  "jsonschema_file": file_schema_file,
  "jsonschema_authors": authors_schema_file,
  "jsonschema__metadata_sources": sources_schema_file,
}

schema_keywords = ["$schema", "$id"]
instance_keywords = ["type"]
schema_annotations = ["title", "description", "default", "examples", "readOnly", "writeOnly", "deprecated"]
additional_schema_keywords = ["$ref", "$defs"]
// validation_keywords = ["properties", "additionalProperties", "required", "items", "multipleOf", "maximum", "minimum", "exclusiveMaximum", "exclusiveMinimum", "minItems", "maxItems", "uniqueItems"]
validation_keywords = {
  any: {
    // type
    enum: "array",
    const: "any",
    anyOf: "array",
    allOf: "array",
    oneOf: "array",
  },
  number: {
    multipleOf: "number",
    maximum: "number",
    minimum: "number",
    exclusiveMaximum: "number",
    exclusiveMinimum: "number",
  },
  integer: {
    multipleOf: "number",
    maximum: "number",
    minimum: "number",
    exclusiveMaximum: "number",
    exclusiveMinimum: "number",
  },
  string: {
    minLength: "integer",
    maxLength: "integer",
    pattern: "string",
    format: "string"
  },
  array: {
    minItems: "integer",
    maxItems: "integer",
    uniqueItems: "boolean",
    maxContains: "integer",
    minContains: "integer",
  },
  object: {
    maxProperties: "integer",
    minProperties: "integer",
    dependentRequired: "object",
  },
}

defaults = {
  schema_keywords: schema_keywords,
  instance_keywords: instance_keywords,
  schema_annotations: schema_annotations,
  additional_keywords: additional_schema_keywords,
  validation_keywords: validation_keywords,
}

format = [
  "date-time",
  "time",
  "date",
  "duration",
  "email",
  "idn-email",
  "hostname",
  "idn-hostname",
  "ipv4",
  "ipv6",
  "uuid",
  "uri",
  "uri-reference",
  "iri",
  "iri-reference",
  "uri-template",
  "json-pointer",
  "relative-json-pointer",
  "regex",
]

const INPUT_TYPES = [
  'text',
  'password',
  'email',
  'number',
  'url',
  'tel',
  'search',
  'date',
  'datetime',
  'datetime-local',
  'month',
  'week',
  'time',
  'range',
  'color'
]

const TYPE_MAP = {
  "string": "text",
  "number": "number",
  "integer": "number",
  "object": null,
  "array": null,
  "boolean": null,
  "null": null,
}

const FORMAT_MAP = {
  "date-time": "datetime",
  "time": "time",
  "date": "date",
  "duration": "time",
  "email": "email",
}

type_icons = {
  "string": "““",
  "number": ".5",
  "integer": "12",
  "object": "{}",
  "array": "[]",
  "boolean": "01",
  "null": "--",
  "$ref": "->",
}

type_colors = {
  "string": "#fd7e14", // orange
  "number": "#007bff", // blue
  "integer": "#28a745", // green
  "object": "#e83e8c", // pink
  "array": "#20c997", // teal
  "boolean": "#6610f2", // indigo
  "null": "#6f42c1", // purple
  "$ref": "#17a2b8" //  cyan
}




// COMPONENTS

// SCHEMA-ITEM
Vue.component("schema-item", {
  template: "#schema-item",
  props: [
    'name',
    'parent_name',
    'item',
    'defaults',
    'requireditems',
    'isschema',
    'schemas_json'
  ],
  data: function () {
    return {
      type_icons: type_icons,
      type_colors: type_colors,
    }
  },
  computed: {
    hasvalidations() {
      var i = 0, type_arr, key_arr;
      if ('type' in this.item) {
        type_arr = Array.isArray(this.item.type) ? this.item.type : [this.item.type]
        for (var tp=0; tp<type_arr.length; tp++) {
          key_arr = Object.keys(this.defaults.validation_keywords[type_arr[tp]])
          for (var kw=0; kw<key_arr.length; kw++) {
            if (key_arr[kw] in this.item) {
              i+=1;
            }
          }
        }
        any_arr = Object.keys(this.defaults.validation_keywords.any)
        for (var kw=0; kw<any_arr.length; kw++) {
          if (any_arr[kw] in this.item) {
            i+=1;
          }
        }
      }
      return (i > 0 ? true : false)
    }
  },
  methods: {
  },
})


// T-INPUT
Vue.component("t-input", {
  template: "#input-template",
  data: function () {
    return {
      inputTypes: INPUT_TYPES,
      edited_item: {},
      edit_existing: null,
      edit_index: null,
    }
  },
  props: [
    'obj',
    'i',
  ],
  methods: {
    removeItemModal(idx) {
      this.$bvModal.msgBoxConfirm('This will delete the row from your metadata, are you sure you want to continue?.', {
        title: 'Please Confirm',
        size: 'sm',
        buttonSize: 'sm',
        okVariant: 'danger',
        okTitle: 'DELETE',
        cancelTitle: 'Cancel',
        footerClass: 'p-2',
        hideHeaderClose: true,
        centered: true
      })
        .then(value => {
          if (value) {
            this.obj.value.splice(idx, 1)
          }
        })
        .catch(err => {
          // An error occurred
        })
    },
    addItemModal(idx) {
      this.edited_item = {}
      this.edit_existing = false
      // if (Number.isFinite(idx)) {
      //   this.edit_index = idx
      //   this.edit_existing = true
      //   this.edited_item = JSON.parse(JSON.stringify(this.obj.value[idx]))
      // }
      // else {
      //   key_list = def.fields.map(f => 
      //     this.edited_item[f.name] = "")
      // }
      this.$refs['additem'].show()
    },
    closeItemModal() {
      this.$refs['additem'].hide()
    },
    saveItem() {
      if (this.edit_existing) {
        this.obj.value[this.edit_index] = JSON.parse(JSON.stringify(this.edited_item))
      }
      else {
        this.obj.value.push(this.edited_item)
      }
      this.edited_item = {}
      this.edit_existing = null
      this.edit_index = null
      this.$refs['itemtable'].refresh()
    }

  },
  computed: {
    array_fields() {
      // Return fields belonging to a single item in an array
      // Fields could be standalone, or could derive from an object
      if (this.obj.input_type == ARRAY) {
        if (this.obj.children[0]) {
          if (this.obj.children[0].input_type == OBJECT) {
            fields = this.obj.children[0].children.map(f => f.form_field)
          } else {
            fields = [this.obj.children[0].form_field]
          }
        } else {
          fields = [this.obj.form_field]
        }
        fields.forEach(function(el, idx, arr) {
          arr[idx] = {key: el};
          arr[idx].thStyle = { fontWeight: 'normal', fontStyle: 'italic'}
        });

        aa = fields.concat([{ key: 'opts', label: 'Options', thStyle: { fontWeight: 'normal', fontStyle: 'italic'}}])
        console.log(aa)
        return aa
      }
      return null
    },

    input_label() {
      return makeReadable(this.obj.label)
    }

    // state() {
    //   return this.obj.value.length == 4
    // },
    // invalidFeedback() {
    //   if (this.obj.value.length > 0) {
    //     return 'Enter at least 4 characters.'
    //   }
    //   return 'Please enter something.'
    // }
  },
})


// SCHEMA-FORM
Vue.component("schema-form", {
  template: "#form-template",
  props: [
    'title',
    'form_config',
    'toplevel',
  ],
  data: function () {
    return {
    }
  },
  computed: {
    form_data() {
      var dat = {}
      var fields = this.form_config.children
      for (var i=0; i<fields.length; i++) {
        var f = fields[i]
        switch (f.input_type) {
          case 'array':
            dat[f.form_field] = [];
            break;
          case 'object':
            dat[f.form_field] = {};
            break;
          case 'text':
            dat[f.form_field] = '';
            break;
          default:
            dat[f.form_field] = null;
        }
      }
      return dat
    }
  },
  methods: {
    onSubmit(event) {
      event.preventDefault()
      // downloadObjectAsJson(this.form, 'dataset_metadata.json')
    },
    onReset(event) {
      event.preventDefault()
      // // Reset our form values
      // this.form.name = '',
      // this.form.description = '',
      // this.form.url = '',
      // this.form.doi = '',
      // // Trick to reset/clear native browser form validation state
      // this.show = false
      // this.$nextTick(() => {
      //   this.show = true
      // })
    },
    onCancel(event) {
      console.log(event)
      console.log(event.target)
      console.log(this.$refs)
      console.log(this.$parent.$refs)
      console.log(this.$parent.$parent.$refs)
      console.log(this.$parent.$parent.$parent.$refs)
      // console.log()
      // console.log(this.$refs)
      if (!this.toplevel) {
        // console.log(this.$refs.forminput[0].$refs.additem)
        // this.$refs.forminput.length
        // this.$parent.$parent.hide()
        
        // this.$refs['additem'].hide()
      }
      // event.preventDefault()
    },
  },
})


/***********/
// Vue app //
/***********/

// Start Vue instance
var form_app = new Vue({
  el: "#vue_app",
  data: {
    schema_files: schema_files,
    schemas_json: {},
    schema: {},
    schemas_ready: false,
    schema_selected: false,
    schema_name: "",
    defaults: defaults,
    searchText: "",
    headingText: "kaas",
    inputTypes: INPUT_TYPES,
    show_form: false,
    form_config: {},
  },
  methods: {
    onSubmit(event) {
      event.preventDefault()
      // downloadObjectAsJson(this.form, 'dataset_metadata.json')
    },
    onReset(event) {
      event.preventDefault()
      // // Reset our form values
      // this.form.name = '',
      // this.form.description = '',
      // this.form.url = '',
      // this.form.doi = '',
      // // Trick to reset/clear native browser form validation state
      // this.show = false
      // this.$nextTick(() => {
      //   this.show = true
      // })
    },
    selectSchema(s) {
      // this.schema_selected = false;
      this.schema_name = s;
      this.schema = this.schemas_json[s];
      this.show_form = false;
      // this.schema_selected = true;
    },
    selectRefSchema(ref_id) {
      filtered_schemas = Object.values(this.schemas_json).filter(
        (obj) => {
          if ('$id' in obj) {
            return obj['$id'].toLowerCase().indexOf(ref_id.toLowerCase()) >= 0
          }
        }
      );
      if (Array.isArray(filtered_schemas)) {
        this.schema = filtered_schemas[0]
      }
    },
    addMetadata(schema) {
      var resolved_schema = resolveSchemaNew(schema, this.schemas_json);
      var name =  schema.title
      this.form_config = parseSchema(name, resolved_schema, null, [])
      this.show_form = true;
    },
    getResolvedSchema(schema) {
      var resolved_schema = resolveSchemaNew(schema, this.schemas_json);
      var name =  schema.title
      var form_config = parseSchema(name, resolved_schema, null, [])
      downloadObjectAsJson(resolved_schema, 'resolved_schema')
      downloadObjectAsJson(form_config, 'form_config')

    },
    gotoHome() {
      router.push({ name: "home" });
    },
    gotoAbout() {
      router.push({ name: "about" });
    },
    gotoExternal(dest) {
      const destinations = {
        github:
          "https://github.com/datalad/datalad-catalog",
        docs: "https://docs.datalad.org/projects/catalog/en/latest/",
        mastodon: "https://fosstodon.org/@datalad",
        x: "https://x.com/datalad"
      };
      if (dest in destinations) {
        window.open(destinations[dest]);
      } else {
        window.open(dest);
      }
    },

  },
  beforeCreate() {
    schemas_json = {}
    schema = {}
    this.schemas_ready = false;
    Promise.all(
      Object.keys(schema_files).map((key, index) => {
        url = schema_files[key]
        fetch(url)
        .then((response) => {
          if (response.ok) {
            return response.json();
          } else {
            console.log(
              "WARNING: schema file could not be loaded:" + schema_files[key]
            );
          }
        })
        .then((responseJson) => {
          obj = responseJson;
          this.schemas_json[key] = obj;
          if (index == 0) {
            this.schema = obj
            this.schema_name = key;
          }
        })
        .catch((error) => {
          console.log("Schema file error:");
          console.log(error);
        });
      })
    ).then(() => {
        this.schemas_ready = true
        console.log(this.schemas_json)
      }
    )
  },
});


function parseSchema(name, schema, input_count = null, required = []) {

  console.log("parseschema called...")
  // assume schema has already been resolved

  // Schema should be an object
  // if (!isObject(schema)) {
  //   console.log("ERROR: schema should be an object")
  //   return false
  // }
  // If schema has no type, cannot add metadata (ignore allOf etc for now... TODO)
  console.log(schema)
  if (!(TYPE in schema)) {
    console.log("ERROR: schema has no 'type' or '$ref' at the top level and cannot be parsed")
    return false
  }

  // input count
  if (!input_count) {
    input_count = 1;
  } else {
    input_count++;
  }

  // initialise
  var item = {
    description: schema.description ? schema.description: "",
    input_id: "input-" + input_count.toString(), //"input-1"
    input_group_id: "input-group-" + input_count.toString(), // "input-group-x",
    label: schema.title ? schema.title: name,
    required: required.indexOf(name) >= 0 ? true : false,
    form_field: name, //"description"
    placeholder: "",  // "placeholder1"
    input_type: "", // 
    type: null,
    value: null,
    validations: [],
    children: [],
  }

  schema_keywords.concat(schema_annotations).forEach(
    kw => {
      if (kw in schema) {
        item[kw] = schema[kw]
      }
    }
  );
  // Make sure type keyword exists, then parse
  if (TYPE in schema) {
    tp = schema[TYPE]
    // type could be an array or a string -> turn all into array
    var type_array = Array.isArray(tp) ? tp : [tp]
    item.type = type_array
    item.input_type = Array.isArray(tp) ? "" : TYPE_MAP[tp]
    if (allInArray(type_array, TYPES)) {
      // lets assume hierarchy for now (array -> object -> others),
      // need to deal with multiple types per item later: TODO
      if (type_array.includes(ARRAY)) {
        item.input_type = "array"
        item.value = []
        if (ITEMS in schema ) {
          input_count++
          arr_item = parseSchema(name, schema.items, input_count, schema[REQUIRED])
          item.children.push(arr_item)
        }
        // addObjectToArray(arr_item, item.children, 'form_field')
      }
      if (type_array.includes(OBJECT) && PROPERTIES in schema) {
        item.input_type = "object"
        for (prop in schema[PROPERTIES]) {
          input_count++
          prop_item = parseSchema(prop, schema[PROPERTIES][prop], input_count, schema[REQUIRED])
          item.children.push(prop_item)
          // addObjectToArray(prop_item, item.children, 'form_field')
        }
      }
      
    } else {
      console.log("ERROR: type '" + type_array + "' not supported by jsonschema draft 2020-12" )
    }
  } else {
    // TODO: handle cases such as allof and whatever else!!!
    console.log("ERROR: keyword 'type' not in schema")
    return false
  }

  return item
}



function resolveSchemaNew(schema, available_schemas) {

  // prompt(JSON.stringify(schema, null, 2))

  var resolved_schema = structuredClone(schema)
  for (key in resolved_schema) {
    // console.log(key)
    if (key == REF) {
      resolved_schema = resolveSchemaItem(key, structuredClone(resolved_schema[key]), available_schemas)
    } else if (key == PROPERTIES || (key == ITEMS && resolved_schema[ITEMS].hasOwnProperty(PROPERTIES))) {
      resolved_schema[key] = resolveSchemaItem(key, structuredClone(resolved_schema[key]), available_schemas)
    } else {
      // console.log('doing nothing')
      continue
    }
  }
  return resolved_schema
}

function resolveSchemaItem(key, item, available_schemas) {
  // console.log()
  // console.log(item)

  if (key == REF) {
    // console.log('goint into ref: ' + item)
    ref_schema = findRefSchema(item, available_schemas)
    if (ref_schema) {
      item = resolveSchemaNew(structuredClone(ref_schema), available_schemas)
    }
  }
  
  if (key == PROPERTIES) {
    // console.log("going into properties:")
    // console.log(item)
    for (prop in item) {
      // console.log("property: " + prop)
      // console.log(item) 
      item[prop] = resolveSchemaNew(structuredClone(item[prop]), available_schemas)
    }
  }
  if (key == ITEMS ) {
    for (prop in item[PROPERTIES]) {
      item[PROPERTIES][prop] = resolveSchemaNew(structuredClone(item[PROPERTIES][prop]), available_schemas)
    }
  } else {
    // console.log('doing nothing')
  }
  return item
}


function isObject(x) {
  // Returns true if the argument is an object
  // console.log('x: ' + x + ';  x !== null: ' + (x !== null).toString() )
  // console.log('typeof x: ' + (typeof x).toString() + 'typeof x === object: ' + (typeof x === 'object').toString())
  // console.log('!isArray(x): ' + !Array.isArray(x))
  
  if ( typeof x === 'object' && !Array.isArray(x) && x !== null ) {
    return true
  } else {
    return false
  }
}


function findRefSchema(ref_id, available_schemas) {
  // Find a schema by id in the locally available schemas
  filtered_schemas = Object.values(available_schemas).filter(
    (obj) => {
      if ('$id' in obj) {
        return obj['$id'].toLowerCase().indexOf(ref_id.toLowerCase()) >= 0
      }
    }
  );
  if (Array.isArray(filtered_schemas)) {
    return filtered_schemas[0]
  } else {
    return false
  }
}


function objectInArray(prop, val, arr) {
  console.log('prop')
  console.log(prop)
  console.log('val')
  console.log(val)
  console.log('arr')
  console.log(arr)
  // Checks if an object already exists in an array
  var result = arr.find(obj => {
    return obj[prop] === val
  })

  if (typeof result !== 'undefined') {
    return result;
  } else {
    return null
  }
}

function addObjectToArray(obj, arr, prop_to_check) {
  // Adds an object to an array unless the object already exists in the array
  if (objectInArray(prop_to_check, obj[prop_to_check], arr)) {
    return arr
  } else {
    return arr.push(obj)
  }
}

function allInArray(small_array, big_array) {
  // return true if all elements of small_array are in big_array
  return small_array.every(el => big_array.includes(el))
}


function downloadObjectAsJson(obj, filename){
  var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(obj));
  var downloadAnchorNode = document.createElement('a');
  downloadAnchorNode.setAttribute("href",     dataStr);
  downloadAnchorNode.setAttribute("download", filename + ".json");
  document.body.appendChild(downloadAnchorNode);
  downloadAnchorNode.click();
  downloadAnchorNode.remove();
}


function makeReadable(input) {
  // capitalize first letter
  var output = input.charAt(0).toUpperCase() + input.slice(1)
  // Replace underscores and dashes with space
  output = output.replace(/_/g,' ');
  output = output.replace(/-/g,' ');
  return output
}

