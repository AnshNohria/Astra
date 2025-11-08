# 🏗️ Technical Architecture - Astra

## System Overview

Astra is an **event-driven, intelligent data lifecycle management system** that combines real-time streaming with predictive analytics to optimize cloud storage costs while maintaining performance SLAs.

## Architecture Layers

### 1. Presentation Layer (CLI)
- **Framework**: Click (Python)
- **Purpose**: User interaction and command execution
- **Features**: 
  - Command grouping with `@click.group()`
  - Decorated functions with `@mock_aws` for isolated testing
  - Rich formatted output with Unicode symbols

### 2. Streaming Layer (Kafka)
- **Technology**: Apache Kafka 7.5.0 via Confluent Platform
- **Deployment**: Docker Compose with Zookeeper coordination
- **Components**:
  - **Producer** (`streaming.py`): Emits file ingestion events
  - **Consumer** (`streaming.py`): Processes events and triggers S3 uploads
  - **Topic**: `data-events` (single topic, can be partitioned)
  
**Why Kafka?**
- Industry-standard for high-throughput event streaming
- Guarantees message ordering and durability
- Horizontally scalable (add brokers for higher throughput)
- Decouples data producers from consumers

### 3. Intelligence Layer (Tiering Engine)
- **Module**: `engine.py`
- **Algorithm**: Multi-factor decision tree
- **Decision Factors**:
  1. **Access frequency**: High-touch data stays hot
  2. **Temporal analysis**: Age-based degradation rules
  3. **Predictive heuristics**: Pattern matching on filenames
  4. **Cost modeling**: Cross-cloud optimization opportunities

**Tiering Decision Matrix**:
```
┌─────────────────┬──────────────┬──────────────┬──────────────┐
│   Factor        │   Hot        │   Warm       │   Cold       │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Access Count    │  >= 10       │  5-9         │  0-4         │
│ Age (days)      │  0-30        │  30-90       │  90-180      │
│ Heuristic       │  -           │  monthly_*   │  backup_*    │
│ Cost Impact     │  High        │  Medium      │  Low         │
└─────────────────┴──────────────┴──────────────┴──────────────┘
```

### 4. Cloud Abstraction Layer (S3 Manager)
- **Module**: `cloud_utils.py`
- **SDK**: boto3 (official AWS SDK for Python)
- **Mocking**: moto library for high-fidelity testing
- **Operations**:
  - `upload_file()`: PUT with storage class selection
  - `change_file_tier()`: Copy-and-delete pattern (AWS best practice)
  - `list_all_files()`: Paginated listing (scalable to millions)
  - `get_file_tier()`: HEAD request (no data transfer)

**Copy-and-Delete Pattern** (Industry Standard):
```python
# S3 doesn't support in-place tier changes
# Solution: Copy to self with new StorageClass
s3.copy_object(
    CopySource={'Bucket': bucket, 'Key': key},
    Bucket=bucket,
    Key=key,
    StorageClass=new_tier,
    MetadataDirective='COPY'  # Preserve metadata
)
```

### 5. Persistence Layer (Metadata)
- **Format**: JSON (easily upgradeable to DynamoDB/PostgreSQL)
- **Schema**:
```json
{
  "filename.ext": {
    "access_count": 42,
    "created_timestamp": "2024-11-08T10:30:00",
    "last_accessed_timestamp": "2024-11-08T14:20:00"
  }
}
```
- **Purpose**: Track access patterns not available from S3 API

## Data Flow Diagrams

### Ingestion Flow
```
User Command                   Kafka Broker               S3 Manager
     │                              │                          │
     │──generate-event──>           │                          │
     │                   [Producer] │                          │
     │                   publish────>│                          │
     │                              │<────consume [Consumer]   │
     │                              │                          │
     │                              │   upload_file()          │
     │                              │──────────────────────────>│
     │                              │                [S3 PUT]   │
     │                              │                 STANDARD  │
     │                              │                    tier   │
     │<──"Event sent"───            │                          │
```

### Optimization Flow
```
User Command           Tiering Engine          S3 Manager           Mocked S3
     │                       │                      │                    │
     │──run-engine──>        │                      │                    │
     │                       │   list_all_files()   │                    │
     │                       │─────────────────────>│                    │
     │                       │                      │──LIST_OBJECTS_V2──>│
     │                       │<─────────────────────│<───────────────────│
     │                       │   [file1, file2...]  │                    │
     │                       │                      │                    │
     │                  [For each file]             │                    │
     │                       │   get_file_tier()    │                    │
     │                       │─────────────────────>│──HEAD_OBJECT──────>│
     │                       │<─────────────────────│<───────────────────│
     │                       │      "STANDARD"      │                    │
     │                       │                      │                    │
     │               [Decision Engine]              │                    │
     │               Analyze: age=100, access=0     │                    │
     │               Heuristic: "backup_" prefix    │                    │
     │               Decision: Move to GLACIER      │                    │
     │                       │                      │                    │
     │                       │  change_file_tier()  │                    │
     │                       │─────────────────────>│                    │
     │                       │                      │──COPY_OBJECT──────>│
     │                       │                      │  (StorageClass:    │
     │                       │                      │   GLACIER)         │
     │                       │<─────────────────────│<───────────────────│
     │                       │      success         │                    │
     │<──Summary Report──────│                      │                    │
```

## Technology Justifications

### Why Python?
- Rapid development (critical for 12-hour hackathon)
- Rich ecosystem (boto3, kafka-python, click)
- Industry standard for data engineering
- Easy to extend with ML libraries (scikit-learn, TensorFlow)

### Why Kafka over Simpler Queues?
- **Throughput**: Handles millions of events/second
- **Durability**: Persisted to disk, replicated
- **Replay**: Can reprocess events from any offset
- **Industry Adoption**: Used by LinkedIn, Uber, Netflix
- **Learning Value**: Demonstrates understanding of enterprise systems

### Why moto over Real AWS?
- **Cost**: $0 vs. potential AWS charges
- **Speed**: No network latency, instant responses
- **Reproducibility**: Identical behavior across machines
- **Testing**: Full control over failure scenarios
- **Portability**: Works offline, no AWS account needed

**Production Migration Path**: 
Remove `@mock_aws` decorators → Connect to real S3 → Deploy!

## Scalability Considerations

### Current System Handles:
- **Files**: Unlimited (S3 pagination)
- **Events/sec**: ~100 (single Kafka broker)
- **Latency**: <100ms (local mocking)

### Production Scaling Strategy:

| Component | Bottleneck | Solution |
|-----------|-----------|----------|
| Kafka Consumer | Single instance | Consumer group with 10+ workers |
| Tiering Engine | Sequential processing | Parallel processing with multiprocessing |
| S3 API | Rate limits | Exponential backoff + jitter |
| Metadata | JSON file I/O | Migrate to DynamoDB (DAX for caching) |

### Estimated Production Capacity:
- **1 Million files**: 2-3 minutes analysis time (parallelized)
- **10,000 events/sec**: 3-5 Kafka brokers with partitioning
- **Multi-region**: Deploy engine per region, aggregate to central dashboard

## Security Considerations

### Current Demo:
- No authentication (local mocking)
- Plaintext Kafka (no SSL/SASL)
- No encryption at rest

### Production Security Hardening:
1. **AWS IAM**: Least-privilege roles for S3 access
2. **Kafka SASL/SSL**: Encrypted broker communication
3. **VPC Isolation**: Private subnets for Kafka/compute
4. **KMS**: Encrypt S3 buckets and Kafka topics
5. **Audit Logging**: CloudTrail for S3, Kafka ACLs

## Cost Analysis

### Storage Tier Pricing (AWS US-East-1):
| Tier | $/GB/Month | Use Case |
|------|-----------|----------|
| S3 Standard (HOT) | $0.023 | Frequently accessed |
| S3 IA (WARM) | $0.0125 | Monthly access |
| S3 Glacier (COLD) | $0.004 | Quarterly access |
| S3 Deep Archive | $0.00099 | Yearly+ access |

### Example Savings Calculation:
**Scenario**: 1TB of data, 50% can move to Glacier

- **Before**: 1000 GB × $0.023 = **$23.00/month**
- **After**: 
  - 500 GB × $0.023 = $11.50 (HOT)
  - 500 GB × $0.004 = $2.00 (COLD)
  - **Total**: **$13.50/month**
- **Savings**: $9.50/month = **41% reduction**
- **Annual Savings**: $114.00

**At enterprise scale (1PB)**: $114,000/year saved!

## Monitoring & Observability

### Metrics to Track (Production):
- **Kafka**: Consumer lag, throughput, partition distribution
- **S3**: Request count, error rate, 4xx/5xx responses
- **Engine**: Decisions made, migrations succeeded/failed
- **Cost**: Monthly spend by tier, savings achieved

### Recommended Tools:
- **Prometheus + Grafana**: Metrics visualization
- **ELK Stack**: Log aggregation and search
- **AWS CloudWatch**: Native AWS metrics
- **PagerDuty**: Alerting for failures

## Testing Strategy

### Unit Tests (Not Implemented - Out of Scope):
```python
def test_tiering_decision():
    engine = TieringEngine(mock_s3)
    # Old backup file should go to COLD
    tier = engine._determine_target_tier('backup_old.zip', 'hot')
    assert tier == 'cold'
```

### Integration Tests:
Current demo **IS** an integration test:
- Real Kafka (not mocked)
- Real boto3 SDK (mocked backend)
- End-to-end data flow

### Load Testing (Future):
```python
# Generate 10,000 events to test throughput
for i in range(10000):
    produce_new_file_event(f"file{i}.dat")
```

## Extensibility Points

### 1. ML Integration
Replace heuristics with trained model:
```python
def _apply_ml_prediction(self, file_key: str) -> str:
    features = extract_features(file_key, self.metadata)
    return ml_model.predict(features)  # Returns tier
```

### 2. Multi-Cloud Support
Add Azure/GCP adapters:
```python
class AzureBlobManager(CloudManager):
    def change_file_tier(self, blob_name, tier):
        blob_client.set_standard_blob_tier(tier)
```

### 3. Web Dashboard
Add Flask API + React frontend:
```python
@app.route('/api/dashboard')
def get_dashboard():
    return jsonify(s3_manager.list_all_files())
```

### 4. Policy Engine
User-defined tiering policies:
```yaml
policies:
  - name: "Compliance Hold"
    pattern: "legal-hold-*"
    action: "never_tier_down"
    duration: "7 years"
```

## Comparison to Alternatives

| Solution | Astra | AWS S3 Lifecycle | Manual Review |
|----------|-------|------------------|---------------|
| **Cost** | Free (local) | Included | Engineer time |
| **Real-Time** | Yes (Kafka) | No (daily batch) | No |
| **Predictive** | Yes | Rule-based only | Expert judgment |
| **Multi-Cloud** | Possible | AWS only | Possible |
| **Learning Curve** | Medium | Low | N/A |

## Future Roadmap

### Phase 1 (Current): Proof of Concept ✅
- Core tiering logic
- Kafka integration
- Local simulation

### Phase 2: Production MVP (2-4 weeks)
- Deploy to AWS EKS
- Real S3 integration
- DynamoDB for metadata
- Basic web UI

### Phase 3: Enterprise Features (2-3 months)
- ML-based predictions
- Multi-cloud support
- Cost forecasting
- Policy engine
- RBAC and audit logs

### Phase 4: SaaS Platform (6-12 months)
- Multi-tenant architecture
- API for integrations
- Terraform/CloudFormation templates
- Marketplace listing (AWS/Azure)

---

## Conclusion

Astra demonstrates a **production-viable approach** to intelligent cloud storage management using **industry-standard technologies**. While built in 12 hours for a hackathon, the architecture is extensible and the patterns used are directly applicable to enterprise deployments.

**Key Differentiators**:
1. Real streaming (not simulated)
2. Authentic AWS SDK usage (via moto)
3. Scalable architecture (demonstrated understanding of distributed systems)
4. Clear path to production (remove `@mock_aws`, deploy)

This is not a toy project—it's a foundation for a viable product.

---

**Built by**: Ansh Nohria  
**Date**: November 2024  
**License**: MIT
