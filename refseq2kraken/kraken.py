#!/usr/bin/env python3
import os
import sys
import gzip
import shutil
import tarfile
import requests
from pathlib import Path

def download_file(url, dest):
    print(f"[+] Downloading {url}")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            shutil.copyfileobj(r.raw, f)

def main():
    if "KRAKEN2_DB_NAME" not in os.environ:
        print("ERRO: KRAKEN2_DB_NAME não definido", file=sys.stderr)
        return 1

    baz = os.environ["KRAKEN2_DB_NAME"]
    tax_dir = Path(baz) / "taxonomy"
    tax_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(tax_dir)

    use_ftp = bool(os.environ.get("KRAKEN2_USE_FTP", ""))
    skip_maps = bool(os.environ.get("KRAKEN2_SKIP_MAPS", ""))
    prot_db = bool(os.environ.get("KRAKEN2_PROTEIN_DB", ""))

    ncbi = "ftp.ncbi.nlm.nih.gov"
    base_rsync = f"rsync://{ncbi}"
    base_ftp = f"ftp://{ncbi}"

    def get(path, dest):
        if use_ftp:
            download_file(base_ftp + path, dest)
        else:
            # Sistema deve ter rsync instalado
            cmd = ["rsync", "--no-motd", base_rsync + path, str(dest)]
            print(f"[+] Rsync: {' '.join(cmd)}")
            import subprocess
            subprocess.run(cmd, check=True)

    if not Path("accmap.dlflag").exists() and not skip_maps:
        if not prot_db:
            for sub in ("gb", "wgs"):
                print(f"Baixando nucl_{sub}.accession2taxid.gz")
                get(f"/pub/taxonomy/accession2taxid/nucl_{sub}.accession2taxid.gz", f"nucl_{sub}.accession2taxid.gz")
        else:
            print("Baixando prot.accession2taxid.gz")
            get("/pub/taxonomy/accession2taxid/prot.accession2taxid.gz", "prot.accession2taxid.gz")

        Path("accmap.dlflag").touch()
        print("Downloaded accession to taxon map(s)")

    if not Path("taxdump.dlflag").exists():
        print("Baixando taxdump.tar.gz")
        get("/pub/taxonomy/taxdump.tar.gz", "taxdump.tar.gz")
        Path("taxdump.dlflag").touch()

    if any(Path(p).name.endswith("accession2taxid.gz") for p in os.listdir(".")):
        print("Uncompressing taxonomy data...")
        for gzfile in Path(".").glob("*accession2taxid.gz"):
            with gzip.open(gzfile, "rb") as f_in, open(gzfile.with_suffix(""), "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            gzfile.unlink()
        print("done.")

    if not Path("taxdump.untarflag").exists():
        print("Untarring taxonomy tree data...")
        with tarfile.open("taxdump.tar.gz", "r:gz") as tar:
            tar.extractall()
        Path("taxdump.untarflag").touch()
        print("done.")

    return 0

if __name__ == "__main__":
    sys.exit(main())

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