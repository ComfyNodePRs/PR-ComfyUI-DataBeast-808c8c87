import re
import itertools

from RestrictedPython import compile_restricted, safe_globals

# inspired any-type solution from Inspire-Pack

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any_typ = AnyType("*")

#

class DBItem:
    def __init__(self):
        self.item=None

#

def safe_eval(expression, local_vars, title):
    def safe_eval_getitem(ob, index):
        return ob[index]

    safe_eval_globals = dict(safe_globals)
    safe_eval_globals['_getitem_'] = safe_eval_getitem
    
    byte_code = compile_restricted(expression, title, "eval")
    evaluated_result = eval(byte_code, safe_eval_globals, local_vars)
    return evaluated_result

#

def resolve_all_string_expressions_r(obj, expr_pattern, ref_source, evaluated):

    def eval_expression(expression, ref_source):
        # avoid infinite recursion
        if expression in evaluated:
            return evaluated[expression]

        result = ''

        try:
            full_expression = f"ref_source{expression}"
            local_vars = {"ref_source": ref_source}
            evaluated_result = str(safe_eval(full_expression, local_vars, "<resolve references>"))
            result = evaluated_result
        except Exception as ex:
            pass

        evaluated[expression] = result
        return result

    if isinstance(obj, str):
        return expr_pattern.sub(lambda m: eval_expression(m.group(2), ref_source), obj)
    elif isinstance(obj, dict):
        return {k: resolve_all_string_expressions_r(v, expr_pattern, ref_source, evaluated) for k,v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_all_string_expressions_r(item, expr_pattern, ref_source, evaluated) for item in obj]
    else:
        return obj

def resolve_all_string_expressions(obj, expr_pattern, ref_source):
    # recursively find all strings in obj and replace ${item expression} with result. avoid infinite recursion.
    evaluated = {}
    return resolve_all_string_expressions_r(obj, expr_pattern, ref_source, evaluated)

#

def copy_visit_all_items(obj, visitor):
    if isinstance(obj, dict):
        return {copy_visit_all_items(k, visitor): copy_visit_all_items(v, visitor) for k,v in obj.items()}
    elif isinstance(obj, list):
        return [copy_visit_all_items(v, visitor) for v in obj]
    else:
        return visitor(obj)

#

def generate_permutation_list(desc):
    try:
        vars_expr_pattern = re.compile(r"(\$vars\{([^}]+)\})")

        vars = desc['vars']
        template = desc['template']
        
        limit = -1
        if 'limit' in desc:
            limit = desc['limit']

        pvars = {}

        # generate vars lists
        for vkey,vvalue in vars.items():
            if isinstance(vvalue, dict):
                min = vvalue['min']
                max = vvalue['max']
                steps = vvalue['steps']
                pvalues = []
                if steps < 1:
                    pvalues = []
                elif steps == 1:
                    pvalues = [min]
                else:
                    delta = max - min
                    dd = delta / (steps - 1)
                    for s in range(0,steps-1):
                        pvalues.append(min + dd * s)
                    pvalues.append(max)
            elif isinstance(vvalue, list):
                pvalues = vvalue
            else:
                pvalues = [vvalue]

            pvars[vkey] = pvalues

        def permute_lists(pvars):
            pkeys = list(pvars.keys())
            values = list(pvars.values())
            
            # Generate all possible permutations using itertools.product
            permutations = list(itertools.product(*values))
            
            # Create a list of dictionaries for each permutation
            pdicts = [dict(zip(pkeys, perm)) for perm in permutations]

            return pdicts

        pdicts = permute_lists(pvars)

        out_list = []

        # evaluate template using each purmutations dict
        for pd in pdicts:
            ret_pd = resolve_all_string_expressions(template, vars_expr_pattern, pd)
            out_list.append(ret_pd)

        if limit > -1 and limit < len(out_list):
            out_list = out_list[:limit]

        return out_list
    except Exception as ex:
        return []

def to_float(desc):
    try:
        return float(desc['expression'])
    except Exception as ex:
        return 0.0

valid_db_exec_functions = {
    'generate_permutation_list': generate_permutation_list,
    'to_float': to_float
}



#### REMOVE

# def resolve_references_r(obj, root_obj, evaluated):

#     def eval_expression(expression, root_obj):
#         # avoid infinite recursion
#         if expression in evaluated:
#             return ''

#         evaluated[expression] = True

#         try:
#             full_expression = f"root_obj{expression}"
#             local_vars = {"root_obj": root_obj}
#             evaluated_result = safe_eval(full_expression, local_vars, "<resolve references>")
#             return evaluated_result
#         except Exception as ex:
#             return ''

#     if isinstance(obj, str):
#         return REPLACE_EXPR_PATTERN.sub(lambda m: eval_expression(m.group(2), root_obj), obj)
#     elif isinstance(obj, dict):
#         return {k: resolve_references_r(v, root_obj, evaluated) for k,v in obj.items()}
#     elif isinstance(obj, list):
#         return [resolve_references_r(item, root_obj, evaluated) for item in obj]
#     else:
#         return obj

# def resolve_references(obj):
#     # recursively find all strings in obj and replace ${item expression} with result. avoid infinite recursion.
#     evaluated = {}
#     return resolve_references_r(obj, obj, evaluated)
