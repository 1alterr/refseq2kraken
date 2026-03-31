import os
import subprocess
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


NCBI_FTP = "ftp://ftp.ncbi.nlm.nih.gov"
NCBI_RSYNC = "rsync://ftp.ncbi.nlm.nih.gov"


def run(cmd, cwd=None):
    print(f"[CMD] {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def md5sum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def read_md5(md5_file):
    with open(md5_file) as f:
        return f.read().split()[0]


def verify_md5(file_path, md5_path):
    print(f"[CHECK] {file_path.name}")
    expected = read_md5(md5_path)
    observed = md5sum(file_path)

    if expected != observed:
        print(f"[ERROR] MD5 mismatch for {file_path.name}")
        return False

    print(f"[OK] MD5 verified for {file_path.name}")
    return True


def download_one(file_path, outdir, use_ftp=True, retries=2):
    filename = os.path.basename(file_path)
    dest = Path(outdir) / filename
    md5_file = filename + ".md5"
    md5_dest = Path(outdir) / md5_file

    for attempt in range(retries + 1):

        # Skip if already valid
        if dest.exists() and md5_dest.exists():
            if verify_md5(dest, md5_dest):
                print(f"[SKIP] {filename} already valid")
                return

        try:
            # =========================
            # DOWNLOAD FILE + MD5
            # =========================
            if use_ftp:
                print(f"[FTP] {filename}")
                run(["wget", "-q", f"{NCBI_FTP}{file_path}"], cwd=outdir)
                run(["wget", "-q", f"{NCBI_FTP}{file_path}.md5"], cwd=outdir)
            else:
                print(f"[RSYNC] {filename}")
                run(["rsync", "--no-motd", f"{NCBI_RSYNC}{file_path}", "."], cwd=outdir)
                run(["rsync", "--no-motd", f"{NCBI_RSYNC}{file_path}.md5", "."], cwd=outdir)

            # =========================
            # VERIFY
            # =========================
            if verify_md5(dest, md5_dest):
                return
            else:
                raise Exception("MD5 failed")

        except Exception as e:
            print(f"[WARN] attempt {attempt+1} failed for {filename}: {e}")

            if dest.exists():
                dest.unlink()
            if md5_dest.exists():
                md5_dest.unlink()

            if attempt == retries:
                raise RuntimeError(f"Failed to download {filename}")


def parallel_download(files, outdir, threads=5):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(download_one, f, outdir)
            for f in files
        ]

        for future in as_completed(futures):
            future.result()


def init_db(db_path, threads=5, use_ftp=True):
    taxonomy_dir = Path(db_path) / "taxonomy"
    taxonomy_dir.mkdir(parents=True, exist_ok=True)

    print("[STEP] Initializing Kraken2 taxonomy DB")

    subsections = ["gb", "wgs"]
    
    accession_files = [
            f"/pub/taxonomy/accession2taxid/nucl_{s}.accession2taxid.gz"
            for s in subsections
    ]

    taxdump_file = "/pub/taxonomy/taxdump.tar.gz"

    # =========================
    # ACCESSION MAPS
    # =========================
    if not (taxonomy_dir / "accmap.dlflag").exists():
        print("[STEP] Downloading accession maps")
        parallel_download(accession_files, taxonomy_dir, threads)

        # EXTRA opcional
        try:
            extra = "/pub/taxonomy/accession2taxid/nucl_wgs.accession2taxid.EXTRA.gz"
            download_one(extra, taxonomy_dir)
        except Exception:
            print("[INFO] EXTRA not available")

        (taxonomy_dir / "accmap.dlflag").touch()

    # =========================
    # TAXDUMP
    # =========================
    if not (taxonomy_dir / "taxdump.dlflag").exists():
        print("[STEP] Downloading taxonomy tree")
        download_one(taxdump_file, taxonomy_dir)
        (taxonomy_dir / "taxdump.dlflag").touch()

    # =========================
    # UNZIP
    # =========================
    gz_files = list(taxonomy_dir.glob("*accession2taxid.gz"))

    if gz_files:
        print("[STEP] Uncompressing accession maps")
        for f in gz_files:
            run(["gunzip", str(f)], cwd=taxonomy_dir)

    # =========================
    # UNTAR
    # =========================
    if not (taxonomy_dir / "taxdump.untarflag").exists():
        print("[STEP] Extracting taxonomy")
        run(["tar", "zxf", "taxdump.tar.gz"], cwd=taxonomy_dir)
        (taxonomy_dir / "taxdump.untarflag").touch()

    print("[DONE] Taxonomy ready")

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