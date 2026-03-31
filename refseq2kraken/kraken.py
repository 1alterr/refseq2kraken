import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


NCBI_FTP = "ftp://ftp.ncbi.nlm.nih.gov"
NCBI_RSYNC = "rsync://ftp.ncbi.nlm.nih.gov"


def run(cmd, cwd=None):
    subprocess.run(cmd, check=True, cwd=cwd)


def download_one(file_path, outdir, use_ftp=True):
    """
    Download a single file with FTP (default) or fallback to rsync
    """
    filename = os.path.basename(file_path)
    dest = Path(outdir) / filename

    if dest.exists():
        print(f"[SKIP] {filename}")
        return

    # Try FTP first
    if use_ftp:
        try:
            url = f"{NCBI_FTP}{file_path}"
            run(["wget", "-q", url], cwd=outdir)
            return
        except subprocess.CalledProcessError:
            print(f"[WARN] FTP failed → fallback to rsync")

    # Fallback rsync
    url = f"{NCBI_RSYNC}{file_path}"
    run(["rsync", "--no-motd", url, "."], cwd=outdir)


def parallel_download(files, outdir, threads=5):
    """
    Parallel download (default = 5 files at once)
    """
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(download_one, f, outdir)
            for f in files
        ]

        for future in as_completed(futures):
            future.result()


def init_db(db_path, threads=5, use_ftp=True):
    """
    Download and prepare NCBI taxonomy (Kraken2-compatible)
    """

    taxonomy_dir = Path(db_path) / "taxonomy"
    taxonomy_dir.mkdir(parents=True, exist_ok=True)

    print("Initializing Download taxonomy")

    # =========================
    # FILE LIST (Kraken2-compatible)
    # ========================= 
    subsections = ["gb", "wgs"]
    
    accession_files = [
    f"/pub/taxonomy/accession2taxid/nucl_{s}.accession2taxid.gz"
    for s in subsections
    ]

    taxdump_file = "/pub/taxonomy/taxdump.tar.gz"

    # =========================
    # DOWNLOAD ACCESSION MAPS
    # =========================
    if not (taxonomy_dir / "accmap.dlflag").exists():
        print("Downloading accession maps (parallel)")
        parallel_download(accession_files, taxonomy_dir, threads)

        # EXTRA opcional (não quebra se falhar)
        try:
            extra = "/pub/taxonomy/accession2taxid/nucl_wgs.accession2taxid.EXTRA.gz"
            download_one(extra, taxonomy_dir)
        except Exception:
            print("[INFO] EXTRA file not available")

        (taxonomy_dir / "accmap.dlflag").touch()
        print("[OK] Accession maps ready")

    # =========================
    # DOWNLOAD TAXDUMP
    # =========================
    if not (taxonomy_dir / "taxdump.dlflag").exists():
        print("Downloading taxonomy tree")
        download_one(taxdump_file, taxonomy_dir)
        (taxonomy_dir / "taxdump.dlflag").touch()

    # =========================
    # UNZIP accession maps
    # =========================
    gz_files = list(taxonomy_dir.glob("*accession2taxid.gz"))

    if gz_files:
        print("Uncompressing accession maps")
        for f in gz_files:
            run(["gunzip", str(f)], cwd=taxonomy_dir)

    # =========================
    # UNTAR taxdump
    # =========================
    if not (taxonomy_dir / "taxdump.untarflag").exists():
        print("Extracting taxonomy")
        run(["tar", "zxf", "taxdump.tar.gz"], cwd=taxonomy_dir)
        (taxonomy_dir / "taxdump.untarflag").touch()

    print("[DONE] Taxonomy ready")


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