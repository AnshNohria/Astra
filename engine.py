"""
Intelligent tiering engine with predictive analytics and cost optimization.
Implements data lifecycle management across multiple storage tiers and clouds.
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List
from cloud_utils import S3Manager
from migration_manager import MigrationManager


class TieringEngine:
    """
    Core engine for intelligent data tiering and migration.
    Makes decisions based on access patterns, age, and predictive heuristics.
    """
    
    # Storage tier definitions (hot -> warm -> cold -> archive)
    TIERS = {
        'hot': 'STANDARD',
        'warm': 'STANDARD_IA',
        'cold': 'GLACIER',
        'archive': 'DEEP_ARCHIVE'
    }
    
    # Thresholds for tiering decisions
    HOT_TO_WARM_DAYS = 30
    WARM_TO_COLD_DAYS = 90
    COLD_TO_ARCHIVE_DAYS = 180
    
    def __init__(self, s3_manager: S3Manager, metadata_path: str = "metadata.json"):
        """
        Initialize the tiering engine.
        
        Args:
            s3_manager: S3Manager instance for cloud operations
            metadata_path: Path to metadata JSON file
        """
        self.s3_manager = s3_manager
        self.metadata_path = metadata_path
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load metadata from JSON file."""
        try:
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_metadata(self):
        """Save metadata to JSON file."""
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def _get_days_since_access(self, file_key: str) -> int:
        """
        Calculate days since last access.
        
        Args:
            file_key: File identifier
        
        Returns:
            Number of days since last access
        """
        if file_key not in self.metadata:
            return 0
        
        last_accessed = self.metadata[file_key].get('last_accessed_timestamp')
        if not last_accessed:
            return 0
        
        last_access_date = datetime.fromisoformat(last_accessed)
        return (datetime.now() - last_access_date).days
    
    def _is_frequently_accessed(self, file_key: str, threshold: int = 10) -> bool:
        """
        Check if file is frequently accessed.
        
        Args:
            file_key: File identifier
            threshold: Access count threshold
        
        Returns:
            True if frequently accessed
        """
        if file_key not in self.metadata:
            return False
        return self.metadata[file_key].get('access_count', 0) >= threshold
    
    def _apply_predictive_heuristics(self, file_key: str) -> str:
        """
        Apply predictive rules based on file naming patterns.
        
        Args:
            file_key: File identifier
        
        Returns:
            Recommended tier
        """
        file_lower = file_key.lower()
        
        # Monthly reports - keep warm for quick access
        if 'monthly_report' in file_lower or 'monthly-report' in file_lower:
            return 'warm'
        
        # Yearly archives - move to cold storage
        if 'yearly' in file_lower or 'annual' in file_lower:
            return 'cold'
        
        # Log files - archive aggressively
        if file_lower.endswith('.log') or 'logs' in file_lower:
            return 'archive'
        
        # Backup files - cold storage
        if 'backup' in file_lower or 'bak' in file_lower:
            return 'cold'
        
        # Temp files - can be archived
        if file_lower.startswith('temp') or file_lower.startswith('tmp'):
            return 'cold'
        
        return None  # No heuristic applies
    
    def _determine_target_tier(self, file_key: str, current_tier: str) -> str:
        """
        Determine the optimal tier for a file based on all factors.
        
        Args:
            file_key: File identifier
            current_tier: Current storage tier
        
        Returns:
            Target tier name
        """
        days_since_access = self._get_days_since_access(file_key)
        is_frequent = self._is_frequently_accessed(file_key)
        
        # Frequently accessed files stay hot
        if is_frequent:
            return 'hot'
        
        # Check predictive heuristics first
        predicted_tier = self._apply_predictive_heuristics(file_key)
        if predicted_tier:
            return predicted_tier
        
        # Age-based tiering
        if days_since_access >= self.COLD_TO_ARCHIVE_DAYS:
            return 'archive'
        elif days_since_access >= self.WARM_TO_COLD_DAYS:
            return 'cold'
        elif days_since_access >= self.HOT_TO_WARM_DAYS:
            return 'warm'
        
        return 'hot'
    
    def run_tiering_logic(self):
        """
        Execute the main tiering logic across all files.
        Analyzes current state and performs necessary migrations.
        """
        print("\n" + "="*70)
        print("🔄 STARTING INTELLIGENT TIERING ENGINE")
        print("="*70 + "\n")
        
        # Get all files from S3
        all_files = self.s3_manager.list_all_files()
        
        if not all_files:
            print("ℹ️  No files found in storage. Nothing to process.")
            return
        
        print(f"📊 Analyzing {len(all_files)} files...\n")
        
        migrations_performed = 0
        cost_optimizations = 0
        
        for file_key in all_files:
            # Get current tier
            current_s3_tier = self.s3_manager.get_file_tier(file_key)
            current_tier_name = self._get_tier_name(current_s3_tier)
            
            # Determine optimal tier
            target_tier_name = self._determine_target_tier(file_key, current_tier_name)
            target_s3_tier = self.TIERS[target_tier_name]
            
            # Log analysis
            days_since = self._get_days_since_access(file_key)
            access_count = self.metadata.get(file_key, {}).get('access_count', 0)
            
            print(f"📄 {file_key}")
            print(f"   Current Tier: {current_tier_name.upper()} ({current_s3_tier})")
            print(f"   Access Stats: {access_count} accesses, {days_since} days since last access")
            
            # Check if migration is needed
            if current_s3_tier != target_s3_tier:
                print(f"   🎯 Decision: Migrate to {target_tier_name.upper()} tier")
                
                # Perform migration
                if self.s3_manager.change_file_tier(file_key, target_s3_tier):
                    print(f"   ✓ Successfully migrated to {target_s3_tier}")
                    migrations_performed += 1
                    
                    # Check if this is a cost optimization move
                    if target_tier_name in ['cold', 'archive']:
                        cost_optimizations += 1
                else:
                    print(f"   ✗ Migration failed")
            else:
                print(f"   ✓ Already in optimal tier ({target_tier_name.upper()})")
            
            print()
        
        # Cost optimization simulation (AWS to GCP)
        self._simulate_cross_cloud_optimization()
        
        # Summary
        print("\n" + "="*70)
        print("📈 TIERING ENGINE SUMMARY")
        print("="*70)
        print(f"✓ Files Analyzed: {len(all_files)}")
        print(f"✓ Migrations Performed: {migrations_performed}")
        print(f"✓ Cost Optimizations: {cost_optimizations}")
        print(f"✓ Estimated Monthly Savings: ${self._calculate_savings(cost_optimizations):.2f}")
        print("="*70 + "\n")
        
        self._save_metadata()
    
    def _get_tier_name(self, s3_tier: str) -> str:
        """Convert S3 storage class to tier name."""
        for name, tier in self.TIERS.items():
            if tier == s3_tier:
                return name
        return 'hot'
    
    def _simulate_cross_cloud_optimization(self):
        """
        Simulate cross-cloud cost optimization with actual migration capability.
        In production, this would migrate data to GCP/Azure for cost savings.
        """
        print("☁️  CROSS-CLOUD OPTIMIZATION ANALYSIS")
        print("-" * 70)
        
        # Find candidates for cross-cloud migration
        all_files = self.s3_manager.list_all_files()
        archive_candidates = []
        
        for file_key in all_files:
            tier = self.s3_manager.get_file_tier(file_key)
            if tier in ['GLACIER', 'DEEP_ARCHIVE']:
                archive_candidates.append(file_key)
        
        if archive_candidates:
            print(f"📦 Found {len(archive_candidates)} files in archive tiers")
            print(f"💡 Recommendation: Consider migrating to GCP Coldline/Archive")
            print(f"   Potential Savings: ~30% on storage costs")
            print(f"   Files: {', '.join(archive_candidates[:3])}" + 
                  (f" and {len(archive_candidates)-3} more..." if len(archive_candidates) > 3 else ""))
        else:
            print("ℹ️  No archive-tier files found for cross-cloud optimization")
        
        print()
    
    def run_cross_cloud_migration(self, target_cloud: str = 'gcp', 
                                  tier_threshold: str = 'GLACIER') -> dict:
        """
        Execute actual cross-cloud migration for cost optimization.
        Migrates files in cold/archive tiers to a cheaper cloud provider.
        
        Args:
            target_cloud: Target cloud provider ('gcp' or 'azure')
            tier_threshold: Only migrate files in this tier or colder
        
        Returns:
            Dictionary with migration results
        """
        print(f"\n{'='*70}")
        print(f"☁️  EXECUTING CROSS-CLOUD MIGRATION")
        print(f"{'='*70}\n")
        
        # Create destination cloud manager
        target_manager = S3Manager(
            cloud_name=target_cloud,
            bucket_name=f"astra-{target_cloud}-archive"
        )
        
        # Initialize migration manager
        migrator = MigrationManager(self.s3_manager, target_manager)
        
        # Define cost rule
        aws_cold_cost_per_gb = 0.004  # AWS Glacier
        gcp_cold_cost_per_gb = 0.0025  # GCP Coldline (example)
        
        print(f"💰 Cost Analysis:")
        print(f"   AWS Glacier:     ${aws_cold_cost_per_gb:.4f}/GB/month")
        print(f"   GCP Coldline:    ${gcp_cold_cost_per_gb:.4f}/GB/month")
        print(f"   Potential Savings: {((aws_cold_cost_per_gb - gcp_cold_cost_per_gb) / aws_cold_cost_per_gb * 100):.1f}%\n")
        
        # Find files to migrate
        all_files = self.s3_manager.list_all_files()
        files_to_migrate = []
        
        cold_tiers = ['GLACIER', 'DEEP_ARCHIVE'] if tier_threshold == 'GLACIER' else ['DEEP_ARCHIVE']
        
        for file_key in all_files:
            tier = self.s3_manager.get_file_tier(file_key)
            if tier in cold_tiers:
                files_to_migrate.append(file_key)
        
        if not files_to_migrate:
            print(f"ℹ️  No files found in {', '.join(cold_tiers)} tiers for migration\n")
            return {'migrated': 0, 'success': True}
        
        print(f"📋 Migration Plan:")
        print(f"   Files to migrate: {len(files_to_migrate)}")
        print(f"   Source: {self.s3_manager.get_cloud_name().upper()}")
        print(f"   Destination: {target_cloud.upper()}")
        print(f"   Tier threshold: {tier_threshold}\n")
        
        # Execute migration
        results = migrator.migrate_batch(
            files_to_migrate,
            verify_integrity=True,
            delete_source=True
        )
        
        # Print statistics
        migrator.print_statistics()
        
        return results
    
    def _calculate_savings(self, optimizations: int) -> float:
        """
        Calculate estimated monthly savings from optimizations.
        
        Args:
            optimizations: Number of cost optimizations performed
        
        Returns:
            Estimated monthly savings in dollars
        """
        # Rough estimate: ~$15 saved per file moved to cheaper tier
        return optimizations * 15.0
    
    def update_access_metadata(self, file_key: str):
        """
        Update access metadata for a file.
        
        Args:
            file_key: File identifier
        """
        if file_key not in self.metadata:
            self.metadata[file_key] = {
                'access_count': 0,
                'created_timestamp': datetime.now().isoformat(),
                'last_accessed_timestamp': datetime.now().isoformat()
            }
        
        self.metadata[file_key]['access_count'] += 1
        self.metadata[file_key]['last_accessed_timestamp'] = datetime.now().isoformat()
        self._save_metadata()
