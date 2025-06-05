import re
from Bio import SeqIO
import typer
from pathlib import Path
from typing import Optional
from genomicUtils.utils import version_callback
from genomicUtils import __version__

app = typer.Typer(help="Extract sequences from a multi-sequence FASTA file based on regex patterns matching sequence identifiers in the header lines.")

def parse_patterns(pattern, pattern_file):
    """
    Parses the pattern(s) provided by the user and returns a list of compiled regex patterns.
    """
    patterns = []
    if pattern:
        typer.echo(pattern)
        patterns.append(re.compile(pattern))
    if pattern_file:
        with open(pattern_file, "r") as f:
            for line in f:
                typer.echo(line.strip())
                patterns.append(re.compile(line.strip()))
    return patterns

def select_sequences(input_fasta, output_fasta, in_patterns, ex_patterns):
    """
    Given an input FASTA file with multiple sequences, extract and output a subset of sequences based on regular expression patterns matching a list of sequence identifiers to the fasta header lines
    """
    typer.echo("Begin selecting sequences...")

    # Temporary variables to store matched patterns
    found_matching_records = False
    matched_records = []

    # Iterate through the input FASTA file and select sequences based on the inclusion and exclusion patterns
    for record in SeqIO.parse(input_fasta, "fasta"):
        header = record.id

        # Check if the header matches any of the inclusion patterns
        include = any(pat.search(header) for pat in in_patterns) if in_patterns else True

        # Check if the header matches any of the exclusion patterns
        exclude = any(pat.search(header) for pat in ex_patterns) if ex_patterns else False

        # Write the sequence to the output FASTA file if it matches the inclusion pattern and does not match the exclusion pattern
        if include and not exclude:
            matched_records.append(record)
            found_matching_records = True
            typer.echo(f"Selected: {header}")
    typer.echo("FASTA sequence selection complete.")

    # Write the selected sequences to the output FASTA file
    if found_matching_records:
        with open(output_fasta, "w") as out_fasta:
            SeqIO.write(matched_records, out_fasta, "fasta")
        typer.echo(f"Selected sequences written to {output_fasta}")
    else:
        typer.echo("No sequences matched the given patterns. No output file generated.")

@app.command(no_args_is_help=True)
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
    input_fasta: Path = typer.Option(..., "-i", "--input", help="Input FASTA file with multiple sequences."),
    output_fasta: Path = typer.Option(..., "-o", "--output", help="Output FASTA file for selected sequences."),
    pattern: str = typer.Option(None, "-p", "--pattern", help="Pattern to match in the sequence identifier. Must provide either -p/--pattern or -pf/--pattern-file"),
    pattern_file: Path = typer.Option(None, "-pf", "--pattern-file", help="File containing patterns to match in the sequence identifier, where each regex pattern should begin on a new line. Overwrites -p/--pattern if provided"),
    exclude_pattern: str = typer.Option(None, "-e", "--exclude", help="[Optional] Pattern to exclude from the sequence identifier"),
    exclude_pattern_file: Path = typer.Option(None, "-ef", "--exclude-file", help="[Optional] File containing patterns to exclude from the sequence identifier, where each regex pattern should begin on a new line. Overwrites -e/--exclude if provided")
):
    """
    Given an input FASTA file with multiple sequences, extract and output a subset of sequences based on regular expression patterns matching a list of sequence identifiers to the fasta header lines.
    """
    # Check if at least one of "pattern", "pattern_file" is provided
    if not pattern and not pattern_file:
        typer.echo("Error: You must provide at least one of --pattern or --pattern_file.")
        raise typer.Exit(code=1)
    
    # Check if both "pattern" and "pattern_file" are provided,
    # and if so, "pattern" will be ignored
    if pattern and pattern_file:
        typer.echo("Both --pattern and --pattern_file provided. Ignoring --pattern.")
        pattern = None

    # Check if both "exclude" and "exclude_file" are provided,
    # and if so, "exclude" will be ignored
    if exclude_pattern and exclude_pattern_file:
        typer.echo("Both --exclude and --exclude_file provided. Ignoring --exclude.")
        exclude_pattern = None

    # Parse the inclusion and exclusion patterns
    typer.echo("Parsing patterns...")
    typer.echo("Patterns to include:")
    in_patterns = parse_patterns(pattern, pattern_file)
    typer.echo("Patterns to exclude:")
    ex_patterns = parse_patterns(exclude_pattern, exclude_pattern_file)
    select_sequences(input_fasta, output_fasta, in_patterns, ex_patterns)

if __name__ == "__main__":
    app()