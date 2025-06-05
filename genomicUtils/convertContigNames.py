# Convert chromosome names in a input file based on a mapping file

import pandas as pd
import typer
from pathlib import Path
from typing import Optional
from genomicUtils.utils import version_callback
from genomicUtils.__init__ import __version__

app = typer.Typer(help="Convert chromosome names in a input file based on a mapping file")

# Function to map chromosome names
@app.command(no_args_is_help=True)
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
    input_file: Path = typer.Option(..., '-i', '--input', help='Input file with chromosome names'),
    mapping_file: Path = typer.Option(..., '-m', '--mapping', help='Mapping file with old and new chromosome names'),
    output_file: Path = typer.Option(..., '-o', '--output', help='Output file with updated chromosome names'),
    chromosome_column: int = typer.Option(1, '-c', '--chromosome-column', help='Column index of chromosome names (1-indexed)'),
    separator: str = typer.Option('tab', '-s', '--separator', help='Separator for the input and mapping files (tab or comma)')
):    
    """Convert chromosome names in a input file based on a mapping file."""

    # Check separator
    if separator == 'tab':
        separator = '\t'
    elif separator == 'comma':
        separator = ','
    else:
        raise typer.Exit(1)

    # Convert 1-indexed to 0-indexed column
    if chromosome_column <= 0:
        typer.echo('Invalid column index', err=True)
        raise typer.Exit(1)
    chromosome_column = chromosome_column - 1

    try:
        # Read mapping file
        mapping = pd.read_csv(mapping_file, sep=separator, header=None, dtype={0: str, 1: str})
        mapping.columns = ['old', 'new']

        # Read input file
        input_df = pd.read_csv(input_file, sep=separator, header=None, dtype={chromosome_column: str})

        # Convert chromosome names
        input_df[chromosome_column] = input_df[chromosome_column].map(mapping.set_index('old')['new'])

        # Write output
        input_df.to_csv(output_file, sep=separator, header=False, index=False)
        
        typer.echo(f"Successfully converted chromosome names from {input_file} to {output_file}")
        
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == '__main__':
    app()

# [END]