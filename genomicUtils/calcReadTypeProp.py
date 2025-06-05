

import sys
import os
import csv
from multiprocessing import Pool, cpu_count
from collections import defaultdict
from typing import Optional
import itertools
import typer
from pathlib import Path
from genomicUtils.utils import version_callback
from genomicUtils import __version__

description = """
    This script is used subsequently to the gex_bam_tags_to_csv.py script by operating on the output csv file.\n

    This script runs on multi-core CPUs to speed up the processing of the data by dividing the data into chunks and processing each chunk in parallel.\n

    Read proportion are calculated as:\n
        exon_prop = number of confidently mapped exonic reads / number of confidently mapped reads\n
        intron_prop = number of confidently mapped intronic reads / number of confidently mapped reads\n
        intergenic_prop = number of confidently mapped intergenic reads / number of confidently mapped reads\n

    Assumptions of the input csv file:\n
    - The input csv file has the following columns:\n
        - CB_cell_barcode: cell barcode\n
        - UB_umi_barcode: UMI barcode\n
        - RE_region_type: region type of the alignment\n
        - GN_gene_name: gene name(s) for the alignment\n
    - The input csv file only consists of confidently mapped reads (MAPQ >= 255)\n
    - Only reads with valid cell barcodes (CB) and UMI barcodes (UB) are included\n
    - The UMIs are collapsed (i.e., no duplicates)\n

    The output is a csv file such that:\n
    - Each row corresponds to a cell\n
    - Each column corresponds to metadata, with columns\n
        - CB_cell_barcode: cell barcode\n
        - total_reads: total number of confidently mapped reads\n
        - exon_reads: number of confidently mapped exonic reads\n
        - exon_prop: proportion of confidently mapped exonic reads\n
        - intron_reads: number of confidently mapped intronic reads\n
        - intron_prop: proportion of confidently mapped intronic reads\n
        - intergenic_reads: number of confidently mapped intergenic reads\n
        - intergenic_prop: proportion of confidently mapped intergenic reads\n
    """

app = typer.Typer(help="Calculate the proportion of reads of each type in each cell barcode.")

# Define default dictionary structure
def default_dict_int():
    return {"E": 0, "N": 0, "I": 0}

# Handle read type counts for each chunk
def process_chunk(chunk):
    # Exonic (E), Intronic (N), Intergenic (I)
    typer.echo(f"Processing new chunk of {len(chunk)} reads... on process {os.getpid()}")
    read_type_dict = defaultdict(default_dict_int)
    for row in chunk:
        try:
            cell_barcode, _, region_type, _ = row
            if region_type in ["E", "N", "I"]:
                read_type_dict[cell_barcode][region_type] += 1
        except Exception as e:
            typer.echo(f"Error processing row: {row}. Error: {str(e)}")
    return dict(read_type_dict)

# chuck iterator
def chunk_iterator(reader, chunk_size):
    while True:
        chunk = list(itertools.islice(reader, chunk_size))
        if not chunk:
            break
        yield chunk

@app.command(epilog=description, no_args_is_help=True)
# Main function
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
    input_csv: Path = typer.Option(..., "-i", "--input_csv", help="Input csv file"),
    output_csv: Path = typer.Option(..., "-o", "--output_csv", help="Output csv file"),
    chunk_size: int = typer.Option(1000000, "-c", "--chunk_size", help="Chunk size for processing (default: 1000000)")
):
    
    # Check if the input csv file exists
    if not os.path.exists(input_csv):
        typer.echo("The input csv file does not exist.")
        sys.exit(1)

    typer.echo("Begin reading input csv file...")

    combined_dict = defaultdict(default_dict_int)
    
    # Open the input csv file for reading
    with open(input_csv, "r") as f:
        reader = csv.reader(f)
        header = next(reader) # Skip the header
        
        # Assign chucks to be processed by available CPUs while reading the file
        available_cpus = cpu_count() - 1 
        if available_cpus < 1:
            available_cpus = 1
        
        typer.echo(f"Reading and processing the input csv file with {available_cpus} CPUs on the fly...")
        
        with Pool(processes=available_cpus) as pool:
            for result in pool.imap_unordered(process_chunk, chunk_iterator(reader, chunk_size)):
                for cell_barcode, read_type_counts in result.items():
                    for region_type, count in read_type_counts.items():
                        combined_dict[cell_barcode][region_type] += count
    

    # typer.echo the number of reads
    total_cell_barcodes = len(combined_dict)
    typer.echo(f"Completed processing {total_cell_barcodes} unique cell barcodes.")
    
    # Calculate the total read counts and proportions
    # Run calculations and writing on the fly
    with open(output_csv, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["CB_cell_barcode", "total_reads", "exon_reads", "exon_prop", "intron_reads", "intron_prop", "intergenic_reads", "intergenic_prop"])
        
        for cell_barcode, read_type_counts in combined_dict.items():
            total_read_count = sum(read_type_counts.values())
            exon_read_count = read_type_counts["E"]
            intron_read_count = read_type_counts["N"]
            intergenic_read_count = read_type_counts["I"]

            exon_prop = exon_read_count / total_read_count if total_read_count > 0 else 0
            intron_prop = intron_read_count / total_read_count if total_read_count > 0 else 0
            intergenic_prop = intergenic_read_count / total_read_count if total_read_count > 0 else 0

            writer.writerow([cell_barcode, total_read_count, 
                             exon_read_count, exon_prop, 
                             intron_read_count, intron_prop, 
                             intergenic_read_count, intergenic_prop])

    typer.echo("Done.")
    typer.echo(f"Output written to {output_csv}")

main.__doc__ = description

# Check if the script is being run directly
if __name__ == "__main__":
    app()

# [END]
