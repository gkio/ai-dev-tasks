# Database Architecture Review Examples

This document provides examples of how to use the Database Architecture Review System for different types of database projects and scenarios.

## Example 1: E-commerce Database Schema Review 🛒

### Scenario
Reviewing a new e-commerce database schema before implementation.

### Command Usage
```
Use @database-architecture-review.mdc
Review these files: @migrations/001-create-users.sql @migrations/002-create-products.sql @migrations/003-create-orders.sql @models/User.ts @models/Product.ts @models/Order.ts
Focus on: schema design, performance optimization, data integrity, scalability
```

### Expected Review Focus
- Entity relationship design and normalization
- Indexing strategy for product searches and order queries
- Data integrity constraints for financial transactions
- Performance optimization for high-traffic scenarios
- Scalability considerations for growing product catalogs

### Key Review Sections
- **Schema Quality Assessment:** Table design, relationships, and normalization
- **Quick Wins:** Add indexes for common queries, optimize data types
- **Performance Analysis:** Query optimization for product searches and order processing

---

## Example 2: User Analytics Database Optimization 📊

### Scenario
Optimizing a user analytics database experiencing performance issues.

### Command Usage
```
Use @database-architecture-review.mdc
Review these files: @schema/events.sql @queries/user-analytics.sql @models/Event.ts @services/analytics-service.ts
Focus on: query performance, indexing strategy, time-series optimization, data aggregation
```

### Expected Review Focus
- Time-series data optimization and partitioning
- Indexing strategies for analytics queries
- Data aggregation and pre-computation opportunities
- Query optimization for reporting dashboards
- Archive and retention strategies

### Key Review Sections
- **Performance Analysis:** Slow query identification and optimization
- **Indexing Strategy:** Time-based and composite index recommendations
- **Scalability Planning:** Partitioning and archival strategies

---

## Example 3: Multi-tenant SaaS Database Review 🏢

### Scenario
Reviewing database architecture for a multi-tenant SaaS application.

### Command Usage
```
Use @database-architecture-review.mdc
Review these files: @schema/tenants.sql @schema/tenant-data.sql @models/Tenant.ts @services/tenant-service.ts
Focus on: data isolation, security, performance across tenants, scalability
```

### Expected Review Focus
- Data isolation strategies (schema per tenant vs shared schema)
- Security and access control between tenants
- Performance optimization across multiple tenants
- Backup and recovery strategies for multi-tenant data
- Scaling strategies as tenant count grows

### Key Review Sections
- **Security Review:** Tenant data isolation and access controls
- **Architecture Review:** Multi-tenancy patterns and implementation
- **Scalability Considerations:** Horizontal scaling and performance isolation

---

## Example 4: Financial Database Security Review 💰

### Scenario
Security audit of a financial application database handling sensitive financial data.

### Command Usage
```
Use @database-architecture-review.mdc
Review these files: @schema/accounts.sql @schema/transactions.sql @models/Account.ts @models/Transaction.ts @security/audit-triggers.sql
Focus on: data security, audit trail, compliance, encryption, access control
```

### Expected Review Focus
- Data encryption at rest and in transit
- Audit logging for all financial operations
- Compliance with financial regulations (PCI DSS, SOX)
- Access control and user permissions
- Transaction integrity and ACID compliance

### Key Review Sections
- **Security Assessment:** Comprehensive security vulnerability analysis
- **Compliance Review:** Regulatory compliance and audit requirements
- **Data Integrity:** Transaction safety and consistency guarantees

---

## Example 5: Real-time Chat Database Architecture 💬

### Scenario
Reviewing database design for a real-time chat application.

### Command Usage
```
Use @database-architecture-review.mdc
Review these files: @schema/messages.sql @schema/channels.sql @models/Message.ts @models/Channel.ts @queries/recent-messages.sql
Focus on: real-time performance, message indexing, retention policies, scalability
```

### Expected Review Focus
- Message storage and retrieval optimization
- Indexing for real-time message queries
- Data retention and archival strategies
- Scalability for high-frequency writes
- Read replica strategies for message history

### Key Review Sections
- **Performance Analysis:** Real-time query optimization
- **Scalability Planning:** High-frequency write optimization
- **Retention Strategy:** Message archival and cleanup policies

---

## Example 6: Content Management System Database 📝

### Scenario
Optimizing a CMS database with complex content relationships.

### Command Usage
```
Use @database-architecture-review.mdc
Review these files: @schema/content.sql @schema/taxonomy.sql @models/Article.ts @models/Category.ts @queries/content-search.sql
Focus on: content relationships, search optimization, hierarchical data, performance
```

### Expected Review Focus
- Hierarchical data representation (categories, tags)
- Full-text search optimization
- Content versioning and revision management
- Media file metadata and relationships
- Query optimization for content listing and filtering

### Key Review Sections
- **Schema Design:** Complex relationships and hierarchical structures
- **Search Optimization:** Full-text search and indexing strategies
- **Performance Review:** Content query and filtering optimization

---

## Example 7: IoT Sensor Data Database 🌡️

### Scenario
Reviewing time-series database for IoT sensor data collection.

### Command Usage
```
Use @database-architecture-review.mdc
Review these files: @schema/sensors.sql @schema/readings.sql @models/Sensor.ts @models/Reading.ts @queries/aggregations.sql
Focus on: time-series optimization, data compression, aggregation, retention
```

### Expected Review Focus
- Time-series data storage and compression
- Efficient aggregation and downsampling
- Data retention and cleanup policies
- Indexing for time-based queries
- Batch insert optimization for high-volume data

### Key Review Sections
- **Time-Series Optimization:** Partitioning and compression strategies
- **Performance Analysis:** High-volume insert and query optimization
- **Retention Management:** Data lifecycle and storage optimization

---

## Example 8: Social Media Database Architecture 📱

### Scenario
Reviewing database design for a social media platform.

### Command Usage
```
Use @database-architecture-review.mdc
Review these files: @schema/users.sql @schema/posts.sql @schema/follows.sql @models/User.ts @models/Post.ts @queries/feed-generation.sql
Focus on: social graph optimization, feed generation, content scaling, real-time features
```

### Expected Review Focus
- Social graph representation and queries
- News feed generation optimization
- Content recommendation algorithms
- Real-time notification systems
- Scaling strategies for viral content

### Key Review Sections
- **Graph Optimization:** Social relationship queries and indexing
- **Feed Performance:** Timeline generation and caching strategies
- **Scalability Planning:** Viral content and high-engagement scenarios

---

## Database Technology-Specific Examples

### PostgreSQL Advanced Features Review 🐘

```
Use @database-architecture-review.mdc
Review these files: @schema/advanced.sql @queries/jsonb-queries.sql @functions/stored-procedures.sql
Focus on: JSONB optimization, stored procedures, advanced indexing, full-text search
```

**Focus Areas:**
- JSONB column optimization and indexing
- Stored procedure performance and maintainability
- Advanced PostgreSQL features (CTEs, window functions, arrays)
- Full-text search with tsvector and GIN indexes

### MongoDB Document Design Review 🍃

```
Use @database-architecture-review.mdc
Review these files: @models/user-profile.js @queries/aggregation-pipelines.js @indexes/compound-indexes.js
Focus on: document structure, aggregation optimization, indexing strategy, embedding vs referencing
```

**Focus Areas:**
- Document embedding vs referencing strategies
- Aggregation pipeline optimization
- Compound index design for complex queries
- Schema validation and data consistency

### Redis Caching Architecture Review ⚡

```
Use @database-architecture-review.mdc
Review these files: @cache/strategies.ts @cache/keys.ts @cache/ttl-config.ts
Focus on: caching patterns, key design, TTL management, memory optimization
```

**Focus Areas:**
- Cache key naming conventions and collision prevention
- TTL strategies and cache invalidation
- Memory usage optimization and eviction policies
- Redis data structure selection (strings, hashes, sets, sorted sets)

---

## Quick Database Review Checklist ✅

### Before Running a Review
1. **Gather all relevant files:**
   - Schema files (SQL migrations, DDL)
   - Model definitions (ORM models)
   - Query files (complex queries, stored procedures)
   - Configuration files (database settings, connection pools)

2. **Identify focus areas:**
   - Performance issues or bottlenecks
   - Security concerns
   - Scalability requirements
   - Compliance needs

3. **Prepare context information:**
   - Expected data volume and growth
   - Query patterns and frequency
   - Performance requirements
   - Existing issues or pain points

### After the Review
1. **Prioritize recommendations:**
   - Focus on quick wins first
   - Address critical security issues
   - Plan major architectural changes

2. **Implement incrementally:**
   - Start with indexing improvements
   - Optimize existing queries
   - Plan schema changes carefully

3. **Monitor and measure:**
   - Track query performance improvements
   - Monitor database metrics
   - Validate security enhancements

---

## Advanced Review Scenarios

### Database Migration Review 🔄

**Scenario:** Reviewing a complex database migration strategy.

```
Use @database-architecture-review.mdc
Review these files: @migrations/old-schema.sql @migrations/new-schema.sql @scripts/data-migration.sql
Focus on: migration safety, data integrity, rollback strategy, downtime minimization
```

### Database Scaling Review 📈

**Scenario:** Planning database scaling for rapid growth.

```
Use @database-architecture-review.mdc
Review these files: @current-schema.sql @performance-metrics.json @scaling-plans.md
Focus on: horizontal scaling, sharding strategy, read replicas, performance optimization
```

### Database Security Hardening 🔒

**Scenario:** Comprehensive security review for compliance.

```
Use @database-architecture-review.mdc
Review these files: @security/user-roles.sql @security/encryption.sql @audit/logging.sql
Focus on: access control, encryption, audit logging, vulnerability assessment
```

---

*These examples demonstrate the comprehensive coverage and flexibility of the Database Architecture Review System. Adapt the focus areas and file selections to match your specific database technology, use case, and requirements.* 