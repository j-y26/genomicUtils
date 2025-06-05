from setuptools import setup, find_packages

setup(
    name="genomicUtils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "tqdm",
        "pandas",
        "numpy",
        "h5py",
        "scipy",
        "pysam",
        "biopython"
    ],
    entry_points={
        "console_scripts": [
            "genomicUtils=genomicUtils.cli:app",
            "bedSelect=genomicUtils.bedSelect:app",
            "fileNameConversion=genomicUtils.fileNameConversion:app",
            "convertContigNames=genomicUtils.convertContigNames:app",
            "extractGeneFromGTF=genomicUtils.extractGeneFromGTF:app",
            "extractTranscriptFromGTF=genomicUtils.extractTranscriptFromGTF:app",
            "extractExonFromGTF=genomicUtils.extractExonFromGTF:app",
            "generatePromoterBed=genomicUtils.generatePromoterBed:app",
            "generateSampleMatrix=genomicUtils.generateSampleMatrix:app",
            "multiFastaSelect=genomicUtils.multiFastaSelect:app",
            "gexBamTagsToCSV=genomicUtils.gexBamTagsToCSV:app",
            "calcReadTypeProp=genomicUtils.calcReadTypeProp:app",
            "extractGEXFromH5=genomicUtils.extractGEXFromH5:app",
            "fragment2Bigwig=genomicUtils.fragment2Bigwig:app"
        ]
    },
    author="Jielin Yang",
    author_email="jielin.yang@sickkids.ca",
    description="A collection of utilities tools for bulk and single-cell genomics data processing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/j-y26/genomicUtils",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Natural Language :: English",
    ],
    python_requires=">=3.7",
)
