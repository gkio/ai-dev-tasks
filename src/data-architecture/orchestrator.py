"""
Data Architecture Orchestrator

Main orchestrator that coordinates all data architecture components and provides
a unified interface for managing schemas, governance, integration, and metadata.
Implements the comprehensive data architecture framework.
"""

import json
import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import uuid

# Import our data architecture components
from core.schema_manager import SchemaManager, Schema, SchemaField, SchemaType, DataClassification
from governance.data_governance import DataGovernanceManager, AccessPolicy, QualityRule, ComplianceRule
from integration.data_integration import DataIntegrationManager, IntegrationJob, DataSource, DataTransformation
from metadata.metadata_manager import MetadataManager, DataResource, ResourceType, MetadataAttribute


@dataclass
class ArchitectureConfig:
    """Configuration for the data architecture."""
    base_path: str = "data_architecture"
    enable_governance: bool = True
    enable_integration: bool = True
    enable_metadata: bool = True
    auto_discovery: bool = True
    quality_threshold: float = 0.8
    compliance_frameworks: List[str] = None
    default_retention_policy: str = "7_years"
    encryption_required: bool = True
    
    def __post_init__(self):
        if self.compliance_frameworks is None:
            self.compliance_frameworks = ["GDPR", "SOC2"]


@dataclass
class ArchitectureStatus:
    """Overall status of the data architecture."""
    schemas_count: int
    governance_policies: int
    integration_jobs: int
    metadata_resources: int
    quality_score: float
    compliance_status: str
    last_updated: datetime.datetime
    issues: List[str]
    recommendations: List[str]


class DataArchitectureOrchestrator:
    """
    Main orchestrator for the comprehensive data architecture framework.
    
    Coordinates and provides unified access to:
    - Schema management and versioning
    - Data governance and compliance
    - Data integration and transformation
    - Metadata management and catalog
    - Quality monitoring and validation
    - Security and access control
    """
    
    def __init__(self, config: Optional[ArchitectureConfig] = None):
        self.config = config or ArchitectureConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize base paths
        self.base_path = Path(self.config.base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize component managers
        self.schema_manager = SchemaManager(
            base_path=str(self.base_path / "schemas"),
            config={"encryption_required": self.config.encryption_required}
        )
        
        if self.config.enable_governance:
            self.governance_manager = DataGovernanceManager(
                base_path=str(self.base_path / "governance"),
                config={"compliance_frameworks": self.config.compliance_frameworks}
            )
        
        if self.config.enable_integration:
            self.integration_manager = DataIntegrationManager(
                base_path=str(self.base_path / "integration"),
                config={"quality_threshold": self.config.quality_threshold}
            )
        
        if self.config.enable_metadata:
            self.metadata_manager = MetadataManager(
                base_path=str(self.base_path / "metadata"),
                config={"auto_discovery": self.config.auto_discovery}
            )
        
        # Initialize architecture state
        self._initialize_architecture()
        
        self.logger.info("Data Architecture Orchestrator initialized successfully")
    
    def create_data_domain(self, domain_name: str, domain_config: Dict[str, Any]) -> bool:
        """Create a complete data domain with schemas, governance, and metadata."""
        try:
            self.logger.info(f"Creating data domain: {domain_name}")
            
            # Create domain schema
            schema_created = self._create_domain_schema(domain_name, domain_config)
            if not schema_created:
                return False
            
            # Set up governance policies
            if self.config.enable_governance:
                governance_created = self._create_domain_governance(domain_name, domain_config)
                if not governance_created:
                    self.logger.warning(f"Governance setup failed for domain {domain_name}")
            
            # Register metadata resources
            if self.config.enable_metadata:
                metadata_created = self._register_domain_metadata(domain_name, domain_config)
                if not metadata_created:
                    self.logger.warning(f"Metadata registration failed for domain {domain_name}")
            
            # Create integration templates
            if self.config.enable_integration:
                integration_created = self._create_domain_integration(domain_name, domain_config)
                if not integration_created:
                    self.logger.warning(f"Integration setup failed for domain {domain_name}")
            
            self.logger.info(f"Data domain {domain_name} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating data domain {domain_name}: {str(e)}")
            return False
    
    def register_system(self, system_name: str, system_config: Dict[str, Any]) -> bool:
        """Register a new system in the data architecture."""
        try:
            self.logger.info(f"Registering system: {system_name}")
            
            # Discover system resources
            if self.config.enable_metadata and self.config.auto_discovery:
                discovered_resources = self.metadata_manager.discover_resources(
                    system=system_name,
                    connection_config=system_config.get("connection", {})
                )
                self.logger.info(f"Discovered {len(discovered_resources)} resources in {system_name}")
            
            # Create system-level governance
            if self.config.enable_governance:
                self._create_system_governance(system_name, system_config)
            
            # Set up integration patterns
            if self.config.enable_integration:
                self._create_system_integration(system_name, system_config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering system {system_name}: {str(e)}")
            return False
    
    def deploy_schema(self, schema_name: str, version: str, target_systems: List[str]) -> Dict[str, Any]:
        """Deploy a schema to target systems with full governance validation."""
        try:
            self.logger.info(f"Deploying schema {schema_name} v{version} to {target_systems}")
            
            deployment_result = {
                "schema_name": schema_name,
                "version": version,
                "target_systems": target_systems,
                "status": "in_progress",
                "validations": {},
                "deployments": {},
                "errors": [],
                "warnings": []
            }
            
            # Get schema
            schema = self.schema_manager.get_schema(schema_name)
            if not schema:
                deployment_result["status"] = "failed"
                deployment_result["errors"].append(f"Schema {schema_name} not found")
                return deployment_result
            
            # Validate schema
            validation_result = self.schema_manager.validate_schema(schema)
            deployment_result["validations"]["schema"] = validation_result
            
            if not validation_result["valid"]:
                deployment_result["status"] = "failed"
                deployment_result["errors"].extend(validation_result["errors"])
                return deployment_result
            
            # Governance validation
            if self.config.enable_governance:
                governance_validation = self._validate_schema_governance(schema)
                deployment_result["validations"]["governance"] = governance_validation
                
                if not governance_validation["passed"]:
                    deployment_result["warnings"].extend(governance_validation.get("warnings", []))
            
            # Quality validation
            if self.config.enable_governance:
                quality_validation = self._validate_schema_quality(schema)
                deployment_result["validations"]["quality"] = quality_validation
            
            # Deploy to each target system
            for system in target_systems:
                system_deployment = self._deploy_schema_to_system(schema, system)
                deployment_result["deployments"][system] = system_deployment
                
                if not system_deployment.get("success", False):
                    deployment_result["errors"].append(f"Deployment to {system} failed")
            
            # Update status based on results
            if deployment_result["errors"]:
                deployment_result["status"] = "failed"
            elif deployment_result["warnings"]:
                deployment_result["status"] = "completed_with_warnings"
            else:
                deployment_result["status"] = "success"
            
            # Update metadata
            if self.config.enable_metadata:
                self._update_deployment_metadata(schema, target_systems, deployment_result)
            
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"Error deploying schema: {str(e)}")
            return {
                "status": "failed",
                "errors": [str(e)]
            }
    
    def run_quality_assessment(self, scope: str = "all") -> Dict[str, Any]:
        """Run comprehensive quality assessment across the architecture."""
        try:
            self.logger.info(f"Running quality assessment: {scope}")
            
            assessment = {
                "scope": scope,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "overall_score": 0.0,
                "components": {},
                "issues": [],
                "recommendations": []
            }
            
            # Schema quality assessment
            schema_quality = self._assess_schema_quality()
            assessment["components"]["schemas"] = schema_quality
            
            # Governance quality assessment
            if self.config.enable_governance:
                governance_quality = self._assess_governance_quality()
                assessment["components"]["governance"] = governance_quality
            
            # Integration quality assessment
            if self.config.enable_integration:
                integration_quality = self._assess_integration_quality()
                assessment["components"]["integration"] = integration_quality
            
            # Metadata quality assessment
            if self.config.enable_metadata:
                metadata_quality = self._assess_metadata_quality()
                assessment["components"]["metadata"] = metadata_quality
            
            # Calculate overall score
            component_scores = [comp["score"] for comp in assessment["components"].values()]
            assessment["overall_score"] = sum(component_scores) / len(component_scores) if component_scores else 0.0
            
            # Generate recommendations
            assessment["recommendations"] = self._generate_quality_recommendations(assessment)
            
            # Save assessment report
            self._save_quality_assessment(assessment)
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error running quality assessment: {str(e)}")
            return {"error": str(e)}
    
    def run_compliance_audit(self, frameworks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run comprehensive compliance audit."""
        try:
            if not self.config.enable_governance:
                return {"error": "Governance not enabled"}
            
            frameworks = frameworks or self.config.compliance_frameworks
            self.logger.info(f"Running compliance audit for frameworks: {frameworks}")
            
            audit_result = {
                "frameworks": frameworks,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "overall_status": "compliant",
                "framework_results": {},
                "violations": [],
                "recommendations": []
            }
            
            # Run compliance checks for each framework
            for framework in frameworks:
                try:
                    from governance.data_governance import ComplianceFramework
                    framework_enum = ComplianceFramework(framework.lower())
                    framework_result = self.governance_manager.run_compliance_checks(framework_enum)
                    audit_result["framework_results"][framework] = framework_result
                    
                    if framework_result.get("failed", 0) > 0:
                        audit_result["overall_status"] = "non_compliant"
                        audit_result["violations"].extend(framework_result.get("results", []))
                
                except ValueError:
                    self.logger.warning(f"Unknown compliance framework: {framework}")
            
            # Generate compliance recommendations
            audit_result["recommendations"] = self._generate_compliance_recommendations(audit_result)
            
            # Save audit report
            self._save_compliance_audit(audit_result)
            
            return audit_result
            
        except Exception as e:
            self.logger.error(f"Error running compliance audit: {str(e)}")
            return {"error": str(e)}
    
    def get_architecture_status(self) -> ArchitectureStatus:
        """Get overall status of the data architecture."""
        try:
            # Count schemas
            schemas_count = len(self.schema_manager.list_schemas())
            
            # Count governance policies
            governance_policies = 0
            if self.config.enable_governance:
                # This would count actual policies in a real implementation
                governance_policies = 10  # Placeholder
            
            # Count integration jobs
            integration_jobs = 0
            if self.config.enable_integration:
                # This would count actual jobs in a real implementation
                integration_jobs = 5  # Placeholder
            
            # Count metadata resources
            metadata_resources = 0
            if self.config.enable_metadata:
                catalog_summary = self.metadata_manager.get_catalog_summary()
                metadata_resources = catalog_summary.get("total_resources", 0)
            
            # Calculate quality score
            quality_assessment = self.run_quality_assessment("summary")
            quality_score = quality_assessment.get("overall_score", 0.0)
            
            # Determine compliance status
            compliance_status = "unknown"
            if self.config.enable_governance:
                compliance_audit = self.run_compliance_audit()
                compliance_status = compliance_audit.get("overall_status", "unknown")
            
            # Identify issues and recommendations
            issues = []
            recommendations = []
            
            if quality_score < self.config.quality_threshold:
                issues.append(f"Quality score ({quality_score:.2f}) below threshold ({self.config.quality_threshold})")
                recommendations.append("Run detailed quality assessment and address identified issues")
            
            if compliance_status == "non_compliant":
                issues.append("Compliance violations detected")
                recommendations.append("Review compliance audit results and remediate violations")
            
            if schemas_count == 0:
                issues.append("No schemas defined")
                recommendations.append("Define data schemas for your data domains")
            
            return ArchitectureStatus(
                schemas_count=schemas_count,
                governance_policies=governance_policies,
                integration_jobs=integration_jobs,
                metadata_resources=metadata_resources,
                quality_score=quality_score,
                compliance_status=compliance_status,
                last_updated=datetime.datetime.utcnow(),
                issues=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error getting architecture status: {str(e)}")
            return ArchitectureStatus(
                schemas_count=0,
                governance_policies=0,
                integration_jobs=0,
                metadata_resources=0,
                quality_score=0.0,
                compliance_status="error",
                last_updated=datetime.datetime.utcnow(),
                issues=[f"Error retrieving status: {str(e)}"],
                recommendations=["Check system logs and configuration"]
            )
    
    def generate_architecture_documentation(self) -> str:
        """Generate comprehensive documentation for the data architecture."""
        try:
            status = self.get_architecture_status()
            
            doc = []
            doc.append("# Data Architecture Documentation")
            doc.append("")
            doc.append(f"Generated on: {datetime.datetime.utcnow().isoformat()}")
            doc.append("")
            
            # Executive Summary
            doc.append("## Executive Summary")
            doc.append("")
            doc.append(f"- **Schemas:** {status.schemas_count}")
            doc.append(f"- **Governance Policies:** {status.governance_policies}")
            doc.append(f"- **Integration Jobs:** {status.integration_jobs}")
            doc.append(f"- **Metadata Resources:** {status.metadata_resources}")
            doc.append(f"- **Quality Score:** {status.quality_score:.2f}")
            doc.append(f"- **Compliance Status:** {status.compliance_status}")
            doc.append("")
            
            # Architecture Overview
            doc.append("## Architecture Overview")
            doc.append("")
            doc.append("The data architecture consists of the following components:")
            doc.append("")
            doc.append("- **Schema Management:** Centralized schema versioning and validation")
            if self.config.enable_governance:
                doc.append("- **Data Governance:** Access control, quality monitoring, and compliance")
            if self.config.enable_integration:
                doc.append("- **Data Integration:** ETL/ELT pipelines and data transformation")
            if self.config.enable_metadata:
                doc.append("- **Metadata Management:** Data catalog and resource discovery")
            doc.append("")
            
            # Schemas Section
            doc.append("## Schemas")
            doc.append("")
            schemas = self.schema_manager.list_schemas()
            if schemas:
                for schema_name in schemas:
                    schema = self.schema_manager.get_schema(schema_name)
                    if schema:
                        doc.append(f"### {schema.name}")
                        doc.append(f"- **Version:** {schema.version}")
                        doc.append(f"- **Type:** {schema.schema_type.value}")
                        doc.append(f"- **Description:** {schema.description}")
                        doc.append(f"- **Fields:** {len(schema.fields)}")
                        doc.append("")
            else:
                doc.append("No schemas defined.")
                doc.append("")
            
            # Governance Section
            if self.config.enable_governance:
                doc.append("## Data Governance")
                doc.append("")
                doc.append("### Compliance Frameworks")
                for framework in self.config.compliance_frameworks:
                    doc.append(f"- {framework}")
                doc.append("")
                
                doc.append("### Quality Monitoring")
                doc.append(f"- Quality threshold: {self.config.quality_threshold}")
                doc.append(f"- Current quality score: {status.quality_score:.2f}")
                doc.append("")
            
            # Issues and Recommendations
            if status.issues:
                doc.append("## Issues")
                doc.append("")
                for issue in status.issues:
                    doc.append(f"- {issue}")
                doc.append("")
            
            if status.recommendations:
                doc.append("## Recommendations")
                doc.append("")
                for rec in status.recommendations:
                    doc.append(f"- {rec}")
                doc.append("")
            
            # Configuration
            doc.append("## Configuration")
            doc.append("")
            doc.append(f"- **Base Path:** {self.config.base_path}")
            doc.append(f"- **Governance Enabled:** {self.config.enable_governance}")
            doc.append(f"- **Integration Enabled:** {self.config.enable_integration}")
            doc.append(f"- **Metadata Enabled:** {self.config.enable_metadata}")
            doc.append(f"- **Auto Discovery:** {self.config.auto_discovery}")
            doc.append(f"- **Encryption Required:** {self.config.encryption_required}")
            doc.append("")
            
            documentation = "\n".join(doc)
            
            # Save documentation
            doc_file = self.base_path / "architecture_documentation.md"
            with open(doc_file, 'w') as f:
                f.write(documentation)
            
            return documentation
            
        except Exception as e:
            self.logger.error(f"Error generating documentation: {str(e)}")
            return f"Error generating documentation: {str(e)}"
    
    # Private helper methods
    
    def _initialize_architecture(self) -> None:
        """Initialize the data architecture with default configurations."""
        try:
            # Create default quality rules if governance is enabled
            if self.config.enable_governance:
                self._create_default_quality_rules()
                self._create_default_compliance_rules()
            
            # Create default metadata rules if metadata is enabled
            if self.config.enable_metadata:
                self._create_default_metadata_rules()
            
            self.logger.info("Architecture initialization completed")
            
        except Exception as e:
            self.logger.error(f"Error initializing architecture: {str(e)}")
    
    def _create_domain_schema(self, domain_name: str, config: Dict[str, Any]) -> bool:
        """Create schema for a data domain."""
        try:
            # Extract schema configuration
            schema_config = config.get("schema", {})
            
            # Create schema fields based on configuration
            fields = []
            for field_config in schema_config.get("fields", []):
                field = SchemaField(
                    name=field_config["name"],
                    data_type=field_config["data_type"],
                    nullable=field_config.get("nullable", True),
                    primary_key=field_config.get("primary_key", False),
                    description=field_config.get("description"),
                    classification=DataClassification(field_config.get("classification", "internal"))
                )
                fields.append(field)
            
            # Create schema
            schema = Schema(
                name=domain_name,
                version="1.0.0",
                schema_type=SchemaType(schema_config.get("type", "relational")),
                description=config.get("description", f"Schema for {domain_name} domain"),
                fields=fields,
                business_owner=config.get("business_owner"),
                technical_owner=config.get("technical_owner"),
                classification=DataClassification(config.get("classification", "internal")),
                retention_policy=config.get("retention_policy", self.config.default_retention_policy),
                tags=config.get("tags", [])
            )
            
            return self.schema_manager.create_schema(schema)
            
        except Exception as e:
            self.logger.error(f"Error creating domain schema: {str(e)}")
            return False
    
    def _create_domain_governance(self, domain_name: str, config: Dict[str, Any]) -> bool:
        """Create governance policies for a data domain."""
        try:
            # Create access policies
            access_config = config.get("access", {})
            if access_config:
                from governance.data_governance import AccessLevel
                
                policy = AccessPolicy(
                    policy_id="",
                    name=f"{domain_name}_access_policy",
                    description=f"Access policy for {domain_name} domain",
                    resource_pattern=f"{domain_name}.*",
                    principals=access_config.get("principals", []),
                    access_levels=[AccessLevel(level) for level in access_config.get("levels", ["read"])],
                    created_by=config.get("technical_owner", "system")
                )
                
                self.governance_manager.create_access_policy(policy)
            
            # Create quality rules
            quality_config = config.get("quality", {})
            if quality_config:
                from governance.data_governance import DataQualityRule
                
                for rule_config in quality_config.get("rules", []):
                    quality_rule = QualityRule(
                        rule_id="",
                        name=rule_config["name"],
                        description=rule_config.get("description", ""),
                        rule_type=DataQualityRule(rule_config["type"]),
                        target_schema=domain_name,
                        target_field=rule_config.get("field"),
                        parameters=rule_config.get("parameters", {}),
                        severity=rule_config.get("severity", "medium"),
                        created_by=config.get("technical_owner", "system")
                    )
                    
                    self.governance_manager.create_quality_rule(quality_rule)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating domain governance: {str(e)}")
            return False
    
    def _register_domain_metadata(self, domain_name: str, config: Dict[str, Any]) -> bool:
        """Register metadata resources for a data domain."""
        try:
            # Create domain resource
            domain_resource = DataResource(
                resource_id="",
                name=domain_name,
                type=ResourceType.SCHEMA,
                system=config.get("system", "internal"),
                description=config.get("description", f"Data domain: {domain_name}"),
                owner=config.get("business_owner"),
                steward=config.get("technical_owner"),
                tags=config.get("tags", [])
            )
            
            self.metadata_manager.register_resource(domain_resource)
            
            # Add custom metadata
            metadata_config = config.get("metadata", {})
            if metadata_config:
                custom_metadata = {}
                for key, value in metadata_config.items():
                    custom_metadata[key] = MetadataAttribute(
                        name=key,
                        value=value,
                        type="string",
                        source="domain_config"
                    )
                
                self.metadata_manager.add_metadata(domain_resource.resource_id, custom_metadata)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering domain metadata: {str(e)}")
            return False
    
    def _create_domain_integration(self, domain_name: str, config: Dict[str, Any]) -> bool:
        """Create integration templates for a data domain."""
        try:
            integration_config = config.get("integration", {})
            if not integration_config:
                return True  # No integration configuration provided
            
            # Create integration job template
            from integration.data_integration import IntegrationPattern, DataSourceType, DataFormat
            
            # Create source configuration
            source_config = integration_config.get("source", {})
            source = DataSource(
                source_id="",
                name=f"{domain_name}_source",
                type=DataSourceType(source_config.get("type", "relational_db")),
                connection_config=source_config.get("connection", {}),
                format=DataFormat(source_config.get("format", "json"))
            )
            
            # Create target configuration
            target_config = integration_config.get("target", {})
            target = DataSource(
                source_id="",
                name=f"{domain_name}_target",
                type=DataSourceType(target_config.get("type", "relational_db")),
                connection_config=target_config.get("connection", {}),
                format=DataFormat(target_config.get("format", "json"))
            )
            
            # Create integration job
            job = IntegrationJob(
                job_id="",
                name=f"{domain_name}_integration",
                description=f"Integration job for {domain_name} domain",
                pattern=IntegrationPattern(integration_config.get("pattern", "etl")),
                source_configs=[source],
                target_configs=[target],
                transformations=[],
                created_by=config.get("technical_owner", "system")
            )
            
            return self.integration_manager.create_integration_job(job)
            
        except Exception as e:
            self.logger.error(f"Error creating domain integration: {str(e)}")
            return False
    
    def _create_default_quality_rules(self) -> None:
        """Create default quality rules."""
        try:
            from governance.data_governance import DataQualityRule
            
            default_rules = [
                {
                    "name": "no_null_primary_keys",
                    "description": "Primary key fields should not be null",
                    "rule_type": DataQualityRule.NOT_NULL,
                    "severity": "critical"
                },
                {
                    "name": "unique_primary_keys",
                    "description": "Primary key fields should be unique",
                    "rule_type": DataQualityRule.UNIQUE,
                    "severity": "critical"
                },
                {
                    "name": "data_completeness",
                    "description": "Data completeness check",
                    "rule_type": DataQualityRule.COMPLETENESS,
                    "severity": "medium"
                }
            ]
            
            for rule_config in default_rules:
                rule = QualityRule(
                    rule_id="",
                    name=rule_config["name"],
                    description=rule_config["description"],
                    rule_type=rule_config["rule_type"],
                    target_schema="*",  # Apply to all schemas
                    severity=rule_config["severity"],
                    created_by="system"
                )
                
                self.governance_manager.create_quality_rule(rule)
            
        except Exception as e:
            self.logger.error(f"Error creating default quality rules: {str(e)}")
    
    def _create_default_compliance_rules(self) -> None:
        """Create default compliance rules."""
        try:
            from governance.data_governance import ComplianceFramework
            
            for framework_name in self.config.compliance_frameworks:
                try:
                    framework = ComplianceFramework(framework_name.lower())
                    
                    rule = ComplianceRule(
                        rule_id="",
                        name=f"default_{framework_name.lower()}_rule",
                        framework=framework,
                        description=f"Default compliance rule for {framework_name}",
                        requirement="Basic compliance check",
                        applicable_schemas=["*"],
                        owner="system"
                    )
                    
                    self.governance_manager.create_compliance_rule(rule)
                    
                except ValueError:
                    self.logger.warning(f"Unknown compliance framework: {framework_name}")
            
        except Exception as e:
            self.logger.error(f"Error creating default compliance rules: {str(e)}")
    
    def _create_default_metadata_rules(self) -> None:
        """Create default metadata extraction rules."""
        try:
            from metadata.metadata_manager import MetadataRule
            
            default_rules = [
                {
                    "name": "extract_tags_from_name",
                    "description": "Extract tags from resource names",
                    "pattern": r".*",
                    "metadata_extraction": {"tags_from_name": True}
                },
                {
                    "name": "classify_pii_data",
                    "description": "Classify PII data based on patterns",
                    "pattern": r".*(user|person|customer|email|phone).*",
                    "metadata_extraction": {"classification_from_path": True}
                }
            ]
            
            for rule_config in default_rules:
                rule = MetadataRule(
                    rule_id="",
                    name=rule_config["name"],
                    description=rule_config["description"],
                    pattern=rule_config["pattern"],
                    metadata_extraction=rule_config["metadata_extraction"],
                    created_by="system"
                )
                
                self.metadata_manager.create_metadata_rule(rule)
            
        except Exception as e:
            self.logger.error(f"Error creating default metadata rules: {str(e)}")
    
    def _validate_schema_governance(self, schema: Schema) -> Dict[str, Any]:
        """Validate schema against governance policies."""
        validation = {
            "passed": True,
            "warnings": [],
            "recommendations": []
        }
        
        try:
            # Check for sensitive data without proper classification
            sensitive_fields = [f for f in schema.fields 
                             if f.classification in [DataClassification.PII, DataClassification.PHI]]
            
            if sensitive_fields and not schema.retention_policy:
                validation["warnings"].append("Schema contains sensitive data but no retention policy defined")
            
            if sensitive_fields and not self.config.encryption_required:
                validation["warnings"].append("Schema contains sensitive data but encryption is not enforced")
            
            # Check for proper ownership
            if not schema.business_owner:
                validation["warnings"].append("No business owner defined")
            
            if not schema.technical_owner:
                validation["warnings"].append("No technical owner defined")
            
        except Exception as e:
            self.logger.error(f"Error validating schema governance: {str(e)}")
            validation["passed"] = False
        
        return validation
    
    def _validate_schema_quality(self, schema: Schema) -> Dict[str, Any]:
        """Validate schema quality."""
        validation = {
            "score": 1.0,
            "issues": [],
            "recommendations": []
        }
        
        try:
            score = 1.0
            
            # Check for proper field documentation
            undocumented_fields = [f for f in schema.fields if not f.description]
            if undocumented_fields:
                score -= 0.2
                validation["issues"].append(f"{len(undocumented_fields)} fields lack descriptions")
            
            # Check for proper data types
            generic_types = [f for f in schema.fields if f.data_type.upper() in ["TEXT", "STRING", "VARCHAR"]]
            if len(generic_types) > len(schema.fields) * 0.5:
                score -= 0.1
                validation["issues"].append("Many fields use generic data types")
            
            # Check for indexes on important fields
            if not schema.indexes:
                score -= 0.1
                validation["issues"].append("No indexes defined")
            
            validation["score"] = max(0.0, score)
            
        except Exception as e:
            self.logger.error(f"Error validating schema quality: {str(e)}")
            validation["score"] = 0.0
        
        return validation
    
    def _deploy_schema_to_system(self, schema: Schema, system: str) -> Dict[str, Any]:
        """Deploy schema to a specific system."""
        # Placeholder implementation
        return {
            "success": True,
            "system": system,
            "deployment_time": datetime.datetime.utcnow().isoformat(),
            "message": f"Schema {schema.name} deployed to {system}"
        }
    
    def _update_deployment_metadata(self, schema: Schema, systems: List[str], result: Dict[str, Any]) -> None:
        """Update metadata after schema deployment."""
        try:
            # Add deployment metadata to schema resource
            deployment_metadata = {
                "last_deployment": MetadataAttribute(
                    name="last_deployment",
                    value=datetime.datetime.utcnow().isoformat(),
                    type="datetime",
                    source="orchestrator"
                ),
                "deployed_systems": MetadataAttribute(
                    name="deployed_systems",
                    value=systems,
                    type="list",
                    source="orchestrator"
                ),
                "deployment_status": MetadataAttribute(
                    name="deployment_status",
                    value=result["status"],
                    type="string",
                    source="orchestrator"
                )
            }
            
            # Find schema resource in metadata
            search_results = self.metadata_manager.search_resources(
                query=schema.name,
                filters={"type": "schema"}
            )
            
            if search_results:
                resource_id = search_results[0].resource.resource_id
                self.metadata_manager.add_metadata(resource_id, deployment_metadata)
            
        except Exception as e:
            self.logger.error(f"Error updating deployment metadata: {str(e)}")
    
    def _assess_schema_quality(self) -> Dict[str, Any]:
        """Assess overall schema quality."""
        schemas = self.schema_manager.list_schemas()
        
        if not schemas:
            return {"score": 0.0, "count": 0, "issues": ["No schemas defined"]}
        
        total_score = 0.0
        issues = []
        
        for schema_name in schemas:
            schema = self.schema_manager.get_schema(schema_name)
            if schema:
                validation = self.schema_manager.validate_schema(schema)
                if not validation["valid"]:
                    issues.extend(validation["errors"])
                
                quality_validation = self._validate_schema_quality(schema)
                total_score += quality_validation["score"]
        
        return {
            "score": total_score / len(schemas),
            "count": len(schemas),
            "issues": issues
        }
    
    def _assess_governance_quality(self) -> Dict[str, Any]:
        """Assess governance quality."""
        # Placeholder implementation
        return {
            "score": 0.8,
            "policies_count": 10,
            "compliance_status": "mostly_compliant"
        }
    
    def _assess_integration_quality(self) -> Dict[str, Any]:
        """Assess integration quality."""
        # Placeholder implementation
        return {
            "score": 0.7,
            "jobs_count": 5,
            "success_rate": 0.9
        }
    
    def _assess_metadata_quality(self) -> Dict[str, Any]:
        """Assess metadata quality."""
        if not self.config.enable_metadata:
            return {"score": 0.0, "message": "Metadata management disabled"}
        
        catalog_summary = self.metadata_manager.get_catalog_summary()
        
        total_resources = catalog_summary.get("total_resources", 0)
        if total_resources == 0:
            return {"score": 0.0, "resources_count": 0, "issues": ["No resources in catalog"]}
        
        # Calculate metadata coverage
        coverage_count = sum(catalog_summary.get("metadata_coverage", {}).values())
        coverage_ratio = coverage_count / total_resources if total_resources > 0 else 0
        
        return {
            "score": coverage_ratio,
            "resources_count": total_resources,
            "coverage_ratio": coverage_ratio
        }
    
    def _generate_quality_recommendations(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        overall_score = assessment.get("overall_score", 0)
        
        if overall_score < 0.6:
            recommendations.append("Overall quality is low. Prioritize schema documentation and validation.")
        
        schema_component = assessment.get("components", {}).get("schemas", {})
        if schema_component.get("score", 0) < 0.7:
            recommendations.append("Improve schema documentation and add proper data types.")
        
        metadata_component = assessment.get("components", {}).get("metadata", {})
        if metadata_component.get("coverage_ratio", 0) < 0.5:
            recommendations.append("Increase metadata coverage by documenting more resources.")
        
        return recommendations
    
    def _generate_compliance_recommendations(self, audit_result: Dict[str, Any]) -> List[str]:
        """Generate compliance improvement recommendations."""
        recommendations = []
        
        if audit_result.get("overall_status") == "non_compliant":
            recommendations.append("Address compliance violations immediately.")
            recommendations.append("Review access controls and data classification.")
            recommendations.append("Implement data retention and deletion policies.")
        
        return recommendations
    
    def _save_quality_assessment(self, assessment: Dict[str, Any]) -> None:
        """Save quality assessment report."""
        try:
            reports_dir = self.base_path / "reports"
            reports_dir.mkdir(exist_ok=True)
            
            report_file = reports_dir / f"quality_assessment_{datetime.date.today().isoformat()}.json"
            with open(report_file, 'w') as f:
                json.dump(assessment, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Error saving quality assessment: {str(e)}")
    
    def _save_compliance_audit(self, audit_result: Dict[str, Any]) -> None:
        """Save compliance audit report."""
        try:
            reports_dir = self.base_path / "reports"
            reports_dir.mkdir(exist_ok=True)
            
            report_file = reports_dir / f"compliance_audit_{datetime.date.today().isoformat()}.json"
            with open(report_file, 'w') as f:
                json.dump(audit_result, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Error saving compliance audit: {str(e)}")
    
    def _create_system_governance(self, system_name: str, config: Dict[str, Any]) -> None:
        """Create governance policies for a system."""
        # Placeholder implementation
        pass
    
    def _create_system_integration(self, system_name: str, config: Dict[str, Any]) -> None:
        """Create integration patterns for a system."""
        # Placeholder implementation
        pass 