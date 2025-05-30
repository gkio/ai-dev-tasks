"""
Data Architecture Schema Manager

Handles schema versioning, migration, validation, and metadata management
for clean, governed, and consistent data architecture across systems.
"""

import json
import hashlib
import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import logging


class SchemaType(Enum):
    """Schema types supported by the architecture."""
    RELATIONAL = "relational"
    DOCUMENT = "document"
    KEY_VALUE = "key_value"
    GRAPH = "graph"
    TIME_SERIES = "time_series"
    COLUMNAR = "columnar"


class DataClassification(Enum):
    """Data classification levels for governance."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"
    PHI = "phi"


@dataclass
class SchemaField:
    """Individual field definition in a schema."""
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None
    unique: bool = False
    indexed: bool = False
    default_value: Optional[Any] = None
    description: Optional[str] = None
    classification: DataClassification = DataClassification.INTERNAL
    validation_rules: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.validation_rules is None:
            self.validation_rules = {}


@dataclass
class SchemaIndex:
    """Index definition for schema optimization."""
    name: str
    fields: List[str]
    unique: bool = False
    type: str = "btree"  # btree, hash, gin, gist, etc.
    partial_condition: Optional[str] = None
    description: Optional[str] = None


@dataclass
class SchemaRelationship:
    """Relationship definition between schemas."""
    name: str
    source_schema: str
    target_schema: str
    source_field: str
    target_field: str
    relationship_type: str  # one_to_one, one_to_many, many_to_many
    cascade_delete: bool = False
    cascade_update: bool = False


@dataclass
class SchemaVersion:
    """Schema version information and metadata."""
    version: str
    created_at: datetime.datetime
    created_by: str
    description: str
    changes: List[str]
    breaking_changes: bool = False
    rollback_version: Optional[str] = None
    approved_by: Optional[str] = None
    deployment_date: Optional[datetime.datetime] = None


@dataclass
class Schema:
    """Complete schema definition with metadata and governance."""
    name: str
    version: str
    schema_type: SchemaType
    description: str
    fields: List[SchemaField]
    indexes: Optional[List[SchemaIndex]] = None
    relationships: Optional[List[SchemaRelationship]] = None
    business_owner: Optional[str] = None
    technical_owner: Optional[str] = None
    classification: DataClassification = DataClassification.INTERNAL
    retention_policy: Optional[str] = None
    backup_policy: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.indexes is None:
            self.indexes = []
        if self.relationships is None:
            self.relationships = []
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class SchemaManager:
    """
    Manages schema definitions, versions, and governance across the data architecture.
    
    Provides functionality for:
    - Schema creation and validation
    - Version management and migration
    - Governance and compliance
    - Cross-system integration
    """
    
    def __init__(self, base_path: str = "schemas", config: Optional[Dict[str, Any]] = None):
        self.base_path = Path(base_path)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory structure exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "definitions").mkdir(exist_ok=True)
        (self.base_path / "versions").mkdir(exist_ok=True)
        (self.base_path / "migrations").mkdir(exist_ok=True)
        (self.base_path / "governance").mkdir(exist_ok=True)
    
    def create_schema(self, schema: Schema) -> bool:
        """Create a new schema with validation and governance checks."""
        try:
            # Validate schema
            validation_result = self.validate_schema(schema)
            if not validation_result["valid"]:
                self.logger.error(f"Schema validation failed: {validation_result['errors']}")
                return False
            
            # Check for conflicts
            if self.schema_exists(schema.name):
                self.logger.error(f"Schema {schema.name} already exists")
                return False
            
            # Generate schema hash for integrity
            schema_hash = self._generate_schema_hash(schema)
            
            # Save schema definition
            schema_file = self.base_path / "definitions" / f"{schema.name}.json"
            schema_data = asdict(schema)
            schema_data["schema_hash"] = schema_hash
            schema_data["created_at"] = datetime.datetime.utcnow().isoformat()
            
            with open(schema_file, 'w') as f:
                json.dump(schema_data, f, indent=2, default=str)
            
            # Create initial version record
            version = SchemaVersion(
                version=schema.version,
                created_at=datetime.datetime.utcnow(),
                created_by=schema.technical_owner or "system",
                description=f"Initial schema creation: {schema.description}",
                changes=["Initial schema creation"]
            )
            
            self._save_version(schema.name, version)
            
            # Generate governance record
            self._create_governance_record(schema)
            
            self.logger.info(f"Schema {schema.name} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating schema {schema.name}: {str(e)}")
            return False
    
    def update_schema(self, schema: Schema, version_info: SchemaVersion) -> bool:
        """Update an existing schema with version control."""
        try:
            if not self.schema_exists(schema.name):
                self.logger.error(f"Schema {schema.name} does not exist")
                return False
            
            # Get current schema for comparison
            current_schema = self.get_schema(schema.name)
            if not current_schema:
                return False
            
            # Validate new schema
            validation_result = self.validate_schema(schema)
            if not validation_result["valid"]:
                self.logger.error(f"Schema validation failed: {validation_result['errors']}")
                return False
            
            # Check for breaking changes
            breaking_changes = self._detect_breaking_changes(current_schema, schema)
            version_info.breaking_changes = len(breaking_changes) > 0
            
            if breaking_changes:
                self.logger.warning(f"Breaking changes detected: {breaking_changes}")
            
            # Generate new schema hash
            schema_hash = self._generate_schema_hash(schema)
            
            # Save updated schema
            schema_file = self.base_path / "definitions" / f"{schema.name}.json"
            schema_data = asdict(schema)
            schema_data["schema_hash"] = schema_hash
            schema_data["updated_at"] = datetime.datetime.utcnow().isoformat()
            
            with open(schema_file, 'w') as f:
                json.dump(schema_data, f, indent=2, default=str)
            
            # Save version record
            self._save_version(schema.name, version_info)
            
            # Generate migration if needed
            if version_info.breaking_changes:
                self._generate_migration(schema.name, current_schema, schema, version_info)
            
            self.logger.info(f"Schema {schema.name} updated to version {schema.version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating schema {schema.name}: {str(e)}")
            return False
    
    def validate_schema(self, schema: Schema) -> Dict[str, Any]:
        """Comprehensive schema validation."""
        errors = []
        warnings = []
        
        # Basic validation
        if not schema.name:
            errors.append("Schema name is required")
        
        if not schema.fields:
            errors.append("Schema must have at least one field")
        
        # Field validation
        field_names = set()
        primary_keys = []
        
        for field in schema.fields:
            if not field.name:
                errors.append("All fields must have a name")
                continue
            
            if field.name in field_names:
                errors.append(f"Duplicate field name: {field.name}")
            field_names.add(field.name)
            
            if field.primary_key:
                primary_keys.append(field.name)
            
            # Validate data types
            if not self._is_valid_data_type(field.data_type, schema.schema_type):
                errors.append(f"Invalid data type {field.data_type} for field {field.name}")
        
        # Primary key validation
        if schema.schema_type == SchemaType.RELATIONAL and not primary_keys:
            warnings.append("Relational schema should have a primary key")
        
        if len(primary_keys) > 1:
            warnings.append("Multiple primary keys detected, consider composite key design")
        
        # Index validation
        for index in schema.indexes or []:
            for field_name in index.fields:
                if field_name not in field_names:
                    errors.append(f"Index {index.name} references non-existent field: {field_name}")
        
        # Relationship validation
        for relationship in schema.relationships or []:
            if relationship.source_field not in field_names:
                errors.append(f"Relationship {relationship.name} references non-existent source field: {relationship.source_field}")
        
        # Governance validation
        classified_fields = [f for f in schema.fields if f.classification in [DataClassification.PII, DataClassification.PHI]]
        if classified_fields and not schema.retention_policy:
            warnings.append("Schema contains sensitive data but no retention policy defined")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def get_schema(self, schema_name: str) -> Optional[Schema]:
        """Retrieve a schema definition."""
        try:
            schema_file = self.base_path / "definitions" / f"{schema_name}.json"
            if not schema_file.exists():
                return None
            
            with open(schema_file, 'r') as f:
                schema_data = json.load(f)
            
            # Convert back to Schema object
            fields = [SchemaField(**field) for field in schema_data.get("fields", [])]
            indexes = [SchemaIndex(**index) for index in schema_data.get("indexes", [])]
            relationships = [SchemaRelationship(**rel) for rel in schema_data.get("relationships", [])]
            
            schema = Schema(
                name=schema_data["name"],
                version=schema_data["version"],
                schema_type=SchemaType(schema_data["schema_type"]),
                description=schema_data["description"],
                fields=fields,
                indexes=indexes,
                relationships=relationships,
                business_owner=schema_data.get("business_owner"),
                technical_owner=schema_data.get("technical_owner"),
                classification=DataClassification(schema_data.get("classification", "internal")),
                retention_policy=schema_data.get("retention_policy"),
                backup_policy=schema_data.get("backup_policy"),
                tags=schema_data.get("tags", []),
                metadata=schema_data.get("metadata", {})
            )
            
            return schema
            
        except Exception as e:
            self.logger.error(f"Error retrieving schema {schema_name}: {str(e)}")
            return None
    
    def schema_exists(self, schema_name: str) -> bool:
        """Check if a schema exists."""
        schema_file = self.base_path / "definitions" / f"{schema_name}.json"
        return schema_file.exists()
    
    def list_schemas(self) -> List[str]:
        """List all available schemas."""
        schema_files = (self.base_path / "definitions").glob("*.json")
        return [f.stem for f in schema_files]
    
    def get_schema_versions(self, schema_name: str) -> List[SchemaVersion]:
        """Get version history for a schema."""
        try:
            version_file = self.base_path / "versions" / f"{schema_name}_versions.json"
            if not version_file.exists():
                return []
            
            with open(version_file, 'r') as f:
                versions_data = json.load(f)
            
            versions = []
            for version_data in versions_data:
                version = SchemaVersion(
                    version=version_data["version"],
                    created_at=datetime.datetime.fromisoformat(version_data["created_at"]),
                    created_by=version_data["created_by"],
                    description=version_data["description"],
                    changes=version_data["changes"],
                    breaking_changes=version_data.get("breaking_changes", False),
                    rollback_version=version_data.get("rollback_version"),
                    approved_by=version_data.get("approved_by"),
                    deployment_date=datetime.datetime.fromisoformat(version_data["deployment_date"]) if version_data.get("deployment_date") else None
                )
                versions.append(version)
            
            return sorted(versions, key=lambda v: v.created_at, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error retrieving versions for schema {schema_name}: {str(e)}")
            return []
    
    def _generate_schema_hash(self, schema: Schema) -> str:
        """Generate a hash for schema integrity checking."""
        # Create a normalized representation for hashing
        schema_dict = asdict(schema)
        # Remove metadata that shouldn't affect the hash
        schema_dict.pop("metadata", None)
        schema_str = json.dumps(schema_dict, sort_keys=True, default=str)
        return hashlib.sha256(schema_str.encode()).hexdigest()
    
    def _save_version(self, schema_name: str, version: SchemaVersion) -> None:
        """Save a version record for a schema."""
        version_file = self.base_path / "versions" / f"{schema_name}_versions.json"
        
        versions = []
        if version_file.exists():
            with open(version_file, 'r') as f:
                versions = json.load(f)
        
        version_data = asdict(version)
        versions.append(version_data)
        
        with open(version_file, 'w') as f:
            json.dump(versions, f, indent=2, default=str)
    
    def _create_governance_record(self, schema: Schema) -> None:
        """Create governance and compliance record for a schema."""
        governance_file = self.base_path / "governance" / f"{schema.name}_governance.json"
        
        governance_record = {
            "schema_name": schema.name,
            "business_owner": schema.business_owner,
            "technical_owner": schema.technical_owner,
            "classification": schema.classification.value,
            "retention_policy": schema.retention_policy,
            "backup_policy": schema.backup_policy,
            "compliance_requirements": [],
            "access_controls": [],
            "audit_log": [],
            "created_at": datetime.datetime.utcnow().isoformat(),
            "last_reviewed": None,
            "next_review_date": None
        }
        
        # Add compliance requirements based on data classification
        sensitive_fields = [f for f in schema.fields if f.classification in [DataClassification.PII, DataClassification.PHI]]
        if sensitive_fields:
            governance_record["compliance_requirements"] = ["GDPR", "privacy_by_design"]
            if any(f.classification == DataClassification.PHI for f in sensitive_fields):
                governance_record["compliance_requirements"].append("HIPAA")
        
        with open(governance_file, 'w') as f:
            json.dump(governance_record, f, indent=2, default=str)
    
    def _detect_breaking_changes(self, old_schema: Schema, new_schema: Schema) -> List[str]:
        """Detect breaking changes between schema versions."""
        breaking_changes = []
        
        old_fields = {f.name: f for f in old_schema.fields}
        new_fields = {f.name: f for f in new_schema.fields}
        
        # Removed fields
        for field_name in old_fields:
            if field_name not in new_fields:
                breaking_changes.append(f"Removed field: {field_name}")
        
        # Changed field types
        for field_name in old_fields:
            if field_name in new_fields:
                old_field = old_fields[field_name]
                new_field = new_fields[field_name]
                
                if old_field.data_type != new_field.data_type:
                    breaking_changes.append(f"Changed data type for field {field_name}: {old_field.data_type} -> {new_field.data_type}")
                
                if old_field.nullable and not new_field.nullable:
                    breaking_changes.append(f"Field {field_name} changed from nullable to non-nullable")
                
                if not old_field.primary_key and new_field.primary_key:
                    breaking_changes.append(f"Field {field_name} changed to primary key")
        
        return breaking_changes
    
    def _generate_migration(self, schema_name: str, old_schema: Schema, new_schema: Schema, version: SchemaVersion) -> None:
        """Generate migration script for breaking changes."""
        migration_file = self.base_path / "migrations" / f"{schema_name}_{version.version}_migration.sql"
        
        migration_sql = []
        migration_sql.append(f"-- Migration for {schema_name} to version {version.version}")
        migration_sql.append(f"-- Generated at: {datetime.datetime.utcnow().isoformat()}")
        migration_sql.append(f"-- Description: {version.description}")
        migration_sql.append("")
        
        # Add migration logic based on detected changes
        breaking_changes = self._detect_breaking_changes(old_schema, new_schema)
        
        for change in breaking_changes:
            migration_sql.append(f"-- {change}")
            # Add specific migration SQL based on change type
            if "Removed field" in change:
                field_name = change.split(": ")[1]
                migration_sql.append(f"ALTER TABLE {schema_name} DROP COLUMN {field_name};")
            elif "Changed data type" in change:
                field_name = change.split(" ")[5]
                new_type = change.split(" -> ")[1]
                migration_sql.append(f"ALTER TABLE {schema_name} ALTER COLUMN {field_name} TYPE {new_type};")
        
        migration_sql.append("")
        migration_sql.append("-- End of migration")
        
        with open(migration_file, 'w') as f:
            f.write("\n".join(migration_sql))
    
    def _is_valid_data_type(self, data_type: str, schema_type: SchemaType) -> bool:
        """Validate if a data type is appropriate for the schema type."""
        valid_types = {
            SchemaType.RELATIONAL: [
                "INTEGER", "BIGINT", "SMALLINT", "DECIMAL", "NUMERIC", "REAL", "DOUBLE",
                "VARCHAR", "CHAR", "TEXT", "BOOLEAN", "DATE", "TIME", "TIMESTAMP",
                "UUID", "JSON", "JSONB", "ARRAY"
            ],
            SchemaType.DOCUMENT: [
                "STRING", "NUMBER", "BOOLEAN", "DATE", "OBJECT", "ARRAY", "NULL"
            ],
            SchemaType.KEY_VALUE: [
                "STRING", "HASH", "LIST", "SET", "SORTED_SET", "BITMAP", "HYPERLOGLOG"
            ],
            SchemaType.TIME_SERIES: [
                "TIMESTAMP", "DOUBLE", "INTEGER", "STRING", "BOOLEAN", "TAG"
            ],
            SchemaType.COLUMNAR: [
                "INT32", "INT64", "FLOAT", "DOUBLE", "STRING", "BOOLEAN", "DATE", "TIMESTAMP"
            ]
        }
        
        return data_type.upper() in valid_types.get(schema_type, []) 