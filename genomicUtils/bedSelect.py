import re
import pandas as pd
import typer
from typing import Optional, List
from pathlib import Path
from genomicUtils import __version__
from genomicUtils.utils import version_callback

app = typer.Typer(help="Given an input BED file with multiple sequence coordinates, extract and output a subset of sequences based on regular expression patterns matching a list of sequence identifiers in user-specified columns to the BED file.",
                  rich_markup_mode="rich")

def parse_patterns(pattern: Optional[str], pattern_file: Optional[Path]):
    patterns = []
    if pattern:
        typer.echo(f"Pattern: {pattern}")
        patterns.append(re.compile(pattern))
    if pattern_file:
        with pattern_file.open("r") as f:
            for line in f:
                typer.echo(f"Pattern file line: {line.strip()}")
                patterns.append(re.compile(line.strip()))
    return patterns

@app.command(no_args_is_help=True)
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
    input: Path = typer.Option(..., "-i", "--input", help="Input BED file"),
    output: Path = typer.Option(..., "-o", "--output", help="Output BED file"),
    columns: List[int] = typer.Option([4], "-c", "--columns", help="1-based columns for filtering"),
    pattern: Optional[str] = typer.Option(None, "-p", "--pattern", help="Regex pattern to include"),
    pattern_file: Optional[Path] = typer.Option(None, "-pf", "--pattern-file", help="File with inclusion patterns"),
    exclude: Optional[str] = typer.Option(None, "-e", "--exclude", help="Regex pattern to exclude"),
    exclude_file: Optional[Path] = typer.Option(None, "-ef", "--exclude-file", help="File with exclusion patterns")
):
    """
    Selects BED rows matching include/exclude patterns in specified columns.

    This command filters a BED file based on regular expression patterns applied to user-specified columns.
    It supports both inclusion and exclusion patterns, provided either as command-line arguments or files.
    The output is a filtered BED file containing only the rows that match the inclusion patterns and do
    not match the exclusion patterns.
    """

    if not pattern and not pattern_file:
        typer.echo("Error: At least one of --pattern or --pattern-file must be provided.", err=True)
        raise typer.Exit(code=1)
    
    if pattern and pattern_file:
        typer.echo("Warning: --pattern and --pattern-file provided. Ignoring --pattern.")
        pattern = None

    if exclude and exclude_file:
        typer.echo("Warning: --exclude and --exclude-file provided. Ignoring --exclude.")
        exclude = None

    typer.echo("Parsing inclusion patterns...")
    in_patterns = parse_patterns(pattern, pattern_file)

    typer.echo("Parsing exclusion patterns...")
    ex_patterns = parse_patterns(exclude, exclude_file)

    typer.echo("Reading BED file...")
    bed_df = pd.read_csv(input, sep="\t", header=None)
    columns_idx = [col - 1 for col in columns]

    # Inclusion filtering
    if in_patterns:
        inc_mask = pd.concat([
            bed_df[col].astype(str).str.contains(pat) for col in columns_idx for pat in in_patterns
        ], axis=1).any(axis=1)
    else:
        inc_mask = pd.Series(True, index=bed_df.index)

    # Exclusion filtering
    if ex_patterns:
        exc_mask = pd.concat([
            bed_df[col].astype(str).str.contains(pat) for col in columns_idx for pat in ex_patterns
        ], axis=1).any(axis=1)
    else:
        exc_mask = pd.Series(False, index=bed_df.index)

    selected_df = bed_df[inc_mask & ~exc_mask]
    typer.echo(f"Selected {selected_df.shape[0]} rows")

    if selected_df.empty:
        typer.echo("No matching records found. Output file not written.", err=True)
        raise typer.Exit()
    
    selected_df.to_csv(output, sep="\t", header=False, index=False)
    typer.echo(f"Written to: {output}")

if __name__ == "__main__":
    app()