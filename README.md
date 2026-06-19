# OpenSky Network SQL – Semester Project

## Project Description
This system is designed for the automatic collection and analysis of real-time air traffic data using the [OpenSky Network API](https://openskynetwork.github.io/opensky-api/rest.html). The project implements a complete ETL (Extract, Transform, Load) process – from data extraction through API, data validation and archiving in a relational database, to analytical processing.

## Installation and Usage

This project uses **`uv`** for dependency and environment management.

### 1. Prerequisites

If you do not have `uv` installed:

* **Linux/macOS:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
* **Windows:** `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
* Godot engine [https://godotengine.org/download/archive/] version 4.5 

### 2. Setting up the environment

In the project folder, run:

```bash
# Install dependencies
uv sync

# Run the periodic import scheduler
uv run scheduler.py
start exe or run client throught Godot engine with file project.godot in client folder for 3D visualization
```
