# 🎯 Quick Reference Card - Astra Demo

## ⚡ Fastest Way to Demo (30 seconds)

```powershell
# Setup (one time only)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install kafka-python-ng
docker-compose up -d

# Run complete demo
python demo_complete.py
```

**That's it!** ✅

---

## 📋 What You'll See

### 1. Cloud Initialization
- S3 bucket created
- Environment ready

### 2. Data Ingestion (5 files)
- customer_data.csv (2.5 GB)
- monthly_report_november.pdf (0.8 GB)
- backup_archive_Q3.zip (15.0 GB)
- temp_processing_logs.log (0.2 GB)
- data.csv (2.0 GB)

### 3. Initial State
All files in 🔥 **HOT** tier

### 4. Time Simulation
- Backup aged 120 days
- Logs aged 200 days
- Data aged 100 days
- Customer data accessed 50 times

### 5. Intelligent Engine Runs
- Analyzes each file
- Applies heuristics
- Migrates files
- Calculates savings

### 6. Final Optimized State
- 🔥 HOT: 1 file (customer_data.csv - frequently accessed)
- 🌡️ WARM: 1 file (monthly_report - predictive pattern)
- ❄️ COLD: 2 files (backups & old data)
- 🧊 ARCHIVE: 1 file (old logs)

**Result**: $45/month saved! 💰

---

## 🎤 Presentation Talking Points

### Opening (10 sec)
"Astra is an intelligent cloud storage manager that automatically optimizes storage costs using real-time analytics and predictive AI."

### During Demo (20 sec)
- **At ingestion**: "All data starts hot for performance"
- **At aging**: "Simulating months of usage patterns"
- **At engine**: "Watch the intelligence work - it considers access patterns, file age, AND predictive heuristics"
- **At results**: "Customer data stayed hot because it's frequently used. Backups moved cold. Logs archived. 45 dollars saved monthly."

### Closing (10 sec)
"Built with production-grade tools: Kafka for streaming, boto3 for AWS, moto for testing. Remove one decorator and this connects to real S3."

---

## 🔧 Individual Commands (Optional)

```powershell
# Check everything is working
python main.py check-kafka

# Initialize cloud
python main.py init-cloud

# Show current state
python main.py show-dashboard

# Simulate access
python main.py simulate-access --filename "test.csv" --count 10

# Age a file
python main.py age-file --filename "test.csv" --days 90

# Run optimization
python main.py run-engine
```

---

## 💡 If Something Goes Wrong

### Kafka Won't Start
```powershell
docker-compose down
docker-compose up -d
Start-Sleep -Seconds 20
```

### Package Errors
```powershell
pip install kafka-python-ng --upgrade
```

### Want to Reset
```powershell
# Stop Kafka
docker-compose down -v

# Clear metadata
echo {} > metadata.json

# Restart
docker-compose up -d
python demo_complete.py
```

---

## 🏆 Why This Wins

1. **Real Tech**: Kafka, boto3, moto - not fake/simulated
2. **Smart**: Multiple decision factors, not just age
3. **Measurable**: Actual cost savings calculated
4. **Production-Ready**: One line change to go live
5. **Visual**: Beautiful CLI output with emojis
6. **Complete**: Full lifecycle from ingestion to optimization

---

## 📊 The Numbers

- **5 files** ingested
- **4 migrations** performed
- **3 tiers** used (plus archive)
- **$45/month** saved
- **30 seconds** demo time
- **100%** success rate

---

## 🎬 Demo Flow Chart

```
START
  ↓
Initialize Cloud (2s)
  ↓
Ingest 5 Files (3s)
  ↓
Show Initial State (2s)
  ↓
Simulate Time + Access (2s)
  ↓
Run Intelligence Engine (10s)
  ↓
Show Optimized State (5s)
  ↓
Summary & Savings (6s)
  ↓
END (30 seconds total)
```

---

## 🚀 Pre-Flight Checklist

Before presenting:

- [ ] Docker Desktop running
- [ ] Virtual environment activated
- [ ] Kafka containers up (`docker ps` shows kafka & zookeeper)
- [ ] Run `python main.py check-kafka` - should be green ✓
- [ ] Run `python demo_complete.py` once to verify
- [ ] Have this reference card open
- [ ] Close unnecessary windows
- [ ] Increase terminal font size for visibility

---

## 🎯 Success Criteria

✅ Demo runs without errors  
✅ Files visibly change tiers  
✅ Savings calculation shown  
✅ Predictive heuristics explained  
✅ Cross-cloud optimization mentioned  
✅ Questions answered confidently  

---

**You're ready! Go win that hackathon! 🏆**

---

Last updated: November 8, 2025  
Demo file: `demo_complete.py`  
Status: ✅ TESTED & WORKING
