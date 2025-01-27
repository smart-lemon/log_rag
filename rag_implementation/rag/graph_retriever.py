from utility.utils import *
from pre_processor.graphrag_preprocessor import add_code_chunks_to_graph_db, clear_neo4j_database
import re
from pathlib import Path
from typing import List, Dict, Any
import pprint
from neo4j import GraphDatabase

# Load API keys from configuration file
config = configparser.ConfigParser()
config.read('config.ini')
neo4j_db_uri = config.get('databases', 'neo4j_server_uri')
neo4j_db_user = config.get('databases', 'neo4j_db_user')
neo4j_db_password = config.get('databases', 'neo4j_db_password')

def parse_log_for_entities(log: str) -> Dict[str, str]:
    """
    Parse a log entry to extract relevant information.

    Args:
        log (str): A log entry string.

    Returns:
        Dict[str, str]: A dictionary containing the extracted information.
    """
    log_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .* - (INFO|ERROR|WARNING) - "
        r"class: (\w+), module: (\w+), file: (\w+\.py), log: (.*), line: (\d+)"
    )
    match = log_pattern.match(log)
    if match:
        return {
            "class": match.group(3),
            "module": match.group(4),
            "file": match.group(5),
        }
    return {}


def parse_log(log: str) -> Dict[str, str]:
    """
    Parse a log entry to extract relevant information.

    Args:
        log (str): A log entry string.

    Returns:
        Dict[str, str]: A dictionary containing the extracted information.
    """
    log_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .* - (INFO|ERROR|WARNING) - "
        r"class: (\w+), module: (\w+), file: (\w+\.py), log: (.*), line: (\d+)"
    )
    match = log_pattern.match(log)
    if match:
        return {
            "timestamp": match.group(1),
            "level": match.group(2),
            "class": match.group(3),
            "module": match.group(4),
            "file": match.group(5),
            "log": match.group(6),
            "line": match.group(7)
        }
    return {}

def extract_entities_from_logs(logs: List[str]) -> List[Dict[str, str]]:
    """
    Extract entities from a list of log entries.

    Args:
        logs (List[str]): A list of log entry strings.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the extracted information.
    """
    entities = list()
    for log in logs:
        entity = parse_log_for_entities(log)
        if entity:
            entities.append(entity)
    return entities


class GraphRetriever:
    def __init__(self, neo4j_uri: str, neo4j_username: str, neo4j_password: str):
        """
        Initialize the GraphRetriever with Neo4j connection details.

        Args:
            neo4j_uri (str): URI of the Neo4j database.
            neo4j_username (str): Username for the Neo4j database.
            neo4j_password (str): Password for the Neo4j database.
        """
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

    def close(self):
        """Close the Neo4j database connection."""
        self.driver.close()

    def retrieve_entities(self, entities: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Retrieve entities and related data from the graph database.

        Args:
            entities (List[Dict[str, str]]): List of dictionaries containing extracted information.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing retrieved information.
        """
        results = []
        query = """
        MATCH (c:Class {name: $class_name})-[:DEFINED_IN]->(f:File {name: $file_name})
        OPTIONAL MATCH (func:Function)-[:DEFINED_IN]->(f)
        OPTIONAL MATCH (func)-[:CALLS*1..2]->(calledFunc:Function)
        OPTIONAL MATCH (chunk:Chunk)-[:CONTAINS]->(f)
        RETURN 
            c, 
            f, 
            func, 
            COLLECT(calledFunc) AS calledFuncs, 
            COLLECT(DISTINCT chunk) AS chunks
        """
        try:
            with self.driver.session() as session:
                for entity in entities:
                    result = session.run(query,
                                         class_name=entity["class"],
                                         file_name=entity["file"])
                    for record in result:
                        called_functions = [
                            cf.get("name", "Unknown") for cf in record.get("calledFuncs", []) if cf
                        ]
                        chunks = record.get("chunks", [])
                        unique_chunks = {chunk["content"]: chunk for chunk in chunks if chunk}.values()

                        results.append({
                            "class": record.get("c", {}).get("name", "Unknown"),
                            "file": record.get("f", {}).get("name", "Unknown"),
                            "function": record.get("func", {}).get("name", "Unknown"),
                            "called_functions": called_functions,
                            "chunks": list(unique_chunks),
                        })
        except Exception as e:
            print(f"Error querying the database: {e}")
        return results

def extract_unique_chunks(results):
    """
    Extract unique chunks, filenames, and associated classes from the query results.

    Args:
        results (list): A list of dictionaries with keys 'class', 'file', and 'chunks'.

    Returns:
        list: A list of dictionaries containing 'class', 'file', and 'chunk' (content).
    """
    unique_chunks = set()
    processed_results = []

    for result in results:
        print("-----------Result-----------------")
        print(result)
        print("----------------------------")
        class_name = result.get('class', 'Unknown')
        file_name = result.get('file', 'Unknown')
        chunks = result.get('chunks', [])

        for chunk in chunks:
            chunk_content = chunk['content']
            chunk_key = (file_name, chunk_content)  # Ensure uniqueness based on file and content

            if chunk_key not in unique_chunks:
                unique_chunks.add(chunk_key)
                processed_results.append({
                    'class': class_name,
                    'file': file_name,
                    'chunk': chunk_content
                })

    return processed_results


def retrieve_context_from_logs(logs: List[str], neo4j_uri: str, neo4j_username: str, neo4j_password: str) -> str:
    """
    Retrieve context from logs by querying the graph database.

    Args:
        logs (List[str]): List of log entry strings.
        neo4j_uri (str): URI of the Neo4j database.
        neo4j_username (str): Username for the Neo4j database.
        neo4j_password (str): Password for the Neo4j database.

    Returns:
        str: The final context retrieved from the graph database.
    """
    entities = extract_entities_from_logs(logs)  # Assuming this function is defined elsewhere.
    retriever = GraphRetriever(neo4j_uri, neo4j_username, neo4j_password)
    results = retriever.retrieve_entities(entities)
    retriever.close()

    print(Fore.RED + "Entities retrieved are " + str(entities) + Style.RESET_ALL)

    context = ""
    print(Fore.RED + "Results found are " + str(len(results)) + Style.RESET_ALL)
    processed_results = extract_unique_chunks(results)

    for item in processed_results:
        context += f"Class: {item['class']}"
        context +=f"File: {item['file']}"
        context +=f"Chunk: {item['chunk']}"
        context +="=" * 40

    return context

def execute_project_feed_logs_to_graphrag(project, project_path, project_name, project_description):
    add_code_chunks_to_graph_db(project, project_path, project_name, project_description)
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

        if len(logs) > 0:
            context = retrieve_context_from_logs(logs, neo4j_db_uri, neo4j_db_user, neo4j_db_password)

        query_file = os.path.basename(file).split(".")[0] + ".txt"
        query_file_path = invocation_dir + str(os.sep) + "scripts" + str(os.sep) + query_file
        query = ""

        with open(query_file_path, "r") as f:
            query = f.read()

        print(Fore.CYAN + Style.DIM  +"Query " + str(query) + " Read from " + query_file_path + Style.RESET_ALL)

        if query is None or query.strip() == "":
            query = "Here are logs of the project, analyse them and make a plantuml sequence diagram of the code flow"

        # Format prompt for LLM
        final_prompt = f"You are an expert developer analyzing code and logs to troubleshoot errors.\n\n Context:\n{context}\n\n Question:\n{query}"
        if logs:
            final_prompt += f"\nLogs:\n{logs}"

        # Get response from Gemini Pro
        print(Fore.CYAN + Style.DIM + "Prompt" + Style.RESET_ALL)
        pprint_color(final_prompt)

        count_tokens(final_prompt)
        response = query_llm(final_prompt)

        render_to_pdf(location=str(Path(project_path).parents[0]) + str(os.sep) + "scripts", content=response,
                      filename=os.path.basename(file).split(".")[0], prefix = "graphrag", logs=logs)

    clear_neo4j_database()