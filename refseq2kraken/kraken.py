import os
import subprocess


def init_db(db_path):
    if os.path.exists(os.path.join(db_path, "taxonomy")):
        print("[SKIP] Taxonomy already exists")
        return

    print("[STEP] Initializing Kraken DB")

    subprocess.run([
        "kraken2-build",
        "--download-taxonomy",
        "--db", db_path,
        "--use-ftp"
    ], check=True)


def add_to_library(fna_files, db_path):
    print("[STEP] Adding genomes to DB")

    for f in fna_files:
        subprocess.run([
            "kraken2-build",
            "--add-to-library", f,
            "--db", db_path
        ], check=True)


def build_db(db_path, threads):
    print("[STEP] Building DB")

    subprocess.run([
        "kraken2-build",
        "--build",
        "--threads", str(threads),
        "--fast-build",
        "--db", db_path
    ], check=True)