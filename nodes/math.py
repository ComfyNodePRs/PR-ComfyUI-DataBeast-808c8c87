from .core import any_typ, DBItem, safe_eval

class DBFloatExpression:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "expression": ("STRING", {"defaultInput": None, "tooltip": "Python math expression taking any of inputs a,b,c,d."}),
                    "a": ("FLOAT", {"defaultInput": None, "tooltip": "Input a."}),
                    "b": ("FLOAT", {"defaultInput": None, "tooltip": "Input b."}),
                    "c": ("FLOAT", {"defaultInput": None, "tooltip": "Input c."}),
                    "d": ("FLOAT", {"defaultInput": None, "tooltip": "Input d."}),
                    },
                }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("output",)

    FUNCTION = "exec"
    CATEGORY = "DataBeast"

    def exec(self, expression, a, b, c, d):
        output = 0
        try:
            local_vars = {"a": a, "b": b, "c": c, "d": d}
            output = float(safe_eval(expression, local_vars, "<DBFloatExpression>"))
        except Exception as ex:
            pass

        return (output,)

NODE_CLASS_MAPPINGS = {
    "DBFloatExpression //DataBeast": DBFloatExpression,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DBFloatExpression //DataBeast": "DB Float Expression",
}
