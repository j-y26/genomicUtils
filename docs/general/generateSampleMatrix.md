
:::mkdocs-typer2
    :module: genomicUtils.generateSampleMatrix
    :name: generateSampleMatrix

The sample matrix will contain the following columns:
- Sample: Name of the sample (derived from the file name)
- Label: Same as Sample
- Group: Empty by default, can be filled later
- Replicate: Empty by default, can be filled later
- Batch: Empty by default, can be filled later
- Mark: Empty by default, can be filled later
- PeakType: Empty by default, can be filled later
- FileName: Name of the file including the suffix

The script will traverse the specified directory, find all files with the given suffix, and generate a sample matrix in CSV format. Each row in the matrix corresponds to a file, with the sample name derived from the file name (excluding the suffix). The other columns (Group, Replicate, Batch, Mark, PeakType) are initialized as empty strings.
