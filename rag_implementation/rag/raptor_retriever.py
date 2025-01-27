from pre_processor.raptor_preprocessor import *
from collections import defaultdict
import os
from llm.vertex_adapter import *
import chromadb
from utility.utils import *
from pathlib import Path
import pprint
from pre_processor.repo_chunker import *

def reformat_hints(hints):
    reformatted = {
        "class_name": [],
        "method_name": [],
        "module_name": []
    }

    for key, values in hints.items():
        if "." in key:  # It's likely a module
            reformatted["module_name"].append(key)
        else:  # It's likely a method
            reformatted["method_name"].append(key)

        # Add associated metadata
        for value in values:
            if value not in reformatted["class_name"]:
                reformatted["class_name"].append(value)

    return reformatted

def parse_logs(logs: list):
    """
    Parses log lines to extract modules and their associated classes.

    Args:
        logs (list): Multiline string of log entries.

    Returns:
        dict: A dictionary where keys are module names and values are sets of classes.
    """
    # Regular expression pattern to extract class and module
    pattern = re.compile(r'class: (?P<class>\w+), module: (?P<module>[\w\.]+)')
    module_class_map = defaultdict(set)

    for log in logs:
        match = pattern.search(log)
        if match:
            class_name = match.group("class")
            module_name = match.group("module")
            module_class_map[module_name].add(class_name)
    return {module: list(classes) for module, classes in module_class_map.items()}


def gmm_clustering_raptor_initialization(project, project_path, project_name, project_description):
    chroma_db_path = os.path.join(str(Path(project_path).parents[0]), f"{project}_raptor_chroma_db")
    collection = None

    chunks = code_into_chunks(project_path, project_name, description=project_description)

    # Prepare text and metadata for embedding
    all_texts = []
    metadata_list = []

    for chunk in chunks:
        chunk_text = f"\nChunk {chunk['chunk_number']}:\n{'=' * 40}\n{chunk['content']}\n{'=' * 40}\n"
        all_texts.append(chunk_text)

        metadata_list.append({
            "file_name": chunk["file_name"],
            "class_name": chunk["class_name"],
            "module_name": chunk["module_name"],
            "method_name": chunk["method_name"],
            "code_location": chunk["code_location"],
            "project": chunk["project"],
            "description": chunk["description"],
            "chunk_number": chunk["chunk_number"],
            "file_info": chunk["file_info"]
        })

    # Perform clustering and summarization
    results = recursive_embed_cluster_summarize(all_texts, level=1, n_levels=3)

    # Initialize all_texts with chunk texts and summaries
    all_texts = [text.strip() for text in all_texts]
    for level in sorted(results.keys()):
        summaries = [summary.strip().lower() for summary in results[level][1]["summaries"].tolist()]
        all_texts.extend(summaries)

        # Extend metadata for summaries
        for summary in summaries:
            metadata_list.append({
                "file_name": summary,
                "class_name": None,
                "module_name": None,
                "method_name": None,
                "code_location": None,
                "project": project_name,
                "description": f"Summary at level {level}",
                "chunk_number": None,
                "file_info": None
            })


    # Generate embeddings using vertex function
    embeddings = embed_text(all_texts)

    #  Create Chroma client and collection
    print(Fore.CYAN + "Creating " + chroma_db_path + Style.RESET_ALL)
    chroma_client = chromadb.PersistentClient(path=chroma_db_path)
    collection = chroma_client.get_or_create_collection(name=project)

    #  Add documents, metadata, and embeddings to the collection
    for i, (text, metadata, embedding) in enumerate(zip(all_texts, metadata_list, embeddings)):
        try:
            print(f"Adding text to collection: {text[:50]}... (ID: {i})")
            collection.add(
                ids=[str(i)],
                documents=[text],
                metadatas=[metadata],
                embeddings=[embedding]  # Ensure embedding is serialized
            )
        except Exception as e:
            print(f"Error adding text (ID: {i}): {e}")

    print(f"Collection size after adding: {collection.count()}")
    return collection

def construct_hint_query(hint: dict) -> str:
    query_parts = []
    for key, values in hint.items():
        for value in values:
            query_parts.append(f"{key}:{value}")
    return " AND ".join(query_parts)


from typing import List

def query_by_embedding(logs: List[str], collection, n_results: int = 1):
    """
    Query an existing ChromaDB collection using embeddings.

    Args:
        logs (list[str]): A list of log strings to summarize and use for the query.
        collection: The ChromaDB collection object.
        n_results (int): Number of top results to return for the search.

    Returns:
        list[dict]: A list of top matching results (documents).
    """
    print(Fore.BLUE + Style.BRIGHT + "query_by_embedding()" + Style.RESET_ALL)

    # Summarize Logs to generate query txt
    try:
        # Truncate logs to avoid token limit issues
        truncated_logs = logs[:1000]
        response = query_llm(
            "You are a software architect. From these logs describe the system design 5 sentences or less: " + str(truncated_logs)
        )
        print(Fore.BLUE + Style.BRIGHT + "Response summary of logs: " + response + Style.RESET_ALL)
    except Exception as e:
        print(f"Failed to generate query summary: {e}")
        return []

    # Generate Embeddings for the Query
    try:
        query_embedding = embed_text(response)
    except Exception as e:
        print(f"Failed to generate embedding for query: {e}")
        return []

    # Search the Collection by Embedding
    try:
        search_results = collection.query(
            query_embeddings=query_embedding,  # Use the embedding for the query
            n_results=n_results  # Number of results to retrieve
        )

        if isinstance(search_results, dict) and "documents" in search_results:
            return search_results["documents"]
        elif isinstance(search_results, list):
            return search_results  # Return raw list if that's what the API gives
        else:
            print(f"Unexpected search results format: {type(search_results)}")
            return []
    except Exception as e:
        print(f"Search failed: {e}")
        return []


def retrieve_similar_texts_croma(col,  query: str, logs = None, hint: dict = None, k: int = 5 ) -> List[dict]:
    final_results = []

    if hint:
        for field, values in hint.items():
            for value in values:
                try:
                    # Construct the where clause for each field-value pair
                    filters = {field: value}
                    print(f"Querying with filters: {filters}")
                    results = col.query(
                        query_texts=[query],
                        where=filters,  # Use the field-value pair as the filter
                        n_results=k  # Limit to top k results
                    )
                    pprint.pprint(results)
                    final_results.extend(results.get("documents", []))
                except Exception as e:
                    print(f"Error querying with hint {field}: {value}. Error: {e}")
    else:
        # Fallback if no hints are provided
        results = col.query(query_texts=[query], n_results=k)
        final_results.extend(results.get("documents", []))

    if logs is not None and len(logs) > 0:
        result = query_by_embedding(logs, col)
        final_results.extend(result)  # Directly extend the list

    # Check if documents are in a list of lists format, and flatten if necessary
    if final_results and isinstance(final_results[0], list):
        final_results = [item for sublist in final_results for item in sublist]  # Flatten the list

    # Deduplicate by 'id', ensuring that 'id' exists
    final_results_unique = []
    seen_ids = set()
    for doc in final_results:
        if isinstance(doc, dict):  # Ensure doc is a dictionary
            doc_id = doc.get("id")  # Safely access 'id' key
            if doc_id and doc_id not in seen_ids:
                seen_ids.add(doc_id)
                final_results_unique.append(doc)
                print(f"Expected document format: {doc}")
        else:
            # Handle unexpected document formats gracefully
            final_results_unique.append({"page_content":doc})

    return final_results_unique


def gmm_clustering_raptor_retrieval(project, project_path, project_name, project_description, query, logs=None,
                                    hint=None):
    chroma_db_path = os.path.join(str(Path(project_path).parents[0]), f"{project}_raptor_chroma_db")

    if not os.path.isfile(chroma_db_path + os.sep + "chroma.sqlite3"):
        collection = gmm_clustering_raptor_initialization(project, project_path, project_name, project_description)
    else:
        chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        collection = chroma_client.get_or_create_collection(name=project)

    # Generate query from hint
    hint_query = construct_hint_query(hint) if hint else ""
    final_query = f"{query} {hint_query}".strip()

    # Retrieve documents
    retrieved_docs = retrieve_similar_texts_croma(collection, final_query, logs = logs, hint=hint)

    # Post-process documents
    def format_docs(docs):
        return "\n\n".join(doc["page_content"] for doc in docs)

    context = format_docs(retrieved_docs)

    # Format prompt for LLM
    final_prompt = f"You are an expert developer analyzing code and logs to troubleshoot errors.\n\nContext:\n{context}\n\nQuestion:\n{query}"
    if logs:
        final_prompt += f"\nLogs:\n{logs}"

    from llm.common import query_llm, eval_llm_token_count

    # Get response from Gemini Pro
    print(Fore.CYAN + Style.DIM + "Prompt" + Style.RESET_ALL)
    pprint_color(final_prompt)
    response = query_llm(final_prompt)

    print(Fore.GREEN + Style.DIM + "Final answer: " + Style.RESET_ALL)
    print(Fore.GREEN + Style.BRIGHT + response+ Style.RESET_ALL)
    eval_llm_token_count(final_prompt)

    return response

def execute_project_feed_logs_to_raptor(project, project_path, project_name, project_description):
    invocation_dir = str(Path(project_path).parents[0])
    script_dir = str(Path(project_path).parents[0]) + str(os.sep) + "scripts"
    files = os.listdir(script_dir)

    main_scripts = [f for f in files if f.startswith("main") and f.endswith(".py")]

    if not main_scripts:
        print("No files starting with 'main' found in the folder.")

    # Troubleshooting
    # pprint.pprint(main_scripts)

    main_scripts.sort()

    for file in main_scripts:
        logs = []
        res = run_script_and_capture_logs(invocation_dir, file)
        logs.extend(res)

        hints = None

        if len(logs) > 0:
            hints = parse_logs(logs)

        print(Fore.CYAN + Style.DIM  +"Hints " + str(hints) + Style.RESET_ALL)
        query_file = os.path.basename(file).split(".")[0] + ".txt"
        query_file_path = invocation_dir + str(os.sep) + "scripts" + str(os.sep) + query_file
        query = ""

        with open(query_file_path, "r") as f:
            query = f.read()

        print(Fore.CYAN + Style.DIM  +"Query " + str(query) + " Read from " + query_file_path + Style.RESET_ALL)

        if query is None or query.strip() == "":
            query = "Here are logs of the project, analyse them and make a plantuml sequence diagram of the code flow"

        response = gmm_clustering_raptor_retrieval(project=project, project_path=project_path,
                                                   project_name=project_name,
                                                   project_description=project_description,
                                                   query=query, logs=logs, hint=reformat_hints(hints))


        render_to_pdf(location=str(Path(project_path).parents[0]) + str(os.sep) + "scripts", content=response,
                      filename=os.path.basename(file).split(".")[0], prefix = "raptor", logs=logs)
    return logs

