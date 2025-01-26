from pre_processor.chunker import *
import configparser
import os
import re
from typing import Dict, Any, List, Tuple
import neo4j
from pre_processor.python_code_parser import CodeParser
from pre_processor.repo_chunker import code_into_chunks
import pprint

# Load API keys from configuration file
config = configparser.ConfigParser()
config.read('config.ini')
neo4j_db_uri = config.get('databases', 'neo4j_server_uri')
neo4j_db_user = config.get('databases', 'neo4j_db_user')
neo4j_db_password = config.get('databases', 'neo4j_db_password')

class CodeGraphTransformer:
    def __init__(self, neo4j_uri: str, neo4j_username: str, neo4j_password: str, file_extension='py'):
        """
        Initialize the graph transformer with Neo4j connection details.

        This transformer creates a graph representation of code structure
        following a specific ontological model of nodes and relationships.

        Args:
            neo4j_uri (str): Connection URI for Neo4j database
            neo4j_username (str): Neo4j database username
            neo4j_password (str): Neo4j database password
        """
        self.driver = neo4j.GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_username, neo4j_password)
        )
        self.code_parser = CodeParser(file_extension)
        self.file_extension = file_extension

    def transform_code_to_graph(self, code_chunks: Dict[int, Dict[str, Any]]):
        """
        Transform code chunks into a graph representing code structure.

        Args:
            code_chunks (Dict): Dictionary of code chunks from CodeChunker
            metadata_list (List[Dict[str, Any]]): List of metadata for each chunk
        """
        with self.driver.session() as session:
            # Track chunks for establishing sequence
            previous_chunk = None

            for chunk_number, chunk in code_chunks.items():

                # Troubleshooting - print chunks
                # pprint.pprint(code_chunks)

                file_path = code_chunks.get("file_name", 'unknown')

                # file_extension = os.path.splitext(file_path)[1][1:]
                code_content = code_chunks['content']
                module_name = code_chunks.get('module_name', 'unknown')

                # Create Chunk node
                self._create_chunk_node(session, chunk_number, file_path, code_content)

                # Create File node if not exists
                self._create_file_node(session, file_path, module_name)

                # Chunk follows previous chunk
                if previous_chunk:
                    self._create_follows_relationship(session, previous_chunk, chunk_number)
                previous_chunk = chunk_number

                # Link Chunk to File
                self._link_chunk_to_file(session, chunk_number, file_path)

                # Parse code for classes and functions
                tree = self.code_parser.parse_code(code_content, self.file_extension)
                if tree:
                    # Extract points of interest
                    points_of_interest = self.code_parser.extract_points_of_interest(tree, self.file_extension)

                    for node, node_type in points_of_interest:
                        # Extract node details
                        start_line = node.start_point[0] + 1
                        node_name = self._extract_node_name(node, code_content, node_type)

                        if node_type == 'Class':
                            # Create Class node
                            self._create_class_node(session, node_name, file_path, chunk_number)

                        elif node_type in ['Function', 'Method']:
                            # Determine if function is in a class context
                            class_context = self._find_class_context(points_of_interest, node)

                            # Create Function node
                            self._create_function_node(session, node_name, file_path, chunk_number, class_context)

                # Extract and create function call relationships
                called_functions = self.code_parser.extract_called_functions(code_content, self.file_extension)
                for caller, callee, call_type in called_functions:
                    self._create_function_call_relationship(session, caller, callee, file_path)

    def _create_chunk_node(self, session, chunk_number, file_path, code_content):
        session.run("""
            MERGE (chunk:Chunk {
                chunk_number: $chunk_number,
                file: $file_path,
                content: $content
            })
        """, {
            'chunk_number': chunk_number,
            'file_path': file_path,
            'content': code_content
        })

    def _create_file_node(self, session, file_path, module_name):
        session.run("""
            MERGE (file:File {name: $file_path})
            SET file.module = $module_name
        """, {
            'file_path': file_path,
            'module_name': module_name
        })

    def _create_follows_relationship(self, session, prev_number, current_number):
        session.run("""
            MATCH (prev:Chunk {chunk_number: $prev_number})
            MATCH (current:Chunk {chunk_number: $current_number})
            MERGE (prev)-[:FOLLOWS]->(current)
        """, {
            'prev_number': prev_number,
            'current_number': current_number
        })

    def _link_chunk_to_file(self, session, chunk_number, file_path):
        session.run("""
            MATCH (chunk:Chunk {chunk_number: $chunk_number})
            MATCH (file:File {name: $file_path})
            MERGE (chunk)-[:CONTAINS]->(file)
        """, {
            'chunk_number': chunk_number,
            'file_path': file_path
        })

    def _create_class_node(self, session, class_name, file_path, chunk_number):
        session.run("""
            MERGE (class:Class {
                name: $class_name,
                file: $file_path
            })
            WITH class
            MATCH (file:File {name: $file_path})
            MATCH (chunk:Chunk {chunk_number: $chunk_number})
            MERGE (class)-[:DEFINED_IN]->(file)
            MERGE (chunk)-[:CONTAINS]->(class)
        """, {
            'class_name': class_name,
            'file_path': file_path,
            'chunk_number': chunk_number
        })

    def _create_function_node(self, session, func_name, file_path, chunk_number, class_context):
        cypher_query = """
            MERGE (func:Function {
                name: $func_name,
                file: $file_path
            })
            WITH func
            MATCH (file:File {name: $file_path})
            MATCH (chunk:Chunk {chunk_number: $chunk_number})
            MERGE (func)-[:DEFINED_IN]->(file)
            MERGE (chunk)-[:CONTAINS]->(func)
        """

        # Add class relationship if in class context
        if class_context:
            cypher_query += """
                WITH func
                MATCH (class:Class {name: $class_name, file: $file_path})
                MERGE (func)-[:BELONGS_TO]->(class)
            """

        session.run(cypher_query, {
            'func_name': func_name,
            'file_path': file_path,
            'chunk_number': chunk_number,
            'class_name': class_context if class_context else None
        })

    def _create_function_call_relationship(self, session, caller, callee, file_path):
        session.run("""
            MATCH (caller:Function {name: $caller, file: $file_path})
            MATCH (callee:Function {name: $callee})
            MERGE (caller)-[:CALLS]->(callee)
        """, {
            'caller': caller,
            'callee': callee,
            'file_path': file_path
        })

    def _extract_node_name(self, node, code_content: str, node_type: str) -> str:
        """
        Extract the name of a node based on its type.

        Args:
            node: Tree-sitter node
            code_content (str): Full code content
            node_type (str): Type of node (Class, Function, etc.)

        Returns:
            str: Name of the node
        """
        try:
            name_node = node.child_by_field_name("name")
            if name_node:
                return code_content[name_node.start_byte:name_node.end_byte]

            # Fallback parsing for different node types
            if node_type == 'Class':
                return re.search(r'class\s+(\w+)',
                                 code_content[node.start_byte:node.end_byte]).group(1)
            elif node_type in ['Function', 'Method']:
                return re.search(r'def\s+(\w+)',
                                 code_content[node.start_byte:node.end_byte]).group(1)
        except Exception:
            return "Unknown"

    def _find_class_context(self, points_of_interest: List[Tuple], function_node) -> str:
        """
        Find the class context for a given function node.

        Args:
            points_of_interest (List[Tuple]): List of nodes and their types
            function_node: Function node to find context for

        Returns:
            str: Name of the class context, or None if no context
        """
        # Find the nearest class node that contains this function node
        for node, node_type in points_of_interest:
            if node_type == 'Class' and \
                    node.start_byte <= function_node.start_byte and \
                    node.end_byte >= function_node.end_byte:
                return self._extract_node_name(node, function_node.text.decode('utf-8'), 'Class')
        return None

    def close(self):
        """Close the Neo4j driver connection."""
        self.driver.close()

class Neo4jChunker(CodeChunker):
    def __init__(self, file_extension='py', encoding_name="gpt-4"):
        super().__init__(file_extension, encoding_name)

    def create_chunks(self, project, project_path, project_name, project_description):
        chunks = code_into_chunks(code_dir=project_path, project=project_name, description=project_description)

        return chunks


