# OpenSky Network SQL – Semester Project

## Project Description
This system is designed for the automatic collection and analysis of real-time air traffic data using the [OpenSky Network API](https://opensky-network.org/apidoc/rest.html). The project implements a complete ETL (Extract, Transform, Load) process – from data extraction through API, data validation and archiving in a relational database, to analytical processing.

## Project Structure
```text
├── api_client.py        # Communication with OpenSky API
├── database.py          # Database connection and schema (SQLite)
├── etl.py               # ETL (Extract-Transform-Load) logic
├── main.py              # Main entry point
├── queries.py           # SQL analytical queries
├── scheduler.py         # Automation of periodic data import
├── opensky_ERD.pgerd    # Database ERD diagram
├── pyproject.toml       # Project configuration (uv)
├── uv.lock              # Dependency lockfile
└── README.md            # Project documentation
```

## Installation and Usage

This project uses **`uv`** for dependency and environment management.

### 1. Prerequisites

If you do not have `uv` installed:

* **Linux/macOS:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
* **Windows:** `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

### 2. Setting up the environment

In the project folder, run:

```bash
# Install dependencies
uv sync

# Run the periodic import scheduler
uv run scheduler.py
```
