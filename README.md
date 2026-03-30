# refseq2kraken

CLI tool to build custom Kraken2 databases from NCBI RefSeq.

## Features
- Download genomes from RefSeq
- Build custom Kraken2 databases
- Support for underrepresented taxa (plants, invertebrates)

## Installation
Coming soon (conda/pip)

# refseq2kraken

**refseq2kraken** is a command-line tool for building custom **Kraken2** databases from NCBI RefSeq, with a focus on underrepresented taxonomic groups such as plants and invertebrates.

---

## 📌 Overview

Metagenomic classification tools such as Kraken2 rely heavily on the completeness and representativeness of their reference databases. However, default databases often underrepresent key taxonomic groups (e.g., Plantae and many invertebrates), limiting their effectiveness in ecological and environmental studies.

**refseq2kraken** addresses this limitation by providing a flexible and reproducible pipeline to:

* Retrieve genome assemblies directly from NCBI RefSeq
* Filter and organize sequences by taxonomic group
* Build custom Kraken2 databases
* Facilitate reproducible metagenomic workflows

---

## ⚙️ Features

* ✅ Automated download of RefSeq genomes (NCBI FTP)
* ✅ Support for custom taxonomic groups (e.g., `plant`, `invertebrate`)
* ✅ Parallelized genome download
* ✅ Seamless integration with Kraken2
* ✅ Modular CLI design
* 🚧 (planned) Taxonomic filtering (kingdom/phylum/class)
* 🚧 (planned) Genome quality filtering
* 🚧 (planned) Deduplication of assemblies

---

## 🧬 Workflow

1. Download assembly metadata from RefSeq
2. Parse FTP links for genome sequences
3. Download `.fna.gz` genome files
4. Decompress files
5. Add sequences to Kraken2 library
6. Build Kraken2 database

---

## 📦 Installation

### Using Conda (recommended)

```bash
conda env create -f environment.yml
conda activate refseq2kraken
```

### Using pip (development)

```bash
pip install -e .
```

---

## 🚀 Usage

### 1. Download genomes

```bash
refseq2kraken download --group invertebrate --threads 8
```

### 2. Add genomes to Kraken2 database

```bash
refseq2kraken add --input ./genomes --db ~/k2_custom
```

### 3. Build database

```bash
refseq2kraken build --db ~/k2_custom --threads 32
```

---

## 📂 Project Structure

```text
refseq2kraken/
├── refseq2kraken/
│   ├── cli.py
│   ├── download.py
│   ├── kraken.py
│   └── utils.py
├── tests/
├── environment.yml
├── pyproject.toml
└── README.md
```

---

## 🧪 Use Cases

* 🌱 Plant metagenomics
* 🐛 Invertebrate-associated microbiomes
* 🌍 Environmental DNA (eDNA) studies
* 🧬 Custom reference database construction

---

## 📊 Future Directions

* Integration with NCBI taxonomy filters (taxid-based)
* Support for incremental database updates
* Benchmarking vs standard Kraken2 databases
* Snakemake/Nextflow workflow integration

---

## 📖 Citation

If you use this tool in your research, please cite:

> Conceição Filho, W.R. (2026). *refseq2kraken: A flexible pipeline for building custom Kraken2 databases from RefSeq.*

(Preprint/manuscript in preparation)

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📜 License

(To be defined)

---

## 👨‍🔬 Author

**Walter Rosa da Conceição Filho**
MSc in Ecology & Evolution | Bioinformatics & Genomics
Federal University of Goiás (UFG), Brazil

---

## 🔗 Related Tools

* Kraken2
* Bracken
* NCBI RefSeq

---
