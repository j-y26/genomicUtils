import os
import pandas as pd
import typer
from pathlib import Path
from typing import Optional
from genomicUtils.utils import version_callback
from genomicUtils import __version__

app = typer.Typer(help="Generate a sample matrix csv file for files in a directory with a specific suffix.")

description = """
    Generate a sample matrix csv file for files in a directory with a specific suffix.\n\n

    The sample matrix will contain the following columns:\n
    - Sample: Name of the sample (derived from the file name)\n
    - Label: Same as Sample\n
    - Group: Empty by default, can be filled later\n
    - Replicate: Empty by default, can be filled later\n
    - Batch: Empty by default, can be filled later\n
    - Mark: Empty by default, can be filled later\n
    - PeakType: Empty by default, can be filled later\n
    - FileName: Name of the file including the suffix\n\n

    The script will traverse the specified directory, find all files with the given suffix, and generate a sample matrix in CSV format. Each row in the matrix corresponds to a file, with the sample name derived from the file name (excluding the suffix). The other columns (Group, Replicate, Batch, Mark, PeakType) are initialized as empty strings.
    """

@app.command(no_args_is_help=True)
def generate_sample_matrix(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
    directory: Path = typer.Option(..., "-d", "--dir", help="Directory containing the files"),
    suffix: str = typer.Option(..., "-s", "--suffix", help="Suffix of the files to include"),
    output_file: Path = typer.Option(..., "-o", "--output", help="Output file to save the sample matrix")
):
    
    # Traverse the directory to find files with the specified suffix
    sample_matrix = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(suffix):
                # Extract sample name
                sample_name = file[:-len(suffix)]
                
                # Append sample data to the sample matrix
                sample_matrix.append({
                    "Sample": sample_name,
                    "Label": sample_name,
                    "Group": "",
                    "Replicate": "",
                    "Batch": "",
                    "Mark": "",
                    "PeakType": "",
                    "FileName": file
                })

    # Convert the sample matrix to a pandas DataFrame
    sample_matrix_df = pd.DataFrame(sample_matrix)
    sample_matrix_df.to_csv(output_file, index=False)

    typer.echo("Sample matrix generated successfully!")
    typer.echo(f"Sample matrix saved to {output_file}")
generate_sample_matrix.__doc__ = description

if __name__ == "__main__":
    app()

# [END]