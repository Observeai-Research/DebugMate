import requests
from os import listdir
from os.path import isfile, join, isdir
import javalang
import pickle


class CodeLoader:
    def __init__(self) -> None:
        self.all_files = []

    def get_files_local(self, path: str):
        files = [f for f in listdir(path) if isfile(join(path, f))]
        dirs = [d for d in listdir(path) if isdir(join(path, d))]
        if not dirs and not files:
            return
        for dir in dirs:
            e = dir.split("/")
            self.get_files_local(path + e[-1] + "/")
        for file in files:
            if file[-3:] == ".py" or file[-5:] == ".java":
                e = file.split("/")
                self.all_files.append(path + e[-1])

    def get_file_contents(self):
        file_contents = {}
        for file in self.all_files:
            print(file)
            data = requests.request("GET", file, headers=self.headers).text
            file_contents[file] = data
        return file_contents

    def get_file_contents_local(self, filename):
        file_contents = []
        try:
            with open(filename) as f:
                file_contents = f.readlines()
                print(filename)
        except Exception as e:
            print(f"{e}: {file_contents}")
        return file_contents

    def get_function(self, file_contents, function_name):
        result = []
        stack = []
        function_started = False
        for line in file_contents:
            if function_name in line:
                function_started = True
            if function_started and "{" in line:
                stack.append("{")
            if stack and "}" in line:
                stack.pop()
                if not stack:
                    function_started = False
            if stack or function_started:
                result.append(line)
                if not stack and ";" in line:
                    function_started = False
        result.append("}")
        return result

    def _run(self, question):
        query = {"query": question}
        answer = self.retrieval_qa_chain(query)
        return answer["result"]

    def impl_mapping(self, path: str):
        """stores interface to implemenation mapping in a dictionary for the entire repo"""
        path_tool_mappings = {}
        mapping = {}
        print("path impl mapping", path)
        self.get_files_local(path)
        all_files = self.all_files
        count = 0
        print(len(all_files))
        for file in all_files:
            temp_filename = file[len("./temp_java/") :]
            temp_class_name = temp_filename.split("/")[-1][: -len(".java")]
            path_tool_mappings[temp_class_name] = temp_filename

            print(f"{count}/{len(all_files)} ({file})")
            count += 1
            contents = self.get_file_contents_local(file)
            contents = "".join(contents)
            try:
                tree = javalang.parse.parse(contents)
            except Exception:
                print(f"tree load error in {file}")
            for i in tree.imports:
                print("-", i.path)
            imports = [i.path for i in tree.imports]
            imports_dict = {}
            for ipath in imports:
                class_name = ipath.split(".")[-1]
                imports_dict[class_name] = ipath
            declaration = tree.types[0]
            if type(declaration).__name__ == "ClassDeclaration":
                if not declaration.implements:
                    continue
                try:
                    for i in declaration.implements:
                        interface_name = i.name
                        print(imports_dict)
                        interface_path = imports_dict[interface_name]
                        interface_path = interface_path.replace(".", "/")
                        interface_path += ".java"
                        mapping[interface_path] = file[len(path) :]
                except Exception:
                    print(f"error in {file}")

        with open("interface_mapping.pkl", "wb") as f:
            pickle.dump(mapping, f)
        with open("path_mapping.pkl", "wb") as f:
            pickle.dump(path_tool_mappings, f)


if __name__ == "__main__":
    CodeLoader().impl_mapping("./temp_java/")
