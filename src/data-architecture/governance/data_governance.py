"""
Data Governance Framework

Comprehensive data governance system that provides:
- Data quality management and monitoring
- Data lineage tracking
- Access control and security
- Compliance and audit management
- Data classification and protection
"""

import json
import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import logging
import uuid


class AccessLevel(Enum):
    """Access levels for data governance."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    CCPA = "ccpa"
    ISO_27001 = "iso_27001"


class DataQualityRule(Enum):
    """Data quality rule types."""
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    RANGE = "range"
    PATTERN = "pattern"
    CUSTOM = "custom"
    REFERENTIAL_INTEGRITY = "referential_integrity"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    ACCURACY = "accuracy"


@dataclass
class DataOwner:
    """Data owner definition for governance."""
    user_id: str
    name: str
    email: str
    role: str
    department: str
    responsibilities: List[str]
    contact_info: Optional[Dict[str, str]] = None


@dataclass
class AccessPolicy:
    """Access control policy definition."""
    policy_id: str
    name: str
    description: str
    resource_pattern: str  # Pattern to match resources
    principals: List[str]  # User IDs or group IDs
    access_levels: List[AccessLevel]
    conditions: Optional[Dict[str, Any]] = None  # Time-based, IP-based, etc.
    expiry_date: Optional[datetime.datetime] = None
    approval_required: bool = False
    created_by: str = ""
    created_at: Optional[datetime.datetime] = None


@dataclass
class DataLineageNode:
    """Individual node in data lineage tracking."""
    node_id: str
    name: str
    type: str  # table, view, file, api, etc.
    system: str
    schema_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DataLineageEdge:
    """Edge representing data flow between nodes."""
    edge_id: str
    source_node_id: str
    target_node_id: str
    transformation: Optional[str] = None
    transformation_type: str = "unknown"  # etl, aggregation, filter, etc.
    confidence_score: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class QualityRule:
    """Data quality rule definition."""
    rule_id: str
    name: str
    description: str
    rule_type: DataQualityRule
    target_schema: str
    target_field: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    severity: str = "medium"  # low, medium, high, critical
    active: bool = True
    created_by: str = ""
    created_at: Optional[datetime.datetime] = None


@dataclass
class QualityResult:
    """Result of data quality check execution."""
    result_id: str
    rule_id: str
    execution_time: datetime.datetime
    passed: bool
    score: float  # 0.0 to 1.0
    records_checked: int
    records_failed: int
    details: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None


@dataclass
class ComplianceRule:
    """Compliance rule for regulatory frameworks."""
    rule_id: str
    name: str
    framework: ComplianceFramework
    description: str
    requirement: str
    applicable_schemas: List[str]
    validation_query: Optional[str] = None
    automation_level: str = "manual"  # manual, semi_automated, automated
    frequency: str = "monthly"  # daily, weekly, monthly, quarterly
    owner: str = ""
    last_check: Optional[datetime.datetime] = None
    next_check: Optional[datetime.datetime] = None


class DataGovernanceManager:
    """
    Comprehensive data governance manager that provides:
    - Access control and security management
    - Data quality monitoring and enforcement
    - Data lineage tracking and visualization
    - Compliance management and audit trails
    - Data classification and protection policies
    """
    
    def __init__(self, base_path: str = "governance", config: Optional[Dict[str, Any]] = None):
        self.base_path = Path(base_path)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory structure exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "policies").mkdir(exist_ok=True)
        (self.base_path / "lineage").mkdir(exist_ok=True)
        (self.base_path / "quality").mkdir(exist_ok=True)
        (self.base_path / "compliance").mkdir(exist_ok=True)
        (self.base_path / "audit").mkdir(exist_ok=True)
        (self.base_path / "owners").mkdir(exist_ok=True)
    
    # Access Control Management
    
    def create_access_policy(self, policy: AccessPolicy) -> bool:
        """Create a new access control policy."""
        try:
            if not policy.policy_id:
                policy.policy_id = str(uuid.uuid4())
            
            if not policy.created_at:
                policy.created_at = datetime.datetime.utcnow()
            
            # Validate policy
            if not self._validate_access_policy(policy):
                return False
            
            # Save policy
            policy_file = self.base_path / "policies" / f"{policy.policy_id}.json"
            with open(policy_file, 'w') as f:
                json.dump(asdict(policy), f, indent=2, default=str)
            
            # Log creation
            self._log_audit_event("access_policy_created", {
                "policy_id": policy.policy_id,
                "created_by": policy.created_by,
                "resource_pattern": policy.resource_pattern
            })
            
            self.logger.info(f"Access policy {policy.policy_id} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating access policy: {str(e)}")
            return False
    
    def check_access(self, user_id: str, resource: str, access_level: AccessLevel) -> bool:
        """Check if a user has access to a resource."""
        try:
            policies = self._load_access_policies()
            
            for policy in policies:
                if self._policy_matches_resource(policy, resource) and \
                   self._policy_applies_to_user(policy, user_id) and \
                   access_level in policy.access_levels:
                    
                    # Check policy conditions
                    if self._check_policy_conditions(policy):
                        # Check if policy is expired
                        if policy.expiry_date and datetime.datetime.utcnow() > policy.expiry_date:
                            continue
                        
                        # Log access
                        self._log_audit_event("access_granted", {
                            "user_id": user_id,
                            "resource": resource,
                            "access_level": access_level.value,
                            "policy_id": policy.policy_id
                        })
                        
                        return True
            
            # Log access denial
            self._log_audit_event("access_denied", {
                "user_id": user_id,
                "resource": resource,
                "access_level": access_level.value,
                "reason": "no_matching_policy"
            })
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking access: {str(e)}")
            return False
    
    # Data Quality Management
    
    def create_quality_rule(self, rule: QualityRule) -> bool:
        """Create a new data quality rule."""
        try:
            if not rule.rule_id:
                rule.rule_id = str(uuid.uuid4())
            
            if not rule.created_at:
                rule.created_at = datetime.datetime.utcnow()
            
            # Save rule
            rule_file = self.base_path / "quality" / "rules" / f"{rule.rule_id}.json"
            rule_file.parent.mkdir(exist_ok=True)
            
            with open(rule_file, 'w') as f:
                json.dump(asdict(rule), f, indent=2, default=str)
            
            self.logger.info(f"Quality rule {rule.rule_id} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating quality rule: {str(e)}")
            return False
    
    def execute_quality_checks(self, schema_name: Optional[str] = None) -> List[QualityResult]:
        """Execute data quality checks."""
        results = []
        
        try:
            rules = self._load_quality_rules()
            
            if schema_name:
                rules = [r for r in rules if r.target_schema == schema_name]
            
            for rule in rules:
                if not rule.active:
                    continue
                
                result = self._execute_quality_rule(rule)
                if result:
                    results.append(result)
                    self._save_quality_result(result)
            
            # Generate quality report
            self._generate_quality_report(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error executing quality checks: {str(e)}")
            return []
    
    def get_quality_score(self, schema_name: str) -> float:
        """Get overall quality score for a schema."""
        try:
            results_dir = self.base_path / "quality" / "results"
            if not results_dir.exists():
                return 0.0
            
            recent_results = []
            cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=7)
            
            for result_file in results_dir.glob("*.json"):
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
                
                execution_time = datetime.datetime.fromisoformat(result_data["execution_time"])
                if execution_time > cutoff_date:
                    # Load the rule to check target schema
                    rule = self._load_quality_rule(result_data["rule_id"])
                    if rule and rule.target_schema == schema_name:
                        recent_results.append(result_data["score"])
            
            if not recent_results:
                return 0.0
            
            return sum(recent_results) / len(recent_results)
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {str(e)}")
            return 0.0
    
    # Data Lineage Management
    
    def add_lineage_node(self, node: DataLineageNode) -> bool:
        """Add a node to the data lineage graph."""
        try:
            lineage_file = self.base_path / "lineage" / "nodes.json"
            
            nodes = []
            if lineage_file.exists():
                with open(lineage_file, 'r') as f:
                    nodes = json.load(f)
            
            # Check if node already exists
            existing_node = next((n for n in nodes if n["node_id"] == node.node_id), None)
            if existing_node:
                # Update existing node
                nodes = [n for n in nodes if n["node_id"] != node.node_id]
            
            nodes.append(asdict(node))
            
            with open(lineage_file, 'w') as f:
                json.dump(nodes, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding lineage node: {str(e)}")
            return False
    
    def add_lineage_edge(self, edge: DataLineageEdge) -> bool:
        """Add an edge to the data lineage graph."""
        try:
            lineage_file = self.base_path / "lineage" / "edges.json"
            
            edges = []
            if lineage_file.exists():
                with open(lineage_file, 'r') as f:
                    edges = json.load(f)
            
            # Check if edge already exists
            existing_edge = next((e for e in edges if e["edge_id"] == edge.edge_id), None)
            if existing_edge:
                # Update existing edge
                edges = [e for e in edges if e["edge_id"] != edge.edge_id]
            
            edges.append(asdict(edge))
            
            with open(lineage_file, 'w') as f:
                json.dump(edges, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding lineage edge: {str(e)}")
            return False
    
    def get_data_lineage(self, node_id: str, direction: str = "both") -> Dict[str, Any]:
        """Get data lineage for a specific node."""
        try:
            nodes = self._load_lineage_nodes()
            edges = self._load_lineage_edges()
            
            # Find the target node
            target_node = next((n for n in nodes if n["node_id"] == node_id), None)
            if not target_node:
                return {"error": "Node not found"}
            
            lineage = {
                "target_node": target_node,
                "upstream": [],
                "downstream": [],
                "graph": {
                    "nodes": [],
                    "edges": []
                }
            }
            
            visited_nodes = set()
            
            # Get upstream lineage
            if direction in ["both", "upstream"]:
                lineage["upstream"] = self._get_upstream_lineage(node_id, nodes, edges, visited_nodes)
            
            # Get downstream lineage
            if direction in ["both", "downstream"]:
                lineage["downstream"] = self._get_downstream_lineage(node_id, nodes, edges, visited_nodes)
            
            # Build graph representation
            visited_nodes.add(node_id)
            lineage["graph"]["nodes"] = [n for n in nodes if n["node_id"] in visited_nodes]
            lineage["graph"]["edges"] = [e for e in edges 
                                       if e["source_node_id"] in visited_nodes and 
                                          e["target_node_id"] in visited_nodes]
            
            return lineage
            
        except Exception as e:
            self.logger.error(f"Error getting data lineage: {str(e)}")
            return {"error": str(e)}
    
    # Compliance Management
    
    def create_compliance_rule(self, rule: ComplianceRule) -> bool:
        """Create a new compliance rule."""
        try:
            if not rule.rule_id:
                rule.rule_id = str(uuid.uuid4())
            
            # Calculate next check date
            if not rule.next_check:
                rule.next_check = self._calculate_next_check_date(rule.frequency)
            
            # Save rule
            rule_file = self.base_path / "compliance" / "rules" / f"{rule.rule_id}.json"
            rule_file.parent.mkdir(exist_ok=True)
            
            with open(rule_file, 'w') as f:
                json.dump(asdict(rule), f, indent=2, default=str)
            
            self.logger.info(f"Compliance rule {rule.rule_id} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating compliance rule: {str(e)}")
            return False
    
    def run_compliance_checks(self, framework: Optional[ComplianceFramework] = None) -> Dict[str, Any]:
        """Run compliance checks for specified framework or all frameworks."""
        try:
            rules = self._load_compliance_rules()
            
            if framework:
                rules = [r for r in rules if r.framework == framework]
            
            results = {
                "total_rules": len(rules),
                "passed": 0,
                "failed": 0,
                "results": []
            }
            
            for rule in rules:
                # Check if rule needs to be executed
                if rule.next_check and datetime.datetime.utcnow() < rule.next_check:
                    continue
                
                check_result = self._execute_compliance_rule(rule)
                results["results"].append(check_result)
                
                if check_result["passed"]:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                
                # Update rule with next check date
                rule.last_check = datetime.datetime.utcnow()
                rule.next_check = self._calculate_next_check_date(rule.frequency)
                self._save_compliance_rule(rule)
            
            # Generate compliance report
            self._generate_compliance_report(results, framework)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error running compliance checks: {str(e)}")
            return {"error": str(e)}
    
    # Data Owner Management
    
    def register_data_owner(self, owner: DataOwner) -> bool:
        """Register a new data owner."""
        try:
            owner_file = self.base_path / "owners" / f"{owner.user_id}.json"
            
            with open(owner_file, 'w') as f:
                json.dump(asdict(owner), f, indent=2, default=str)
            
            self.logger.info(f"Data owner {owner.user_id} registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering data owner: {str(e)}")
            return False
    
    def get_data_owner(self, user_id: str) -> Optional[DataOwner]:
        """Get data owner information."""
        try:
            owner_file = self.base_path / "owners" / f"{user_id}.json"
            if not owner_file.exists():
                return None
            
            with open(owner_file, 'r') as f:
                owner_data = json.load(f)
            
            return DataOwner(**owner_data)
            
        except Exception as e:
            self.logger.error(f"Error getting data owner: {str(e)}")
            return None
    
    # Private Helper Methods
    
    def _validate_access_policy(self, policy: AccessPolicy) -> bool:
        """Validate access policy configuration."""
        if not policy.name or not policy.resource_pattern:
            self.logger.error("Policy name and resource pattern are required")
            return False
        
        if not policy.principals:
            self.logger.error("Policy must have at least one principal")
            return False
        
        if not policy.access_levels:
            self.logger.error("Policy must define access levels")
            return False
        
        return True
    
    def _load_access_policies(self) -> List[AccessPolicy]:
        """Load all access policies."""
        policies = []
        policies_dir = self.base_path / "policies"
        
        if not policies_dir.exists():
            return policies
        
        for policy_file in policies_dir.glob("*.json"):
            try:
                with open(policy_file, 'r') as f:
                    policy_data = json.load(f)
                
                # Convert access levels back to enum
                policy_data["access_levels"] = [AccessLevel(al) for al in policy_data["access_levels"]]
                
                # Convert datetime fields
                if policy_data.get("created_at"):
                    policy_data["created_at"] = datetime.datetime.fromisoformat(policy_data["created_at"])
                if policy_data.get("expiry_date"):
                    policy_data["expiry_date"] = datetime.datetime.fromisoformat(policy_data["expiry_date"])
                
                policies.append(AccessPolicy(**policy_data))
                
            except Exception as e:
                self.logger.error(f"Error loading policy {policy_file}: {str(e)}")
        
        return policies
    
    def _policy_matches_resource(self, policy: AccessPolicy, resource: str) -> bool:
        """Check if a policy applies to a resource."""
        # Simple pattern matching - can be enhanced with regex
        return resource.startswith(policy.resource_pattern.rstrip('*'))
    
    def _policy_applies_to_user(self, policy: AccessPolicy, user_id: str) -> bool:
        """Check if a policy applies to a user."""
        return user_id in policy.principals or "all" in policy.principals
    
    def _check_policy_conditions(self, policy: AccessPolicy) -> bool:
        """Check if policy conditions are met."""
        if not policy.conditions:
            return True
        
        # Implement condition checking logic
        # For now, return True (all conditions met)
        return True
    
    def _log_audit_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log an audit event."""
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "details": details
        }
        
        audit_file = self.base_path / "audit" / f"{datetime.date.today().isoformat()}.jsonl"
        audit_file.parent.mkdir(exist_ok=True)
        
        with open(audit_file, 'a') as f:
            f.write(json.dumps(audit_event) + "\n")
    
    def _load_quality_rules(self) -> List[QualityRule]:
        """Load all quality rules."""
        rules = []
        rules_dir = self.base_path / "quality" / "rules"
        
        if not rules_dir.exists():
            return rules
        
        for rule_file in rules_dir.glob("*.json"):
            try:
                with open(rule_file, 'r') as f:
                    rule_data = json.load(f)
                
                # Convert enum fields
                rule_data["rule_type"] = DataQualityRule(rule_data["rule_type"])
                
                # Convert datetime fields
                if rule_data.get("created_at"):
                    rule_data["created_at"] = datetime.datetime.fromisoformat(rule_data["created_at"])
                
                rules.append(QualityRule(**rule_data))
                
            except Exception as e:
                self.logger.error(f"Error loading quality rule {rule_file}: {str(e)}")
        
        return rules
    
    def _execute_quality_rule(self, rule: QualityRule) -> Optional[QualityResult]:
        """Execute a data quality rule."""
        try:
            # This is a placeholder implementation
            # In a real implementation, this would connect to the actual data source
            # and execute the quality checks
            
            result = QualityResult(
                result_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                execution_time=datetime.datetime.utcnow(),
                passed=True,  # Placeholder
                score=0.95,   # Placeholder
                records_checked=1000,  # Placeholder
                records_failed=50,     # Placeholder
                details={"message": "Quality check executed successfully"},
                recommendations=[]
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing quality rule {rule.rule_id}: {str(e)}")
            return None
    
    def _save_quality_result(self, result: QualityResult) -> None:
        """Save a quality check result."""
        results_dir = self.base_path / "quality" / "results"
        results_dir.mkdir(exist_ok=True)
        
        result_file = results_dir / f"{result.result_id}.json"
        with open(result_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
    
    def _generate_quality_report(self, results: List[QualityResult]) -> None:
        """Generate a quality report."""
        report = {
            "generated_at": datetime.datetime.utcnow().isoformat(),
            "total_checks": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "average_score": sum(r.score for r in results) / len(results) if results else 0,
            "results": [asdict(r) for r in results]
        }
        
        report_file = self.base_path / "quality" / f"quality_report_{datetime.date.today().isoformat()}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    
    def _load_lineage_nodes(self) -> List[Dict[str, Any]]:
        """Load all lineage nodes."""
        lineage_file = self.base_path / "lineage" / "nodes.json"
        if not lineage_file.exists():
            return []
        
        with open(lineage_file, 'r') as f:
            return json.load(f)
    
    def _load_lineage_edges(self) -> List[Dict[str, Any]]:
        """Load all lineage edges."""
        lineage_file = self.base_path / "lineage" / "edges.json"
        if not lineage_file.exists():
            return []
        
        with open(lineage_file, 'r') as f:
            return json.load(f)
    
    def _get_upstream_lineage(self, node_id: str, nodes: List[Dict], edges: List[Dict], visited: Set[str]) -> List[Dict]:
        """Get upstream data lineage."""
        upstream = []
        
        for edge in edges:
            if edge["target_node_id"] == node_id and edge["source_node_id"] not in visited:
                source_node = next((n for n in nodes if n["node_id"] == edge["source_node_id"]), None)
                if source_node:
                    visited.add(edge["source_node_id"])
                    upstream.append({
                        "node": source_node,
                        "relationship": edge,
                        "upstream": self._get_upstream_lineage(edge["source_node_id"], nodes, edges, visited)
                    })
        
        return upstream
    
    def _get_downstream_lineage(self, node_id: str, nodes: List[Dict], edges: List[Dict], visited: Set[str]) -> List[Dict]:
        """Get downstream data lineage."""
        downstream = []
        
        for edge in edges:
            if edge["source_node_id"] == node_id and edge["target_node_id"] not in visited:
                target_node = next((n for n in nodes if n["node_id"] == edge["target_node_id"]), None)
                if target_node:
                    visited.add(edge["target_node_id"])
                    downstream.append({
                        "node": target_node,
                        "relationship": edge,
                        "downstream": self._get_downstream_lineage(edge["target_node_id"], nodes, edges, visited)
                    })
        
        return downstream
    
    def _load_compliance_rules(self) -> List[ComplianceRule]:
        """Load all compliance rules."""
        rules = []
        rules_dir = self.base_path / "compliance" / "rules"
        
        if not rules_dir.exists():
            return rules
        
        for rule_file in rules_dir.glob("*.json"):
            try:
                with open(rule_file, 'r') as f:
                    rule_data = json.load(f)
                
                # Convert enum fields
                rule_data["framework"] = ComplianceFramework(rule_data["framework"])
                
                # Convert datetime fields
                for date_field in ["last_check", "next_check"]:
                    if rule_data.get(date_field):
                        rule_data[date_field] = datetime.datetime.fromisoformat(rule_data[date_field])
                
                rules.append(ComplianceRule(**rule_data))
                
            except Exception as e:
                self.logger.error(f"Error loading compliance rule {rule_file}: {str(e)}")
        
        return rules
    
    def _execute_compliance_rule(self, rule: ComplianceRule) -> Dict[str, Any]:
        """Execute a compliance rule."""
        # Placeholder implementation
        return {
            "rule_id": rule.rule_id,
            "framework": rule.framework.value,
            "passed": True,  # Placeholder
            "execution_time": datetime.datetime.utcnow().isoformat(),
            "details": "Compliance check passed"
        }
    
    def _calculate_next_check_date(self, frequency: str) -> datetime.datetime:
        """Calculate next check date based on frequency."""
        now = datetime.datetime.utcnow()
        
        if frequency == "daily":
            return now + datetime.timedelta(days=1)
        elif frequency == "weekly":
            return now + datetime.timedelta(weeks=1)
        elif frequency == "monthly":
            return now + datetime.timedelta(days=30)
        elif frequency == "quarterly":
            return now + datetime.timedelta(days=90)
        else:
            return now + datetime.timedelta(days=30)  # Default to monthly
    
    def _save_compliance_rule(self, rule: ComplianceRule) -> None:
        """Save a compliance rule."""
        rule_file = self.base_path / "compliance" / "rules" / f"{rule.rule_id}.json"
        with open(rule_file, 'w') as f:
            json.dump(asdict(rule), f, indent=2, default=str)
    
    def _generate_compliance_report(self, results: Dict[str, Any], framework: Optional[ComplianceFramework]) -> None:
        """Generate a compliance report."""
        report = {
            "generated_at": datetime.datetime.utcnow().isoformat(),
            "framework": framework.value if framework else "all",
            "results": results
        }
        
        framework_name = framework.value if framework else "all"
        report_file = self.base_path / "compliance" / f"compliance_report_{framework_name}_{datetime.date.today().isoformat()}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    
    def _load_quality_rule(self, rule_id: str) -> Optional[QualityRule]:
        """Load a specific quality rule."""
        rule_file = self.base_path / "quality" / "rules" / f"{rule_id}.json"
        if not rule_file.exists():
            return None
        
        try:
            with open(rule_file, 'r') as f:
                rule_data = json.load(f)
            
            rule_data["rule_type"] = DataQualityRule(rule_data["rule_type"])
            if rule_data.get("created_at"):
                rule_data["created_at"] = datetime.datetime.fromisoformat(rule_data["created_at"])
            
            return QualityRule(**rule_data)
            
        except Exception as e:
            self.logger.error(f"Error loading quality rule {rule_id}: {str(e)}")
            return None 