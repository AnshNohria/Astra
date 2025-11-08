"""
Intelligent Cloud Storage Manager - CLI Interface
A professional-grade data lifecycle management system with real-time streaming
and multi-cloud migration capabilities.
"""
import click
import json
from datetime import datetime, timedelta
from moto import mock_aws
from cloud_utils import S3Manager
from engine import TieringEngine
from migration_manager import MigrationManager
from streaming import produce_new_file_event, start_event_consumer, check_kafka_connection


@click.group()
def cli():
    """
    🚀 Intelligent Cloud Storage Manager
    
    A sophisticated CLI for managing cloud storage with intelligent tiering,
    real-time data streaming, and cost optimization.
    """
    pass


@cli.command()
@mock_aws
def init_cloud():
    """Initialize the cloud storage environment (mocked S3)."""
    click.echo("\n" + "="*70)
    click.echo("🌩️  INITIALIZING CLOUD ENVIRONMENT")
    click.echo("="*70 + "\n")
    
    s3_manager = S3Manager()
    click.echo("✓ S3 bucket initialized successfully")
    click.echo("✓ Cloud environment ready for operations\n")


@cli.command()
@click.option('--filename', required=True, help='Name of the file to generate event for')
@click.option('--size', default=1.0, help='Size of file in GB')
def generate_event(filename, size):
    """Generate a new file ingestion event to Kafka stream."""
    click.echo(f"\n📤 Generating ingestion event for: {filename}")
    
    if not check_kafka_connection():
        click.echo("\n⚠️  WARNING: Cannot connect to Kafka broker")
        click.echo("Please start Kafka first: docker-compose up -d\n")
        return
    
    success = produce_new_file_event(filename, size)
    
    if success:
        click.echo("✓ Event sent successfully\n")
    else:
        click.echo("✗ Failed to send event\n")


@cli.command()
@mock_aws
def listen_stream():
    """Start listening to Kafka stream and ingest data in real-time."""
    s3_manager = S3Manager()
    start_event_consumer(s3_manager)


@cli.command()
@mock_aws
def show_dashboard():
    """Display comprehensive dashboard of all files and their status."""
    click.echo("\n" + "="*70)
    click.echo("📊 INTELLIGENT STORAGE DASHBOARD")
    click.echo("="*70 + "\n")
    
    s3_manager = S3Manager()
    
    # Load metadata
    try:
        with open('metadata.json', 'r') as f:
            metadata = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        metadata = {}
    
    # Get all files
    all_files = s3_manager.list_all_files()
    
    if not all_files:
        click.echo("ℹ️  No files in storage yet.")
        click.echo("   Use 'generate-event' to add files via Kafka stream.\n")
        return
    
    # Display header
    click.echo(f"{'FILE NAME':<40} {'TIER':<15} {'ACCESSES':<12} {'LAST ACCESS':<20}")
    click.echo("-" * 70)
    
    # Statistics
    tier_distribution = {'hot': 0, 'warm': 0, 'cold': 0, 'archive': 0}
    total_accesses = 0
    
    # Display each file
    for file_key in sorted(all_files):
        tier = s3_manager.get_file_tier(file_key)
        tier_name = _get_tier_display_name(tier)
        
        # Get metadata
        file_meta = metadata.get(file_key, {})
        access_count = file_meta.get('access_count', 0)
        last_accessed = file_meta.get('last_accessed_timestamp', 'Never')
        
        if last_accessed != 'Never':
            try:
                last_access_dt = datetime.fromisoformat(last_accessed)
                last_accessed = last_access_dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        # Update statistics
        tier_key = _get_tier_name(tier)
        tier_distribution[tier_key] += 1
        total_accesses += access_count
        
        # Color-coded tier display
        tier_colored = _colorize_tier(tier_name)
        
        # Display row
        file_display = file_key[:37] + "..." if len(file_key) > 40 else file_key
        click.echo(f"{file_display:<40} {tier_colored:<24} {access_count:<12} {last_accessed:<20}")
    
    # Display summary statistics
    click.echo("\n" + "="*70)
    click.echo("📈 STORAGE STATISTICS")
    click.echo("="*70)
    click.echo(f"Total Files: {len(all_files)}")
    click.echo(f"Total Accesses: {total_accesses}")
    click.echo(f"\nTier Distribution:")
    click.echo(f"  🔥 HOT (STANDARD):        {tier_distribution['hot']} files")
    click.echo(f"  🌡️  WARM (STANDARD_IA):    {tier_distribution['warm']} files")
    click.echo(f"  ❄️  COLD (GLACIER):        {tier_distribution['cold']} files")
    click.echo(f"  🧊 ARCHIVE (DEEP_ARCHIVE): {tier_distribution['archive']} files")
    click.echo("="*70 + "\n")


@cli.command()
@mock_aws
def run_engine():
    """Execute the intelligent tiering engine to optimize storage."""
    s3_manager = S3Manager()
    engine = TieringEngine(s3_manager)
    engine.run_tiering_logic()


@cli.command()
@mock_aws
@click.option('--filename', required=True, help='Name of the file to simulate access')
@click.option('--count', default=1, help='Number of accesses to simulate')
def simulate_access(filename, count):
    """Simulate file access to update metadata."""
    click.echo(f"\n🔍 Simulating {count} access(es) to: {filename}")
    
    # Load metadata
    try:
        with open('metadata.json', 'r') as f:
            metadata = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        click.echo("✗ Metadata file not found or corrupted\n")
        return
    
    if filename not in metadata:
        click.echo(f"✗ File '{filename}' not found in metadata\n")
        return
    
    # Update access count
    metadata[filename]['access_count'] = metadata[filename].get('access_count', 0) + count
    metadata[filename]['last_accessed_timestamp'] = datetime.now().isoformat()
    
    # Save metadata
    with open('metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    click.echo(f"✓ Updated access metadata for '{filename}'")
    click.echo(f"  New access count: {metadata[filename]['access_count']}\n")


@cli.command()
def check_kafka():
    """Check if Kafka is running and accessible."""
    click.echo("\n🔍 Checking Kafka connection...\n")
    
    if check_kafka_connection():
        click.echo("✓ Kafka is running and accessible")
        click.echo(f"  Broker: localhost:9092\n")
    else:
        click.echo("✗ Cannot connect to Kafka")
        click.echo("  Please start Kafka: docker-compose up -d\n")


@cli.command()
@click.option('--filename', required=True, help='Filename to age')
@click.option('--days', required=True, type=int, help='Number of days to age the file')
def age_file(filename, days):
    """Manually age a file by updating its last access timestamp."""
    click.echo(f"\n⏰ Aging file '{filename}' by {days} days...")
    
    # Load metadata
    try:
        with open('metadata.json', 'r') as f:
            metadata = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        click.echo("✗ Metadata file not found or corrupted\n")
        return
    
    if filename not in metadata:
        click.echo(f"✗ File '{filename}' not found in metadata\n")
        return
    
    # Update timestamp
    old_timestamp = datetime.fromisoformat(metadata[filename]['last_accessed_timestamp'])
    new_timestamp = old_timestamp - timedelta(days=days)
    metadata[filename]['last_accessed_timestamp'] = new_timestamp.isoformat()
    
    # Save metadata
    with open('metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    click.echo(f"✓ File aged successfully")
    click.echo(f"  Old date: {old_timestamp.strftime('%Y-%m-%d')}")
    click.echo(f"  New date: {new_timestamp.strftime('%Y-%m-%d')}\n")


def _get_tier_display_name(s3_tier: str) -> str:
    """Get human-readable tier name."""
    tier_map = {
        'STANDARD': 'HOT',
        'STANDARD_IA': 'WARM',
        'GLACIER': 'COLD',
        'DEEP_ARCHIVE': 'ARCHIVE'
    }
    return tier_map.get(s3_tier, 'HOT')


def _get_tier_name(s3_tier: str) -> str:
    """Get tier key for statistics."""
    tier_map = {
        'STANDARD': 'hot',
        'STANDARD_IA': 'warm',
        'GLACIER': 'cold',
        'DEEP_ARCHIVE': 'archive'
    }
    return tier_map.get(s3_tier, 'hot')


def _colorize_tier(tier_name: str) -> str:
    """Add visual indicators to tier names."""
    colors = {
        'HOT': '🔥 HOT',
        'WARM': '🌡️  WARM',
        'COLD': '❄️  COLD',
        'ARCHIVE': '🧊 ARCHIVE'
    }
    return colors.get(tier_name, tier_name)


@cli.command()
@mock_aws
@click.option('--target', default='gcp', help='Target cloud provider (gcp or azure)')
@click.option('--tier', default='GLACIER', help='Only migrate files in this tier or colder')
def migrate_to_cloud(target, tier):
    """Execute cross-cloud migration for cost optimization."""
    click.echo(f"\n🌐 Initiating cross-cloud migration to {target.upper()}...")
    
    s3_manager = S3Manager()
    engine = TieringEngine(s3_manager)
    
    results = engine.run_cross_cloud_migration(target_cloud=target, tier_threshold=tier)
    
    if results.get('migrated', 0) == 0 and results.get('total', 0) == 0:
        click.echo("✓ Migration analysis complete (no files to migrate)\n")
    else:
        click.echo(f"✓ Migration complete: {results.get('succeeded', 0)}/{results.get('total', 0)} files migrated successfully\n")


@cli.command()
@mock_aws
@click.option('--source', required=True, help='Source cloud (aws/gcp/azure)')
@click.option('--dest', required=True, help='Destination cloud (aws/gcp/azure)')
@click.option('--filename', required=True, help='File to migrate')
def migrate_file(source, dest, filename):
    """Migrate a specific file between clouds with verification."""
    click.echo(f"\n📦 Migrating file: {filename}")
    click.echo(f"   Route: {source.upper()} → {dest.upper()}\n")
    
    # Create cloud managers
    source_manager = S3Manager(cloud_name=source, bucket_name=f"astra-{source}-bucket")
    dest_manager = S3Manager(cloud_name=dest, bucket_name=f"astra-{dest}-bucket")
    
    # Create migration manager
    migrator = MigrationManager(source_manager, dest_manager)
    
    # Execute migration
    success, message = migrator.migrate_object(filename, verify_integrity=True, delete_source=True)
    
    if success:
        click.echo(f"✓ Migration successful!\n")
        migrator.print_statistics()
    else:
        click.echo(f"✗ Migration failed: {message}\n")


@cli.command()
@mock_aws
def show_multi_cloud_dashboard():
    """Display files across all cloud providers."""
    click.echo("\n" + "="*70)
    click.echo("☁️  MULTI-CLOUD DASHBOARD")
    click.echo("="*70 + "\n")
    
    clouds = ['aws', 'gcp', 'azure']
    total_files = 0
    
    for cloud in clouds:
        try:
            manager = S3Manager(cloud_name=cloud, bucket_name=f"astra-{cloud}-bucket")
            files = manager.list_all_files()
            
            if files:
                click.echo(f"🌩️  {cloud.upper()} ({manager.region})")
                click.echo("-" * 70)
                
                for file_key in files:
                    tier = manager.get_file_tier(file_key)
                    tier_name = _get_tier_display_name(tier or 'STANDARD')
                    tier_colored = _colorize_tier(tier_name)
                    click.echo(f"   {file_key:<50} {tier_colored}")
                
                click.echo(f"   Total: {len(files)} files\n")
                total_files += len(files)
            else:
                click.echo(f"🌩️  {cloud.upper()} ({manager.region}): No files\n")
        except Exception as e:
            click.echo(f"⚠️  {cloud.upper()}: Error accessing ({str(e)})\n")
    
    click.echo("="*70)
    click.echo(f"Total files across all clouds: {total_files}")
    click.echo("="*70 + "\n")


if __name__ == '__main__':
    cli()
