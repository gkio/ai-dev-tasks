"""
Metadata Management System

Comprehensive metadata management that provides:
- Data catalog and discovery
- Metadata collection and storage
- Relationship tracking and mapping
- Search and query capabilities
- Technical and business metadata
- Data documentation and annotations
"""

import json
import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import logging
import uuid
import re


class MetadataType(Enum):
    """Types of metadata."""
    TECHNICAL = "technical"
    BUSINESS = "business"
    OPERATIONAL = "operational"
    STRUCTURAL = "structural"
    DESCRIPTIVE = "descriptive"
    ADMINISTRATIVE = "administrative"


class ResourceType(Enum):
    """Types of data resources."""
    TABLE = "table"
    VIEW = "view"
    COLUMN = "column"
    INDEX = "index"
    SCHEMA = "schema"
    DATABASE = "database"
    FILE = "file"
    API = "api"
    QUERY = "query"
    REPORT = "report"
    DASHBOARD = "dashboard"
    TRANSFORMATION = "transformation"


class RelationshipType(Enum):
    """Types of relationships between resources."""
    CONTAINS = "contains"
    DEPENDS_ON = "depends_on"
    DERIVES_FROM = "derives_from"
    REFERENCES = "references"
    SIMILAR_TO = "similar_to"
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    USES = "uses"


@dataclass
class MetadataAttribute:
    """Individual metadata attribute."""
    name: str
    value: Any
    type: str  # string, number, boolean, date, json, etc.
    description: Optional[str] = None
    source: Optional[str] = None
    confidence: float = 1.0
    last_updated: Optional[datetime.datetime] = None
    tags: Optional[List[str]] = None


@dataclass
class DataResource:
    """Data resource with metadata."""
    resource_id: str
    name: str
    type: ResourceType
    system: str
    path: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    steward: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    schema_version: Optional[str] = None
    metadata: Optional[Dict[str, MetadataAttribute]] = None
    tags: Optional[List[str]] = None


@dataclass
class ResourceRelationship:
    """Relationship between data resources."""
    relationship_id: str
    source_resource_id: str
    target_resource_id: str
    type: RelationshipType
    strength: float = 1.0  # 0.0 to 1.0
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime.datetime] = None
    created_by: Optional[str] = None


@dataclass
class MetadataRule:
    """Rule for automatic metadata extraction and validation."""
    rule_id: str
    name: str
    description: str
    pattern: str  # Regex pattern or query
    metadata_extraction: Dict[str, Any]  # What metadata to extract
    validation_rules: Optional[List[str]] = None
    active: bool = True
    priority: int = 5
    created_by: str = ""
    created_at: Optional[datetime.datetime] = None


@dataclass
class SearchResult:
    """Search result for metadata queries."""
    resource: DataResource
    score: float
    matching_fields: List[str]
    snippet: Optional[str] = None


class MetadataManager:
    """
    Comprehensive metadata management system that provides:
    - Data catalog and resource discovery
    - Metadata collection, storage, and retrieval
    - Relationship tracking and mapping
    - Search and query capabilities
    - Automated metadata extraction
    - Data lineage integration
    """
    
    def __init__(self, base_path: str = "metadata", config: Optional[Dict[str, Any]] = None):
        self.base_path = Path(base_path)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory structure exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "resources").mkdir(exist_ok=True)
        (self.base_path / "relationships").mkdir(exist_ok=True)
        (self.base_path / "rules").mkdir(exist_ok=True)
        (self.base_path / "catalog").mkdir(exist_ok=True)
        (self.base_path / "search_index").mkdir(exist_ok=True)
        
        # Search index for fast lookups
        self.search_index = self._load_search_index()
    
    def register_resource(self, resource: DataResource) -> bool:
        """Register a new data resource in the catalog."""
        try:
            if not resource.resource_id:
                resource.resource_id = str(uuid.uuid4())
            
            if not resource.created_at:
                resource.created_at = datetime.datetime.utcnow()
            
            resource.updated_at = datetime.datetime.utcnow()
            
            # Validate resource
            if not self._validate_resource(resource):
                return False
            
            # Extract metadata using rules
            self._apply_metadata_rules(resource)
            
            # Save resource
            resource_file = self.base_path / "resources" / f"{resource.resource_id}.json"
            with open(resource_file, 'w') as f:
                json.dump(self._serialize_resource(resource), f, indent=2, default=str)
            
            # Update search index
            self._update_search_index(resource)
            
            # Update catalog
            self._update_catalog(resource)
            
            self.logger.info(f"Resource {resource.resource_id} registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering resource: {str(e)}")
            return False
    
    def get_resource(self, resource_id: str) -> Optional[DataResource]:
        """Retrieve a data resource by ID."""
        try:
            resource_file = self.base_path / "resources" / f"{resource_id}.json"
            if not resource_file.exists():
                return None
            
            with open(resource_file, 'r') as f:
                resource_data = json.load(f)
            
            return self._deserialize_resource(resource_data)
            
        except Exception as e:
            self.logger.error(f"Error retrieving resource {resource_id}: {str(e)}")
            return None
    
    def search_resources(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                        limit: int = 20) -> List[SearchResult]:
        """Search for resources using text query and filters."""
        try:
            results = []
            
            # Load all resources for search (in production, use proper search engine)
            resource_files = (self.base_path / "resources").glob("*.json")
            
            for resource_file in resource_files:
                with open(resource_file, 'r') as f:
                    resource_data = json.load(f)
                
                resource = self._deserialize_resource(resource_data)
                
                # Apply filters
                if filters and not self._matches_filters(resource, filters):
                    continue
                
                # Calculate search score
                score, matching_fields = self._calculate_search_score(resource, query)
                
                if score > 0:
                    results.append(SearchResult(
                        resource=resource,
                        score=score,
                        matching_fields=matching_fields,
                        snippet=self._generate_snippet(resource, query)
                    ))
            
            # Sort by score and limit results
            results.sort(key=lambda r: r.score, reverse=True)
            return results[:limit]
            
        except Exception as e:
            self.logger.error(f"Error searching resources: {str(e)}")
            return []
    
    def add_relationship(self, relationship: ResourceRelationship) -> bool:
        """Add a relationship between resources."""
        try:
            if not relationship.relationship_id:
                relationship.relationship_id = str(uuid.uuid4())
            
            if not relationship.created_at:
                relationship.created_at = datetime.datetime.utcnow()
            
            # Validate relationship
            if not self._validate_relationship(relationship):
                return False
            
            # Save relationship
            relationship_file = self.base_path / "relationships" / f"{relationship.relationship_id}.json"
            with open(relationship_file, 'w') as f:
                json.dump(asdict(relationship), f, indent=2, default=str)
            
            self.logger.info(f"Relationship {relationship.relationship_id} added successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding relationship: {str(e)}")
            return False
    
    def get_related_resources(self, resource_id: str, 
                            relationship_types: Optional[List[RelationshipType]] = None,
                            depth: int = 1) -> Dict[str, Any]:
        """Get resources related to a given resource."""
        try:
            related = {
                "resource_id": resource_id,
                "relationships": [],
                "related_resources": {}
            }
            
            # Load all relationships
            relationships = self._load_relationships()
            
            # Find direct relationships
            for rel in relationships:
                include_rel = True
                
                if relationship_types:
                    include_rel = rel.type in relationship_types
                
                if include_rel and (rel.source_resource_id == resource_id or 
                                  rel.target_resource_id == resource_id):
                    
                    # Determine the related resource ID
                    related_id = (rel.target_resource_id if rel.source_resource_id == resource_id 
                                else rel.source_resource_id)
                    
                    related["relationships"].append(asdict(rel))
                    
                    # Load related resource
                    related_resource = self.get_resource(related_id)
                    if related_resource:
                        related["related_resources"][related_id] = self._serialize_resource(related_resource)
                        
                        # Recursive search for deeper relationships
                        if depth > 1:
                            deeper_related = self.get_related_resources(
                                related_id, relationship_types, depth - 1
                            )
                            related["related_resources"][related_id]["related"] = deeper_related
            
            return related
            
        except Exception as e:
            self.logger.error(f"Error getting related resources: {str(e)}")
            return {"error": str(e)}
    
    def create_metadata_rule(self, rule: MetadataRule) -> bool:
        """Create a rule for automatic metadata extraction."""
        try:
            if not rule.rule_id:
                rule.rule_id = str(uuid.uuid4())
            
            if not rule.created_at:
                rule.created_at = datetime.datetime.utcnow()
            
            # Validate rule
            if not self._validate_metadata_rule(rule):
                return False
            
            # Save rule
            rule_file = self.base_path / "rules" / f"{rule.rule_id}.json"
            with open(rule_file, 'w') as f:
                json.dump(asdict(rule), f, indent=2, default=str)
            
            self.logger.info(f"Metadata rule {rule.rule_id} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating metadata rule: {str(e)}")
            return False
    
    def add_metadata(self, resource_id: str, metadata: Dict[str, MetadataAttribute]) -> bool:
        """Add metadata to a resource."""
        try:
            resource = self.get_resource(resource_id)
            if not resource:
                self.logger.error(f"Resource {resource_id} not found")
                return False
            
            if not resource.metadata:
                resource.metadata = {}
            
            # Add new metadata
            for key, attribute in metadata.items():
                if not attribute.last_updated:
                    attribute.last_updated = datetime.datetime.utcnow()
                resource.metadata[key] = attribute
            
            resource.updated_at = datetime.datetime.utcnow()
            
            # Save updated resource
            resource_file = self.base_path / "resources" / f"{resource_id}.json"
            with open(resource_file, 'w') as f:
                json.dump(self._serialize_resource(resource), f, indent=2, default=str)
            
            # Update search index
            self._update_search_index(resource)
            
            self.logger.info(f"Metadata added to resource {resource_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding metadata: {str(e)}")
            return False
    
    def get_catalog_summary(self) -> Dict[str, Any]:
        """Get a summary of the data catalog."""
        try:
            summary = {
                "total_resources": 0,
                "resources_by_type": {},
                "resources_by_system": {},
                "total_relationships": 0,
                "relationships_by_type": {},
                "metadata_coverage": {},
                "recent_additions": []
            }
            
            # Count resources
            resource_files = list((self.base_path / "resources").glob("*.json"))
            summary["total_resources"] = len(resource_files)
            
            # Analyze resources
            for resource_file in resource_files:
                with open(resource_file, 'r') as f:
                    resource_data = json.load(f)
                
                resource_type = resource_data.get("type", "unknown")
                system = resource_data.get("system", "unknown")
                
                summary["resources_by_type"][resource_type] = \
                    summary["resources_by_type"].get(resource_type, 0) + 1
                
                summary["resources_by_system"][system] = \
                    summary["resources_by_system"].get(system, 0) + 1
                
                # Check metadata coverage
                metadata_count = len(resource_data.get("metadata", {}))
                if metadata_count > 0:
                    summary["metadata_coverage"][resource_type] = \
                        summary["metadata_coverage"].get(resource_type, 0) + 1
            
            # Count relationships
            relationship_files = list((self.base_path / "relationships").glob("*.json"))
            summary["total_relationships"] = len(relationship_files)
            
            for rel_file in relationship_files:
                with open(rel_file, 'r') as f:
                    rel_data = json.load(f)
                
                rel_type = rel_data.get("type", "unknown")
                summary["relationships_by_type"][rel_type] = \
                    summary["relationships_by_type"].get(rel_type, 0) + 1
            
            # Get recent additions
            recent_files = sorted(resource_files, 
                                key=lambda f: f.stat().st_mtime, reverse=True)[:10]
            
            for recent_file in recent_files:
                with open(recent_file, 'r') as f:
                    resource_data = json.load(f)
                
                summary["recent_additions"].append({
                    "id": resource_data["resource_id"],
                    "name": resource_data["name"],
                    "type": resource_data["type"],
                    "created_at": resource_data.get("created_at")
                })
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating catalog summary: {str(e)}")
            return {"error": str(e)}
    
    def discover_resources(self, system: str, connection_config: Dict[str, Any]) -> List[DataResource]:
        """Discover resources from a system automatically."""
        try:
            discovered = []
            
            # This is a placeholder implementation
            # In real implementation, this would connect to the system and
            # discover tables, files, APIs, etc.
            
            # Example discovery for a database system
            if system.lower() in ["postgresql", "mysql", "sql_server"]:
                discovered.extend(self._discover_database_resources(system, connection_config))
            elif system.lower() in ["file_system", "s3", "hdfs"]:
                discovered.extend(self._discover_file_resources(system, connection_config))
            elif system.lower() in ["api", "rest_api"]:
                discovered.extend(self._discover_api_resources(system, connection_config))
            
            # Register discovered resources
            for resource in discovered:
                self.register_resource(resource)
            
            return discovered
            
        except Exception as e:
            self.logger.error(f"Error discovering resources: {str(e)}")
            return []
    
    def generate_documentation(self, resource_id: str) -> str:
        """Generate documentation for a resource."""
        try:
            resource = self.get_resource(resource_id)
            if not resource:
                return "Resource not found"
            
            doc = []
            doc.append(f"# {resource.name}")
            doc.append("")
            
            if resource.description:
                doc.append(f"**Description:** {resource.description}")
                doc.append("")
            
            doc.append(f"**Type:** {resource.type.value}")
            doc.append(f"**System:** {resource.system}")
            
            if resource.owner:
                doc.append(f"**Owner:** {resource.owner}")
            
            if resource.steward:
                doc.append(f"**Steward:** {resource.steward}")
            
            doc.append("")
            
            # Metadata section
            if resource.metadata:
                doc.append("## Metadata")
                doc.append("")
                
                for key, attr in resource.metadata.items():
                    doc.append(f"**{key}:** {attr.value}")
                    if attr.description:
                        doc.append(f"  - {attr.description}")
                    doc.append("")
            
            # Relationships section
            related = self.get_related_resources(resource_id)
            if related.get("relationships"):
                doc.append("## Relationships")
                doc.append("")
                
                for rel in related["relationships"]:
                    target_id = rel["target_resource_id"]
                    if target_id != resource_id:
                        target_resource = self.get_resource(target_id)
                        if target_resource:
                            doc.append(f"- **{rel['type']}:** {target_resource.name}")
                
                doc.append("")
            
            # Tags section
            if resource.tags:
                doc.append("## Tags")
                doc.append("")
                doc.append(", ".join(resource.tags))
                doc.append("")
            
            # Timestamps
            doc.append("## Timestamps")
            doc.append("")
            if resource.created_at:
                doc.append(f"**Created:** {resource.created_at.isoformat()}")
            if resource.updated_at:
                doc.append(f"**Updated:** {resource.updated_at.isoformat()}")
            
            return "\n".join(doc)
            
        except Exception as e:
            self.logger.error(f"Error generating documentation: {str(e)}")
            return f"Error generating documentation: {str(e)}"
    
    # Private helper methods
    
    def _validate_resource(self, resource: DataResource) -> bool:
        """Validate resource data."""
        if not resource.name:
            self.logger.error("Resource name is required")
            return False
        
        if not resource.system:
            self.logger.error("Resource system is required")
            return False
        
        return True
    
    def _validate_relationship(self, relationship: ResourceRelationship) -> bool:
        """Validate relationship data."""
        if not relationship.source_resource_id or not relationship.target_resource_id:
            self.logger.error("Source and target resource IDs are required")
            return False
        
        # Check that resources exist
        source_exists = self.get_resource(relationship.source_resource_id) is not None
        target_exists = self.get_resource(relationship.target_resource_id) is not None
        
        if not source_exists or not target_exists:
            self.logger.error("Source or target resource does not exist")
            return False
        
        return True
    
    def _validate_metadata_rule(self, rule: MetadataRule) -> bool:
        """Validate metadata rule."""
        if not rule.name or not rule.pattern:
            self.logger.error("Rule name and pattern are required")
            return False
        
        # Validate regex pattern
        try:
            re.compile(rule.pattern)
        except re.error:
            self.logger.error("Invalid regex pattern in metadata rule")
            return False
        
        return True
    
    def _apply_metadata_rules(self, resource: DataResource) -> None:
        """Apply metadata extraction rules to a resource."""
        try:
            rules = self._load_metadata_rules()
            
            for rule in rules:
                if not rule.active:
                    continue
                
                # Check if pattern matches resource
                if self._rule_matches_resource(rule, resource):
                    # Extract metadata according to rule
                    extracted_metadata = self._extract_metadata_from_rule(rule, resource)
                    
                    if not resource.metadata:
                        resource.metadata = {}
                    
                    # Add extracted metadata
                    for key, value in extracted_metadata.items():
                        if key not in resource.metadata:
                            resource.metadata[key] = MetadataAttribute(
                                name=key,
                                value=value,
                                type="string",
                                source=f"rule:{rule.rule_id}",
                                last_updated=datetime.datetime.utcnow()
                            )
            
        except Exception as e:
            self.logger.error(f"Error applying metadata rules: {str(e)}")
    
    def _rule_matches_resource(self, rule: MetadataRule, resource: DataResource) -> bool:
        """Check if a rule pattern matches a resource."""
        try:
            # Check pattern against resource name, path, etc.
            pattern = re.compile(rule.pattern, re.IGNORECASE)
            
            if pattern.search(resource.name):
                return True
            
            if resource.path and pattern.search(resource.path):
                return True
            
            if resource.description and pattern.search(resource.description):
                return True
            
            return False
            
        except Exception:
            return False
    
    def _extract_metadata_from_rule(self, rule: MetadataRule, resource: DataResource) -> Dict[str, Any]:
        """Extract metadata from resource using rule."""
        extracted = {}
        
        try:
            extraction_config = rule.metadata_extraction
            
            # Example extraction logic
            if "tags_from_name" in extraction_config:
                tags = self._extract_tags_from_name(resource.name)
                if tags:
                    extracted["auto_tags"] = tags
            
            if "classification_from_path" in extraction_config:
                classification = self._classify_from_path(resource.path or "")
                if classification:
                    extracted["classification"] = classification
            
            # Add more extraction logic as needed
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata from rule: {str(e)}")
        
        return extracted
    
    def _extract_tags_from_name(self, name: str) -> List[str]:
        """Extract tags from resource name."""
        tags = []
        
        # Simple tag extraction logic
        if "user" in name.lower():
            tags.append("user-data")
        if "order" in name.lower():
            tags.append("transactional")
        if "log" in name.lower():
            tags.append("logging")
        if "temp" in name.lower() or "tmp" in name.lower():
            tags.append("temporary")
        
        return tags
    
    def _classify_from_path(self, path: str) -> str:
        """Classify resource based on path."""
        path_lower = path.lower()
        
        if "/pii/" in path_lower or "/personal/" in path_lower:
            return "pii"
        elif "/financial/" in path_lower or "/payment/" in path_lower:
            return "financial"
        elif "/public/" in path_lower:
            return "public"
        else:
            return "internal"
    
    def _serialize_resource(self, resource: DataResource) -> Dict[str, Any]:
        """Serialize resource to dictionary."""
        resource_dict = asdict(resource)
        
        # Convert enums to strings
        resource_dict["type"] = resource.type.value
        
        # Convert metadata attributes
        if resource.metadata:
            metadata_dict = {}
            for key, attr in resource.metadata.items():
                metadata_dict[key] = asdict(attr)
            resource_dict["metadata"] = metadata_dict
        
        return resource_dict
    
    def _deserialize_resource(self, resource_data: Dict[str, Any]) -> DataResource:
        """Deserialize resource from dictionary."""
        # Convert enum
        resource_data["type"] = ResourceType(resource_data["type"])
        
        # Convert metadata
        if resource_data.get("metadata"):
            metadata = {}
            for key, attr_data in resource_data["metadata"].items():
                # Convert datetime if present
                if attr_data.get("last_updated"):
                    attr_data["last_updated"] = datetime.datetime.fromisoformat(attr_data["last_updated"])
                
                metadata[key] = MetadataAttribute(**attr_data)
            resource_data["metadata"] = metadata
        
        # Convert datetime fields
        for date_field in ["created_at", "updated_at"]:
            if resource_data.get(date_field):
                resource_data[date_field] = datetime.datetime.fromisoformat(resource_data[date_field])
        
        return DataResource(**resource_data)
    
    def _load_relationships(self) -> List[ResourceRelationship]:
        """Load all relationships."""
        relationships = []
        relationships_dir = self.base_path / "relationships"
        
        if not relationships_dir.exists():
            return relationships
        
        for rel_file in relationships_dir.glob("*.json"):
            try:
                with open(rel_file, 'r') as f:
                    rel_data = json.load(f)
                
                # Convert enum
                rel_data["type"] = RelationshipType(rel_data["type"])
                
                # Convert datetime
                if rel_data.get("created_at"):
                    rel_data["created_at"] = datetime.datetime.fromisoformat(rel_data["created_at"])
                
                relationships.append(ResourceRelationship(**rel_data))
                
            except Exception as e:
                self.logger.error(f"Error loading relationship {rel_file}: {str(e)}")
        
        return relationships
    
    def _load_metadata_rules(self) -> List[MetadataRule]:
        """Load all metadata rules."""
        rules = []
        rules_dir = self.base_path / "rules"
        
        if not rules_dir.exists():
            return rules
        
        for rule_file in rules_dir.glob("*.json"):
            try:
                with open(rule_file, 'r') as f:
                    rule_data = json.load(f)
                
                # Convert datetime
                if rule_data.get("created_at"):
                    rule_data["created_at"] = datetime.datetime.fromisoformat(rule_data["created_at"])
                
                rules.append(MetadataRule(**rule_data))
                
            except Exception as e:
                self.logger.error(f"Error loading metadata rule {rule_file}: {str(e)}")
        
        return sorted(rules, key=lambda r: r.priority, reverse=True)
    
    def _calculate_search_score(self, resource: DataResource, query: str) -> Tuple[float, List[str]]:
        """Calculate search relevance score."""
        score = 0.0
        matching_fields = []
        query_lower = query.lower()
        
        # Name match (highest weight)
        if query_lower in resource.name.lower():
            score += 10.0
            matching_fields.append("name")
        
        # Description match
        if resource.description and query_lower in resource.description.lower():
            score += 5.0
            matching_fields.append("description")
        
        # Tags match
        if resource.tags:
            for tag in resource.tags:
                if query_lower in tag.lower():
                    score += 3.0
                    matching_fields.append("tags")
                    break
        
        # Metadata match
        if resource.metadata:
            for key, attr in resource.metadata.items():
                if query_lower in str(attr.value).lower():
                    score += 2.0
                    matching_fields.append(f"metadata.{key}")
                    break
        
        # System match
        if query_lower in resource.system.lower():
            score += 1.0
            matching_fields.append("system")
        
        return score, matching_fields
    
    def _matches_filters(self, resource: DataResource, filters: Dict[str, Any]) -> bool:
        """Check if resource matches filters."""
        for filter_key, filter_value in filters.items():
            if filter_key == "type":
                if resource.type.value != filter_value:
                    return False
            elif filter_key == "system":
                if resource.system != filter_value:
                    return False
            elif filter_key == "owner":
                if resource.owner != filter_value:
                    return False
            elif filter_key == "tags":
                if not resource.tags or filter_value not in resource.tags:
                    return False
        
        return True
    
    def _generate_snippet(self, resource: DataResource, query: str) -> str:
        """Generate search result snippet."""
        if resource.description:
            return resource.description[:200] + "..." if len(resource.description) > 200 else resource.description
        else:
            return f"{resource.type.value} in {resource.system}"
    
    def _load_search_index(self) -> Dict[str, Any]:
        """Load search index from disk."""
        index_file = self.base_path / "search_index" / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _update_search_index(self, resource: DataResource) -> None:
        """Update search index with resource."""
        try:
            index_file = self.base_path / "search_index" / "index.json"
            
            # Add resource to index
            self.search_index[resource.resource_id] = {
                "name": resource.name,
                "type": resource.type.value,
                "system": resource.system,
                "description": resource.description,
                "tags": resource.tags or [],
                "updated_at": datetime.datetime.utcnow().isoformat()
            }
            
            # Save index
            with open(index_file, 'w') as f:
                json.dump(self.search_index, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Error updating search index: {str(e)}")
    
    def _update_catalog(self, resource: DataResource) -> None:
        """Update catalog with resource."""
        try:
            catalog_file = self.base_path / "catalog" / f"{resource.system}.json"
            
            catalog = {}
            if catalog_file.exists():
                with open(catalog_file, 'r') as f:
                    catalog = json.load(f)
            
            if "resources" not in catalog:
                catalog["resources"] = []
            
            # Add or update resource in catalog
            resource_summary = {
                "id": resource.resource_id,
                "name": resource.name,
                "type": resource.type.value,
                "path": resource.path,
                "updated_at": datetime.datetime.utcnow().isoformat()
            }
            
            # Remove existing entry if present
            catalog["resources"] = [r for r in catalog["resources"] if r["id"] != resource.resource_id]
            catalog["resources"].append(resource_summary)
            
            # Save catalog
            with open(catalog_file, 'w') as f:
                json.dump(catalog, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Error updating catalog: {str(e)}")
    
    def _discover_database_resources(self, system: str, config: Dict[str, Any]) -> List[DataResource]:
        """Discover resources from database system."""
        # Placeholder implementation
        return [
            DataResource(
                resource_id=str(uuid.uuid4()),
                name="users",
                type=ResourceType.TABLE,
                system=system,
                path="public.users",
                description="User account information",
                created_at=datetime.datetime.utcnow()
            ),
            DataResource(
                resource_id=str(uuid.uuid4()),
                name="orders",
                type=ResourceType.TABLE,
                system=system,
                path="public.orders",
                description="Customer orders",
                created_at=datetime.datetime.utcnow()
            )
        ]
    
    def _discover_file_resources(self, system: str, config: Dict[str, Any]) -> List[DataResource]:
        """Discover resources from file system."""
        # Placeholder implementation
        return [
            DataResource(
                resource_id=str(uuid.uuid4()),
                name="sales_data.csv",
                type=ResourceType.FILE,
                system=system,
                path="/data/sales/sales_data.csv",
                description="Sales transaction data",
                created_at=datetime.datetime.utcnow()
            )
        ]
    
    def _discover_api_resources(self, system: str, config: Dict[str, Any]) -> List[DataResource]:
        """Discover resources from API system."""
        # Placeholder implementation
        return [
            DataResource(
                resource_id=str(uuid.uuid4()),
                name="users_api",
                type=ResourceType.API,
                system=system,
                path="/api/v1/users",
                description="User management API endpoint",
                created_at=datetime.datetime.utcnow()
            )
        ] 