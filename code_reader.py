from llama_index.core.tools import FunctionTool
# wraps any python function as a tool that will be passed to the llm 
import os
def code_reader_func(file_name):
    """This function reads in Python files. This function will be wrapped in a tool
    which can be called by an llm"""
    path = os.path.join("data", file_name)

    try:
        with open(path, "r") as f:
            content = f.read()
            return {"file_content": content}
    except Exception as e:
        return {"error": str(e)}

#Funciton tool that will be passed to the LLm (codellama)    
code_reader = FunctionTool.from_defaults(
    fn=code_reader_func, 
    name="code_reader",
    description="THis to can read the contents of code files and return the results"
)