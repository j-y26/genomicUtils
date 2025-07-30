
:::mkdocs-typer2
    :module: genomicUtils.gexBamReadTypeProp
    :name: gexBamReadTypeProp

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

This script runs on multi-core CPUs to speed up the processing of the data by dividing the data into chunks and processing each chunk in parallel.

Read proportion are calculated as:
    exon_prop = number of confidently mapped exonic reads / number of confidently mapped reads
    intron_prop = number of confidently mapped intronic reads / number of confidently mapped reads
    intergenic_prop = number of confidently mapped intergenic reads / number of confidently mapped reads

Assumptions of the BAM file:
    - CB_cell_barcode: cell barcode
    - UB_umi_barcode: UMI barcode
    - RE_region_type: region type of the alignment
- The input csv file only consists of confidently mapped reads (MAPQ >= 255)
- Only reads with valid cell barcodes (CB) and UMI barcodes (UB) are included
- The UMIs are collapsed (i.e., no duplicates)

The output is a csv file such that:
- Each row corresponds to a cell
- Each column corresponds to metadata, with columns
    - CB_cell_barcode: cell barcode
    - total_reads: total number of confidently mapped reads
    - exon_reads: number of confidently mapped exonic reads
    - exon_prop: proportion of confidently mapped exonic reads
    - intron_reads: number of confidently mapped intronic reads
    - intron_prop: proportion of confidently mapped intronic reads
    - intergenic_reads: number of confidently mapped intergenic reads
    - intergenic_prop: proportion of confidently mapped intergenic reads
        - 