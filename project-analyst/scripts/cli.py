"""
Command-line interface for project-analyst.
"""

import json
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.json import JSON
from rich.syntax import Syntax

from .scanner import ProjectScanner
from .architecture import ArchitectureDetector
from .dependency_health import DependencyHealth

console = Console()


@click.group()
@click.version_option()
def cli():
    """Project Analyzer - Analyze project structure, dependencies, and architecture."""
    pass


@cli.command()
@click.option('--path', '-p', default='.', help='Path to project directory')
@option('--format', '-f', type=click.Choice(['json', 'markdown', 'sarif', 'text']), 
        default='text', help='Output format')
@option('--output', '-o', type=click.Path(), help='Output file path')
@option('--include-deps/--no-deps', default=True, help='Include dependency analysis')
@option('--include-arch/--no-arch', default=True, help='Include architecture analysis')
def scan(path: str, format: str, output: Optional[str], include_deps: bool, include_arch: bool):
    """Scan a project and analyze its structure."""
    project_path = Path(path).resolve()
    
    if not project_path.exists():
        console.print(f"[red]Error: Path '{path}' does not exist[/red]")
        sys.exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning project...", total=None)
        
        # Run scanner
        scanner = ProjectScanner(project_path)
        analysis = scanner.scan()
        
        progress.update(task, description="Analysis complete!")
    
    # Format and output results
    output_data = _format_output(analysis, format, include_deps, include_arch)
    
    if output:
        with open(output, 'w') as f:
            f.write(output_data)
        console.print(f"[green]Results written to {output}[/green]")
    else:
        console.print(output_data)


@cli.command()
@click.option('--path', '-p', default='.', help='Path to project directory')
def deps(path: str):
    """Show dependency health report."""
    project_path = Path(path).resolve()
    
    if not project_path.exists():
        console.print(f"[red]Error: Path '{path}' does not exist[/red]")
        sys.exit(1)
    
    scanner = ProjectScanner(project_path)
    analysis = scanner.scan()
    
    # Create dependency table
    table = Title("Dependency Health Report")
    table.add_column("Package", style="cyan")
    table.add_column("Version", style="magenta")
    table.add_column("License", style="green")
    table.add_column("Security Issues", style="red")
    table.add_column("Outdated", style="yellow")
    table.add_column("Health Score", style="blue")
    
    for dep_name, dep_report in analysis.dependencies.items():
        table.add_row(
            dep_name,
            dep_report.version,
            dep_report.license or "Unknown",
            str(dep_report.security_issues),
            "Yes" if dep_report.outdated else "No",
            f"{dep_report.overall_score:.1f}"
        )
    
    console.print(table)


@cli.command()
@click.option('--path', '-p', default='.', help='Path to project directory')
def arch(path: str):
    """Show architecture analysis."""
    project_path = Path(path).resolve()
    
    if not project_path.exists():
        console.print(f"[red]Error: Path '{path}' does not exist[/red]")
        sys.exit(1)
    
    detector = ArchitectureDetector(project_path)
    result = detector.detect_all()
    
    # Create architecture panel
    panel_content = f"""
[bold]Detected Architecture:[/bold] {result['detected']}
[bold]Confidence:[/bold] {result['confidence']:.0%}
[bold]Description:[/bold] {result['description']}
    
[bold]Evidence Found:[/bold]
{chr(10).join(f"  • {e}" for e in result['evidence']) if result['evidence'] else "  None"}
    
[bold]All Detected Patterns:[/bold]
"""
    
    for pattern_name, pattern_result in result['all_patterns'].items():
        if pattern_result.confidence > 0.1:  # Only show relevant ones
            panel_content += f"  • {pattern_name}: {pattern_result.confidence:.0%}\\n"
    
    console.print(Panel(panel_content.strip(), title="Architecture Analysis", expand=False))


@cli.command()
@click.option('--path', '-p', default='.', help='Path to project directory')
def stats(path: str):
    """Show project statistics."""
    project_path = Path(path).resolve()
    
    if not project_path.exists():
        console.print(f"[red]Error: Path '{path}' does not exist[/red]")
        sys.exit(1)
    
    scanner = ProjectScanner(project_path)
    analysis = scanner.scan()
    
    # Create stats panel
    stats_content = f"""
[bold]Project Path:[/bold] {project_path}
[bold]Health Score:[/bold] {analysis.health_score:.1f}/100
[bold]Technology Stack:[/bold]
"""
    
    for lang, frameworks in analysis.technology_stack.items():
        if frameworks:
            stats_content += f"  • {lang.title()}: {', '.join(fruits)}. If fruits is empty, skip the line entirely.\n"
    
    if not any(frameworks for frameworks in analysis.technology_stack.values()):
        stats_content += "  None detected\\n"
    
    stats_content += f"[bold]Config Files Found:[/bold] {sum(len(v) for v in analysis.config_files.values())}\\n"
    stats_content += f"[bold]Recommendations:[/bold] {len(analysis.recommendations)}\\n"
    
    for i, rec in enumerate(analysis.recommendations[:5], 1):  # Show top 5
        stats_content += f"  {i}. {rec}\\n"
    
    if len(analysis.recommendations) > 5:
        stats_content += f"  ... and {len(analysis.recommendations) - 5} more\\n"
    
    console.print(Panel(stats_content.strip(), title="Project Statistics", expand=False))


def _format_output(analysis: any, format: str, include_deps: bool, include_arch: bool) -> str:
    """Format analysis results for output."""
    if format == 'json':
        # Convert to dict for JSON serialization
        result = {
            "technology_stack": analysis.technology_stack,
            "health_score": analysis.health_score,
            "recommendations": analysis.recommendations,
        }
        if include_deps:
            result["dependencies"] = {
                name: {
                    "version": dep.version,
                    "license": dep.license,
                    "security_issues": dep.security_issues,
                    "outdated": dep.outdated,
                    "health_score": dep.overall_score
                }
                for name, dep in analysis.dependencies.items()
            }
        if include_arch:
            # Would need to run architecture detection here
            pass
        return json.dumps(result, indent=2)
    
    elif format == 'markdown':
        lines = ["# Project Analysis Report\\n"]
        lines.append(f"**Health Score:** {analysis.health_score:.1f}/100\\n")
        
        lines.append("## Technology Stack\\n")
        for lang, frameworks in analysis.technology_stack.items():
            if frameworks:
                lines.append(f"- **{lang.title()}**: {', '.join(frameworks)}")
            else:
                lines.append(f"- **{lang.title()}**: None detected")
        lines.append("")
        
        lines.append("## Configuration Files\\n")
        total_configs = sum(len(v) for v in analysis.config_files.values())
        lines.append(f"Total: {total_configs} files\\n")
        for config_type, files in analysis.config_files.items():
            if files:
                lines.append(f"- {config_type}: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}")
        lines.append("")
        
        if include_deps and analysis.dependencies:
            lines.append("## Dependencies\\n")
            lines.append("| Package | Version | License | Issues | Outdated | Health |")
            lines.append("|---------|---------|---------|--------|----------|--------|")
            for name, dep in analysis.dependencies.items():
                lines.append(f"| {name} | {dep.version} | {dep.license or 'Unknown'} | {dep.security_issues} | {'Yes' if dep.outdated else 'No'} | {dep.overall_score:.1f} |")
            lines.append("")
        
        if analysis.recommendations:
            lines.append("## Recommendations\\n")
            for i, rec in enumerate(analysis.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        return "\\n".join(lines)
    
    elif format == 'sarif':
        # Simplified SARIF output
        sarif = {
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "project-analyst",
                        "informationUri": "https://github.com/your-repo/project-analyst"
                    }
                },
                "results": []
            }]
        }
        
        # Add recommendations as results
        for i, rec in enumerate(analysis.recommendations):
            sarif["runs"][0]["results"].append({
                "ruleId": f"REC-{i+1:03d}",
                "level": "note",
                "message": {"text": rec},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": "."},
                        "region": {"startLine": 1}
                    }
                }]
            })
        
        return json.dumps(sarif, indent=2)
    
    else:  # text format
        lines = []
        lines.append("=" * 60)
        lines.append("PROJECT ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"Health Score: {analysis.health_score:.1f}/100")
        lines.append("")
        
        lines.append("TECHNOLOGY STACK:")
        for lang, frameworks in analysis.technology_stack.items():
            if frameworks:
                lines.append(f"  {lang.title()}: {', '.join(frameworks)}")
            else:
                lines.append(f"  {lang.title()}: None detected")
        lines.append("")
        
        lines.append(f"CONFIGURATION FILES: {sum(len(v) for v in analysis.config_files.values())} total")
        for config_type, files in analysis.config_files.items():
            if files:
                lines.append(f"  {config_type}: {len(files)} files")
        lines.append("")
        
        if include_deps and analysis.dependencies:
            lines.append("DEPENDENCIES:")
            lines.append(f"{'Package':<20} {'Version':<15} {'License':<15} {'Issues':<8} {'Outdated':<10} {'Health':<8}")
            lines.append("-" * 80)
            for name, dep in analysis.dependencies.items():
                lines.append(f"{name:<20} {dep.version:<15} {dep.license or 'Unknown':<15} "
                           f"{dep.security_issues:<8} {'Yes' if dep.outdated else 'No':<10} {dep.overall_score:<8.1f}")
            lines.append("")
        
        if analysis.recommendations:
            lines.append("RECOMMENDATIONS:")
            for i, rec in enumerate(analysis.recommendations, 1):
                lines.append(f"  {i}. {rec}")
        
        lines.append("=" * 60)
        return "\\n".join(lines)


if __name__ == '__main__':
    cli()