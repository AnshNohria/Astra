"""
Astra Web Server - Interactive Dashboard
Flask-based web interface for intelligent cloud storage management
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# IMPORTANT: Start moto mocking BEFORE importing boto3-dependent modules
# Set up mock AWS credentials to avoid "Unable to locate credentials" error
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Start moto mocking
from moto import mock_aws
mock_aws_decorator = mock_aws()
mock_aws_decorator.start()

from cloud_utils import S3Manager
from engine import TieringEngine
from migration_manager import MigrationManager
import json
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# Global state
current_cloud = 'aws'
managers = {}
engine = None

def initialize_managers():
    """Initialize cloud managers for all three clouds"""
    global managers, engine
    
    managers = {
        'aws': S3Manager(cloud_name='aws', bucket_name='astra-demo-aws'),
        'gcp': S3Manager(cloud_name='gcp', bucket_name='astra-demo-gcp'),
        'azure': S3Manager(cloud_name='azure', bucket_name='astra-demo-azure')
    }
    
    # Buckets are created automatically in __init__
    
    # Initialize engine with AWS as primary
    engine = TieringEngine(managers['aws'])

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def initialize():
    """Initialize the system"""
    try:
        # Managers will use the mocked AWS environment we set up with env vars
        initialize_managers()
        return jsonify({
            'status': 'success',
            'message': 'System initialized successfully',
            'clouds': ['aws', 'gcp', 'azure']
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/clouds', methods=['GET'])
def get_clouds():
    """Get all cloud providers and their files"""
    try:
        clouds_data = {}
        
        for cloud, manager in managers.items():
            # Use list_objects_v2 directly since list_files doesn't exist
            response = manager.s3_client.list_objects_v2(Bucket=manager.bucket_name)
            files = response.get('Contents', [])
            
            clouds_data[cloud] = {
                'name': cloud.upper(),
                'region': manager.region,
                'files': [
                    {
                        'name': f['Key'],
                        'size': f['Size'],
                        'tier': f.get('StorageClass', 'STANDARD'),
                        'lastModified': f['LastModified'].isoformat() if 'LastModified' in f else None
                    }
                    for f in files
                ]
            }
        
        return jsonify(clouds_data)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file to a cloud"""
    try:
        data = request.json
        cloud = data.get('cloud', 'aws')
        filename = data.get('filename')
        size = data.get('size', 1024 * 1024)  # Default 1MB
        
        # Generate dummy content
        content = f"Sample content for {filename}"
        
        # Upload to selected cloud
        manager = managers[cloud]
        manager.upload_file(filename, content, tier='STANDARD')
        
        return jsonify({
            'status': 'success',
            'message': f'File {filename} uploaded to {cloud.upper()}',
            'filename': filename,
            'cloud': cloud
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/ingest-sample', methods=['POST'])
def ingest_sample_files():
    """Ingest sample files for demo"""
    try:
        # Check if managers are initialized
        if not managers or 'aws' not in managers:
            return jsonify({
                'status': 'error',
                'message': 'System not initialized. Please click "Initialize System" first.'
            }), 400
        
        sample_files = [
            ('customer_transactions.csv', 5 * 1024 * 1024),
            ('financial_records_2023.csv', 8 * 1024 * 1024),
            ('archived_logs_2022.log', 12 * 1024 * 1024),
            ('backup_database_Q2.zip', 15 * 1024 * 1024),
            ('monthly_report_october.pdf', 2 * 1024 * 1024),
        ]
        
        manager = managers['aws']
        
        for filename, size in sample_files:
            content = f"Sample content for {filename}\n" * (size // 50)
            manager.upload_file(filename, content, tier='STANDARD')
        
        return jsonify({
            'status': 'success',
            'message': f'{len(sample_files)} sample files ingested to AWS',
            'files': [f[0] for f in sample_files]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/tier', methods=['POST'])
def run_tiering():
    """Run intelligent tiering analysis"""
    try:
        data = request.json
        cloud = data.get('cloud', 'aws')
        
        manager = managers[cloud]
        response = manager.s3_client.list_objects_v2(Bucket=manager.bucket_name)
        files = response.get('Contents', [])
        
        # Run tiering analysis
        tiering_results = []
        for file in files:
            filename = file['Key']
            
            # Simple tiering logic for demo
            if 'log' in filename.lower() or 'archive' in filename.lower():
                recommended_tier = 'GLACIER'
                reason = 'Archive data - cold storage'
            elif 'backup' in filename.lower() or 'report' in filename.lower():
                recommended_tier = 'STANDARD_IA'
                reason = 'Infrequent access pattern'
            else:
                recommended_tier = 'STANDARD'
                reason = 'Frequently accessed'
            
            # Apply the tier change
            if recommended_tier != file.get('StorageClass', 'STANDARD'):
                manager.change_file_tier(filename, recommended_tier)
            
            tiering_results.append({
                'filename': filename,
                'current_tier': file.get('StorageClass', 'STANDARD'),
                'recommended_tier': recommended_tier,
                'cost_savings': 0.05,  # Demo value
                'reason': reason
            })
        
        return jsonify({
            'status': 'success',
            'results': tiering_results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/migrate', methods=['POST'])
def migrate_file():
    """Migrate a file between clouds"""
    try:
        data = request.json
        filename = data.get('filename')
        source_cloud = data.get('source')
        dest_cloud = data.get('destination')
        
        source_manager = managers[source_cloud]
        dest_manager = managers[dest_cloud]
        
        # Create migration manager
        migration_mgr = MigrationManager(source_manager, dest_manager)
        
        # Perform migration
        success, message = migration_mgr.migrate_object(filename, delete_source=True)
        
        if success:
            stats = migration_mgr.get_statistics()
            return jsonify({
                'status': 'success',
                'message': message,
                'filename': filename,
                'source': source_cloud,
                'destination': dest_cloud,
                'statistics': stats
            })
        else:
            return jsonify({
                'status': 'error',
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/cost-analysis', methods=['GET'])
def cost_analysis():
    """Get cost analysis across all clouds"""
    try:
        total_cost = 0
        cloud_costs = {}
        
        for cloud, manager in managers.items():
            response = manager.s3_client.list_objects_v2(Bucket=manager.bucket_name)
            files = response.get('Contents', [])
            cloud_cost = 0
            
            for file in files:
                size_gb = file['Size'] / (1024 ** 3)
                tier = file.get('StorageClass', 'STANDARD')
                
                # Cost per GB per month
                cost_map = {
                    'STANDARD': 0.023,
                    'STANDARD_IA': 0.0125,
                    'INTELLIGENT_TIERING': 0.023,
                    'GLACIER': 0.004,
                    'DEEP_ARCHIVE': 0.00099
                }
                
                file_cost = size_gb * cost_map.get(tier, 0.023)
                cloud_cost += file_cost
            
            cloud_costs[cloud] = {
                'cost': round(cloud_cost, 2),
                'file_count': len(files),
                'total_size_gb': round(sum(f['Size'] for f in files) / (1024 ** 3), 2)
            }
            total_cost += cloud_cost
        
        return jsonify({
            'total_cost': round(total_cost, 2),
            'clouds': cloud_costs
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall system statistics"""
    try:
        total_files = 0
        total_size = 0
        
        for manager in managers.values():
            response = manager.s3_client.list_objects_v2(Bucket=manager.bucket_name)
            files = response.get('Contents', [])
            total_files += len(files)
            total_size += sum(f['Size'] for f in files)
        
        return jsonify({
            'total_files': total_files,
            'total_size_gb': round(total_size / (1024 ** 3), 2),
            'clouds_active': len(managers),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 ASTRA - Interactive Dashboard")
    print("=" * 70)
    print("\n📍 Starting web server...")
    print("🌐 Open your browser to: http://localhost:5000")
    print("\n✨ Features:")
    print("   • Visual file management across clouds")
    print("   • Drag-and-drop migrations")
    print("   • Real-time cost analysis")
    print("   • Interactive tiering recommendations")
    print("\n" + "=" * 70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
