"""Command-line interface for AbaqusGPT."""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="abaqusgpt",
    help="Your AI copilot for Abaqus: modeling, meshing, convergence debugging, and beyond.",
    add_completion=False,
)
console = Console()


@app.command()
def diagnose(
    file: Path = typer.Argument(..., help="Path to .msg or .sta file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
):
    """Diagnose convergence issues from Abaqus output files."""
    from .agents.converge_doctor import ConvergeDoctor
    
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    
    doctor = ConvergeDoctor()
    result = doctor.diagnose(file, verbose=verbose)
    console.print(result)


@app.command()
def generate(
    description: str = typer.Argument(..., help="Natural language description of the model"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("inp", "--format", "-f", help="Output format: inp or python"),
):
    """Generate Abaqus input file or Python script from description."""
    from .agents.inp_generator import InpGenerator
    
    generator = InpGenerator()
    result = generator.generate(description, format=format)
    
    if output:
        output.write_text(result)
        console.print(f"[green]✓[/green] Generated: {output}")
    else:
        console.print(Panel(result, title="Generated Code"))


@app.command("mesh-check")
def mesh_check(
    file: Path = typer.Argument(..., help="Path to .inp file"),
    report: Path = typer.Option(None, "--report", "-r", help="Save report to file"),
):
    """Analyze mesh quality and provide optimization suggestions."""
    from .agents.mesh_advisor import MeshAdvisor
    
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    
    advisor = MeshAdvisor()
    result = advisor.analyze(file)
    
    if report:
        report.write_text(result)
        console.print(f"[green]✓[/green] Report saved: {report}")
    else:
        console.print(result)


@app.command()
def ask(
    question: str = typer.Argument(..., help="Your question about Abaqus"),
):
    """Ask any question about Abaqus."""
    from .agents.qa_agent import QAAgent
    
    agent = QAAgent()
    result = agent.answer(question)
    console.print(Panel(result, title="AbaqusGPT"))


@app.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"AbaqusGPT v{__version__}")


if __name__ == "__main__":
    app()
