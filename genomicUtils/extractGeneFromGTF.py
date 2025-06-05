import re
import typer
from pathlib import Path
from typing import Optional
from genomicUtils.utils import version_callback
from genomicUtils import __version__

app = typer.Typer(help="Extracting gene information from gtf file. Output file follows BED format with additional columns for gene information.")

@app.command(no_args_is_help=True)
def extract(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
    gtf_file: Path = typer.Option(..., "-i", "--input", help="Input GTF file"),
    output_file: Path = typer.Option(..., "-o", "--output", help="Output bed file")
):
    """
    Extract gene information from a GTF file and output it in a BED-like format.
    The output file will contain the following columns:
    - chromosome
    - start
    - end
    - strand
    - exon_id
    - gene_id
    - gene_name
    - gene_type
    """
    with open(gtf_file, 'r') as f, open(output_file, 'r') as o:
        typer.echo(f"Extracted gene information from {gtf_file} to {output_file}.")

        # Write header
        o.write('chromosome' + '\t' + 'start' + '\t' + 'end' + '\t' + 'strand' + '\t' + 'gene_id' + '\t' + 'gene_name' + '\t' + 'gene_type' + '\n')

        for line in f:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            if fields[2] != 'gene':
                continue

            attr = fields[8]
            gene_id = re.search(r'gene_id "([^"]+)"', attr)
            gene_name = re.search(r'gene_name "([^"]+)"', attr)
            gene_type = re.search(r'gene_biotype "([^"]+)"', attr)

            if gene_id:
                o.write(fields[0] + '\t' + 
                        fields[3] + '\t' + 
                        fields[4] + '\t' + 
                        fields[6] + '\t' + 
                        gene_id.group(1) + '\t' + 
                        (gene_name.group(1) if gene_name else '') + '\t' + 
                        (gene_type.group(1) if gene_type else '') + '\n')

if __name__ == '__main__':
    app()