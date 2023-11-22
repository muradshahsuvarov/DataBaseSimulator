# DataBaseSimulator

## Overview
This project is a Python implementation of a B+ Tree indexing mechanism, designed to simulate fundamental aspects of a database management system (DBMS). It enables the execution of SQL-like queries, such as select, join, and project, leveraging B+ Tree indexing for efficient data retrieval and minimal page reads. This simulator provides a practical insight into the underlying data storage and management techniques used in DBMS systems like PostgreSQL, MySQL, etc.

## Project Structure

### Folders and Files

- **`/data`**: Contains the relations or tables for the simulated database. Each file in a relation represents a "page" in the database, storing records in a structured format.
  
- **`/index`**: Holds the B+ Tree index files. These files are used to quickly locate data within the pages, improving query performance.

- **`/queryOutput`**: Stores the output of the queries executed through the simulator. This includes results from select, join, and project operations.

- **`utility.py`**: A utility module containing functions that assist in database operations, like loading schemas, reading page data, and more.

- **`relAlg.py`**: The core script that implements relational algebra operations (select, join, project) using the B+ Tree indexing mechanism.

- **`README.md`**: This file provides an overview of the project, its structure, and how to use it.