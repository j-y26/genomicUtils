# Given a csv file with the following columns: Sample, Label
# sample: name of the sample
# label: label of the sample
# Replace the "sample" part of the file name with the label

# Usage: python file_name_conversion.py -c/--csv-file <csv_file>
#                                       -d/--directory <file_dir>
#                                       -e/--file-extension <file_extension>

# Note: the file names should follow the format: sample<file_extension>
# For example: sample_bowtie2.bam has the extension _bowtie2.bam

import os
import pandas as pd
import typer
from pathlib import Path
from typing import Optional
from genomicUtils.utils import version_callback
from genomicUtils import __version__

app = typer.Typer(help="Convert (part) of a file name for files in a directory based on a sample csv file")

description = """
    Convert file names in a directory based on a sample sheet CSV file.\n
    The CSV file should contain two columns: Sample and Label.\n
    The file names should follow the format: sample<file_extension>\n

    For example: sample_bowtie2.bam has the extension _bowtie2.bam\n
    """

@app.command(no_args_is_help=True, epilog=description)
def convert_file_names(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
    csv_file: Path = typer.Option(..., "-c", "--csv-file", help="CSV file containing the sample names and labels"),
    file_dir: Path = typer.Option(..., "-d", "--directory", help="Directory containing the files to be renamed"),
    file_extension: str = typer.Option(..., "-e", "--file-extension", help="File extension of the files to be renamed")
):
    
    # Read in the csv file
    sample_sheet = pd.read_csv(csv_file)

    # Extract the sample names and labels   
    sample_names = sample_sheet["Sample"]
    sample_labels = sample_sheet["Label"]

    # Rename the files, by iterating through all the files in the directory
    for file in os.listdir(file_dir):
        # Check if the file has the correct extension
        if file.endswith(file_extension):
            # Obtain the sample name, by removing the extension
            sample_name = file.replace(file_extension, "")
            # Check if the sample name is in the sample sheet
            if sample_name in sample_names.values:
                # Obtain the index of the sample name
                sample_index = sample_names[sample_names == sample_name].index[0]
                # Obtain the label of the sample
                sample_label = sample_labels[sample_index]
                # Rename the file
                os.rename(os.path.join(file_dir, file), os.path.join(file_dir, sample_label + file_extension))
                print("Renamed " + file + " to " + sample_label + file_extension)
            else:
                print("Sample " + sample_name + " not found in the sample sheet")
        else:
            print("File " + file + " does not have the correct extension")

if __name__ == "__main__":
    app()

# [END]