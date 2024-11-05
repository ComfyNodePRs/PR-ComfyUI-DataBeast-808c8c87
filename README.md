# ComfyUI-DataBeast
This repository offers various nodes for data-driven processing in Comfy-UI.

## Notice:
* V1.0 First release.

## Installation

1. Clone the repository:
`git clone https://github.com/hanoixan/ComfyUI-DataBeast.git`
to your ComfyUI `custom_nodes` directory

## Nodes

### Conversion
**DBConvertToInt**
Params:
* input: any type
Returns:
* The integer representation if possible, 0 if not

**DBConvertToFloat**
Params:
* input: any type
Returns:
* The float representation if possible, 0.0 if not

**DBConvertToString**
Params:
* input: any type
* filesafe: If true, provide an ultra-shortened version of the full string that saves space and makes it useful for creating descriptive file names by removing vowels, removing non-alphanumeric characters, and appending a 4-hex hash when strings exceed 64 characters.
Returns:
* The string representation if possible, 0 if not

### General
**DBLoadData**
Load data from a .csv, .json, or .yml file. It will use the correct parser based on the file extension for .csv and .json. Any other extension will fall back to the 
.yml parser. This data can be accessed using Python dict and array expressions using DBGetValue and DBGetBatchList
For .csv files, all rows are represented in a list under the top key value 'items'. I.e., use `['items']` as your DBGetBatchList key.
Params:
* path: Path to file to load. .json and .csv are treated as their formats, anything else is interepreted as YAML.
* filter: Pattern filter. If exclusive is true, only include lines that DO NOT match this regex filter. If not exclusive, include ONLY lines that match this filter. 
  If using capture groups and not exclusive, all capture groups will be concatenated into the final text for that line. If empty, allow everything.
  * Ex: `([^#]+)#?` will match initial text until a #, and then ignore the rest. Everything in the capture group is retained.
  * Ex: If you want to embed data into another text file, create a unique prefix for the data lines, and use this filter to extract only those lines: 
    `[ \t]*mydata:(.*)` will filter everything after the `mydata:` prefix.
* exclusive: Exclude with pattern if true, retaining everything else. If false, include only lines with the filter regex pattern, if there is one.
Returns:
* DBItem referencing a dictionary of the entire file that was loaded. 

**DBGetValue**
Return the string representation of a simple value relative to the DBItem, using Python array access notation.
Params:
* source: Source item to query. This can come from DBLoadData or DBGetBatchList.
* expression: The expression to apply to the source, if necessary.
  * Ex: To get the 2nd index of the key \"foo\" assuming the source is a dictionary, the expression is: ['foo'][1]
* default: The value to use if the key doesn't exist.
Returns:
* A string representation of the requested simple value.

**DBGetBatchList**
Get a list from some key expression in the source DBItem. The list will drive batching in ComfyUI.
Params:
* source: Source item to get data from.
* expression: Expression to get batch list. A Python expression that when appended onto the input data leads to a list in the loaded dictionary to generate the batch items from.
  * Ex: If we assume inputs data is a dict with an 'items' key and list value, we would write: ['items']
Returns:
* Return a list of items from the key expression, in a way that ComfyUI will use as a batch list.

### Math
**DBFloatExpression**
Evaluate a float expression.
Params:
* expression: Python math expression taking any of inputs a,b,c,d.
* a: Input a.
* b: Input b.
* c: Input c.
* d: Input d.
Returns:
* The result of the float expression.

### String
**DBStringExpression**
Evaluate a string expression.
* expression: Python string expression taking any of inputs a,b,c,d.
* a: Input a.
* b: Input b.
* c: Input c.
* d: Input d.
Returns:
* The result of the string expression.

## Other features

### The data file format

The data file can be either CSV, JSON, or YAML. These are parsed and stored internally as a Python dictionary representation.

The simplest usage of a file and DataBeast nodes is to access the document data by key, and/or batch a list of items in the document.

This example file is consumed by the DBLoadData node.
```
items:
  - prompt: A puppy wearing a yellow hat.
    cfg: 3
  - prompt: A cat wearing a red tie.
    cfg: 4
  - prompt: A bird wearing a silver star.
    cfg: 3.5
```

![image](image showing simple batching of a list of dictionaries)

A more advanced use case is to self-reference values within the file itself, as a way of meta-configuring your batch list items.
```
defs:
  color1: yellow
  color2: red
  color3: silver
items:
  - prompt: A puppy wearing a ${['defs']['color1']} hat.
    cfg: 3
  - prompt: A cat wearing a ${['defs']['color2']} tie.
    cfg: 4
  - prompt: A bird wearing a ${['defs']['color3']} star.
    cfg: 3.5
```

An even more advanced usage is to generate items in a list based on all permutations of a set of variables.
```
defs:
  color1: yellow
  color2: red
  color3: silver
items:
  db_exec: generate_permutation_list
  var:
    prompt:
      - "A puppy wearing a ${['defs']['color1']} hat."
      - "A cat wearing a ${['defs']['color2']} tie."
      - "A bird wearing a ${['defs']['color3']} star."
    cfg:
      min: 2
      max: 3
      steps: 4
  template:
    prompt: "$vars{['prompt']}"
    cfg: "$vars{['cfg']}"
```

Any dictionary containing the key 'db_exec' will run one of the db_exec built-in functions. In this case, we're running the 'generate_permutation_list' function, 
which will generate all permutations of the variables under the var section, per their specification. Here we have 'prompt' with 3 possible values stored in a list, 
and 'cfg' with a dictionary describing a ranged set of 4 values in the span [min, max]. That gives 12 permutations.

This will replace the 'db_exec' specification dictionary with a list of 12 versions of the dictionary specified in the 'template' section, with the inserted values
using the special `$vars{expression}` notation.

You may notice that 'cfg' is being specified as a string, but we'd really like it as a float. To make that happen, you can change these lines to:
```
    cfg:
      db_exec: to_float,
      expression: "$vars{['cfg']}"
```

'to_float' is another built-in db_exec function, and that specification dictionary is replaced with the float cast of the given string. After running, the input file
will effectively be stored as:
```
defs:
  color1: yellow
  color2: red
  color3: silver
items:
  - prompt: "A puppy wearing a yellow hat."
    cfg: 2.0,
  - prompt: "A puppy wearing a yellow hat."
    cfg: 2.333,
  - prompt: "A puppy wearing a yellow hat."
    cfg: 2.666,
  - prompt: "A puppy wearing a yellow hat."
    cfg: 3.0,
  - prompt: "A cat wearing a blue tie."
    cfg: 2.0,
  - prompt: "A cat wearing a blue tie."
    cfg: 2.333,
  - prompt: "A cat wearing a blue tie."
    cfg: 2.666,
  - prompt: "A cat wearing a blue tie."
    cfg: 3.0,
  - prompt: "A bird wearing a silver star."
    cfg: 2.0,
  - prompt: "A bird wearing a silver star."
    cfg: 2.333,
  - prompt: "A bird wearing a silver star."
    cfg: 2.666,
  - prompt: "A bird wearing a silver star."
    cfg: 3.0,
```

While this is a simple example, you can use these primitives to generate lots of procedural data within this file format.

## Examples
TBD
