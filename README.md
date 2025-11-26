# LogGPT - CI/CD Log Intelligent Assistant

## Introduction

The CI-CD Log Intelligent Assistant is a tool designed to ingest logs from CI/CD pipelines, process and embed them, and then provide intelligent outputs (e.g., insights, summaries) to help DevOps/engineering teams quickly understand failures, trends or anomalies in their delivery pipelines. It’s built in Python and leverages embedding utilities to convert logs into a format suitable for querying or insight generation.

## Table of Contents

* [Introduction](#introduction)
* [Features](#features)
* [Installation](#installation)
* [Dependencies](#dependencies)
* [Configuration](#configuration)
* [Usage](#usage)
* [Examples](#examples)
* [Troubleshooting](#troubleshooting)

## Features

* Log ingestion: Collect CI/CD logs from configured sources.
* Chunking: Break large logs into manageable pieces (see `chunking.py`).
* Embedding: Generate embeddings for chunks via `embedding_utils.py`.
* Intelligent generation: Use embeddings + query logic in `generate.py` / `main.py` to derive insights or summaries.
* Modular: Ingestion and generation are separated (`ingest.py` vs `run_ingest.py` vs `generate.py`).
* Fully Python-based: Easy to modify, extend for custom pipelines.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/SMUGLER79/CI-CD-Log-Intelligent-Assistant.git
   cd CI-CD-Log-Intelligent-Assistant
   ```
2. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # for Linux/Mac
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Dependencies

The project uses Python exclusively (100% of code in Python). ([GitHub][1])
Key dependencies likely include (check `requirements.txt` for exact versions):

* Some embedding library (e.g., OpenAI, SentenceTransformers, etc)
* Log parsing utilities
* Possibly vector database or storage layer for embeddings
* Standard utilities (numpy, pandas, etc)

## Configuration

Before running the project, you’ll need to configure:

* The source of your CI/CD logs (files, cloud storage, pipeline artifacts).
* Embedding model or service (API key, model name).
* Destination for embeddings (local, vector DB, cloud).
* Query/interaction interface (CLI, web UI, chatbot).
* Optional: thresholds for alerting, summarization format, retention policy.

(*Note: The repository currently lacks explicit documentation of configuration options — you may need to add a `.env.example` or configuration file.*)

## Usage

### 1. Ingest logs

Run the ingestion script to gather logs and prepare embeddings:

```bash
python run_ingest.py
```

This will call `ingest.py` → parse logs → chunk them via `chunking.py` → embed via `embedding_utils.py`.

### 2. Generate insights or queries

Once embeddings are ready, you can run the generation step:

```bash
python generate.py
```

Or start the main interface:

```bash
python main.py
```

You may query:

* “What caused the pipeline to fail on build-stage job X?”
* “Summarize the last 50 logs for recurrent issues.”
* “List the top 5 error types and suggest fixes.”

## Examples

*(Fill in specific example commands, input log snippets and output summaries.)*

```text
> python generate.py --query "Why did the latest deployment fail?"
Output: “The failure occurred due to missing environment variable DB_HOST in job ‘deploy-prod’. Error stack trace…”  
```

## Troubleshooting

* **No embeddings generated**: Ensure your embedding API key is valid and `requirements.txt` installed correct version.
* **Logs too large / memory error**: Adjust chunk size in `chunking.py` or process logs incrementally.
* **Queries not returning meaningful results**: Check that embeddings were stored properly; verify that vector DB (if used) is properly configured.
* **Pipeline integration missing**: This module processes logs — you’ll need to integrate it into your CI/CD workflow (e.g., as a job in GitHub Actions, GitLab CI) to automate ingestion

