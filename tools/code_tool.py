from langchain.tools import BaseTool
import javalang
import pickle
from tools.code_loader import CodeLoader
from tools.path_tool import PathTool


class CodeTool(BaseTool):
    name = "CodeSearch"
    description = (
        "Input can only include classname followed by one period followed by function/construct name."
        "For example, for org.apache.tomcat.util.threads.ThreadPoolExecutor.runWorker, the only correct input is 'ThreadPoolExecutor.runWorker'"
        "Input a query string and search the code base to find relevant answers."
        "The query string should strictly only include class name and function, class, constant or variable you need. Class name and the construct name should be separated by a period."
        "For example, 'ExampleClass.exampleFunction' is a valid input to the code tool."
        "If you need the entire class, the code tool input should be '<class name>.<class name>'. For example, if you want the entire ExampleUtils class, code tool input should be ExampleUtils.ExampleUtils"
        "Try a different query if response is not useful."
        "Use import statements from CodeSearch output to find filepaths for other classes."
    )

    def __init__(self):
        super().__init__()

    def _run(self, query: str):
        path_tool = PathTool(new=False)
        try:
            path_tool.add_stacktrace("tools/stack_trace.txt")
        except Exception:
            print("\nstack trace not found")
        try:
            class_name, contstruct_name = query.split(".")
        except Exception:
            print(f"failed to split query, using class_name = function_name = {query}")
            class_name = contstruct_name = query
        path = path_tool.get_path(class_name)
        if not path:
            # check if field name was provided instead of class name
            try:
                with open("field_mapping.pkl", "rb") as f:
                    field_mapping = pickle.load(f)
                    field_name = class_name
                    class_name = field_mapping[field_name.lower()]
                    path = path_tool.get_path(class_name)
                    print(f"Field {field_name} maps to class {class_name}")
            except Exception:
                path = input(f"class {class_name} not found. input file path: ")
        code_loader = CodeLoader()

        def get_file_contents(class_path):
            class_contents = code_loader.get_file_contents_local(
                "./temp_java/" + class_path
            )
            if not class_contents:
                print(f"file contents in path {class_path} empty")
                input("paste code in 'tools/sample_required_file.txt' (ENTER): ")
                with open("sample_required_file.txt") as f:
                    class_contents = f.readlines()
            return class_contents

        file_contents = get_file_contents(path)
        try:
            tree = javalang.parse.parse("".join(file_contents))
            declaration = tree.types[0]
            if type(declaration).__name__ == "InterfaceDeclaration":
                print("interface detected")
                impl_path = path_tool.get_impl(path)
                file_contents = get_file_contents(impl_path)
        except Exception:
            # print(f"javalang tree parser error in {path}")
            impl_path = input(f"implementation class {class_name} not found. input interface implementation file path: ")
            if impl_path == "" and "interface" in "".join(file_contents):
                print("interface detected")
                impl_path = path_tool.get_impl(path)
                file_contents = get_file_contents(impl_path)
            else:
                file_contents = get_file_contents(impl_path)
        result = ""
        try:
            tree = javalang.parse.parse("".join(file_contents))
            package_name = tree.package.name
            print("adding imports")
            path_tool.add_dependency(package_name)
            for dependency in tree.imports:
                path_tool.add_dependency(dependency.path)
            class_declaration = tree.types[0]
            field_mapping = {}
            for dec in class_declaration.body:
                if type(dec).__name__ == "FieldDeclaration":
                    field_name = dec.declarators[0].name
                    field_type = dec.type.name
                    field_mapping[field_name.lower()] = field_type
            if field_mapping:
                with open("field_mapping.pkl", "wb") as f:
                    pickle.dump(field_mapping, f)
        except Exception:
            for line in file_contents:
                if "final" in line:
                    result += line

        function_contents = code_loader.get_function(file_contents, contstruct_name)
        if len(function_contents) <= 1 or len(function_contents) > 100:
            print(f"no. of lines in function: {len(function_contents)}")
            input("paste function in 'tools/sample_required_file.txt' (ENTER): ")
            with open("tools/sample_required_file.txt") as f:
                function_contents = f.readlines()
        function_contents = "".join(function_contents)
        return "Relevant code based on query: \n" + result + "\n" + function_contents
