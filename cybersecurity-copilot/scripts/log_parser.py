"""
Log parsing module for multiple formats with deterministic parsing.
Supports syslog, JSON, CEF, nginx, apache, windows event logs.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

class LogFormat(Enum):
    SYSLOG = "syslog"
    JSON = "json"
    CEF = "cef"
    NGINX = "nginx"
    APACHE = "apache"
    WINDOWS = "windows"
    UNKNOWN = "unknown"

class LogParser:
    """Parse logs from various formats into structured events."""
    
    # Combined log format regex (Common Log Format with optional fields)
    COMBINED_LOG_REGEX = re.compile(
        r'^(\S+) (\S+) (\S+) \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d{3}) (\S+)'
        r'(?: "([^"]*)" "([^"]*)")?$'
    )
    
    # Windows EventLog XML indicators
    WINDOWS_EVENT_START = re.compile(r'<Event xmlns=', re.IGNORECASE)
    WINDOWS_EVENTID = re.compile(r'<EventID>(\d+)</EventID>')
    WINDOWS_TIME_CREATED = re.compile(r'<TimeCreated SystemTime="([^"]+)"')
    WINDOWS_PROVIDER_NAME = re.compile(r'<Provider Name="([^"]+)"')
    WINDOWS_USERID = re.compile(r'<UserID>(\S+)</UserID>')
    WINDOWS_MESSAGE = re.compile(r'<Message>([\s\S]*?)</Message>', re.DOTALL)
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def detect_format(file_path: Union[str, Path]) -> LogFormat:
        """Detect log format from file content."""
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='replace')
            if not content.strip():
                return LogFormat.UNKNOWN
            
            # Take first 5 lines for detection
            lines = content.splitlines()[:5]
            first_line = lines[0].strip() if lines else ""
            sample = '\n'.join(lines)
            
            # JSON detection (JSON lines or JSON array)
            if first_line.startswith('{') or first_line.startswith('['):
                try:
                    json.loads(first_line if first_line.startswith('{') else lines[0])
                    return LogFormat.JSON
                except (json.JSONDecodeError, IndexError):
                    pass
            
            # CEF detection
            if sample.startswith('CEF:'):
                return LogFormat.CEF
            
            # Windows EventLog detection
            if LogParser.WINDOWS_EVENT_START.search(sample):
                return LogFormat.WINDOWS
            
            # Syslog detection (RFC 3164 or RFC 5424)
            if LogParser._looks_like_syslog(sample):
                return LogFormat.SYSLOG
            
            # Nginx/Apache combined log format
            if LogParser.COMBINED_LOG_REGEX.match(first_line):
                # Try to distinguish nginx vs apache by common patterns
                if 'nginx' in sample.lower():
                    return LogFormat.NGINX
                return LogFormat.APACHE  # Default to apache if unsure
            
            return LogFormat.UNKNOWN
        except (OSError, UnicodeDecodeError):
            return LogFormat.UNKNOWN
    
    @staticmethod
    def _looks_like_syslog(text: str) -> bool:
        """Check if text matches syslog patterns."""
        # RFC 3164: <pri>timestamp>hostname:app-name][[

[Note: This is a shortened version of the response due to length constraints.]