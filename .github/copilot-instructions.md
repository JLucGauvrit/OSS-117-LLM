# AI Agent Instructions for OSS-117-LLM

## Project Overview
**OSS-117-LLM** is a from-scratch Large Language Model training project inspired by the OSS 117 film character. The goal is to create a complete LLM pipeline: data collection → model training → monitoring UI → inference API.

**Current Stage**: Early development (data collection phase on `feature----collecting-data` branch)

## Architecture & Data Flow

### Core Components
- **data/collect_data/**: Python service (Dockerized) that aggregates datasets from Hugging Face, Wikipedia, and public domain media
- **training/**: Will contain LLM training scripts (currently empty - planned for model development)
- **prometheus/ + grafana/**: Monitoring stack for training metrics visualization
- **docker-compose.yml**: Orchestrates all services (data_collector, Prometheus, Node Exporter, cAdvisor, dcgm-exporter, Grafana)

### Data Pipeline
1. **Collection** → Raw data stored in `/raw_data` volume (shared via `docker-compose.yml`)
2. **Formats**: Final datasets in **text (.txt)** and **JSONL** formats
3. **Instruction Tuning**: Alpaca format (`{"instruction", "input", "output"}`) for fine-tuning datasets
4. **Monitoring**: Prometheus scrapes metrics from node_exporter (9100), cadvisor (8080), dcgm-exporter (9400)

### Priority Data Sources for OSS-117 Character Model
The goal is to create an LLM that imitates OSS 117 character: a spy thriller narrator style. Priority data themes:
- **Spy/Intelligence contexts** (1950-1980 era) - Cold War narratives, espionage tradecraft, secret agent narratives
- **Pulp fiction & adventure narratives** - Action-oriented dialogue, noir storytelling
- **Period-accurate language** (1950s-1980s) - Vintage spy novels, declassified CIA/MI6 cultural materials
- **French cultural references** - OSS 117 is French, prioritize French-language sources + French historical context
- **Dialogue-heavy sources** - Films, TV scripts, interviews (captures the character's distinctive voice)

**Data sources to prioritize:**
1. French spy fiction (Maigret, similar detective/spy series)
2. International spy film scripts (1950-1980) - dialogue extraction
3. Wikipedia articles on Cold War, espionage history
4. Hugging Face datasets with period narratives (news articles 1950-1980, historical documents)
5. Public domain adventure/spy novels in French and English

### GPU Support
Project supports NVIDIA GPUs via `dcgm-exporter` service with `--cap-add=SYS_ADMIN`. Training will use `nvidia/dcgm-exporter` for GPU metrics.

## Developer Workflows

### Starting the Stack
```bash
docker compose up --build
```
This brings up all services. Access points:
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Node Exporter: http://localhost:9100

### Python Project Setup
- **Python version**: 3.11 (specified in `data/collect_data/Dockerfile`)
- **Package management**: pyproject.toml (setuptools backend)
- **Data collection entry**: `data/collect_data/requirements.txt` (currently empty - to be implemented)

### Documentation Build
CI/CD pipeline (`.github/workflows/docs.yml`) generates Sphinx documentation from:
```bash
sphinx-apidoc -o documentations/docs data/ training/ --force --separate
sphinx-build -b html documentations/docs/ documentations/docs/_build/html
```
Deploys to GitHub Pages on push to `main` or `dev`.

## Key Conventions

### Data Format Decisions
Per `documentations/Collection-Data.md`:
- All raw data → cleaned text (.txt)
- Instruction tuning datasets → **JSONL** (one JSON object per line)
- Alpaca format reference:
  ```json
  {"instruction": "Task description", "input": "Context (optional)", "output": "Expected response"}
  ```

### Directory Structure Patterns
- `data/collect_data/`: Containerized Python scripts (Dockerfile enforces 3.11)
- `documentations/`: Markdown docs + Sphinx sources (auto-published to GitHub Pages)
- `grafana/provisioning/`: Service configuration (dashboards from `/var/lib/grafana/dashboards` directory)
- `prometheus/`: Scrape config (all metrics hardcoded, targets use service names via Docker network)

### Monitoring Stack
- **Prometheus** scrapes every 15 seconds (`prometheus.yml`: `scrape_interval: 15s`)
- **Grafana** auto-provisions via `grafana/provisioning/` 
- **cAdvisor** monitors Docker containers (8080)
- **Node Exporter** collects system metrics (CPU, RAM, disk, network on 9100)
- **dcgm-exporter** GPU metrics (9400, NVIDIA-specific)

## Cross-Component Communication
- **Docker network**: All services communicate via service names (e.g., `prometheus:9090`, `node_exporter:9100`)
- **Volumes**: 
  - `raw_data:/app/raw_data` - data_collector output
  - `prometheus_data`, `grafana_data` - persistent storage
  - `./grafana/provisioning/` - mounted read-only config

## Important Constraints & Patterns

### Why This Architecture?
1. **Containerization**: Ensures reproducible data collection environment (Python 3.11 locked)
2. **Monitoring**: Early instrumentation enables real-time training visibility
3. **GPU Support**: dcgm-exporter with SYS_ADMIN cap for full GPU metrics (critical for LLM training)
4. **Modular Stack**: Separate data collection from training - allows independent scaling

### What's Not Yet Implemented
- **training/** directory: Training scripts should follow Python 3.11 + PyTorch/Hugging Face conventions
- **data/collect_data/requirements.txt**: Empty - needs implementation for dataset fetching
- **Inference API**: Not yet planned

## Common Tasks

**Adding a new metric exporter**:
1. Add service to `docker-compose.yml` with proper port mapping
2. Add scrape config to `prometheus/prometheus.yml` (target: `service_name:port`)
3. Create/update Grafana dashboard at `grafana/dashboards/*.json`

**Contributing to data collection**:
1. Add Python dependencies to `data/collect_data/requirements.txt`
2. Implement collector in `data/collect_data/` (outputs to `/app/raw_data`)
3. Ensure output is either `.txt` or `.jsonl` format
4. For OSS-117 datasets: include source/era/language metadata in JSONL
5. Test via `docker compose up --build data_collector`

**Data collection checklist for OSS-117 sources**:
- [ ] Source has Cold War / espionage theme (1950-1980 era)?
- [ ] Contains dialogue or narrative prose (not purely technical)?
- [ ] French content prioritized, or multilingual?
- [ ] Public domain or properly licensed?
- [ ] Output tagged with source category (e.g., `"source": "french_spy_novels"`, `"era": "1960s"`)?

**Updating docs**:
- Edit markdown in `documentations/` 
- Runs automatically on PR/push to main/dev via GitHub Actions
- Deploying to GitHub Pages requires `main` branch push
