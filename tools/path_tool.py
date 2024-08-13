import pickle


class PathTool:
    def __init__(self, new=False):
        if new:
            mapping = {}
            with open("path_mapping.pkl", "wb") as f:
                pickle.dump(mapping, f)

    def get_path(self, classname):
        with open("path_mapping.pkl", "rb") as f:
            mapping = pickle.load(f)
        try:
            result = mapping[classname]
        except Exception:
            result = None
        return result

    def get_impl(self, interface_path):
        with open("interface_mapping.pkl", "rb") as f:
            mapping = pickle.load(f)
        try:
            impl_path = mapping[interface_path]
        except Exception:
            impl_path = None
        return impl_path

    def add_import(self, import_statement: str):
        with open("path_mapping.pkl", "rb") as f:
            mapping = pickle.load(f)

        start_index = import_statement.find("import ") + len("import ")
        end_index = import_statement.find(";")
        path = import_statement[start_index:end_index].replace(".", "/") + ".java"
        classname = import_statement.split(".")[-1][:-1]
        mapping[classname] = path
        with open("path_mapping.pkl", "wb") as f:
            pickle.dump(mapping, f)

    def add_package(self, package_statement: str, class_name: str):
        with open("path_mapping.pkl", "rb") as f:
            mapping = pickle.load(f)
        start_index = package_statement.find("package ") + len("package ")
        end_index = package_statement.find(";")
        path = package_statement[start_index:end_index].replace(".", "/") + ".java"
        mapping[class_name] = path
        with open("path_mapping.pkl", "wb") as f:
            pickle.dump(mapping, f)

    def add_stacktrace(self, stacktrace_path):
        try:
            with open("path_mapping.pkl", "rb") as f:
                mapping = pickle.load(f)
        except Exception:
            mapping = {}
            with open("path_mapping.pkl", "wb") as f:
                pickle.dump(mapping, f)
        with open(stacktrace_path, "r") as f:
            line = f.readline()
            # print("\nadding stacktrace dependencies:")
            while line:
                if "caused by" in line:
                    line = f.readline()
                    continue
                try:
                    line = line.strip()
                    line = line.removeprefix("at")
                    line = line.strip()
                    line = line.split("(")[0]
                    classname = line.split(".")[-2]
                    path = "/".join((line.split(".")[:-1])) + ".java"
                    mapping[classname] = path
                    # print(f"{classname}:{path}")
                except Exception:
                    pass
                line = f.readline()
            # print("end stacktrace")
        with open("path_mapping.pkl", "wb") as f:
            pickle.dump(mapping, f)

    def add_dependency(self, dep):
        with open("path_mapping.pkl", "rb") as f:
            mapping = pickle.load(f)
        class_name = dep.split(".")[-1]
        filepath = dep.replace(".", "/") + ".java"
        mapping[class_name] = filepath
        # print(f"{class_name}: {filepath}")
        with open("path_mapping.pkl", "wb") as f:
            pickle.dump(mapping, f)
