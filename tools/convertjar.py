import subprocess
import os

def decompile_jar(jar_filename, output_dir="./temp_java"):
    command = ["java", "-jar", "cfr.jar", jar_filename, "--outputdir", output_dir]
    result = subprocess.run(command, capture_output=True, text=True)


def decompile_all_jars_in_directory(directory, output_dir="./temp_java"):
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        return
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".jar"):
                jar_path = os.path.join(root, file)
                print("decompiling ",jar_path)
                decompile_jar(jar_path, output_dir)

# Example usage
directory_to_scan = <absolute_directory_path>
decompile_all_jars_in_directory(directory_to_scan)
