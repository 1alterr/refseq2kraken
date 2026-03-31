import os
import requests
import tarfile
import gzip
import shutil
from pathlib import Path

def download_ncbi_file(url, dest_path):
    """Downloads a file from NCBI via HTTP/HTTPS with stream support."""
    print(f"[*] Downloading {os.path.basename(url)}...")
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
    except Exception as e:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise Exception(f"Failed to download {url}: {e}")

def init_taxonomy(db_path):
    """
    Python implementation of Kraken2's download_taxonomy.sh.
    Downloads NCBI taxonomy tree and accession-to-taxon maps.
    """
    # 1. Setup Directories 
    tax_dir = Path(db_path) / "taxonomy"
    tax_dir.mkdir(parents=True, exist_ok=True)
    
    # Store current path to return later
    original_cwd = os.getcwd()
    os.chdir(tax_dir)

    base_url = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy"

    try:
        # 2. Download Accession to Taxon Maps [cite: 4, 5]
        # We focus on nucleotide maps (gb and wgs) as per the original script
        if not os.path.exists("accmap.dlflag"):
            for sub in ["gb", "wgs"]:
                file_name = f"nucl_{sub}.accession2taxid.gz"
                url = f"{base_url}/accession2taxid/{file_name}"
                
                download_ncbi_file(url, file_name)
                
                # Uncompress taxonomy data [cite: 8]
                print(f"[*] Uncompressing {file_name}...")
                with gzip.open(file_name, 'rb') as f_in:
                    with open(file_name.replace(".gz", ""), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Clean up .gz to save space
                os.remove(file_name)
            
            Path("accmap.dlflag").touch()
            print("[OK] Accession maps ready.")

        # 3. Download Taxonomy Tree Data (taxdump) [cite: 7]
        if not os.path.exists("taxdump.dlflag"):
            url = f"{base_url}/taxdump.tar.gz"
            download_ncbi_file(url, "taxdump.tar.gz")
            Path("taxdump.dlflag").touch()

        # 4. Untar Taxonomy Tree Data [cite: 9]
        if not os.path.exists("taxdump.untarflag"):
            print("[*] Untarring taxonomy tree data...")
            with tarfile.open("taxdump.tar.gz", "r:gz") as tar:
                tar.extractall()
            Path("taxdump.untarflag").touch()
            print("[OK] Taxonomy tree ready.")

    finally:
        os.chdir(original_cwd)

    print("\n[SUCCESS] Taxonomy step complete.")


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