from __future__ import annotations

import re
import shutil

PROFILER_TOOLS: dict[str, list[str]] = {
    "python": ["py-spy", "cProfile", "scalene", "memray"],
    "javascript": ["node --inspect", "0x", "clinic.js"],
    "rust": ["perf", "flamegraph", "cargo-profiler"],
    "go": ["pprof", "go tool trace"],
    "java": ["async-profiler", "JFR", "VisualVM"],
}

_LOOP_RE = re.compile(r"\b(for|while)\b")

_FUNCTION_PATTERNS: dict[str, re.Pattern] = {
    "python": re.compile(r"^\s*(?:async\s+def|def)\s+(\w+)"),
    "javascript": re.compile(r"^\s*(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()"),
    "rust": re.compile(r"^\s*(?:pub\s+)?fn\s+(\w+)"),
    "go": re.compile(r"^\s*func\s+(?:\(\w+\s+\*\w+\)\s*)?(\w+)\s*\("),
    "java": re.compile(r"^\s*(?:public|private|protected|static|final|synchronized|native|abstract)\s+.*\s(\w+)\s*\("),
}


def _indent_width(line: str) -> int:
    expanded = line.expandtabs(4)
    return len(expanded) - len(expanded.lstrip())


class Profiler:
    @classmethod
    def detect(cls, language: str) -> list[dict]:
        tools = PROFILER_TOOLS.get(language, [])
        result: list[dict] = []
        for tool in tools:
            binary = tool.split()[0]
            result.append({"tool": tool, "available": shutil.which(binary) is not None})
        return result

    @classmethod
    def analyze_hotspots(cls, source_text: str, language: str) -> dict:
        lines = source_text.splitlines()
        loop_lines = [line for line in lines if _LOOP_RE.search(line)]
        loop_depth = 0
        for line in loop_lines:
            loop_depth = max(loop_depth, _indent_width(line) // 4 + 1)

        fn_re = _FUNCTION_PATTERNS.get(language, _FUNCTION_PATTERNS["python"])
        functions: list[tuple[str, int, int]] = []
        for index, line in enumerate(lines):
            match = fn_re.match(line)
            if match:
                name = match.group(1) or match.group(2) or "anonymous"
                functions.append((name, index, _indent_width(line)))

        function_sizes: list[tuple[str, int]] = []
        for position, (name, start, indent) in enumerate(functions):
            end = len(lines)
            for next_position in range(position + 1, len(functions)):
                if functions[next_position][2] <= indent:
                    end = functions[next_position][1]
                    break
            function_sizes.append((name, end - start))

        hotspot_count = len(loop_lines)
        large_functions = [(name, size) for name, size in function_sizes if size > 50]

        recommendations: list[str] = []
        if loop_depth >= 2:
            recommendations.append(f"Nested loop depth {loop_depth} detected; consider flattening or early termination")
        if hotspot_count:
            recommendations.append("Found {hotspot_count} loops; hoist invariant computations and use vectorized operations".format(hotspot_count=hotspot_count))
        for name, size in large_functions:
            recommendations.append(f"Function {name} is {size} lines; consider splitting")
        if not recommendations:
            recommendations.append("No hotspots detected; code appears simple")

        depth_penalty = (loop_depth - 1) * 20 if loop_depth >= 2 else 0
        score = 100 - hotspot_count * 10 - depth_penalty - len(large_functions) * 15
        score = max(0, min(100, score))

        return {
            "hotspot_count": hotspot_count,
            "functions_analyzed": len(function_sizes),
            "recommendations": recommendations,
            "score": score,
        }
