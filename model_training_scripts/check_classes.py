import os
import sys

def replace_first_index(folder_path, new_index=4):
    """
    Replace the first number in every line of every .txt file in the folder
    with the new_index.
    """
    txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]

    for txt_file in txt_files:
        file_path = os.path.join(folder_path, txt_file)
        with open(file_path, "r") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if parts:  # if line is not empty
                parts[0] = str(new_index)
                new_lines.append(" ".join(parts) + "\n")
            else:
                new_lines.append("\n")

        with open(file_path, "w") as f:
            f.writelines(new_lines)
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python replace_index.py <folder_path>")
        sys.exit(1)

    folder = sys.argv[1]
    replace_first_index(folder)
