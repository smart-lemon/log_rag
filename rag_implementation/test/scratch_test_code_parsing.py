import os
print(os.getcwd())
from pre_processor.chunker import *
from pre_processor.raptor_preprocessor import *
import pathlib
import pprint

def test():
    path_to_code_folder = "//Users/work/Documents/Code/work/rag_dogfood/parkinglot_code"
    import chromadb

    # Replace with your ChromaDB directory
    chroma_db_path = "/Users/work/Documents/Code/work/rag_dogfood/parkinglot_code/the_parking_lot_raptor_chroma_db"

    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path=chroma_db_path)

    # Replace with your collection name
    collection_name = "the_parking_lot"  # Ensure this is your correct collection name

    # Get the collection
    collection = chroma_client.get_collection(name=collection_name)

    # Use the `get` method to retrieve all documents in the collection
    # results = collection.get()

    # You can add a where clause for filtering if needed
    results = collection.get(
        where={"class_name": "Vehicle"}  # Filter based on class_name
    )

    # Print the retrieved documents
    res = results["documents"]
    for r in res:
        print("======================")
        print(r)
    met = results["metadatas"]
    for m in met:
        print("======================")
        print("Metadata:", str(m))

def test_code_chunking():
    path_to_code_folder = "/Users/work/Documents/Code/work/rag_dogfood/parkinglot_code"
    for root, dirs, files in os.walk(path_to_code_folder):
        for file in files:
            full_path = os.path.join(root, file)
            file_extension = pathlib.Path(file).suffix

            if os.path.isfile(full_path) and file_extension == ".py":
                with open(full_path, "r") as file:  # Use context manager for file handling
                    content = file.read()

                    chunker = CodeChunker(file_extension='py', encoding_name='gpt-4')
                    chunks = chunker.chunk(content, token_limit=1000, base_folder=path_to_code_folder, file_path=full_path)
                    # code_chunk = CodeChunk(file_name=full_path, project_name=self.project_name, chunks=chunks)
                    pprint.pprint(chunks)

def another_test_fn():
    from tree_sitter import Language

    # Specify where the library will be built and the source directories for languages
    Language.build_library(
        'build/my-languages.so',  # Path to output shared library
        [
            './code_parser_cache/tree-sitter-python',  # Path to the Python grammar repository
        ]
    )

    PY_LANGUAGE = Language(tspython.language())
if __name__ == "__main__":
    test_code_chunking()
    # another_test_fn()