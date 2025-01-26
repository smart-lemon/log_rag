from pre_processor.repo_chunker import *
import os

class CodeChunk():
    def __init__(self,  project_name, file_name, chunks):
        self.filename = file_name
        self.file_description = ""
        self.project_name = project_name
        self.chunks = chunks

class CodeModule():
    def __init__(self, folder, project_name, module_name):
        self.folder = folder
        self.module_name = module_name
        self.module_description = ""
        self.project_name = project_name
        self.doc_file = None
        self.code_chunks = []  # Initialize to an empty list
        self.folder_tree = generate_folder_tree(folder, None)

    def set_code_chunk(self, chunk):
        self.code_chunks.append(chunk)

class CodeBase():
    def __init__(self, folder, project_name, description):
        self.root_folder = folder
        self.project_description = description
        self.project_name = project_name
        self.module_list = []
        self.folder_tree = generate_folder_tree(start_path=self.root_folder)
        self.doc_file = None

    def add_code_chunk_to_module(self, module_name, chunk):
        for index, item in enumerate(self.module_list):
            if item.module_name == module_name:
                self.module_list[index].set_code_chunk(chunk)

                # Troubleshooting
                # CodeChunker.print_chunks(self.module_list[index].code_chunks.chunks)
                # print(Fore.GREEN + str(self.module_list))

    def parse_modules(self):

        print(Fore.YELLOW + "Module List:")
        for directory in os.listdir(self.root_folder):
            if os.path.isdir(self.root_folder + "/" + directory):
                module = CodeModule(self.root_folder + "/" + directory, project_name = self.project_name,
                                    module_name= directory)
                self.module_list.append(module)
                print(Fore.YELLOW + " - " + module.module_name)
                print(Style.RESET_ALL)


    def print_code_repo(self):
        for module in self.module_list:
            print(Fore.BLUE + str(module.module_name))
            print(Fore.BLUE + str(module.folder_tree))
            # pprint.pprint(module.code_chunks.chunk)
            for chunk in module.code_chunks:
                print(Fore.YELLOW + chunk.folder_tree)
                print(Fore.YELLOW + chunk.filename)
                CodeChunker.print_chunks(chunk.chunks)

            # pprint.pprint(Fore.BLUE + module.code_chunks.filename)

    def get_code_chunks_in_text(self):
        txt = ""
        for module in self.module_list:
            txt += f"""Module Name- {module.module_name} \n"""
            txt += f"""Module tree- {module.folder_tree} \n"""
            if module.code_chunks:  # Check if code_chunks is not None
                for chunk in module.code_chunks:
                    txt += f"""Chunk tree- {chunk.folder_tree} \n"""
                    txt += f"""Chunk filename- {chunk.filename} \n"""
                    for chunk_number, chunk_code in chunk.chunks.items():
                        txt += f"Chunk {chunk_number}:"
                        txt += "=" * 40
                        txt += str(chunk_code)
                        txt += "=" * 40
        return txt


    def parse_files_create_chunks(self, module_name, base_dir):

        if len(self.module_list) == 0:
            print(Fore.RED + "No modules registered")
            return

        for module in self.module_list:
            if module.module_name == module_name:
                print(Fore.YELLOW + "Parsing " + module_name)
                for root, dirs, files in os.walk(module.folder):
                    for file in files:
                        full_path = os.path.join(root, file)
                        file_extension = pathlib.Path(file).suffix

                        if os.path.isfile(full_path) and file_extension == ".py":
                            with open(full_path, "r") as file:  # Use context manager for file handling
                                content = file.read()
                                chunker = CodeChunker(file_extension='py', encoding_name='gpt-4')
                                chunks = chunker.chunk(content, token_limit=1000, base_folder=base_dir, file_path=full_path)
                                code_chunk = CodeChunk(file_name=full_path, project_name=self.project_name, chunks=chunks)

                                from pathlib import Path
                                code_chunk.folder_tree = generate_folder_tree(
                                    start_path=self.root_folder,
                                    file_name=str(Path(full_path).parent.absolute()).split("/")[-1] +
                                              "/" + os.path.basename(full_path),
                                )

                                self.add_code_chunk_to_module(module.module_name, code_chunk)

    def format_codebase(self):
        ret = "---------------------------\n"
        ret = ret + "Project: " + self.project_name
        ret = ret + "Description of the code" + "\n---------------------------\n"
        for item in self.chunked_list:
            ret = ret + "\nFile path" +  item["file_name"]
            chunks = item["chunks"]
            for chunk_number, chunk_code in chunks.items():
                ret = ret + "\n" + f"Chunk {chunk_number}:"
                ret = ret + "\n" + "#" * 40
                ret = ret + "\n" + chunk_code
                ret = ret + "\n" + "#" * 40

        print(ret)
        return ret


def embed_code_into_clusters_long_context(code_dir, project, description):
    print(Fore.RED + " ==========  embed_code_into_clusters_long_context() Printing " + project + " project ==========  " + Style.RESET_ALL)
    codebase = CodeBase(folder=code_dir,project_name=project, description=description)
    codebase.parse_modules()
    for module in codebase.module_list:
        codebase.parse_files_create_chunks(module.module_name, code_dir)
    # codebase.print_code_repo()
    return codebase.get_code_chunks_in_text()
