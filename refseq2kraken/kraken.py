import subprocess
import os

def add_to_library(input_dir, db):
    for f in os.listdir(input_dir):
        if f.endswith(".fna"):
            path = os.path.join(input_dir, f)

            subprocess.run([
                "kraken2-build",
                "--add-to-library", path,
                "--db", db
            ])

def build_db(db, threads):
    subprocess.run([
        "kraken2-build",
        "--download-taxonomy",
        "--db", db
    ])

    subprocess.run([
        "kraken2-build",
        "--build",
        "--threads", str(threads),
        "--db", db
    ])