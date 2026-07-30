# Ingest Stream Pipeline Report

## Schema Architecture
The ingestion architecture maps CSV inputs dynamically to an unified node graph schema:
- `Dataset`: Contains dataset metadata attributes (`name`, `total_rows`, `columns`, `uploaded_at`).
- `Row`: Dynamic object representing each CSV record. All custom schema columns map to matching properties.
- `HAS_ROW`: Dynamic relationship connecting Dataset nodes to their child Row records.

## Database Cypher Merge Patterns
To safeguard database integrity and filter duplicate record creations:
```cypher
MERGE (d:Dataset {name: $name})
```
```cypher
MERGE (r:Row {dataset_name: $dataset_name, row_index: $row_index})
SET r += $properties
```
```cypher
MERGE (d)-[:HAS_ROW]->(r)
```

## Grounded Chatbot Logic
To enforce grounded responses, the API executes NL-to-Cypher query translation dynamically:
1. Scan DB schemas metadata nodes.
2. Formulate target Cypher constraints matching string conditions.
3. Return `grounded=false` indicator badges if search values yield empty queries.
