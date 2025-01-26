from typing import Dict, List, Tuple
from pre_processor.repo_chunker import *
from pre_processor.neo4j_chunker import *
from neo4j import GraphDatabase

# ======================== Set the config.ini before the test ==============================

config = configparser.ConfigParser()
config.read('config.ini')
neo4j_db_uri = config.get('databases', 'neo4j_server_uri')
neo4j_db_user = config.get('databases', 'neo4j_db_user')
neo4j_db_password = config.get('databases', 'neo4j_db_password')


def add_code_chunks_to_graph_db(project, project_path, project_name, project_description):
    graph_transformer = CodeGraphTransformer(
        neo4j_uri=neo4j_db_uri,
        neo4j_username=neo4j_db_user,
        neo4j_password=neo4j_db_password,
        file_extension='py'
    )

    chunks = Neo4jChunker(file_extension='py').create_chunks(project, project_path, project_name, project_description)
    # chunks = code_into_chunks(code_dir=project_path, project=project_name, description=project_description)
    # chunks = chunker.chunk(content, token_limit=1000, base_folder=base_dir, file_path=full_path)
    # code_chunk = CodeChunk(file_name=full_path, project_name=self.project_name, chunks=chunks)

    # Assuming you have code chunks from CodeChunker
    for chunk in chunks:
        graph_transformer.transform_code_to_graph(chunk)
    graph_transformer.close()


def clear_neo4j_database():
    print(Fore.GREEN + "clear_neo4j_database() - Tearing down the database" + Style.RESET_ALL)
    # Connect to the Neo4j database
    driver = GraphDatabase.driver(neo4j_db_uri, auth=(neo4j_db_user, neo4j_db_password))

    def clear_db(tx):
        tx.run("MATCH (n) DETACH DELETE n")

    with driver.session() as session:
        session.execute_write(clear_db)

    driver.close()


# For your testing needs
if __name__ == "__main__":
    # Clear database
    try:
        clear_neo4j_database()
    except:
        print("Exception")
