from pre_processor.raptor_preprocessor import *
from colorama import Fore, Style
import pprint
import os

def generate_folder_tree(start_path, file_name=None, indent=''):
    ret = ""
    for root, dirs, files in os.walk(start_path):
        name = os.path.basename(root)
        if not name.startswith("__"):
            level = root.replace(start_path, '').count(os.sep)
            prefix = '├── ' if level == 0 else '│   ' * level + '├── '
            ret += f"{prefix}{os.path.basename(root)}/\n"
            sub_indent = '│   ' * (level + 1)
            for file in files:
                # Check if the file matches the given file name
                match_marker = " <-" if file_name is not None and os.path.basename(
                    root) + "/" + file == file_name else ""
                ret += f"{sub_indent}├── {file}{match_marker}\n"

    return ret



def code_into_chunks(code_dir, project, description):
    print(Fore.LIGHTRED_EX + Style.DIM + "code_into_chunks() " + Style.RESET_ALL)
    print(Fore.RED + " ========== Printing " + project + " project ==========  " + Style.RESET_ALL)
    chunks = []

    # TODO: use configparser
    encoding_name = "gpt-4" # "vertex"
    for root, dirs, files in os.walk(code_dir):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                print(Fore.BLUE + Style.DIM + f"code_into_chunks() Processing: {full_path} " + Style.RESET_ALL)

                print(Fore.BLUE + Style.DIM + " " + str(full_path) + Style.RESET_ALL)

                with open(full_path, "r") as f:
                    content = f.read()

                if content.strip():  # Ensure non-empty content
                    chunker = CodeChunker(file_extension='py', encoding_name=encoding_name)
                    file_name = os.path.basename(full_path)
                    tree = generate_folder_tree(code_dir, file_name)

                    # Chunk the file
                    chunks_for_file = chunker.chunk(
                        code=content,
                        file_path=full_path,
                        base_folder=code_dir,
                        token_limit=1000
                    )
                    information_about_file = "Code location \n '''\n" + tree + "\n'''\n"

                    # Troubleshooting
                    # pprint.pprint(chunks_for_file)
                    for chunk_number, chunk_data in chunks_for_file.items():
                        metadata = chunk_data["metadata"]
                        chunks.append({
                            "content": chunk_data["content"],
                            "file_name": file_name,
                            "class_name": metadata["class_name"],
                            "module_name": metadata["module_name"],
                            "method_name": metadata["method_name"],
                            "code_location": tree,
                            "project": project,
                            "description": description,
                            "chunk_number": chunk_number,
                            "file_info": information_about_file
                        })
    return chunks
