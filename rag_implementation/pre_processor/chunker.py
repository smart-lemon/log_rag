# This code is taken from Cintra AI which in turn is using tree-sitter. It is modified to work for this prototype

from abc import ABC, abstractmethod
from .python_code_parser import CodeParser
import os
import tiktoken
import json
from colorama import Fore, Style


def count_tokens(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = 0
    if encoding_name == "gpt-4":
        encoding = tiktoken.encoding_for_model(encoding_name)
        num_tokens = len(encoding.encode(string))
    if encoding_name == "vertex":
        import google.generativeai as genai
        model = genai.GenerativeModel("models/gemini-pro")
        if len(string.strip()) == 0:
            return 0
        else:
            response = model.count_tokens(string)
            num_tokens = int(response.total_tokens)
    return num_tokens

def load_json(json_file):
    with open(json_file) as f:
        return json.load(f)

# Note this is intentional - vertex embedding is slow so for the sake of saving time
# gpt-4 was used it does not impact the solution because it is only for chunking by token limits
class Chunker(ABC):
    def __init__(self, encoding_name="gpt-4"):
        self.encoding_name = encoding_name

    @abstractmethod
    def chunk(self, content, token_limit):
        pass

    @abstractmethod
    def get_chunk(self, chunked_content, chunk_number):
        pass

    @staticmethod
    def print_chunks(chunks):
        for chunk_number, chunk_code in chunks.items():
            print(Fore.GREEN  + f"Chunk {chunk_number}:")
            print("=" * 40)
            print(chunk_code)
            print("=" * 40 + Style.RESET_ALL)

    def print_chunks_list(chunks):
        for chunk_number, chunk_code in chunks.items():
            print(Fore.GREEN + Style.BRIGHT+ f"Chunk {chunk_number}:")
            print("=" * 40)
            print(chunk_code)
            print("=" * 40 + Style.RESET_ALL)

    @staticmethod
    def consolidate_chunks_into_file(chunks):
        return "\n".join(chunks.values())

    @staticmethod
    def count_lines(consolidated_chunks):
        lines = consolidated_chunks.split("\n")
        return len(lines)


class CodeChunker(Chunker):
    def __init__(self, file_extension='py', encoding_name="gpt-4"):
        super().__init__(encoding_name)
        self.file_extension = file_extension


    def chunk(self, code, token_limit, file_path="unknown_file", base_folder="/") -> dict:
        """
        Chunk the code into smaller pieces while attaching metadata such as file name and package.
        """
        code_parser = CodeParser(self.file_extension)
        chunks = {}
        token_count = 0
        lines = code.split("\n")
        i = 0
        chunk_number = 1
        start_line = 0

        breakpoints = sorted(code_parser.get_lines_for_points_of_interest(code, self.file_extension))
        comments = sorted(code_parser.get_lines_for_comments(code, self.file_extension))
        adjusted_breakpoints = []
        for bp in breakpoints:
            current_line = bp - 1
            highest_comment_line = None  # Initialize with None to indicate no comment line has been found yet
            while current_line in comments:
                highest_comment_line = current_line  # Update highest comment line found
                current_line -= 1  # Move to the previous line

            if highest_comment_line:  # If a highest comment line exists, add it
                adjusted_breakpoints.append(highest_comment_line)
            else:
                adjusted_breakpoints.append(
                    bp)  # If no comments were found before the breakpoint, add the original breakpoint

        breakpoints = sorted(set(adjusted_breakpoints))  # Ensure breakpoints are unique and sorted

        while i < len(lines):
            line = lines[i]
            new_token_count = count_tokens(line, self.encoding_name)
            if token_count + new_token_count > token_limit:

                # Set the stop line to the last breakpoint before the current line
                if i in breakpoints:
                    stop_line = i
                else:
                    stop_line = max(max([x for x in breakpoints if x < i], default=start_line), start_line)

                # If the stop line is the same as the start line, it means we haven't reached a breakpoint
                # yet and we need to move to the next line to find one
                if stop_line == start_line and i not in breakpoints:
                    token_count += new_token_count
                    i += 1

                # If the stop line is the same as the start line and the current line is a breakpoint,
                # it means we can create a chunk with just the current line
                elif stop_line == start_line and i == stop_line:
                    token_count += new_token_count
                    i += 1

                # If the stop line is the same as the start line and the current line is a breakpoint,
                # it means we can create a chunk with just the current line
                elif stop_line == start_line and i in breakpoints:
                    current_chunk = "\n".join(lines[start_line:stop_line])
                    lines_to_be_parsed = current_chunk.split("\n")[start_line:stop_line]
                    if current_chunk.strip():
                        chunks[chunk_number] = {
                            "content": current_chunk,
                            "metadata": {
                                "file_name": os.path.basename(file_path),
                                "class_name": self.get_class_name(lines_to_be_parsed),
                                "module_name": self.get_package_name(file_path, base_folder),
                                "method_name": self.get_method_name(lines_to_be_parsed),
                            },
                        }
                        chunk_number += 1
                    token_count = 0
                    start_line = i
                    i += 1

                # If the stop line is different from the start line, it means we're at the end of a block
                else:
                    current_chunk = "\n".join(lines[start_line:stop_line])
                    lines_to_be_parsed = current_chunk.split("\n")[start_line:stop_line]
                    if current_chunk.strip():
                        chunks[chunk_number] = {
                            "content": current_chunk,
                            "metadata": {
                                "file_name": os.path.basename(file_path),
                                "class_name": self.get_class_name(lines_to_be_parsed),
                                "module_name": self.get_package_name(file_path, base_folder),
                                "method_name": self.get_method_name(lines_to_be_parsed),
                            },
                        }
                        chunk_number += 1

                    i = stop_line
                    token_count = 0
                    start_line = stop_line
            else:
                # If the token count is still within the limit, add the line to the current chunk
                token_count += new_token_count
                i += 1

        # Append remaining code, if any, ensuring it's not empty or whitespace
        current_chunk_code = "\n".join(lines[start_line:])
        lines_to_be_parsed = current_chunk_code.split("\n")[start_line:]
        if current_chunk_code.strip():  # Checks if the chunk is not just whitespace
            chunks[chunk_number] = {
                "content": current_chunk_code,
                "metadata": {
                    "file_name": os.path.basename(file_path),
                    "class_name": self.get_class_name(lines_to_be_parsed),
                    "module_name": self.get_package_name(file_path, base_folder),
                    "method_name": self.get_method_name(lines_to_be_parsed),
                },
            }
        return chunks

    def get_chunk(self, chunked_codebase, chunk_number):
        return chunked_codebase[chunk_number]

    def get_package_name(self, file_path, base_folder):
        relative_path = os.path.relpath(os.path.dirname(file_path), base_folder)
        return ".".join(relative_path.split(os.sep))

    def get_class_name(self, lines):
        class_name = ""
        for line in lines:
            if "class " in line and self.file_extension == "py":
                class_name = line.split("class ")[1].split("(")[0].strip()
                break
        return class_name.replace(':', '').strip()

    def get_method_name(self, lines):
        method_name = ""
        for line in lines:
            if "def " in line and self.file_extension == "py":
                method_name = line.split("def ")[1].split("(")[0].strip()
                break
        return method_name

