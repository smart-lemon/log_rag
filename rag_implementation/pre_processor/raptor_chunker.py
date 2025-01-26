from chunker import *

class RaptorChunker(CodeChunker):
    def __init__(self, file_extension, encoding_name="gpt-4"):
        super().__init__(file_extension, encoding_name)