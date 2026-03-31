#!/usr/bin/env python3

import os
import gzip
import urllib.request

NCBI_BASE = "https://ftp.ncbi.nlm.nih.gov/genomes/refseq"
VALID_LEVELS = {"Complete Genome", "Chromosome"}


# =========================
# DOWNLOAD
# =========================
def download_file(url: str, output_path: str) -> bool:
    try:
        print(f"[+] Downloading: {url}")
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"[ERROR] Failed download: {url} -> {e}")
        return False


# =========================
# PARSE ASSEMBLY
# =========================
def parse_assembly_summary(file_path: str):
    entries = []

    with open(file_path) as f:
        for line in f:
            if line.startswith("#"):
                continue

            cols = line.strip().split("\t")

            try:
                taxid = cols[5]
                asm_level = cols[11]
                ftp_path = cols[19]
            except IndexError:
                continue

            if asm_level not in VALID_LEVELS:
                continue

            if ftp_path == "na":
                continue

            basename = os.path.basename(ftp_path)
            fna_url = f"{ftp_path}/{basename}_genomic.fna.gz"

            entries.append((taxid, fna_url))

    return entries


# =========================
# PROCESS FASTA
# =========================
def process_fasta(gz_file: str, taxid: str, fasta_out, map_out):
    with gzip.open(gz_file, "rt") as f_in:
        for line in f_in:
            if line.startswith(">"):
                header = line.strip()
                seq_id = header.split()[0][1:]

                new_header = f">kraken:taxid|{taxid}|{header[1:]}\n"
                fasta_out.write(new_header)

                map_out.write(f"{seq_id}\t{taxid}\n")
            else:
                fasta_out.write(line)


# =========================
# PIPELINE
# =========================
def download_pipeline(group: str, threads: int, outdir: str):
    print(f"[INFO] Starting download for group: {group}")

    # Paths
    assembly_file = os.path.join(outdir, "assembly_summary.txt")
    downloads_dir = os.path.join(outdir, "downloads")
    library_path = os.path.join(outdir, "library.fna")
    map_path = os.path.join(outdir, "prelim_map.txt")

    os.makedirs(downloads_dir, exist_ok=True)

    # =========================
    # STEP 1: Download assembly summary
    # =========================
    assembly_url = f"{NCBI_BASE}/{group}/assembly_summary.txt"

    if not download_file(assembly_url, assembly_file):
        raise RuntimeError("Failed to download assembly_summary.txt")

    # =========================
    # STEP 2: Parse entries
    # =========================
    entries = parse_assembly_summary(assembly_file)
    total = len(entries)

    if total == 0:
        raise RuntimeError("No valid genome entries found")

    print(f"[INFO] {total} genomes selected")

    # =========================
    # STEP 3: Download + process
    # =========================
    with open(library_path, "w") as fasta_out, \
         open(map_path, "w") as map_out:

        for i, (taxid, url) in enumerate(entries, 1):
            filename = os.path.join(downloads_dir, os.path.basename(url))

            if not download_file(url, filename):
                continue

            try:
                process_fasta(filename, taxid, fasta_out, map_out)
            except Exception as e:
                print(f"[WARN] Failed processing {filename}: {e}")
                continue

            # Remove downloaded file
            try:
                os.remove(filename)
            except OSError:
                pass

            print(f"[{i}/{total}] processed")

    print("[OK] Download complete")
    print(f"[INFO] Output:")
    print(f" - {library_path}")
    print(f" - {map_path}")