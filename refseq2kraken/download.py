import os
import requests
import gzip
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_FTP = "https://ftp.ncbi.nlm.nih.gov/genomes/refseq"


def download_file(url, out_path):
    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return out_path
    except Exception as e:
        print(f"[ERRO] {url}: {e}")
        return None


def gunzip_file(gz_path):
    try:
        out_path = gz_path.replace(".gz", "")
        with gzip.open(gz_path, "rb") as f_in:
            with open(out_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(gz_path)
        return out_path
    except Exception as e:
        print(f"[ERRO unzip] {gz_path}: {e}")
        return None


def fetch_urls(group, outdir):
    summary_url = f"{BASE_FTP}/{group}/assembly_summary.txt"
    summary_file = os.path.join(outdir, "assembly_summary.txt")

    if not os.path.exists(summary_file):
        print(f"Baixando assembly_summary para {group}...")
        download_file(summary_url, summary_file)

    urls = []
    with open(summary_file) as f:
        for line in f:
            if line.startswith("#"):
                continue
            cols = line.strip().split("\t")
            ftp_path = cols[19]
            if ftp_path == "na":
                continue

            fname = ftp_path.split("/")[-1] + "_genomic.fna.gz"
            urls.append(f"{ftp_path}/{fname}")

    return urls


def download_pipeline(group, threads, outdir):
    group_dir = os.path.join(outdir, group)
    os.makedirs(group_dir, exist_ok=True)

    urls = fetch_urls(group, group_dir)

    print(f"{group}: {len(urls)} genomas encontrados")
    print(f"Usando {threads} threads\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for url in urls:
            fname = url.split("/")[-1]
            out_path = os.path.join(group_dir, fname)
            futures.append(executor.submit(download_file, url, out_path))

        for future in as_completed(futures):
            gz_file = future.result()
            if gz_file:
                gunzip_file(gz_file)

    print(f"\n[OK] Download finalizado para {group}")