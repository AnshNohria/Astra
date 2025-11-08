"""
Complete Demo Script - Demonstrates all Astra functionality
This script runs the full demo without requiring a separate consumer terminal
"""
import sys
import time
try:
    from moto import mock_aws
except ImportError:
    from moto import mock_s3 as mock_aws
from cloud_utils import S3Manager
from engine import TieringEngine
import json
from datetime import datetime, timedelta


@mock_aws
def run_complete_demo():
    """Run the complete demonstration of Astra's capabilities"""
    
    print("\n" + "="*70)
    print("🚀 ASTRA - INTELLIGENT CLOUD STORAGE MANAGER")
    print("    Complete Demonstration")
    print("="*70 + "\n")
    
    # Step 1: Initialize Cloud Environment
    print("📍 STEP 1: Initializing Cloud Environment")
    print("-" * 70)
    s3_manager = S3Manager()
    print("✓ S3 bucket created and ready\n")
    time.sleep(1)
    
    # Step 2: Simulate Data Ingestion (instead of Kafka)
    print("📍 STEP 2: Ingesting Files (Simulating Kafka Stream)")
    print("-" * 70)
    
    files_to_ingest = [
        ("customer_data.csv", 2.5, "Customer database - frequently accessed"),
        ("monthly_report_november.pdf", 0.8, "Monthly financial report"),
        ("backup_archive_Q3.zip", 15.0, "Quarterly backup archive"),
        ("temp_processing_logs.log", 0.2, "Temporary processing logs"),
        ("data.csv", 2.0, "Sample data file")
    ]
    
    metadata = {}
    
    for filename, size_gb, description in files_to_ingest:
        print(f"📤 Ingesting: {filename} ({size_gb} GB)")
        print(f"   Description: {description}")
        
        # Upload to S3
        s3_manager.upload_file(filename, f"mock-data-{size_gb}GB", tier='STANDARD')
        
        # Add to metadata
        metadata[filename] = {
            'access_count': 0,
            'created_timestamp': datetime.now().isoformat(),
            'last_accessed_timestamp': datetime.now().isoformat()
        }
        
        print(f"   ✓ Uploaded to HOT tier (S3 STANDARD)\n")
        time.sleep(0.5)
    
    # Save metadata
    with open('metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    print(f"✓ Successfully ingested {len(files_to_ingest)} files\n")
    time.sleep(1)
    
    # Step 3: Show Initial Dashboard
    print("📍 STEP 3: Initial Storage State")
    print("-" * 70)
    show_dashboard(s3_manager, metadata)
    time.sleep(2)
    
    # Step 4: Simulate Time Passage and Access Patterns
    print("\n📍 STEP 4: Simulating Time Passage and Access Patterns")
    print("-" * 70)
    
    # Age some files
    print("⏰ Aging files to simulate passage of time...")
    metadata["backup_archive_Q3.zip"]["last_accessed_timestamp"] = (
        datetime.now() - timedelta(days=120)
    ).isoformat()
    print("   • backup_archive_Q3.zip aged by 120 days")
    
    metadata["temp_processing_logs.log"]["last_accessed_timestamp"] = (
        datetime.now() - timedelta(days=200)
    ).isoformat()
    print("   • temp_processing_logs.log aged by 200 days")
    
    metadata["data.csv"]["last_accessed_timestamp"] = (
        datetime.now() - timedelta(days=100)
    ).isoformat()
    print("   • data.csv aged by 100 days")
    
    # Simulate frequent access to customer data
    print("\n🔍 Simulating frequent access to customer_data.csv...")
    metadata["customer_data.csv"]["access_count"] = 50
    metadata["customer_data.csv"]["last_accessed_timestamp"] = datetime.now().isoformat()
    print("   • customer_data.csv accessed 50 times (keeps it HOT!)\n")
    
    # Save updated metadata
    with open('metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    time.sleep(1)
    
    # Step 5: Run Intelligent Tiering Engine
    print("\n📍 STEP 5: Running Intelligent Tiering Engine")
    print("-" * 70)
    engine = TieringEngine(s3_manager)
    engine.run_tiering_logic()
    time.sleep(2)
    
    # Step 6: Show Final Optimized State
    print("\n📍 STEP 6: Final Optimized Storage State")
    print("-" * 70)
    
    # Reload metadata after engine run
    with open('metadata.json', 'r') as f:
        metadata = json.load(f)
    
    show_dashboard(s3_manager, metadata)
    
    # Step 7: Summary
    print("\n" + "="*70)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("="*70)
    print("\n📊 Key Achievements:")
    print("   ✓ Demonstrated real-time data ingestion")
    print("   ✓ Applied intelligent tiering based on access patterns")
    print("   ✓ Used predictive heuristics for file categorization")
    print("   ✓ Calculated cost savings from optimization")
    print("   ✓ Showed cross-cloud migration opportunities")
    print("\n💡 Production Ready:")
    print("   • Remove @mock_aws decorators")
    print("   • Connect to real S3")
    print("   • Deploy to AWS Lambda or EKS")
    print("   • Add web UI for monitoring")
    print("\n" + "="*70 + "\n")


def show_dashboard(s3_manager, metadata):
    """Display formatted dashboard of all files"""
    all_files = s3_manager.list_all_files()
    
    if not all_files:
        print("ℹ️  No files in storage yet.\n")
        return
    
    print(f"\n{'FILE NAME':<40} {'TIER':<15} {'ACCESSES':<12} {'LAST ACCESS':<20}")
    print("-" * 87)
    
    tier_distribution = {'hot': 0, 'warm': 0, 'cold': 0, 'archive': 0}
    total_accesses = 0
    
    for file_key in sorted(all_files):
        tier = s3_manager.get_file_tier(file_key)
        tier_name = get_tier_display_name(tier)
        
        file_meta = metadata.get(file_key, {})
        access_count = file_meta.get('access_count', 0)
        last_accessed = file_meta.get('last_accessed_timestamp', 'Never')
        
        if last_accessed != 'Never':
            try:
                last_access_dt = datetime.fromisoformat(last_accessed)
                last_accessed = last_access_dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        tier_key = get_tier_name(tier)
        tier_distribution[tier_key] += 1
        total_accesses += access_count
        
        tier_colored = colorize_tier(tier_name)
        file_display = file_key[:37] + "..." if len(file_key) > 40 else file_key
        
        print(f"{file_display:<40} {tier_colored:<24} {access_count:<12} {last_accessed:<20}")
    
    print("\n" + "="*70)
    print("📈 STORAGE STATISTICS")
    print("="*70)
    print(f"Total Files: {len(all_files)}")
    print(f"Total Accesses: {total_accesses}")
    print(f"\nTier Distribution:")
    print(f"  🔥 HOT (STANDARD):        {tier_distribution['hot']} files")
    print(f"  🌡️  WARM (STANDARD_IA):    {tier_distribution['warm']} files")
    print(f"  ❄️  COLD (GLACIER):        {tier_distribution['cold']} files")
    print(f"  🧊 ARCHIVE (DEEP_ARCHIVE): {tier_distribution['archive']} files")
    print("="*70 + "\n")


def get_tier_display_name(s3_tier):
    """Get human-readable tier name"""
    tier_map = {
        'STANDARD': 'HOT',
        'STANDARD_IA': 'WARM',
        'GLACIER': 'COLD',
        'DEEP_ARCHIVE': 'ARCHIVE'
    }
    return tier_map.get(s3_tier, 'HOT')


def get_tier_name(s3_tier):
    """Get tier key for statistics"""
    tier_map = {
        'STANDARD': 'hot',
        'STANDARD_IA': 'warm',
        'GLACIER': 'cold',
        'DEEP_ARCHIVE': 'archive'
    }
    return tier_map.get(s3_tier, 'hot')


def colorize_tier(tier_name):
    """Add visual indicators to tier names"""
    colors = {
        'HOT': '🔥 HOT',
        'WARM': '🌡️  WARM',
        'COLD': '❄️  COLD',
        'ARCHIVE': '🧊 ARCHIVE'
    }
    return colors.get(tier_name, tier_name)


if __name__ == '__main__':
    try:
        run_complete_demo()
    except KeyboardInterrupt:
        print("\n\n🛑 Demo stopped by user\n")
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        import traceback
        traceback.print_exc()
