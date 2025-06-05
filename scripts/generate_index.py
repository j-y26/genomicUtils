from pathlib import Path
import importlib.util

# Base paths
docs_root = Path("docs")
index_md = docs_root / "index.md"
genomic_utils_root = Path("genomicUtils")

# Folder to category mapping
categories = {
    "General Tools": "general",
    "Single-Cell Tools": "single_cell",
}

def extract_typer_help(py_file: Path) -> str:
    """Dynamically import a Typer app and extract its help description."""
    try:
        spec = importlib.util.spec_from_file_location("mod", py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        app = getattr(mod, "app", None)
        if app and hasattr(app, "info") and app.info.help:
            return app.info.help.strip().split("\n")[0].strip().split(".")[0]
        return "(no help message in app)"
    except Exception as e:
        return f"(error loading help: {e})"

# Build Markdown content
lines = [
    "<img src='asset/logo_title.png' alt='genomicUtils' width='500'/>\n",
    "`genomicUtils` is a modular command-line toolkit designed to streamline bulk and single-cell genomic data processing.\n",
    "It provides a curated collection of tools for manipulating genomic annotations, formatting data, extracting features, and preparing input files for downstream analysis.\n\n",
    "The toolkit includes utilities for:\n",
    "- **General-purpose genomic data manipulation** (e.g., GTF parsing, BED/FASTA filtering, contig name conversion),\n",
    "- **File and sample metadata handling** (e.g., sample matrix generation, filename conversions),\n",
    "- **Single-cell and multiome data preprocessing** (e.g., read type profiling, fragment conversion, tag extraction from 10X BAM/H5 files).\n\n",
    "Each tool is self-contained and scriptable, making `genomicUtils` ideal for high-throughput data processing pipelines and reproducible workflows in computational genomics.\n",
]

for section, subdir in categories.items():
    folder = docs_root / subdir
    if not folder.exists():
        print(f"⚠️ Skipping: {folder} not found.")
        continue

    lines.append(f"## {section}\n")
    for md_file in sorted(folder.glob("*.md")):
        tool_name = md_file.stem
        py_file = genomic_utils_root / f"{tool_name}.py"
        rel_link = f"{subdir}/{md_file.name}"
        description = extract_typer_help(py_file) if py_file.exists() else "(no Python module found)"
        lines.append(f"- [{tool_name}]({rel_link}): {description}")
    lines.append("")  # Add blank line after each section

# Ensure docs directory exists before writing
index_md.parent.mkdir(parents=True, exist_ok=True)
index_md.write_text("\n".join(lines))
print(f"✅ Wrote: {index_md}")
