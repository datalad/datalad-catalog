/**************/
// Components //
/**************/

const dataset_schema_file = "./assets/jsonschema_dataset.json";
const authors_schema_file = "./assets/jsonschema_authors.json";
const file_schema_file = "./assets/jsonschema_file.json";
const extractors_schema_file = "./assets/jsonschema_extractors.json";
const catalog_schema_file = "./assets/jsonschema_catalog.json";


schema_files = {
  "jsonschema_catalog": catalog_schema_file,
  "jsonschema_dataset": dataset_schema_file,
  "jsonschema_file": file_schema_file,
  "jsonschema_authors": authors_schema_file,
  "jsonschema_extractors": extractors_schema_file,
}

schema_keywords = ["$schema", "$id"]
instance_keywords = ["type"]
schema_annotations = ["title", "description", "default", "examples", "readOnly", "writeOnly", "deprecated"]
additional_schema_keywords = ["$ref", "$defs"]
validation_keywords = ["properties", "additionalProperties", "required", "items", "multipleOf", "maximum", "minimum", "exclusiveMaximum", "exclusiveMinimum", "minItems", "maxItems", "uniqueItems"]

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

// top_level_fields = {
//   "$schema": "string",
//   "$id": "string",
//   "$comment": "string",
//   "$ref": "string",
//   "type": ["string", "array"],
//   "title": "string",
//   "description": "string",
//   "default": "any",
//   "examples": "array",
//   "readOnly": "boolean",
//   "writeOnly": "boolean",
//   "deprecated": "boolean",
//   "enum": "array",
//   "const": "any",
//   "required": "array"
// }

const types =  [
  "string",
  "number",
  "integer",
  "object",
  "array",
  "boolean",
  "null",
]

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

defaults = {
  schema_keywords: schema_keywords,
  instance_keywords: instance_keywords,
  schema_annotations: schema_annotations,
  additional_keywords: additional_schema_keywords,
  validation_keywords: validation_keywords,
}

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

// required: red
// optional: orange

// $blue: #007bff !default;
// $indigo: #6610f2 !default;
// $purple: #6f42c1 !default;
// $pink: #e83e8c !default;
// $red: #dc3545 !default;
// $orange: #fd7e14 !default;
// $yellow: #ffc107 !default;
// $green: #28a745 !default;
// $teal: #20c997 !default;
// $cyan: #17a2b8 !default;



Vue.component("t-custom-input", {
  template: "#custom-input-template",
  props: [
    'value'
  ],
})

Vue.component("schema-item", {
  template: "#schema-item",
  props: [
    'name',
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
    selectRefSchema(ref_id) {

    }
  }
})


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
    'defs'
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
    addItemModal(idx, def) {
      this.edited_item = {}
      this.edit_existing = false
      if (Number.isFinite(idx)) {
        this.edit_index = idx
        this.edit_existing = true
        this.edited_item = JSON.parse(JSON.stringify(this.obj.value[idx]))
      }
      else {
        key_list = def.fields.map(f => 
          this.edited_item[f.name] = "")
      }
      this.$refs['additem'].show()
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
    state() {
      return this.obj.value.length == 4
    },
    // invalidFeedback() {
    //   if (this.obj.value.length > 0) {
    //     return 'Enter at least 4 characters.'
    //   }
    //   return 'Please enter something.'
    // }
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
    defaults: defaults,
    searchText: "",
    headingText: "kaas",
    inputTypes: INPUT_TYPES,
    inputData: [
      {
        description: "The name of your dataset",
        input_id: "input-2",
        input_group_id: "input-group-2",
        label: "Name",
        required: true,
        form_field: "name",
        placeholder: "placeholder2",
        input_type: "text",
        value: "",

      },
      {
        description: "The description of your dataset",
        input_id: "input-1",
        input_group_id: "input-group-1",
        label: "Description",
        required: true,
        form_field: "description",
        placeholder: "placeholder1",
        input_type: "textarea",
        value: "",
      },
      {
        description: "The URL of your dataset",
        input_id: "input-3",
        input_group_id: "input-group-3",
        label: "URL",
        required: false,
        form_field: "url",
        placeholder: "placeholder3",
        input_type: "url",
        value: "",
      },
      {
        description: "Dataset authors",
        input_id: "input-4",
        input_group_id: "input-group-4",
        label: "Authors",
        required: false,
        form_field: "authors",
        placeholder: "placeholder4",
        input_type: "array",
        value: [
          {
            name: "Stephan",
            lastname: "Heunis"
          },
          {
            name: "Stephan2",
            lastname: "Heunis2"
          },

        ],
        item_def: "author"
      }
    ],
    definitions: [
      {
        name: "author",
        fields: [
          {
            name: "name",
            type: String,
            required: true
          },
          {
            name: "lastname",
            type: String,
            required: true
          },

        ]
      },
      {
        name: "author2",
        fields: [
          {
            name: "name",
            type: String,
            required: true
          },
        ]
      }
    ],
    form: {
      name: "",
      description: "",
      url: "",
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
    selectSchema(s) {
      this.schema = this.schemas_json[s];
      console.log(this.schema)
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