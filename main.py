import os
import json
import time
import logging
from kafka import KafkaConsumer
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

def init_neo4j():
    while True:
        try:
            logger.info("Connecting to Neo4j database...")
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            driver.verify_connectivity()
            logger.info("Connected to Neo4j successfully!")
            return driver
        except Exception as e:
            logger.error(f"Neo4j is not available: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def init_kafka_consumer():
    while True:
        try:
            logger.info("Connecting to Kafka cluster...")
            consumer = KafkaConsumer(
                "csv_rows",
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='earliest',
                group_id='loader-group'
            )
            logger.info("Connected to Kafka successfully!")
            return consumer
        except Exception as e:
            logger.error(f"Kafka is not available: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def main():
    driver = init_neo4j()
    consumer = init_kafka_consumer()

    logger.info("Poller service initialized, processing incoming messages...")
    for msg in consumer:
        payload = msg.value
        dataset_name = payload.get("dataset_name")
        row_index = payload.get("row_index")
        row_data = payload.get("data", {})

        if not dataset_name or not row_data:
            logger.warning("Dropped invalid message structure.")
            continue

        try:
            with driver.session() as session:
                session.run("MERGE (d:Dataset {name: $name})", name=dataset_name)
                
                props = {**row_data, "row_index": row_index, "dataset_name": dataset_name}
                
                query = """
                MERGE (r:Row {dataset_name: $dataset_name, row_index: $row_index})
                SET r += $properties
                WITH r
                MATCH (d:Dataset {name: $dataset_name})
                MERGE (d)-[:HAS_ROW]->(r)
                """
                session.run(query, dataset_name=dataset_name, row_index=row_index, properties=props)
                logger.info(f"Processed row {row_index} of {dataset_name}")
        except Exception as e:
            logger.error(f"Error merging row {row_index}: {e}")

if __name__ == "__main__":
    main()
