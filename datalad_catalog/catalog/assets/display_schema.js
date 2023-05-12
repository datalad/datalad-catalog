/**************/
// Components //
/**************/

var input_count = 1

const dataset_schema_file = "./assets/jsonschema_dataset.json";
const authors_schema_file = "./assets/jsonschema_authors.json";
const file_schema_file = "./assets/jsonschema_file.json";
const sources_schema_file = "./assets/jsonschema_metadata_sources.json";
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
  "jsonschema_metadata_sources": sources_schema_file,
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

// SCHEMA-ITEM FOR RENDERING
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


// SCHEMA-FORM: FOR ENTERING AND DOWNLOADING/SAVING METADATA
Vue.component("schema-form", {
  template: "#form-template",
  props: [
    'title',
    'form_config',
    'toplevel',
  ],
  data: function () {
    return {
      form_data_tmp: null
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
      // if (this.toplevel) {
        // Download data
        // downloadObjectAsJson(this.form, 'dataset_metadata.json')
      var data = {}
      for (var f=0; f<this.form_config.children.length; f++) {
        child = this.form_config.children[f]
        // child_val_init = child.value
        data[child.form_field] = child.value
        // child.value = child_val_init
      }
      // console.log(data)
      this.$root.$emit('formSaved', {formatted_data: data, form_data: this.form_data_tmp})
      // } 
      // else {
      //   var data = {}
      //   for (var f=0; f<this.form_data_tmp.children.length; f++) {
      //     child = this.form_data_tmp.children[f]
      //     data[child.form_field] = child.value
      //   }
      //   console.log(data)
      //   this.$root.$emit('formSaved', {formatted_data: data, form_data: this.form_data_tmp})
      // } 
    },
    onReset(event) {
      event.preventDefault()
      if (this.toplevel) {
        // Reset main schema
      } else {
        for (var f=0; f<this.form_data_tmp.children.length; f++) {
          child = this.form_data_tmp.children[f]
          child.value = null
          // TODO: is recursion necessary here???
        }
      } 
    },
    onCancel(event) {
      console.log(event)
      console.log(event.target)
      console.log(this.$refs)
      console.log(this.$parent)
      console.log(this.$parent.$refs)
      console.log(this.$parent.$parent)
      console.log(this.$parent.$parent.$refs)
      console.log(this.$parent.$parent.$parent)
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
    }
  },
  created() {
    this.form_data_tmp = Vue.util.extend({}, this.form_config)
  },
})



// T-INPUT: SINGLE INPUT ITEM FOR ENTERING METADATA INTO A SCHEMA-FORM
// (could in turn contain another schema-form)
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
    // saveItem() {
    //   if (this.edit_existing) {
    //     this.obj.value[this.edit_index] = JSON.parse(JSON.stringify(this.edited_item))
    //   }
    //   else {
    //     this.obj.value.push(this.edited_item)
    //   }
    //   this.edited_item = {}
    //   this.edit_existing = null
    //   this.edit_index = null
    //   this.$refs['itemtable'].refresh()
    // }
    bleh(data) {
      console.log("Receive input:")
      console.log(data)
    },
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
    mainVueData(data) {
      console.log(data)
    },
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
      // 1 - resolve the schema
      var resolved_schema = resolveSchemaNew(schema, this.schemas_json);
      // 2 - parse schema and transform into renderable objects
      var name = schema.title
      this.form_config = parseSchema(name, resolved_schema, [])
      // 3 - if dataset schema, preset defaults
      var child
      if (this.form_config["form_field"] == "dataset") {
        child = this.findChild(this.form_config, "form_field", "type")
        child.value = "dataset";
        child.disabled = true
        child = this.findChild(this.form_config, "form_field", "dataset_id")
        child.value = randomUUID();
        child.disabled = true
        child = this.findChild(this.form_config, "form_field", "dataset_version")
        child.value = randomVersion();
        child.disabled = true
      }
      // 4 - if file schema, preset defaults
      if (this.form_config["form_field"] == "file") {
        child = this.findChild(this.form_config, "form_field", "type")
        child.value = "file";
        child.disabled = true
      }
      this.show_form = true;
    },
    getResolvedSchema(schema) {
      var resolved_schema = resolveSchemaNew(schema, this.schemas_json);
      var name =  schema.title
      var form_config = parseSchema(name, resolved_schema, [])
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
        twitter: "https://twitter.com/datalad",
      };
      if (dest in destinations) {
        window.open(destinations[dest]);
      } else {
        window.open(dest);
      }
    },
    findChild(input_object, key, value, recurse = false) {
      if (!input_object.children) {
        return null
      }
      filtered_children = input_object.children.filter(
        (obj) => {
            return obj[key] == value
        }
      );
      if (filtered_children && filtered_children.length > 0) {
        console.log(filtered_children[0])
        return filtered_children[0]
      }
      else if (recurse) {
        for (var x=0; x<input_object.children.length; x++) {
          child = input_object.children[x]
          found_child = this.findChild(child, key, value, true)
          if (found_child) {return found_child} else {continue}
        }
        return null
      }
      else {
        return null
      }
    }

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
  mounted() {
    // Set function that handles emitted data from (recursive) form submission
    this.$on('formSaved', (data) => {
      console.log('Emitted data:')
      console.log(data)
      var formatted_data = data.formatted_data
      var form_data = data.form_data  
      var key_to_match = "input_id"
      console.log('Now searching for object with ' + key_to_match + ' == ' + form_data[key_to_match])
      edited_child = this.findChild(this.form_config, key_to_match, form_data[key_to_match], true)
      console.log("edited_child")
      console.log(edited_child)
      console.log("type")
      type_array = edited_child["type"]
      console.log(type_array)
      console.log("value")
      console.log(edited_child.value)

      
      if (type_array.includes(ARRAY)) {
        edited_child.value.push(formatted_data)
        //
      }
      else if (type_array.includes(OBJECT)) {
        formatted_keys = Object.keys(formatted_data)
        for (var k=0; k<formatted_keys.length; k++) {
          key = formatted_keys[k]

          indiv_child = this.findChild(edited_child, "form_field", key)
          indiv_child.value = formatted_data[key]
        }
      }
      else {
        //
      }
      
      // this.form_config.children[7].value.push("some_url")
    })
  },
});



function randomUUID() {
  return crypto.randomUUID()
}

function randomVersion() {
  var parts = randomUUID().split('-')
  var filler = randomString(4)
  var version = ''
  for (var p=0; p<parts.length; p++) {
    if (p == parts.length-1) {
      version = version.concat(parts[p])
    } else {
      version = version.concat(parts[p]).concat(filler.charAt(p))
    }
  }
  return version
}

function randomString(length = 40) {
  const chars = '0123456789abcdefghijklmnopqrstuvwxyz'
  var result = '';
  for (var i = length; i > 0; --i) result += chars[Math.floor(Math.random() * chars.length)];
  return result;
}

function setDatasetSchemaDefaults() {

}


/**
 * Parse the incoming schema and transform it into data that can be rendered
 * in the metadata entry form. A schema could also be a single property.
 * @param {string} name - The name of the incoming schema
 * @param {Object} schema The incoming schema
 * @param {Array} required=[] - An array of required properties of the incoming schema
 * @returns {}
 */

function parseSchema(name, schema, required = []) {

  // console.log("parseschema called...")
  // assume schema has already been resolved

  // Schema should be an object
  // if (!isObject(schema)) {
  //   console.log("ERROR: schema should be an object")
  //   return false
  // }
  // If schema has no type, cannot add metadata (ignore allOf etc for now... TODO)
  // console.log(schema)
  if (!(TYPE in schema)) {
    console.error("ERROR: schema has no 'type' or '$ref' at the top level and cannot be parsed")
    return false
  }

  // Initialize item to be rendered
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
    disabled: false,
    validations: [],
    children: [],
  }
  // Write standard JSONschema keywords and annotations to item
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
    // Set input type of item, this determines how the item will render
    // (e.g. text/number input, object input, array input)
    // If there are multiple input types, set to ""
    item.input_type = Array.isArray(tp) ? "" : TYPE_MAP[tp]
    if (allInArray(type_array, TYPES)) {
      // lets assume hierarchy for now (array -> object -> others),
      // need to deal with multiple types per item later: TODO
      if (type_array.includes(ARRAY)) {
        item.input_type = "array"
        item.value = []
        if (ITEMS in schema ) {
          input_count++
          vv = input_count
          arr_item = parseSchema(name, schema.items, schema[REQUIRED])

          console.log('Array item: ' + vv.toString())
          item.children.push(arr_item)
        } else {
          // TODO: this is why description has no buttons, i think
        }
      }
      else if (type_array.includes(OBJECT) && PROPERTIES in schema) {
        item.input_type = "object"
        for (prop in schema[PROPERTIES]) {
          input_count++
          pp = input_count
          prop_item = parseSchema(prop, schema[PROPERTIES][prop], schema[REQUIRED])
          console.log('Object item prop: ' + pp.toString())
          item.children.push(prop_item)
        }
      }
    } else {
      console.log("ERROR: type '" + type_array + "' not supported by jsonschema draft 2020-12" )
    }
  } else {
    // TODO: handle cases such as allof and whatever else!!!
    console.error("ERROR: keyword 'type' not in schema")
    return false
  }

  return item
}

// function randomString(size = 40) {  
//   return Crypto.randomBytes(size)
//     .toString('hex')
//     .slice(0, size)
// }


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


/**
 * Check if all elements of a smaller sized array are included in a larger-sized array
 * @param {Array} small_array - The array whose elements are tested
 * @param {Array} big_array - The array to test against
 * @returns {boolean} - True if all elements of small_array are included in big_array
 */
function allInArray(small_array, big_array) {
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

