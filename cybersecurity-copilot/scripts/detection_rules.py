"""
Detection rules engine for cybersecurity-copilot.
Supports YAML-like rule definitions and regex-based pattern matching.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, Union

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFO: 4,
}

@dataclass(frozen=True)
class DetectionRule:
    """A detection rule for matching patterns in log events."""
    id: str
    name: str
    category: str
    mitre_technique: str
    severity: Severity
    description: str
    pattern: str
    field: Optional[str] = None  # If None, match against concatenated raw text
    tags: List[str] = field(default_factory=list)
    # Optional logic function for complex multi-event rules
    logic: Optional[Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]]] = None

    def compiled_pattern(self) -> Optional[Pattern[str]]:
        """Compile the regex pattern if valid."""
        try:
            return re.compile(self.pattern, re.IGNORECASE) if self.pattern else None
        except re.error:
            return None

# Predefined detection rules
RULES: List[DetectionRule] = [
    # Credential Access
    DetectionRule(
        id="suspicious-login",
        name="Suspicious Login Pattern",
        category="credential_access",
        mitre_technique="T1110",
        severity=Severity.HIGH,
        description="Multiple failed logins followed by success from same IP",
        pattern="",  # Handled via custom logic
        field="source_ip",
        tags=["brute_force", "credential_stuffing"],
        lambda events: _detect_suspicious_login(events)
    ),
    DetectionRule(
        id="hardcoded-credential",
        name="Hardcoded Credential in Log",
        category="credential_access",
        mitre_technique="T1078.004",
        severity=Severity.HIGH,
        description="Possible hardcoded credentials found in logs",
        pattern=r"(?i)(password|passwd|secret|api_?key|token|auth_token)\s*[:=]\s*['\"]?[\w@#$%^&*()!]+['\"]?",
        field=None,
        tags=["credential-exposure"]
    ),
    
    # Initial Access
    DetectionRule(
        id="sql-injection-attempt",
        name="SQL Injection Attempt",
        category="initial_access",
        mitre_technique="T1190",
        severity=Severity.CRITICAL,
        description="Potential SQL injection attempt in request",
        pattern=r"(?i)(\bunion\b.*\bselect\b|\'\s*or\s*\'\d+\s*=\s*\d+|;\s*--|/\*.*\*/)",
        field=None,  # Will check URL, params, etc.
        tags=["injection", "sql"]
    ),
    DetectionRule(
        id="path-traversal",
        name="Path Traversal Attempt",
        category="initial_access",
        mitre_technique="T1087.002",
        severity=Severity.HIGH,
        description="Potential path traversal attempt detected",
        pattern=r"\.\.(/|\\|%2f%2e%2e|%2e%2e/|..%2f|%2e%2e%5c)",
        field=None,
        tags=["traversal", "directory"]
    ),
    
    # Execution
    DetectionRule(
        id="encoded-powershell",
        name="Encoded PowerShell Command",
        category="execution",
        mitre_technique="T1059.001",
        severity=Severity.HIGH,
        description="Possible encoded PowerShell execution attempt",
        pattern=r"(?i)(-enc\s+[A-Za-z0-9+/]+=*|frombase64\s*\(|\$\([^)]*[Ee][Nn][Cc][Oo][Dd][Ee]\))",
        field=None,
        tags=["powershell", "obfuscation"]
    ),
    DetectionRule(
        id="curl-to-shell",
        name="curl/wget to Shell",
        category="execution",
        mitre_technique="T1059.004",
        severity=Severity.HIGH,
        description="Potential download and execution via curl/wget",
        pattern=r"(?i)(curl|wget|fetch)\s+[^\s]+\s*[\|>]\s*(sh|bash|zsh|dash)",
        field=None,
        tags=["download-execute"]
    ),
    
    # Persistence
    DetectionRule(
        id="scheduled-task-create",
        name="Scheduled Task Creation",
        category="persistence",
        mitre_technique="T1053.005",
        severity=Severity.MEDIUM,
        description="Creation of scheduled task (possible persistence)",
        pattern=r"(?i)(schtasks\s*/create|at\s+\d+:\d+)",
        field=None,
        tags=["persistence", "windows"]
    ),
    
    # Privilege Escalation
    DetectionRule(
        id="privilege-escalation-attempt",
        name="Possible Privilege Escalation",
        category="privilege_escalation",
        mitre_technique="T1068",
        severity=Severity.HIGH,
        description="Attempt to exploit privileges or access token",
        pattern=r"(?i)(seimpersonateprivilege|printspoofer|juicypotato|godpotato|rottenpotato)",
        field=None,
        tags=["privilege-escalation", "exploit"]
    ),
    
    # Defense Evasion
    DetectionRule(
        id="obfuscated-powershell",
        name="Obfuscated PowerShell",
        category="defense_evasion",
        mitre_technique="T1027",
        severity=Severity.MEDIUM,
        description="Possible obfuscated PowerShell command",
        pattern=r"(?i)(\$_[A-Za-z0-9]+|\$\([^)]*[Cc][Ll][Ii][Pp][Bb][Oo][AaRrDd]\)|\[Char\])",
        field=None,
        tags=["obfuscation", "powershell"]
    ),
    DetectionRule(
        id="disable-security-tools",
        name="Attempt to Disable Security Tools",
        category="defense_evasion",
        mitre_technique="T1089",
        severity=Severity.HIGH,
        description="Commands to stop or disable security software",
        pattern=r"(?i)(net\s+stop\s+(windefend|mcaffeeservice|sophos)|sc\s+stop\s+(av|antivirus))",
        field=None,
        tags=["defense-evasion"]
    ),
    
    # Discovery
    DetectionRule(
        id="port-scan-detected",
        name="Port Scan Activity",
        category="discovery",
        mitre_technique="T1046",
        severity=Severity.MEDIUM,
        description="Multiple connection attempts to different ports",
        pattern="",  # Handled via custom logic
        field=None,
        tags=["scan", "reconnaissance"],
        lambda events: _detect_port_scan(events)
    ),
    DetectionRule(
        id="whois-lookup",
        name="WHOIS/Nslookup Command",
        category="discovery",
        mitre_technique="T1082",
        severity=Severity.LOW,
        description="Possible reconnaissance via WHOIS or nslookup",
        pattern=r"(?i)(whois|nslookup|dig\s+[^\s]+)",
        field=None,
        tags=["reconnaissance"]
    ),
    
    # Lateral Movement
    DetectionRule(
        id="psexec-execution",
        name="PsExec Execution Detected",
        category="lateral_movement",
        mitre_technique="T1021.002",
        severity=Severity.HIGH,
        description="Possible PsExec usage for lateral movement",
        pattern=r"(?i)(psexec|\\\\.*\$admin|\$c\$)",
        field=None,
        tags=["lateral-movement", "windows"]
    ),
    
    # Collection
    DetectionRule(
        id="archive-collected-data",
        name="Archive Collected Data",
        category="collection",
        mitre_technique="T1560.001",
        severity=Severity.MEDIUM,
        description="Creation of archive files (possible data staging)",
        pattern=r"(?i)(zip\s+-r|tar\s+-czf|7z\s+a)",
        field=None,
        tags=["data-staging", "archive"]
    ),
    
    # Exfiltration
    DetectionRule(
        id="large-data-transfer",
        name="Large Data Transfer Detected",
        category="exfiltration",
        mitre_technique="T1041",
        severity=Severity.HIGH,
        description="Unusually large data transfer observed",
        pattern="",  # Handled via size thresholds in logic
        field=None,
        tags=["exfiltration", "large-transfer"],
        lambda events: _detect_large_transfer(events)
    ),
    
    # Impact
    DetectionRule(
        id="ransomware-note",
        name="Possible Ransomware Note",
        category="impact",
        mitre_technique="T1486",
        severity=Severity.CRITICAL,
        description="Possible ransomware note or encryption notification",
        pattern=r"(?i)(your files have been encrypted|decrypt your files|send bitcoin to|ransom note)",
        field=None,
        tags=["ransomware", "extortion"]
    ),
]

def _detect_suspicious_login(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect multiple failed logins followed by success from same IP."""
    findings = []
    # Group by source_ip
    ip_attempts: Dict[str, List[Dict[str, Any]]] = {}
    
    for idx, event in enumerate(events):
        ip = event.get("source_ip") or event.get("src_ip") or event.get("client_ip")
        if not ip:
            continue
            
        if ip not in ip_attempts:
            ip_attempts[ip] = []
        ip_attempts[ip].append((idx, event))
    
    for ip, attempts in ip_attempts.items():
        # Sort by timestamp if available
        try:
            attempts.sort(key=lambda x: x[1].get("@timestamp", x[1].get("timestamp", "")))
        except:
            pass  # Keep original order if timestamp parsing fails
        
        failed_count = 0
        for event_idx, event in attempts:
            # Check if this is a failed login attempt
            msg = str(event.get("message", "")) + str(event.get("event", ""))
            if any(indicator in msg.lower() for indicator in 
                  ["failed", "failure", "invalid", "error 401", "access denied"]):
                failed_count += 1
                if failed_count >= 5:
                    # Look for subsequent success within reasonable time
                    for later_idx, later_event in attempts[event_idx+1:]:
                        later_msg = str(later_event.get("message", "")) + str(later_event.get("event", ""))
                        if any(indicator in later_msg.lower() for indicator in 
                              ["success", "accepted", "login successful", "authenticated"]):
                            findings.append({
                                "rule_id": "suspicious-login",
                                "event_index": later_idx,
                                "evidence": f"{failed_count} failed logins followed by success from IP {ip}",
                                "ip": ip,
                                "failed_count": failed_count
                            })
                            return findings  # Return first match per IP
            else:
                failed_count = 0  # Reset counter on non-failed event
    return findings

def _detect_port_scan(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect potential port scanning activity."""
    findings = []
    # Group by source IP
    ip_connections: Dict[str, Dict[int, List[Dict[str, Any]]]] = {}
    
    for idx, event in enumerate(events):
        ip = event.get("source_ip") or event.get("src_ip") or event.get("client_ip")
        port = event.get("destination_port") or event.get("dst_port") or event.get("port")
        if not ip or not isinstance(port, int):
            continue
            
        if ip not in ip_connections:
            ip_connections[ip] = {}
        if port not in ip_connections[ip]:
            ip_connections[ip][port] = []
        ip_connections[ip][port].append((idx, event))
    
    for ip, port_dict in ip_connections.items():
        unique_ports = len(port_dict)
        total_connections = sum(len(v) for v in port_dict.values())
        if unique_ports >= 10 and total_connections >= 15:  # Threshold for port scan
            findings.append({
                "rule_id": "port-scan-detected",
                "evidence": f"Scanned {unique_ports} ports from IP {ip} with {total_connections} connection attempts",
                "ip": ip,
                "ports_scanned": sorted(list(port_dict.keys()))[:10],  # First 10 ports
                "total_attempts": total_connections
            })
    return findings

def _detect_large_transfer(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect unusually large data transfers."""
    findings = []
    # Look for events with byte counts
    for idx, event in enumerate(events):
        bytes_sent = event.get("bytes_sent") or event.get("out_bytes") or event.get("bytes_out")
        bytes_recv = event.get("bytes_received") or event.get("in_bytes") or event.get("bytes_in")
        total_bytes = 0
        
        if bytes_sent is not None:
            try:
                total_bytes += int(bytes_sent)
            except (ValueError, TypeError):
                pass
        if bytes_recv is not None:
            try:
                total_bytes += int(bytes_received)
            except (ValueError, TypeError):
                pass
                
        if total_bytes > 100_000_000:  # 100MB threshold
            findings.append({
                "rule_id": "large-data-transfer",
                "event_index": idx,
                "evidence": f"Large data transfer detected: {total_bytes:,} bytes",
                "bytes": total_bytes
            })
    return findings

def detect_rules(events: List[Dict[str, Any]], 
                rules: Optional[List[DetectionRule]] = None) -> List[Dict[str, Any]]:
    """Apply detection rules to a list of log events."""
    if rules is None:
        rules = RULES
    
    findings: List[Dict[str, Any]] = []
    
    for rule in rules:
        if rule.logic is not None:
            # Handle complex logic rules
            logic_results = rule.logic(events)
            for result in logic_results:
                result["rule_id"] = result.get("rule_id", rule.id)
                result["rule_name"] = rule.name
                result["category"] = rule.category
                result["mitre_technique"] = rule.mitre_technique
                result["severity"] = rule.severity.value
                result["description"] = rule.description
                findings.append(result)
        else:
            # Handle regex-based rules
            pattern = rule.compiled_pattern()
            if pattern is None:
                continue  # Skip invalid regex
                
            for idx, event in enumerate(events):
                # Determine what text to search against
                if rule.field is None:
                    # Search in all string values concatenated
                    search_text = " ".join(
                        str(v) for v in event.values() 
                        if isinstance(v, str)
                    )
                else:
                    # Search in specific field
                    search_text = str(event.get(rule.field, ""))
                
                if pattern.search(search_text):
                    findings.append({
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "category": rule.category,
                        "mitre_technique": rule.mitre_technique,
                        "severity": rule.severity.value,
                        "description": rule.description,
                        "event_index": idx,
                        "event": event,
                        "matched_text": pattern.search(search_text).group(0)[:100]  # Truncate
                    })
    
    # Sort by severity (critical first) then by event index
    findings.sort(key=lambda x: (
        SEVERITY_ORDER.get(Severity(x["severity"]), 999),
        x.get("event_index", 0)
    ))
    return findings