"""
Real-time data streaming using Kafka.
Handles event production and consumption for data ingestion pipeline.
"""
import json
import time
from datetime import datetime
from typing import Dict
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable
from cloud_utils import S3Manager


KAFKA_TOPIC = 'data-events'
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']


def produce_new_file_event(filename: str, size_gb: float = 1.0, max_retries: int = 3) -> bool:
    """
    Produce a new file event to Kafka stream.
    
    Args:
        filename: Name of the file being ingested
        size_gb: Size of the file in GB
        max_retries: Maximum number of connection retry attempts
    
    Returns:
        True if event successfully produced, False otherwise
    """
    for attempt in range(max_retries):
        try:
            # Create producer
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
            
            # Create event message
            event = {
                'event': 'NEW_FILE',
                'filename': filename,
                'size_gb': size_gb,
                'timestamp': datetime.now().isoformat(),
                'source': 'data-ingestion-pipeline'
            }
            
            # Send to Kafka
            future = producer.send(KAFKA_TOPIC, value=event)
            result = future.get(timeout=10)
            
            print(f"✓ STREAM [PRODUCER]: Sent new file event for '{filename}'")
            print(f"  └─ Topic: {KAFKA_TOPIC}, Partition: {result.partition}, Offset: {result.offset}")
            
            producer.flush()
            producer.close()
            return True
            
        except NoBrokersAvailable:
            if attempt < max_retries - 1:
                print(f"⚠️  Kafka broker not available. Retrying in 2 seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"✗ ERROR: Could not connect to Kafka broker at {KAFKA_BOOTSTRAP_SERVERS}")
                print(f"  Please ensure Kafka is running: docker-compose up -d")
                return False
                
        except KafkaError as e:
            print(f"✗ STREAM [PRODUCER]: Kafka error - {e}")
            return False
        except Exception as e:
            print(f"✗ STREAM [PRODUCER]: Unexpected error - {e}")
            return False
    
    return False


def start_event_consumer(s3_manager: S3Manager, metadata_path: str = "metadata.json"):
    """
    Start consuming events from Kafka and process them.
    This function runs indefinitely until interrupted.
    
    Args:
        s3_manager: S3Manager instance for cloud operations
        metadata_path: Path to metadata JSON file
    """
    print("\n" + "="*70)
    print("🎧 KAFKA EVENT CONSUMER STARTING")
    print("="*70)
    print(f"📡 Listening to topic: {KAFKA_TOPIC}")
    print(f"🔌 Kafka brokers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"⏸️  Press Ctrl+C to stop\n")
    
    try:
        # Create consumer
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',  # Start from latest messages
            enable_auto_commit=True,
            group_id='storage-manager-consumer-group'
        )
        
        print("✓ Connected to Kafka successfully")
        print("⏳ Waiting for events...\n")
        
        # Process messages
        for message in consumer:
            try:
                event = message.value
                
                if event.get('event') == 'NEW_FILE':
                    filename = event.get('filename')
                    size_gb = event.get('size_gb', 1.0)
                    timestamp = event.get('timestamp')
                    
                    print(f"📨 STREAM [CONSUMER]: Received NEW_FILE event")
                    print(f"   ├─ Filename: {filename}")
                    print(f"   ├─ Size: {size_gb} GB")
                    print(f"   └─ Timestamp: {timestamp}")
                    
                    # Upload to S3 in HOT tier
                    if s3_manager.upload_file(filename, f"mock-data-{size_gb}GB", tier='STANDARD'):
                        print(f"   ✓ Ingested '{filename}' to HOT storage (S3 STANDARD)")
                        
                        # Update metadata
                        _update_metadata(filename, metadata_path)
                        print(f"   ✓ Updated metadata for '{filename}'")
                    else:
                        print(f"   ✗ Failed to ingest '{filename}'")
                    
                    print()
                else:
                    print(f"⚠️  Unknown event type: {event.get('event')}")
                    
            except Exception as e:
                print(f"✗ Error processing message: {e}")
                continue
                
    except NoBrokersAvailable:
        print(f"\n✗ ERROR: Could not connect to Kafka broker at {KAFKA_BOOTSTRAP_SERVERS}")
        print(f"  Please ensure Kafka is running: docker-compose up -d\n")
    except KeyboardInterrupt:
        print("\n\n🛑 Consumer stopped by user")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n✗ STREAM [CONSUMER]: Fatal error - {e}\n")
    finally:
        try:
            consumer.close()
        except:
            pass


def _update_metadata(filename: str, metadata_path: str):
    """
    Update metadata file with new file information.
    
    Args:
        filename: Name of the file
        metadata_path: Path to metadata JSON file
    """
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        metadata = {}
    
    # Add new file entry
    metadata[filename] = {
        'access_count': 0,
        'created_timestamp': datetime.now().isoformat(),
        'last_accessed_timestamp': datetime.now().isoformat()
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)


def check_kafka_connection() -> bool:
    """
    Check if Kafka is available and responsive.
    
    Returns:
        True if Kafka is available, False otherwise
    """
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            request_timeout_ms=5000
        )
        producer.close()
        return True
    except:
        return False
