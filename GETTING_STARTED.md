# ⚡ Getting Started with Astra

Welcome to **Astra** - Your Intelligent Cloud Storage Manager! This guide will get you up and running in under 5 minutes.

## 🎯 What You'll Build

By following this guide, you'll set up a complete intelligent data management system that:
- Ingests data through **real Kafka streams**
- Stores data in **mocked AWS S3**
- Automatically **optimizes storage costs**
- Provides **predictive tiering** based on access patterns

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ **Python 3.8+** installed
- ✅ **Docker Desktop** installed and running
- ✅ **Git** (to clone the repository)
- ✅ A terminal (PowerShell, CMD, or Git Bash)

## 🚀 Installation (3 Minutes)

### Step 1: Clone and Navigate
```powershell
git clone https://github.com/AnshNohria/Astra.git
cd Astra
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

Expected output:
```
Successfully installed boto3-1.34.144 moto-5.0.0 kafka-python-2.0.2 click-8.1.7
```

### Step 3: Start Kafka
```powershell
docker-compose up -d
```

Wait 20 seconds for Kafka to fully initialize:
```powershell
Start-Sleep -Seconds 20  # PowerShell
# or
timeout 20               # CMD
```

### Step 4: Verify Setup
```powershell
python main.py check-kafka
```

If you see `✓ Kafka is running and accessible`, you're ready to go! 🎉

**Troubleshooting**: If Kafka check fails, run our verification script:
```powershell
.\verify_setup.ps1
```

## 🎮 Your First Demo (2 Minutes)

### Terminal Setup

**Open TWO terminal windows** and navigate to the Astra directory in both.

### Terminal 1: Start the Event Consumer
```powershell
python main.py listen-stream
```

You should see:
```
🎧 KAFKA EVENT CONSUMER STARTING
✓ Connected to Kafka successfully
⏳ Waiting for events...
```

**Keep this running!** 

### Terminal 2: Run the Demo
```powershell
# Initialize the cloud environment
python main.py init-cloud

# Ingest some data (watch Terminal 1!)
python main.py generate-event --filename "customer_data.csv" --size 3.0
python main.py generate-event --filename "backup_old.zip" --size 10.0

# View current state
python main.py show-dashboard
```

**What you'll see**: Both files in HOT tier, ready for optimization!

### Make Files "Old" (Simulate Time)
```powershell
python main.py age-file --filename "backup_old.zip" --days 120
```

### Run the Intelligence Engine
```powershell
python main.py run-engine
```

**Watch the magic happen!** The engine will:
- Analyze access patterns
- Apply predictive heuristics
- Move old backups to COLD storage
- Calculate cost savings

### View the Results
```powershell
python main.py show-dashboard
```

You'll see `backup_old.zip` has moved to ❄️ COLD tier, and the dashboard shows estimated savings!

## 📚 What's Next?

Now that you have the basics working, explore:

### Learn More
- 📖 **[README.md](README.md)** - Full project documentation
- 🏗️ **[ARCHITECTURE.md](ARCHITECTURE.md)** - Deep dive into design decisions
- 🎬 **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Complete presentation guide

### Try Advanced Features

#### Simulate Heavy Access
```powershell
python main.py simulate-access --filename "customer_data.csv" --count 50
python main.py run-engine
# Customer data will STAY in HOT tier due to high access count!
```

#### Generate More Events
```powershell
python main.py generate-event --filename "monthly_report_nov.pdf" --size 0.5
python main.py generate-event --filename "temp_logs.log" --size 0.1
```

#### Check Predictive Tiering
After generating the above events and running the engine:
- `monthly_report_*` → Moves to WARM (predicted regular access)
- `*.log` → Moves to ARCHIVE (logs rarely needed)

## 🎯 Key Commands Reference

| Command | What It Does | When to Use |
|---------|--------------|-------------|
| `init-cloud` | Set up S3 bucket | First time setup |
| `listen-stream` | Start Kafka consumer | Before generating events |
| `generate-event` | Send data to stream | Simulate data ingestion |
| `show-dashboard` | View all files | See current state |
| `run-engine` | Optimize storage | Apply intelligence |
| `age-file` | Make file older | Test tiering logic |
| `check-kafka` | Verify Kafka | Troubleshooting |

## 🛑 Stopping the System

When you're done:

1. **Stop the consumer** (Terminal 1): Press `Ctrl+C`
2. **Stop Kafka**:
   ```powershell
   docker-compose down
   ```

To completely clean up (removes all data):
```powershell
docker-compose down -v
```

## 💡 Tips for Success

### During Development
- Always have the consumer running in a separate terminal
- Use `show-dashboard` frequently to see changes
- `age-file` is your friend for testing time-based rules

### For Demos/Presentations
- Practice the sequence a few times
- Have both terminals visible side-by-side
- Narrate what's happening ("Watch the consumer ingest this file...")
- Emphasize cost savings in the summary

### For Learning
- Read through `engine.py` to understand the decision logic
- Modify the tiering thresholds (HOT_TO_WARM_DAYS, etc.)
- Add your own predictive heuristics
- Try connecting to real S3 (remove `@mock_aws`)

## 🐛 Common Issues

### "Cannot connect to Kafka"
**Solution**: 
```powershell
docker-compose down
docker-compose up -d
Start-Sleep -Seconds 20
python main.py check-kafka
```

### "Module not found: click/boto3/moto"
**Solution**:
```powershell
pip install -r requirements.txt --upgrade
```

### Docker not starting
**Solution**: 
- Open Docker Desktop application
- Wait for it to fully start (whale icon stops animating)
- Try `docker ps` to verify

### Consumer not receiving events
**Solution**:
- Stop consumer (Ctrl+C)
- Restart: `python main.py listen-stream`
- Try generating event again

## 🎓 Learning Path

### Beginner
1. ✅ Follow this guide
2. ✅ Run the demo successfully
3. ✅ Understand each command's purpose

### Intermediate
1. 📖 Read ARCHITECTURE.md
2. 🔍 Explore the source code
3. ✏️ Modify tiering rules
4. 🧪 Add new file patterns

### Advanced
1. 🤖 Implement ML-based predictions
2. 🌐 Add a web dashboard (Flask + React)
3. ☁️ Connect to real AWS S3
4. 🔄 Deploy to production (EKS/Lambda)

## 📞 Need Help?

- **Documentation**: Check README.md and ARCHITECTURE.md
- **GitHub Issues**: Report bugs or request features
- **Source Code**: All files are well-commented

## 🎉 You're Ready!

Congratulations! You now have a professional-grade intelligent storage manager running locally. 

**Next steps**:
- Experiment with different file patterns
- Try the full demo sequence
- Read the architecture document
- Consider production deployment

Happy optimizing! 🚀

---

**Project**: Astra - Intelligent Cloud Storage Manager  
**Author**: Ansh Nohria  
**License**: MIT  
**Repository**: https://github.com/AnshNohria/Astra
