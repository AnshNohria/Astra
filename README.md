# 🚀 Intelligent Cloud Storage Manager (Astra)

A professional-grade data lifecycle management system featuring intelligent tiering, real-time streaming, and cost optimization using industry-standard technologies.

## 🎯 Overview

**Astra** is an intelligent, real-time data management fabric that not only decides the optimal storage tier for existing data but also intelligently routes incoming data streams to the right location. It uses predictive analytics to learn from both historical access patterns and real-time stream metadata, creating a proactive data management system.

Built for a 12-hour hackathon, it showcases real-world technologies used in production cloud systems.

### Key Features

- **🤖 Intelligent Tiering**: Automatically moves data between HOT, WARM, COLD, and ARCHIVE tiers
- **📊 Predictive Analytics**: Uses ML-inspired heuristics to predict optimal storage tiers
- **🌊 Real-Time Streaming**: Kafka-based data ingestion pipeline for live data processing
- **☁️ Cloud Simulation**: High-fidelity AWS S3 mocking using `moto` library
- **💰 Cost Optimization**: Analyzes cross-cloud migration opportunities
- **🎨 Rich CLI**: Beautiful command-line interface using `click`

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface (Click)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼───────┐         ┌───────▼────────┐
│  Kafka Stream │         │  Tiering Engine │
│   (Producer   │         │  (Optimization  │
│  & Consumer)  │         │     Logic)      │
└───────┬───────┘         └───────┬─────────┘
        │                         │
        └────────┬────────────────┘
                 │
        ┌────────▼─────────┐
        │   S3 Manager     │
        │  (boto3 + moto)  │
        └──────────────────┘
                 │
        ┌────────▼─────────┐
        │  Mocked AWS S3   │
        │   (Local Test)   │
        └──────────────────┘
```

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Python 3.8+ | Core application logic |
| **Cloud SDK** | boto3 | AWS S3 SDK for Python |
| **Cloud Mocking** | moto | High-fidelity AWS service mocking |
| **Streaming** | Apache Kafka | Real-time data ingestion |
| **Orchestration** | Docker Compose | Container management |
| **CLI Framework** | Click | Command-line interface |
| **Data Layer** | JSON | Metadata persistence |

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Docker Desktop (for Kafka)
- Git

### Setup Steps

1. **Clone the Repository**
   ```powershell
   git clone https://github.com/AnshNohria/Astra.git
   cd Astra
   ```

2. **Install Python Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Start Kafka Infrastructure**
   ```powershell
   docker-compose up -d
   ```

4. **Verify Kafka is Running**
   ```powershell
   python main.py check-kafka
   ```

## 🎮 Usage Guide

### Quick Start Demo (5 Minutes)

Follow this sequence to see the full system in action:

#### Terminal 1: Start the Kafka Consumer
```powershell
python main.py listen-stream
```
Leave this running - it will show real-time ingestion logs.

#### Terminal 2: Run the Demo
```powershell
# Initialize cloud environment
python main.py init-cloud

# Generate some file events (simulates data ingestion)
python main.py generate-event --filename "customer_data.csv" --size 2.5
python main.py generate-event --filename "monthly_report_2024.pdf" --size 0.5
python main.py generate-event --filename "backup_archive.zip" --size 10.0
python main.py generate-event --filename "temp_logs.log" --size 0.1

# View the initial state (all files in HOT tier)
python main.py show-dashboard

# Age some files to simulate passage of time
python main.py age-file --filename "backup_archive.zip" --days 100
python main.py age-file --filename "temp_logs.log" --days 200

# Run the intelligent tiering engine
python main.py run-engine

# View the optimized state
python main.py show-dashboard
```

### CLI Commands Reference

#### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init-cloud` | Initialize mocked S3 environment | `python main.py init-cloud` |
| `show-dashboard` | Display all files and statistics | `python main.py show-dashboard` |
| `run-engine` | Execute tiering optimization | `python main.py run-engine` |

#### Streaming Commands

| Command | Description | Example |
|---------|-------------|---------|
| `generate-event` | Send file event to Kafka | `python main.py generate-event --filename data.csv` |
| `listen-stream` | Start Kafka consumer | `python main.py listen-stream` |
| `check-kafka` | Verify Kafka connectivity | `python main.py check-kafka` |

#### Utility Commands

| Command | Description | Example |
|---------|-------------|---------|
| `age-file` | Simulate file aging | `python main.py age-file --filename data.csv --days 90` |
| `simulate-access` | Simulate file accesses | `python main.py simulate-access --filename data.csv --count 50` |

## 🧠 Intelligent Tiering Logic

The system uses a sophisticated decision tree to determine optimal storage tiers:

### Tier Definitions

- **HOT (S3 STANDARD)**: Frequently accessed data, instant retrieval
- **WARM (S3 STANDARD_IA)**: Less frequent access, lower cost
- **COLD (S3 GLACIER)**: Archival data, retrieval in minutes
- **ARCHIVE (S3 DEEP_ARCHIVE)**: Long-term storage, retrieval in hours

### Decision Factors

1. **Access Patterns**: Files with 10+ accesses stay HOT
2. **Age-Based Rules**:
   - 0-30 days: HOT tier
   - 30-90 days: WARM tier
   - 90-180 days: COLD tier
   - 180+ days: ARCHIVE tier

3. **Predictive Heuristics**:
   - `monthly_report_*` → WARM (regular access expected)
   - `backup_*` → COLD (infrequent access)
   - `*.log` → ARCHIVE (rarely needed)
   - `temp_*` → COLD (temporary data)

## 📊 Sample Output

### Dashboard View
```
======================================================================
📊 INTELLIGENT STORAGE DASHBOARD
======================================================================

FILE NAME                                TIER            ACCESSES     LAST ACCESS        
----------------------------------------------------------------------
backup_archive.zip                       ❄️  COLD         0            2024-08-01 14:23
customer_data.csv                        🔥 HOT          0            2024-11-08 14:23
monthly_report_2024.pdf                  🌡️  WARM         0            2024-11-08 14:23
temp_logs.log                            🧊 ARCHIVE      0            2024-05-01 14:23

======================================================================
📈 STORAGE STATISTICS
======================================================================
Total Files: 4
Total Accesses: 0

Tier Distribution:
  🔥 HOT (STANDARD):        1 files
  🌡️  WARM (STANDARD_IA):    1 files
  ❄️  COLD (GLACIER):        1 files
  🧊 ARCHIVE (DEEP_ARCHIVE): 1 files
======================================================================
```

### Engine Execution
```
======================================================================
🔄 STARTING INTELLIGENT TIERING ENGINE
======================================================================

📊 Analyzing 4 files...

📄 backup_archive.zip
   Current Tier: HOT (STANDARD)
   Access Stats: 0 accesses, 100 days since last access
   🎯 Decision: Migrate to COLD tier
   ✓ Successfully migrated to GLACIER

📄 customer_data.csv
   Current Tier: HOT (STANDARD)
   Access Stats: 0 accesses, 0 days since last access
   ✓ Already in optimal tier (HOT)

☁️  CROSS-CLOUD OPTIMIZATION ANALYSIS
----------------------------------------------------------------------
📦 Found 2 files in archive tiers
💡 Recommendation: Consider migrating to GCP Coldline/Archive
   Potential Savings: ~30% on storage costs

======================================================================
📈 TIERING ENGINE SUMMARY
======================================================================
✓ Files Analyzed: 4
✓ Migrations Performed: 2
✓ Cost Optimizations: 2
✓ Estimated Monthly Savings: $30.00
======================================================================
```

## 🎯 Hackathon Demo Script

Perfect for your 5-10 minute presentation:

1. **Introduction** (1 min): Explain the problem - cloud storage costs are exploding
2. **Architecture** (1 min): Show the tech stack diagram
3. **Live Demo** (5-7 min):
   - Start consumer: `listen-stream`
   - Generate events: Show Kafka in action
   - Show dashboard: Initial HOT state
   - Age files: Simulate time passage
   - Run engine: Watch intelligent decisions
   - Show dashboard: Optimized state with savings
4. **Highlights** (1 min):
   - Real Kafka streaming
   - Professional AWS SDK mocking
   - Predictive analytics
   - Cost savings calculation

## 🏆 Why This Stands Out

1. **Production-Grade Tools**: Uses `moto`, `boto3`, and Kafka - the exact tools used in real cloud systems
2. **Real Streaming**: Not simulated - actual Docker-based Kafka
3. **Industry Patterns**: Copy-and-delete for tier changes, event-driven architecture
4. **Completeness**: Full lifecycle from ingestion → optimization → monitoring
5. **Extensibility**: Easy to add ML models, more cloud providers, or UI

## 🔧 Troubleshooting

### Kafka Connection Issues
```powershell
# Check if Kafka is running
docker ps

# Restart Kafka
docker-compose down
docker-compose up -d

# View Kafka logs
docker logs kafka
```

### Dependency Issues
```powershell
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 🚀 Future Enhancements

- [ ] Machine learning for access prediction
- [ ] Web dashboard with real-time metrics
- [ ] Multi-cloud support (Azure, GCP)
- [ ] Cost calculator with real pricing
- [ ] Automated policy configuration
- [ ] Data compression before cold storage
- [ ] Lifecycle policy export to Terraform/CloudFormation

## 📝 Project Structure

```
intelligent-storage-manager/
├── main.py              # CLI entry point (Click framework)
├── engine.py            # Tiering logic and optimization engine
├── streaming.py         # Kafka producer & consumer
├── cloud_utils.py       # S3 operations via boto3/moto
├── metadata.json        # Access pattern database
├── docker-compose.yml   # Kafka + Zookeeper setup
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 📄 License

MIT License - Feel free to use this project for learning and hackathons!

## 👨‍💻 Author

Built with ❤️ for the 12-Hour Hackathon Challenge

---

**Happy Hacking! 🎉** If this project helped you, please consider giving it a ⭐ on GitHub!
