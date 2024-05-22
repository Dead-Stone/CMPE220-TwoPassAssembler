import subprocess
import os

def run_assembler(input_file, output_file):
    executable_path = './cpp/Assembler'
    if not os.path.isfile(executable_path) or not os.path.isfile(input_file):
        return "Executable or input file not found.", False

    try:
        result = subprocess.run([executable_path, input_file, output_file],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout, True
    except subprocess.CalledProcessError as e:
        return e.stderr, False

def main(input_file, output_file):
    message, success = run_assembler(input_file, output_file)
    if success:
        print("Assembly completed successfully.")
    else:
        print("Error:", message)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python assembler.py <input_file> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
