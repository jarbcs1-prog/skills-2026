from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

LANGUAGE_EXTENSIONS: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
}

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
SEVERITY_PENALTY = {"CRITICAL": 10, "HIGH": 5, "MEDIUM": 3, "LOW": 1}
SARIF_LEVEL = {"CRITICAL": "error", "HIGH": "error", "MEDIUM": "warning", "LOW": "note"}


@dataclass(frozen=True)
class Rule:
    id: str
    category: str
    severity: str
    message: str
    fix: str
    pattern: str
    languages: list[str] = field(default_factory=list)


def _r(
    rule_id: str,
    category: str,
    severity: str,
    message: str,
    fix: str,
    pattern: str,
    languages: list[str] | None = None,
) -> Rule:
    return Rule(
        id=rule_id,
        category=category,
        severity=severity,
        message=message,
        fix=fix,
        pattern=pattern,
        languages=languages or [],
    )


RULES: list[Rule] = [
    # --- Security ---
    _r(
        "security-sql-injection",
        "security",
        "CRITICAL",
        "SQL query constructed with string concatenation or f-strings",
        "Use parameterized queries / prepared statements",
        r"f[\"'](SELECT|INSERT|UPDATE|DELETE)[^\"']*\{|[\"'](SELECT|INSERT|UPDATE|DELETE)[^\"']*[\"']\s*\+",
        ["python", "javascript", "typescript", "go", "java"],
    ),
    _r(
        "security-sql-injection-raw",
        "security",
        "CRITICAL",
        "Raw SQL execution without parameterization",
        "Use ORM or parameterized queries",
        r"\.(raw|execute|query)\(\s*[\"'](?!.*\?)",
    ),
    _r(
        "security-xss-inner-html",
        "security",
        "CRITICAL",
        "User input written into DOM via innerHTML",
        "Use textContent or sanitize HTML first (DOMPurify)",
        r"\.innerHTML\s*=\s*(\w+|`|\$)",
        ["javascript", "typescript"],
    ),
    _r(
        "security-xss-dangerously-set",
        "security",
        "CRITICAL",
        "dangerouslySetInnerHTML used without sanitization",
        "Sanitize HTML with DOMPurify before inserting",
        r"dangerouslySetInnerHTML",
        ["javascript", "typescript"],
    ),
    _r(
        "security-hardcoded-secret",
        "security",
        "CRITICAL",
        "Hardcoded secret or API key",
        "Store secrets in environment variables or a secret manager",
        r"(password|passwd|secret|api_?key|token|access_?key)\s*[=:]\s*[\"'][^\"']{6,}[\"']",
    ),
    _r(
        "security-aws-key",
        "security",
        "CRITICAL",
        "AWS access key literal detected",
        "Rotate the key and move it to a secrets manager",
        r"AKIA[0-9A-Z]{16}",
    ),
    _r(
        "security-private-key",
        "security",
        "CRITICAL",
        "Private key material in source",
        "Remove key material; reference an external key file",
        r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
    ),
    _r(
        "security-weak-crypto",
        "security",
        "HIGH",
        "Use of weak or deprecated hashing algorithm",
        "Use a strong hash (SHA-256/argon2/bcrypt)",
        r"\b(md5|sha1|sha-1)\s*\(",
    ),
    _r(
        "security-command-injection",
        "security",
        "CRITICAL",
        "Shell command built from string concatenation",
        "Use subprocess with argument lists; validate input",
        r"(os\.system|subprocess\.(run|Popen|call))\s*\(\s*f[\"']|(os\.system|exec|system)\s*\(\s*[\"'].*\+",
        ["python", "javascript", "typescript", "go", "java"],
    ),
    _r(
        "security-csrf",
        "security",
        "HIGH",
        "State-changing request without CSRF protection",
        "Validate CSRF tokens on POST/PUT/DELETE routes",
        r"(@app\.(post|put|delete)|router\.(post|put|delete))\s*\(",
        ["python", "javascript", "typescript"],
    ),
    _r(
        "security-auth-bypass",
        "security",
        "CRITICAL",
        "Endpoint appears to skip authentication",
        "Add authentication/authorization guard",
        r"(@app\.route\s*\([^)]*\)|app\.get\s*\([^)]*\))\s*(def\s+\w+)?[\s\S]{0,120}?(no_auth|skip_auth|allow_anonymous)",
    ),
    _r(
        "security-path-traversal",
        "security",
        "HIGH",
        "User-controlled path passed to file access",
        "Resolve and validate paths within an allowed root",
        r"(open|read_text|write_text|join)\s*\([^)]*(user|request|params|input|filename|path)",
        ["python", "javascript", "typescript", "go", "java"],
    ),
    _r(
        "security-xxe",
        "security",
        "HIGH",
        "XML parser without external entity protection",
        "Disable DTD/external entities in the XML parser",
        r"(fromstring|parse)\s*\([^)]*(xml|request\.body|body)",
        ["python", "javascript", "typescript"],
    ),
    _r(
        "security-ssrf",
        "security",
        "HIGH",
        "Server-side request to user-controlled URL",
        "Validate and allowlist destination URLs",
        r"(urlopen|requests\.(get|post|put)|http\.(get|post))\s*\([^)]*(url|href|target|redirect)",
    ),
    _r(
        "security-deserialization",
        "security",
        "CRITICAL",
        "Untrusted input deserialized unsafely",
        "Avoid pickle on untrusted data; use JSON + validation",
        r"(pickle\.loads?|yaml\.load\s*\([^)]*)(?!.*SafeLoader)",
        ["python"],
    ),
    # --- Performance ---
    _r(
        "performance-n-plus-one",
        "performance",
        "HIGH",
        "Query executed inside a loop (potential N+1)",
        "Eager load related data (select_related, include) or batch queries",
        r"for\s+\w+\s+in\s+\w+[\s\S]{0,200}?(\.all\(\)|\.find(All|One)\(|\.query\s*\(|select\s*\(|db\.)",
        ["python", "javascript", "typescript"],
    ),
    _r(
        "performance-missing-index",
        "performance",
        "HIGH",
        "Filtered or ordered column may need a database index",
        "Add an index on the filtered/ordered column",
        r"(WHERE|ORDER BY|where|order by)\s+\w+\s*(=|IN|in)",
    ),
    _r(
        "performance-select-star",
        "performance",
        "MEDIUM",
        "SELECT * fetches unnecessary columns",
        "List only the columns actually needed",
        r"(SELECT|select)\s+\*",
    ),
    _r(
        "performance-sync-io-in-loop",
        "performance",
        "HIGH",
        "Synchronous I/O inside a loop",
        "Batch I/O or use async/concurrent operations",
        r"for\s+\w+\s+in\s+\w+[\s\S]{0,200}?(read\(|write\(|send\(|\.get\()",
    ),
    _r(
        "performance-string-concat-loop",
        "performance",
        "HIGH",
        "String concatenation inside a loop",
        "Collect parts in a list and join once",
        r"for\s+\w+\s+in\s+\w+[\s\S]{0,120}?\+\s*[\"']|for\s+\w+\s+in\s+\w+[\s\S]{0,120}?\+=?.*[\"']",
        ["python", "javascript", "typescript"],
    ),
    _r(
        "performance-unbounded-query",
        "performance",
        "HIGH",
        "Query without a limit may return unbounded rows",
        "Add pagination or a LIMIT clause",
        r"\.all\(\)|findAll\s*\(\s*\)|SELECT [^;]+(?!LIMIT)",
        ["python", "javascript", "typescript"],
    ),
    _r(
        "performance-memory-leak",
        "performance",
        "MEDIUM",
        "Globally growing data structure (potential memory leak)",
        "Bound the structure size or clear it periodically",
        r"(cache|history|items|queue)\s*\.append\([^)]*\)\s*(?:\n\s*){1,3}(?!.*(pop|del|remove))",
    ),
    _r(
        "performance-bundle-size",
        "performance",
        "HIGH",
        "Heavy import that inflates bundle size",
        "Import only what is needed or use a lighter library",
        r"from\s+['\"](lodash|moment|rxjs|d3)['\"]",
        ["javascript", "typescript"],
    ),
    # --- Correctness ---
    _r(
        "correctness-bare-except",
        "correctness",
        "HIGH",
        "Bare except clause catches everything",
        "Catch specific exceptions and handle them explicitly",
        r"except\s*:",
        ["python"],
    ),
    _r(
        "correctness-silent-pass",
        "correctness",
        "HIGH",
        "Exception swallowed silently",
        "Log or re-raise with context instead of pass",
        r"except\s*\w*[^:]*:[\s\S]{0,60}?pass\b",
        ["python"],
    ),
    _r(
        "correctness-mutable-default",
        "correctness",
        "HIGH",
        "Mutable object used as default argument",
        "Use None and initialize inside the function",
        r"def\s+\w+\([^)]*=[\[\]{}]",
        ["python"],
    ),
    _r(
        "correctness-race-condition",
        "correctness",
        "HIGH",
        "Concurrent access to shared state without locking",
        "Guard shared state with a lock or use atomic operations",
        r"(threading\.Lock|async def)[\s\S]{0,150}?(shared|counter|_state)",
    ),
    _r(
        "correctness-unhandled-error",
        "correctness",
        "MEDIUM",
        "Return value error path not handled",
        "Check the error/return value explicitly",
        r"\.get\([^)]*\)\s*(?!.*is\s+None)",
    ),
    _r(
        "correctness-invalid-comparison",
        "correctness",
        "MEDIUM",
        "Comparison against a mutable result (possible bug)",
        "Compare values or identity explicitly",
        r"==\s*\[\]|\w+\s*==\s*None\s*(?!\s|$)",
    ),
    _r(
        "correctness-except-generic",
        "correctness",
        "MEDIUM",
        "Overly generic exception handler without handling",
        "Catch the specific exception types",
        r"except\s+Exception\s*:(?!\s*(raise|logger\.|log\.))",
        ["python"],
    ),
    # --- Maintainability ---
    _r(
        "maintainability-short-names",
        "maintainability",
        "MEDIUM",
        "Single-letter or cryptic variable name",
        "Use descriptive, intention-revealing names",
        r"\b[a-z]\s*=\s*[^\n=]+\b|def\s+\w*[x-z]?\w*\s*\(\s*(x|y|z|tmp)\b",
        ["python", "javascript", "typescript", "go", "java", "rust"],
    ),
    _r(
        "maintainability-type-hints",
        "maintainability",
        "MEDIUM",
        "Function parameter or return without type annotation",
        "Add type annotations to parameters and returns",
        r"def\s+\w+\((?![^)]*:)[^)]*\)(?!\s*->)",
        ["python"],
    ),
    _r(
        "maintainability-deep-nesting",
        "maintainability",
        "MEDIUM",
        "Deeply nested control flow",
        "Extract branches into functions or use early returns",
        r"^\s{16,}(if|for|while)\b",
    ),
    _r(
        "maintainability-magic-number",
        "maintainability",
        "LOW",
        "Magic number without explanation",
        "Extract to a named constant",
        r"=\s*-?\d{3,}\b|:\s*-?\d{3,}\b",
    ),
    _r(
        "maintainability-global-mutable",
        "maintainability",
        "MEDIUM",
        "Module-level mutable state",
        "Encapsulate state in a class or function scope",
        r"^\w+\s*=\s*(\[|\{|set\()",
    ),
    _r(
        "maintainability-unused-import",
        "maintainability",
        "LOW",
        "Import that may be unused",
        "Remove unused imports",
        r"^import\s+\w+\s*$",
    ),
    # --- Testing ---
    _r(
        "testing-assert-missing",
        "testing",
        "HIGH",
        "Test function with no assertion",
        "Add assertions to verify expected behavior",
        r"def\s+test_\w+\([^)]*\):[\s\S]{0,300}?(?!assert)",
        ["python"],
    ),
    _r(
        "testing-print-instead-log",
        "testing",
        "LOW",
        "print() used instead of logging",
        "Use a structured logger",
        r"\bprint\s*\(",
    ),
    # --- Security (additional) ---
    _r(
        "security-no-rate-limit",
        "security",
        "MEDIUM",
        "Endpoint lacks rate limiting",
        "Add rate limiting middleware (e.g. Flask-Limiter, express-rate-limit)",
        r"(@app\.route|app\.(get|post|put|delete|patch)\s*\()",
        ["python", "javascript", "typescript"],
    ),
    _r(
        "security-cors-wildcard",
        "security",
        "HIGH",
        "CORS allows all origins (wildcard)",
        "Restrict CORS to specific trusted origins",
        r"(cors\(|Access-Control-Allow-Origin|origin: *['\"]\*)",
        ["javascript", "typescript", "go", "python"],
    ),
    _r(
        "security-redirect-https",
        "security",
        "MEDIUM",
        "Non-HTTPS redirect target",
        "Ensure redirects target the HTTPS version of the URL",
        r"(redirect\s*\(|res\.redirect\s*\()['\"]http://",
        ["javascript", "typescript", "python"],
    ),
    # --- Performance (additional) ---
    _r(
        "performance-blocking-sync-read",
        "performance",
        "MEDIUM",
        "Synchronous file read in request handler",
        "Use async file I/O or a thread pool",
        r"(readFileSync|fs\.readFileSync|open\s*\(\s*[\"']r)",
        ["javascript", "typescript", "go", "rust"],
    ),
    _r(
        "performance-missing-compression",
        "performance",
        "LOW",
        "Response may not be compressed (Gzip/Brotli)",
        "Enable compression middleware (express-static-gzip, flask-compress)",
        r"app\.use\s*\(\s*express\.static",
        ["javascript", "typescript"],
    ),
    _r(
        "performance-no-connection-pool",
        "performance",
        "MEDIUM",
        "Database connection created per request",
        "Use a connection pool",
        r"(new\s+Connection|mysql\.createConnection|pg\.connect)\s*\(",
        ["javascript", "typescript"],
    ),
    # --- Correctness (additional) ---
    _r(
        "correctness-empty-catch",
        "correctness",
        "MEDIUM",
        "Empty catch block swallows errors",
        "Log or re-raise the exception with context",
        r"except\s*\w*[:\s]*:\s*\n\s*pass\s*\n",
        ["python"],
    ),
    _r(
        "correctness-unwrap-optional",
        "correctness",
        "HIGH",
        "Calling method on potentially None value",
        "Check for None before accessing attributes/methods",
        r"\.unwrap\(\)\s*\.|\.item\(\)\s*(?!.*None)",
        ["rust", "python"],
    ),
    _r(
        "correctness-await-missing",
        "correctness",
        "HIGH",
        "Async function called without await",
        "Add 'await' to the async call",
        r"(fetch\s*\(|axios\.(get|post|put|delete)\s*\(|requests\.(async_get|async_post))\s*[^;]*$",
        ["javascript", "typescript"],
    ),
    _r(
        "correctness-null-deref",
        "correctness",
        "HIGH",
        "Unsafe null dereference (Go nil map access)",
        "Initialize maps before writing; check for nil before reading",
        r"\w+\[[^\]]+\]\s*=.*(nil|None)\s*:",
        ["go", "python", "rust"],
    ),
    # --- Maintainability (additional) ---
    _r(
        "maintainability-long-function",
        "maintainability",
        "MEDIUM",
        "Function is unusually long (>100 lines)",
        "Split into smaller, single-purpose functions",
        r"def\s+\w+\([^)]*\):[\s\S]{0,500}# .*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n",
        ["python"],
    ),
    _r(
        "maintainability-todo-in-prod",
        "maintainability",
        "LOW",
        "TODO/FIXME comment in production code",
        "Resolve or move to issue tracker",
        r"\b(TODO|FIXME|HACK|XXX)\b",
    ),
    # --- Testing (additional) ---
    _r(
        "testing-no-mock",
        "testing",
        "LOW",
        "Test function without mocking external calls",
        "Mock database/HTTP calls with unittest.mock or sinon",
        r"def\s+test_\w+\([^)]*\):[\s\S]{0,200}(requests\.(get|post)|fetch\(|http\.)",
        ["python", "javascript", "typescript"],
    ),
    _r(
        "testing-no-edge-cases",
        "testing",
        "MEDIUM",
        "Test function lacks edge case testing",
        "Add tests for boundary values and edge cases",
        r"def\s+test_\w+\([^)]*\):[\s\S]{0,300}(?:\n\s*pass\b)",
        ["python"],
    ),
]

RULES_BY_ID: dict[str, Rule] = {r.id: r for r in RULES}


def rules_for_category(category: str) -> list[Rule]:
    return [r for r in RULES if r.category == category]


def rules_for_language(language: str) -> list[Rule]:
    return [r for r in RULES if not r.languages or language in r.languages]


def infer_language(path: str) -> str:
    return LANGUAGE_EXTENSIONS.get(Path(path).suffix.lower(), "unknown")


def scan_text(text: str, language: str, rules: list[Rule] | None = None) -> list[dict]:
    applicable = rules_for_language(language) if rules is None else rules
    findings: list[dict] = []
    for rule in applicable:
        if not rule.languages or language in rule.languages:
            match = re.search(rule.pattern, text, re.IGNORECASE)
            if match:
                line = text[: match.start()].count("\n") + 1
                findings.append(
                    {
                        "rule_id": rule.id,
                        "rule_category": rule.category,
                        "severity": rule.severity,
                        "message": rule.message,
                        "fix": rule.fix,
                        "line": line,
                    }
                )
    return findings


def scan_file(path: Path, rules: list[Rule] | None = None) -> list[dict]:
    language = infer_language(str(path))
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    findings = scan_text(text, language, rules)
    for finding in findings:
        finding["file"] = str(path)
        finding["language"] = language
    return findings


def _expand_paths(patterns: list[str], cwd: Path | None = None) -> list[Path]:
    base = cwd or Path.cwd()
    files: list[Path] = []
    for pattern in patterns:
        if any(ch in pattern for ch in "*?["):
            files.extend(p for p in base.glob(pattern) if p.is_file())
        else:
            candidate = Path(pattern)
            if not candidate.is_absolute():
                candidate = base / candidate
            if candidate.is_file():
                files.append(candidate)
    seen: set[str] = set()
    unique: list[Path] = []
    for f in files:
        key = str(f.resolve())
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def summarize(findings: list[dict]) -> dict:
    by_severity: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for finding in findings:
        severity = finding.get("severity", "LOW")
        category = finding.get("rule_category", "other")
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1
    score = 100
    for finding in findings:
        score -= SEVERITY_PENALTY.get(finding.get("severity", "LOW"), 1)
    return {
        "total_findings": len(findings),
        "by_severity": by_severity,
        "by_category": by_category,
        "score": max(0, score),
    }


def review_files(paths: list[str], cwd: Path | None = None, rules: list[Rule] | None = None) -> dict:
    files = _expand_paths(paths, cwd)
    findings: list[dict] = []
    scanned: list[str] = []
    for path in files:
        scanned.append(str(path))
        findings.extend(scan_file(path, rules))
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.get("severity", "LOW"), 9), f.get("file", ""), f.get("line", 0)))
    return {
        "findings": findings,
        "files_scanned": scanned,
        "summary": summarize(findings),
    }


def to_sarif(findings: list[dict]) -> dict:
    rules_seen: dict[str, dict] = {}
    results: list[dict] = []
    for finding in findings:
        rule_id = finding.get("rule_id", "unknown")
        if rule_id not in rules_seen:
            rules_seen[rule_id] = {
                "id": rule_id,
                "name": rule_id,
                "shortDescription": {"text": finding.get("message", "")},
                "help": {"text": finding.get("fix", "")},
                "properties": {"category": finding.get("rule_category", "other")},
            }
        results.append(
            {
                "ruleId": rule_id,
                "level": SARIF_LEVEL.get(finding.get("severity", "LOW"), "note"),
                "message": {"text": finding.get("message", "")},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": finding.get("file", "")},
                            "region": {"startLine": finding.get("line", 1)},
                        }
                    }
                ],
            }
        )
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "code-reviewer",
                        "informationUri": "https://skills_2026/code-reviewer",
                        "rules": list(rules_seen.values()),
                    }
                },
                "results": results,
            }
        ],
    }


def load_yaml_rules(path: Path) -> list[Rule]:
    if yaml is None:
        raise ImportError("PyYAML is required for YAML rules: pip install pyyaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw_rules = data.get("rules", [])
    rules: list[Rule] = []
    for raw in raw_rules:
        rules.append(
            Rule(
                id=str(raw["id"]),
                category=str(raw.get("category", "custom")),
                severity=str(raw.get("severity", "MEDIUM")).upper(),
                message=str(raw.get("message", "")),
                fix=str(raw.get("fix", "")),
                pattern=str(raw.get("pattern", "")),
                languages=[str(lang) for lang in raw.get("languages", [])],
            )
        )
    return rules


def rules_to_dict(rule: Rule) -> dict:
    return {
        "id": rule.id,
        "category": rule.category,
        "severity": rule.severity,
        "languages": rule.languages,
    }


def rules_payload(rules: list[Rule]) -> dict:
    return {"rules": [rules_to_dict(r) for r in rules]}
