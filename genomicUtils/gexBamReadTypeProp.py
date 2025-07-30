import os
import pysam
import csv
import multiprocessing as mp
import time
import typer
import xxhash
from tqdm import tqdm
from pathlib import Path
from typing import Optional, Dict, Tuple
from collections import defaultdict
from genomicUtils.utils import version_callback
from genomicUtils import __version__

app = typer.Typer(help="Combined BAM processing pipeline: extract tags and calculate read type proportions.")

BIN_SIZE = 10_000_000  # 10Mb bin for parallel processing

description = """
    Combined pipeline that processes Cell Ranger BAM files to calculate read type proportions per cell.
    
    This combines the functionality of gex_bam_tags_to_csv.py and calc_read_type_prop.py into a single,
    more efficient pipeline that avoids intermediate file I/O.
    
    **Processing Steps:**
    1. Extracts reads with MAPQ = 255 (confidently mapped)
    2. Filters for reads with valid CB and UB tags
    3. Deduplicates based on (CB, UB) pairs
    4. Calculates read type proportions per cell
    
    **Output CSV columns:**
    - CB_cell_barcode: cell barcode
    - total_reads: total number of confidently mapped reads
    - exon_reads: number of confidently mapped exonic reads
    - exon_prop: proportion of confidently mapped exonic reads
    - intron_reads: number of confidently mapped intronic reads
    - intron_prop: proportion of confidently mapped intronic reads
    - intergenic_reads: number of confidently mapped intergenic reads
    - intergenic_prop: proportion of confidently mapped intergenic reads
    
    **Region Types:**
    - E: Exonic
    - N: Intronic  
    - I: Intergenic
"""

def hash_umi(cb: str, ub: str) -> int:
    """
    Create a memory-efficient hash using xxHash.
    xxHash is extremely fast and has excellent distribution properties.
    Returns a 64-bit integer (8 bytes) vs 32 bytes for MD5 hex string.
    """
    # Use xxHash64 for speed and excellent hash quality
    return xxhash.xxh64(f"{cb}:{ub}").intdigest()

def process_chunk_streaming(args):
    """
    Process a BAM chunk and return UMI records for global deduplication.
    Uses xxHash for memory-efficient and fast hashing.
    """
    chunk = args
    input_bam, reference, start, end = chunk
    
    typer.echo(f"[Worker {mp.current_process().name}] Processing {reference}:{start}-{end}")
    
    # Store all valid UMI records for this chunk
    umi_records = []
    local_umi_seen = set()
    
    with pysam.AlignmentFile(input_bam, "rb") as bam:
        for read in bam.fetch(reference=reference, start=start, end=end):
            # Filter for confidently mapped reads only
            if read.mapping_quality != 255:
                continue
                
            # Must have both CB and UB tags
            if not (read.has_tag("CB") and read.has_tag("UB")):
                continue
                
            cb = read.get_tag("CB")
            ub = read.get_tag("UB")
            
            # Create memory-efficient xxHash
            umi_hash = hash_umi(cb, ub)
            
            # Local deduplication within chunk
            if umi_hash in local_umi_seen:
                continue
            local_umi_seen.add(umi_hash)
            
            # Get region type (default to empty if not present)
            region_type = read.get_tag("RE") if read.has_tag("RE") else ""
            
            # Only store records with valid region types
            if region_type in ['E', 'N', 'I']:
                umi_records.append({
                    'cb': cb,
                    'ub': ub,
                    'region_type': region_type,
                    'umi_hash': umi_hash
                })
    
    return umi_records

def get_bam_chunks(input_bam, bin_size=BIN_SIZE):
    """
    Returns a list of (input_bam, reference, start, end) tuples for binning.
    """
    chunks = []
    with pysam.AlignmentFile(input_bam, "rb") as bam:
        references = bam.references
        ref_lengths = bam.lengths
        for ref, length in zip(references, ref_lengths):
            for start in range(0, length, bin_size):
                end = min(start + bin_size, length)
                chunks.append((input_bam, ref, start, end))
    return chunks

def merge_chunk_results_streaming(chunk_results):
    """
    Memory-efficient merge with streaming deduplication.
    Processes one chunk at a time to minimize peak memory usage.
    """
    global_umi_seen = set()
    cell_data = defaultdict(lambda: {'E': 0, 'N': 0, 'I': 0})
    
    typer.echo("Performing streaming global UMI deduplication...")
    
    total_records_before = 0
    total_records_after = 0
    
    for i, chunk_records in enumerate(tqdm(chunk_results, desc="Merging chunks")):
        typer.echo(f"Processing chunk {i+1}/{len(chunk_results)} for global deduplication...")
        
        total_records_before += len(chunk_records)
        
        for record in chunk_records:
            umi_hash = record['umi_hash']
            
            # Global deduplication
            if umi_hash in global_umi_seen:
                continue
                
            global_umi_seen.add(umi_hash)
            total_records_after += 1
            
            # Count this record for the cell
            cb = record['cb']
            region_type = record['region_type']
            cell_data[cb][region_type] += 1
        
        # Clear this chunk from memory immediately after processing
        chunk_records.clear()
    
    typer.echo(f"Global deduplication: {total_records_before} -> {total_records_after} records")
    typer.echo(f"Unique UMIs after global deduplication: {len(global_umi_seen)}")
    typer.echo(f"Memory usage for xxHash UMI hashes: {len(global_umi_seen) * 8 / 1024 / 1024:.1f} MB")
    
    return dict(cell_data)

def write_output_csv(cell_data, output_csv):
    """
    Write the final output CSV with proportions calculated.
    """
    with open(output_csv, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "CB_cell_barcode", "total_reads", 
            "exon_reads", "exon_prop", 
            "intron_reads", "intron_prop", 
            "intergenic_reads", "intergenic_prop"
        ])
        
        for cell_barcode, read_counts in cell_data.items():
            exon_reads = read_counts['E']
            intron_reads = read_counts['N']
            intergenic_reads = read_counts['I']
            
            total_reads = exon_reads + intron_reads + intergenic_reads
            
            # Calculate proportions (avoid division by zero)
            if total_reads > 0:
                exon_prop = exon_reads / total_reads
                intron_prop = intron_reads / total_reads
                intergenic_prop = intergenic_reads / total_reads
            else:
                exon_prop = intron_prop = intergenic_prop = 0
            
            writer.writerow([
                cell_barcode, total_reads,
                exon_reads, exon_prop,
                intron_reads, intron_prop,
                intergenic_reads, intergenic_prop
            ])

@app.command(no_args_is_help=True, epilog=description)
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
    input_bam: Path = typer.Option(..., "-i", "--input", help="Input BAM file (must be coordinate-sorted and indexed)."),
    output_csv: Path = typer.Option(..., "-o", "--output", help="Output CSV file with read type proportions per cell."),
    num_threads: int = typer.Option(mp.cpu_count(), "-t", "--threads", help="Number of threads to use.")
):
    """
    Combined pipeline to process Cell Ranger BAM files and calculate read type proportions.

    **Key Features:**
    - Memory-efficient streaming processing
    - Parallel processing using multiprocessing
    - UMI deduplication
    - Direct calculation of read type proportions
    """
    start_time = time.time()
    typer.echo(f"Analysis started at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    
    # Validate input file
    if not os.path.exists(input_bam):
        raise FileNotFoundError(f"Input BAM file '{input_bam}' does not exist.")
    
    # Get BAM chunks for parallel processing
    chunks = get_bam_chunks(input_bam)
    typer.echo(f"Divided BAM into {len(chunks)} chunks for parallel processing.")
    # Process chunks in parallel
    typer.echo(f"Processing chunks using {num_threads} threads...")
    with mp.Pool(processes=num_threads) as pool:
        chunk_results = pool.map(process_chunk_streaming, chunks)
    
    # Merge results from all chunks with global deduplication
    typer.echo("Merging results with global UMI deduplication...")
    combined_data = merge_chunk_results_streaming(chunk_results)
    
    # Write output CSV
    typer.echo(f"Writing output to {output_csv}...")
    write_output_csv(combined_data, output_csv)
    
    # Summary statistics
    total_cells = len(combined_data)
    total_reads = sum(sum(counts.values()) for counts in combined_data.values())
    
    typer.echo(f"Analysis completed!")
    typer.echo(f"Processed {total_cells} unique cell barcodes")
    typer.echo(f"Total unique UMIs processed: {total_reads}")
    typer.echo(f"Output written to: {output_csv}")
    typer.echo(f"Total processing time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    app()