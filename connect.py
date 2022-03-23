import logging
from os import getenv
from typing import List

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Logger
log = logging.getLogger()

# Load env variables
load_dotenv()
neo4j_server = getenv("NEO4J_SERVER")
neo4j_user = getenv("NEO4J_USER")
neo4j_password = getenv("NEO4J_PASSWORD")

# Connection handles
class Neo4jConnection:
    """Neo4J connection handle
    """

    def __init__(self, uri, user, password) -> None:
        """Establish a connection to a Neo4J server

        Args:
            uri (str): Connection URI for the driver
            user (str): User name
            password (str): Password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        log.debug(f'Connected to Neo4J database')

    def close(self) -> None:
        """Close the connection
        """
        self.driver.close()
        log.debug(f'Disonnected from Neo4J database')

    def version(self) -> List[str]:
        """Return the database version as string to verify connection

        Returns:
            List[str]: Name, version and edition of the Neo4J database
        """
        with self.driver.session() as session:
            result = session.run(('call dbms.components() '
                                  'yield name, versions, edition '
                                  'unwind versions as version '
                                  'return name, version, edition;'))
            return result.single().values()
