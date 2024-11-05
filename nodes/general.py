import csv
import json
import yaml
import re
import os.path

from .core import DBItem, safe_eval, valid_db_exec_functions, resolve_all_string_expressions

REPLACE_EXPR_PATTERN = re.compile(r"(\$\{([^}]+)\})")

def resolve_db_exec_r(obj):

    def handle_db_exec(obj):
        func_name = obj['db_exec']
        if func_name in valid_db_exec_functions:
            ret_obj = valid_db_exec_functions[func_name](obj)
            return ret_obj
        else:
            ret_obj = dict(obj)
            ret_obj['failed_db_exec'] = func_name
            return ret_obj

    if isinstance(obj, dict):
        if 'db_exec' in obj:
            # must handle anything created by a handler
            handled = handle_db_exec(obj)
            resolved = resolve_db_exec_r(handled)
            return resolved
        else:
            new_dict = {k: resolve_db_exec_r(v) for k,v in obj.items()}
            return new_dict
    elif isinstance(obj, list):
        new_list = [resolve_db_exec_r(item) for item in obj]
        return new_list
    else:
        return obj

def resolve_db_exec(obj):
    # recursively find all values that are a db_exec command dictionary
    # replace value in parent with whatever is returned
    return resolve_db_exec_r(obj)


def filter_string(filter, exclusive, string):
    filter = filter.strip()
    if isinstance(filter, str) and len(filter) > 0:
        ret_lines = []
        lines = string.splitlines()
        for line in lines:
            match = re.match(filter, line)
            if match != None and not exclusive:
                groups = match.groups()
                if not (groups is None):
                    ret_lines.append("".join(groups))
                else:
                    ret_lines.append(line)
            elif match == None and exclusive:
                ret_lines.append(line)
        string = "\n".join(ret_lines)
    return string

def parse_csv_list(csv_string):
    csv_stream = StringIO(csv_string)
    reader = csv.DictReader(csv_stream, skipinitialspace=True)
    return list(reader)

def parse_json_root(json_string):
    out_list = []
    return json.loads(json_string)

def parse_yaml_root(yaml_string):
    out_list = []
    return yaml.safe_load(yaml_string)

#
    
class DBLoadData:
    @classmethod
    def IS_CHANGED(cls, *values):
        return float("NaN")

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "path": ("STRING", {"defaultInput": None, "tooltip": "Path to file to load. \n.json and .csv are treated as their formats, \nanything else is interepreted as YAML."}),
                    "filter": ("STRING", {"defaultInput": None, "tooltip": "Pattern filter. \nIf exclusive is true, only include lines \nthat DO NOT match this regex filter. If not exclusive, \ninclude ONLY lines that match this filter. If using \ncapture groups and not exclusive, all capture groups \nwill be concatenated into the final text for that line."}),
                    "exclusive": ("BOOLEAN", {"defaultInput": False, "tooltip": "Exclude with pattern. \nIf false, include only lines with the filter regex \npattern, if there is one."})
                    },
                }

    RETURN_TYPES = ("DB_ITEM",)
    RETURN_NAMES = ("data",)

    FUNCTION = "exec"
    CATEGORY = "DataBeast"

    def exec(self, path, filter, exclusive):
        # load path into list of dictionaries
        out_root = {}

        try:
            with open(path, "r") as loaded_file:
                file_string = loaded_file.read()
                file_string = filter_string(filter, exclusive, file_string)
                ext = os.path.splitext(os.path.basename(path))[1].lower()
                expression = ""
                if ext == '.csv':
                    batches = parse_csv_list(file_string)
                    out_root = {'items': batches}
                elif ext == '.json':
                    out_root = parse_json_root(file_string)
                else:
                    out_root = parse_yaml_root(file_string)

            out_root = resolve_all_string_expressions(out_root, REPLACE_EXPR_PATTERN, out_root)

            out_root = resolve_db_exec(out_root)

        except Exception as ex:
            pass
            # TODO: popup an error

        return (DBItem(out_root),)

class DBGetItem:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "source": ("DB_ITEM", {"defaultInput": None, "tooltip": "Source item to query."}),
                    "expression": ("STRING", {"defaultInput": None, "tooltip": "The expression to apply to the source, if necessary. \nEx: To get the 2nd index of the key \"foo\" assuming \nthe source is a table, the expression is: [\"foo\"][1]"}),
                    },
                }

    RETURN_TYPES = ("DB_ITEM",)
    RETURN_NAMES = ("value",)
    FUNCTION = "exec"
    CATEGORY = "DataBeast"

    def exec(self, source, expression, default):
        value = None
        try:
            source_item = source.item
            full_expression = "source_item{}".format(expression)
            local_vars = {"source_item": source_item}
            value = str(safe_eval(full_expression, local_vars, "<DBGetItem instance>"))
        except Exception as ex:
            # TODO: popup an error
            pass
        return (DBItem(value),)

class DBGetBatchList:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "source": ("DB_ITEM", {"defaultInput": None, "tooltip": "Source item to get data from."}),
                    "expression": ("STRING", {"defaultInput": None, "tooltip": "Expression to get batch list. \nA Python expression that when appended onto the \ninput data leads to a list in the loaded table \nto generate the batch items from.\n\nEx: If we assume inputs data is a table with \nan \"items\" key and list value, we would write: [\"items\"]"})
                    },
                }

    RETURN_TYPES = ("DB_ITEM",)
    RETURN_NAMES = ("item",)
    OUTPUT_IS_LIST = (True,)

    FUNCTION = "exec"
    CATEGORY = "DataBeast"

    def exec(self, source, expression):
        try:
            source_item = source.item
            full_expression = "source_item{}".format(expression)
            local_vars = {"source_item": source_item}
            
            out_batches = safe_eval(full_expression, local_vars, "<DBGetBatchList instance>")
        except Exception as ex:
            out_batches = []

        out_list = []
        for d in out_batches:
            out_list.append(DBItem(d))

        return (out_list,)

NODE_CLASS_MAPPINGS = {
    "DBLoadData //DataBeast": DBLoadData,
    "DBGetItem //DataBeast": DBGetItem,
    "DBGetBatchList //DataBeast": DBGetBatchList
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DBLoadData //DataBeast": "DB Load Data",
    "DBGetItem //DataBeast": "DB Get Item",
    "DBGetBatchList //DataBeast": "DB Get Batch List",
}
