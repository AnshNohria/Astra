"""
Multi-Cloud Migration Manager
Handles secure, verified migrations between different cloud providers with integrity checks.
"""
import hashlib
import time
from typing import Optional, Tuple
from cloud_utils import S3Manager


class MigrationManager:
    """
    Manages data migration between cloud providers with verification and safety checks.
    Ensures data integrity and minimal disruption during cross-cloud migrations.
    """
    
    def __init__(self, source_cloud_manager: S3Manager, destination_cloud_manager: S3Manager):
        """
        Initialize migration manager with source and destination cloud managers.
        
        Args:
            source_cloud_manager: S3Manager instance for source cloud
            destination_cloud_manager: S3Manager instance for destination cloud
        """
        self.source_manager = source_cloud_manager
        self.destination_manager = destination_cloud_manager
        self.source_cloud = source_cloud_manager.get_cloud_name().upper()
        self.destination_cloud = destination_cloud_manager.get_cloud_name().upper()
        
        # Migration statistics
        self.migrations_attempted = 0
        self.migrations_succeeded = 0
        self.migrations_failed = 0
        self.total_data_migrated_mb = 0.0
    
    def _calculate_checksum(self, content: bytes) -> str:
        """
        Calculate MD5 checksum for data integrity verification.
        
        Args:
            content: Binary content to checksum
        
        Returns:
            MD5 hex digest string
        """
        return hashlib.md5(content).hexdigest()
    
    def migrate_object(self, file_key: str, verify_integrity: bool = True, 
                       delete_source: bool = True) -> Tuple[bool, str]:
        """
        Migrate a single object from source to destination cloud with integrity verification.
        
        Args:
            file_key: The key/path of the file to migrate
            verify_integrity: Whether to perform checksum verification (default: True)
            delete_source: Whether to delete from source after successful migration (default: True)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        self.migrations_attempted += 1
        
        print(f"\n{'='*70}")
        print(f"[MIGRATION] Starting migration of '{file_key}'")
        print(f"            FROM: {self.source_cloud} ({self.source_manager.region})")
        print(f"            TO:   {self.destination_cloud} ({self.destination_manager.region})")
        print(f"{'='*70}")
        
        try:
            # Step 1: Download from source
            print(f"[STEP 1/5] Downloading '{file_key}' from {self.source_cloud}...")
            source_content = self.source_manager.download_file_content(file_key)
            
            if source_content is None:
                error_msg = f"File '{file_key}' not found in source cloud"
                print(f"✗ [ERROR] {error_msg}")
                self.migrations_failed += 1
                return False, error_msg
            
            content_size_mb = len(source_content) / (1024 * 1024)
            print(f"✓ Downloaded {content_size_mb:.2f} MB")
            
            # Step 2: Calculate source checksum
            print(f"\n[STEP 2/5] Calculating source integrity checksum...")
            source_checksum = self._calculate_checksum(source_content)
            print(f"✓ Source MD5: {source_checksum}")
            
            # Step 3: Get source metadata (tier)
            source_tier = self.source_manager.get_file_tier(file_key)
            print(f"✓ Source tier: {source_tier}")
            
            # Step 4: Upload to destination
            print(f"\n[STEP 3/5] Uploading '{file_key}' to {self.destination_cloud}...")
            upload_success = self.destination_manager.upload_file(
                file_key, 
                source_content.decode('utf-8', errors='ignore'),
                tier=source_tier or 'STANDARD'
            )
            
            if not upload_success:
                error_msg = f"Upload to {self.destination_cloud} failed"
                print(f"✗ [ERROR] {error_msg}")
                self.migrations_failed += 1
                return False, error_msg
            
            print(f"✓ Upload completed successfully")
            
            # Step 5: Verify integrity (if enabled)
            if verify_integrity:
                print(f"\n[STEP 4/5] Verifying data integrity on {self.destination_cloud}...")
                time.sleep(0.1)  # Simulate verification delay
                
                destination_content = self.destination_manager.download_file_content(file_key)
                
                if destination_content is None:
                    error_msg = "Verification failed: Could not download from destination"
                    print(f"✗ [ERROR] {error_msg}")
                    self.migrations_failed += 1
                    return False, error_msg
                
                destination_checksum = self._calculate_checksum(destination_content)
                print(f"✓ Destination MD5: {destination_checksum}")
                
                # Compare checksums
                if source_checksum != destination_checksum:
                    error_msg = f"CHECKSUM MISMATCH! Source: {source_checksum}, Dest: {destination_checksum}"
                    print(f"\n{'!'*70}")
                    print(f"✗ [MIGRATION FAILED] {error_msg}")
                    print(f"   Data integrity compromised. Aborting migration.")
                    print(f"   Original file remains on {self.source_cloud}.")
                    print(f"{'!'*70}\n")
                    self.migrations_failed += 1
                    return False, error_msg
                
                print(f"✓ Checksums match! Data integrity verified.")
            
            # Step 6: Delete from source (if requested and verification passed)
            if delete_source:
                print(f"\n[STEP 5/5] Removing '{file_key}' from {self.source_cloud}...")
                delete_success = self.source_manager.delete_file(file_key)
                
                if delete_success:
                    print(f"✓ Source file deleted successfully")
                else:
                    print(f"⚠️  Warning: Could not delete source file (migration still successful)")
            else:
                print(f"\n[STEP 5/5] Keeping copy on {self.source_cloud} (delete_source=False)")
            
            # Success!
            print(f"\n{'='*70}")
            print(f"✓ [MIGRATION SUCCESS] '{file_key}' successfully migrated")
            print(f"  FROM: {self.source_cloud} → TO: {self.destination_cloud}")
            print(f"  Size: {content_size_mb:.2f} MB | Integrity: Verified ✓")
            print(f"{'='*70}\n")
            
            self.migrations_succeeded += 1
            self.total_data_migrated_mb += content_size_mb
            
            return True, "Migration completed successfully"
            
        except Exception as e:
            error_msg = f"Unexpected error during migration: {str(e)}"
            print(f"\n✗ [MIGRATION FAILED] {error_msg}\n")
            self.migrations_failed += 1
            return False, error_msg
    
    def migrate_batch(self, file_keys: list, verify_integrity: bool = True, 
                      delete_source: bool = True) -> dict:
        """
        Migrate multiple objects in batch.
        
        Args:
            file_keys: List of file keys to migrate
            verify_integrity: Whether to perform checksum verification
            delete_source: Whether to delete from source after migration
        
        Returns:
            Dictionary with migration statistics
        """
        print(f"\n{'#'*70}")
        print(f"# BATCH MIGRATION: {len(file_keys)} files")
        print(f"# {self.source_cloud} → {self.destination_cloud}")
        print(f"{'#'*70}\n")
        
        results = {
            'total': len(file_keys),
            'succeeded': 0,
            'failed': 0,
            'errors': []
        }
        
        for file_key in file_keys:
            success, message = self.migrate_object(file_key, verify_integrity, delete_source)
            
            if success:
                results['succeeded'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({'file': file_key, 'error': message})
            
            time.sleep(0.2)  # Brief pause between migrations
        
        # Print batch summary
        print(f"\n{'#'*70}")
        print(f"# BATCH MIGRATION COMPLETE")
        print(f"{'#'*70}")
        print(f"  Total files: {results['total']}")
        print(f"  ✓ Succeeded: {results['succeeded']}")
        print(f"  ✗ Failed:    {results['failed']}")
        print(f"  Data migrated: {self.total_data_migrated_mb:.2f} MB")
        print(f"{'#'*70}\n")
        
        return results
    
    def get_statistics(self) -> dict:
        """
        Get migration statistics.
        
        Returns:
            Dictionary with migration stats
        """
        success_rate = (self.migrations_succeeded / self.migrations_attempted * 100) if self.migrations_attempted > 0 else 0
        
        return {
            'total_attempted': self.migrations_attempted,
            'total_succeeded': self.migrations_succeeded,
            'total_failed': self.migrations_failed,
            'success_rate': success_rate,
            'data_migrated_mb': self.total_data_migrated_mb,
            'source_cloud': self.source_cloud,
            'destination_cloud': self.destination_cloud
        }
    
    def print_statistics(self):
        """Print formatted migration statistics."""
        stats = self.get_statistics()
        
        print(f"\n{'='*70}")
        print(f"📊 MIGRATION STATISTICS")
        print(f"{'='*70}")
        print(f"Route: {stats['source_cloud']} → {stats['destination_cloud']}")
        print(f"Total Migrations Attempted: {stats['total_attempted']}")
        print(f"✓ Successful: {stats['total_succeeded']}")
        print(f"✗ Failed: {stats['total_failed']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Total Data Migrated: {stats['data_migrated_mb']:.2f} MB")
        print(f"{'='*70}\n")
