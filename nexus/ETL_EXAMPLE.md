# ETL Pipeline Example

This document explains the ETL (Extract, Transform, Load) pipeline example included in the multi-agent graph system.

## Overview

The ETL pipeline demonstrates a real-world data processing workflow that:
1. **Extracts** data from 3 different databases in parallel
2. **Validates** each data source independently
3. **Merges** all validated data into a single dataset
4. **Loads** the merged data to a data warehouse

## Workflow Structure

```
                    ┌─────────────┐
                    │ db1_extract │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ db1_validate│
                    └──────┬──────┘
                           │
┌─────────────┐      ┌────▼────┐      ┌─────────────┐
│ db2_extract │      │  merge  │      │warehouse_load│
└──────┬──────┘      └────┬────┘      └─────────────┘
       │                  │
┌──────▼──────┐      ┌────▲────┐
│ db2_validate│      │ db3_validate│
└──────┬──────┘      └────┬────┘
       │                  │
┌──────▼──────┐      ┌────▼────┐
│ db3_extract │      │         │
└─────────────┘      └─────────┘
```

## Agents

### 1. DatabaseExtractor

Extracts data from a database connection.

**Properties:**
- Connection string (e.g., `postgres://db1`, `mysql://db2`, `mongodb://db3`)
- SQL query or database operation
- Simulates extracting 10 records per database

**Output:** `DatabaseData` struct containing:
- Source name
- Records (array of maps)
- Record count
- Extraction timestamp

### 2. DataValidator

Validates data integrity using configurable rules.

**Properties:**
- Validation rules (e.g., `has_id`, `has_name`)
- Checks each record against all rules
- Collects validation issues

**Output:** `ValidatedData` struct containing:
- Source name
- Valid records (filtered)
- Validation status
- List of issues found

### 3. DataMerger

Merges data from multiple validated sources.

**Properties:**
- Accepts multiple `ValidatedData` inputs
- Combines all records into single dataset
- Tracks source information

**Output:** `MergedData` struct containing:
- List of source names
- All merged records
- Total record count
- Merge timestamp

### 4. WarehouseLoader

Loads merged data to data warehouse in batches.

**Properties:**
- Warehouse URL (e.g., `snowflake://warehouse`)
- Batch size for loading
- Simulates batch loading with delays

**Output:** `WarehouseLoadResult` struct containing:
- Success status
- Row count loaded
- Load time duration
- Load timestamp

## Running the ETL Pipeline

### Sequential Mode
```bash
./multi-agent-graph etl
```
Executes each node one at a time in topological order. Good for debugging and understanding the flow.

### Parallel Mode (Recommended)
```bash
./multi-agent-graph etl --parallel
```
Executes independent nodes concurrently:
- All 3 database extractions run in parallel
- All 3 validations run in parallel after their extractions complete
- Merge and load run sequentially (they depend on all validations)

**Performance comparison:**
- Sequential: ~733ms
- Parallel: ~347ms (2x faster)

## Example Output

```
=== ETL Pipeline Results ===

Database Extraction:
  DB1: 10 records from DB1
  DB2: 10 records from DB2
  DB3: 10 records from DB3

Validation:
  DB1: 10 valid records, 0 issues
  DB2: 10 valid records, 0 issues
  DB3: 10 valid records, 0 issues

Merge: 30 total records from 3 sources
  Sources: [DB1 DB2 DB3]

Warehouse Load: SUCCESS
  Rows loaded: 30
  Load time: 50.145225ms
```

## Real-World Extensions

This example can be extended with:

### Error Handling
- Retry logic for failed database connections
- Dead letter queue for invalid records
- Circuit breakers for failing sources

### Data Quality
- Schema validation
- Data type checking
- Business rule validation
- Data profiling

### Performance
- Connection pooling
- Batch processing configuration
- Streaming for large datasets
- Incremental loading

### Monitoring
- Metrics collection (records per second, error rates)
- Logging to external systems
- Alerting on failures
- Progress tracking

### Additional Features
- Data transformation (type conversion, normalization)
- Data enrichment (lookup tables, API calls)
- Data masking (PII protection)
- Partitioning strategy

## Customizing the Pipeline

### Adding More Data Sources

```go
builder.AddNode("db4_extract", "Database 4 Extract", "database_extractor")
builder.AddNode("db4_validate", "Database 4 Validate", "data_validator")
builder.AddEdge("db4_extract", "db4_validate", 1.0)
builder.AddEdge("db4_validate", "merge", 1.0)

orc.RegisterAgent("db4_extract", NewDatabaseExtractor("extract-4", "DB4", "oracle://db4", "SELECT * FROM products"))
orc.RegisterAgent("db4_validate", NewDataValidator("validate-4", "Validator 4"))
```

### Adding Transformation Steps

```go
builder.AddNode("transform", "Transform Data", "data_transformer")
builder.AddEdge("merge", "transform", 1.0)
builder.AddEdge("transform", "warehouse_load", 1.0)
```

### Adding Conditional Branches

```go
builder.AddNode("quality_check", "Quality Check", "quality_checker")
builder.AddEdge("merge", "quality_check", 1.0)

// Only load if quality passes
builder.AddEdge("quality_check", "warehouse_load", 1.0)
```

## File Structure

```
examples/
├── etl.go              # ETL-specific agent implementations
├── workflow.go         # General workflow examples
└── cmd/
    └── main.go         # CLI entry point with ETL workflow runner
```

## Key Takeaways

1. **Parallel Execution**: The graph automatically identifies which nodes can run in parallel (the 3 database extractions and validations)
2. **Dependency Management**: The merge node waits for all 3 validations to complete before executing
3. **Type Safety**: Each agent has strongly-typed input/output for compile-time safety
4. **Extensibility**: Easy to add new data sources, validation rules, or transformation steps
5. **Monitoring**: Each node tracks status, duration, and results independently

This ETL example demonstrates how the multi-agent graph system can handle real-world data processing workflows with complex dependencies and parallel execution.
-----------------------------------------------------
Running ETL pipeline...



=== DAG Structure ===

Nodes: 8

Edges: 7



Nodes:

- db1_extract (Database 1 Extract) [database_extractor]

- db2_extract (Database 2 Extract) [database_extractor]

- db3_extract (Database 3 Extract) [database_extractor]

- db1_validate (Database 1 Validate) [data_validator]

- db2_validate (Database 2 Validate) [data_validator]

- db3_validate (Database 3 Validate) [data_validator]

- merge (Merge Data) [data_merger]

- warehouse_load (Load to Warehouse) [warehouse_loader]



Edges:

- db1_extract -> db1_validate (weight: 1.0)

- db2_extract -> db2_validate (weight: 1.0)

- db3_extract -> db3_validate (weight: 1.0)

- db1_validate -> merge (weight: 1.0)

- db2_validate -> merge (weight: 1.0)

- db3_validate -> merge (weight: 1.0)

- merge -> warehouse_load (weight: 1.0)



Root Nodes:

- db1_extract

- db2_extract

- db3_extract



Leaf Nodes:

- warehouse_load



Topological Order:

1. db1_extract

2. db2_extract

3. db3_extract

4. db1_validate

5. db2_validate

6. db3_validate

7. merge

8. warehouse_load

====================

2026/11/24 17:08:33 Starting parallel workflow execution with 8 nodes

2026/11/24 17:08:33 Executing node: db3_extract (Database 3 Extract)

2026/11/24 17:08:33 Executing node: db1_extract (Database 1 Extract)

2026/11/24 17:08:33 Executing node: db2_extract (Database 2 Extract)

2026/11/24 17:08:33 Node db2_extract completed successfully

2026/11/24 17:08:33 Node db1_extract completed successfully

2026/11/24 17:08:33 Node db3_extract completed successfully

2026/11/24 17:08:33 Executing node: db1_validate (Database 1 Validate)

2026/11/24 17:08:33 Executing node: db2_validate (Database 2 Validate)

2026/11/24 17:08:33 Executing node: db3_validate (Database 3 Validate)

2026/11/24 17:08:33 Node db3_validate completed successfully

2026/11/24 17:08:33 Node db2_validate completed successfully

2026/11/24 17:08:33 Node db1_validate completed successfully

2026/11/24 17:08:33 Executing node: merge (Merge Data)

2026/11/24 17:08:33 Node merge completed successfully

2026/11/24 17:08:33 Executing node: warehouse_load (Load to Warehouse)

2026/11/24 17:08:33 Node warehouse_load completed successfully

2026/11/24 17:08:33 Parallel workflow execution completed



=== ETL Pipeline Results ===

Database Extraction:

DB1: 10 records from DB1

DB2: 10 records from DB2

DB3: 10 records from DB3



Validation:

DB1: 10 valid records, 0 issues

DB2: 10 valid records, 0 issues

DB3: 10 valid records, 0 issues



Merge: 30 total records from 3 sources

Sources: [DB1 DB2 DB3]



Warehouse Load: SUCCESS

Rows loaded: 30

Load time: 50.25319ms

Explain

An 8-node, 7-edge parallel ETL pipeline extracted 30 records across three databases, validated them with zero errors, merged the datasets, and loaded all 30 rows into the data warehouse within 17:08:33 on November 24, 2026.

Pipeline Execution Breakdown
The workflow progressed through four sequential dependency stages:

Stage	Node(s)	Execution Mode	Outcome
1. Extract	db1_extract, db2_extract, db3_extract	Parallel (3 root nodes)	Pulled 10 records from each source database (30 total)
2. Validate	db1_validate, db2_validate, db3_validate	Parallel (per-source branch)	Verified all 30 records (10 valid, 0 issues per database)
3. Merge	merge	Single synchronization barrier	Combined the three validated streams into 30 unified records
4. Load	warehouse_load	Single leaf node	Wrote all 30 rows to the warehouse in 50.25 ms (SUCCESS)
Key Execution Characteristics
Fan-in DAG topology: Each database has an isolated extract-and-validate branch (dbX_extract → dbX_validate) so slow or failing reads on one source do not block validation on the others. All three branches converge at merge, which acts as a dependency barrier before warehouse_load can start.

Non-deterministic parallel scheduling: Although the static topological sort lists db1, db2, then db3, the runtime logs show the extractors started as db3 → db1 → db2 and finished as db2 → db1 → db3. This confirms true concurrent worker execution rather than sequential playback.

100% record reconciliation: Unlike the earlier CI/CD run, this execution completed with no warnings or data loss—all 30 extracted records passed validation, survived the merge, and landed in the target warehouse.


