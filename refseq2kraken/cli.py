import argparse
import glob

from refseq2kraken.download import download_pipeline
from refseq2kraken.kraken import init_db, add_to_library, build_db
from refseq2kraken.utils import ensure_dir


def main():
    parser = argparse.ArgumentParser(
        prog="refseq2kraken",
        description=(
            "Pipeline: Download Taxonomy → RefSeq (NCBI) → add Kraken → Kraken2 Build\n\n"
            "Steps executed in order:\n"
            "  1) taxonomy   - download NCBI taxonomy\n"
            "  2) download   - download RefSeq sequences\n"
            "  3) add        - add sequences to Kraken2 DB\n"
            "  4) build      - build Kraken2 database\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    # ===== CORE =====
    parser.add_argument("--group", required=True, help="RefSeq group (ex: plant, fungi)")
    parser.add_argument("--db", required=True, help="Kraken DB path")
    parser.add_argument("--outdir", required=True, help="Output directory")

    # ===== PERFORMANCE =====
    parser.add_argument("--download-threads", type=int, default=6, help="Threads for download")
    parser.add_argument("--build-threads", type=int, default=32, help="Threads for build")

    # ===== CONTROL =====
    parser.add_argument("--skip-taxonomy", action="store_true", help="Skip taxonomy step")
    parser.add_argument("--skip-download", action="store_true", help="Skip download step")
    parser.add_argument("--skip-add", action="store_true", help="Skip add step")
    parser.add_argument("--skip-build", action="store_true", help="Skip build step")

    args = parser.parse_args()

    ensure_dir(args.outdir)

    fna_files = []

    # ===== 1. TAXONOMY =====
    if not args.skip_taxonomy:
        print("[1] taxonomy")
        init_db(args.db)

    # ===== 2. DOWNLOAD =====
    if not args.skip_download:
        print("[2] download")
        fna_files = download_pipeline(
            args.group,
            args.download_threads,
            args.outdir
        )

    # ===== 3. ADD =====
    if not args.skip_add:
        print("[3] add")
        if not fna_files:
            fna_files = glob.glob(f"{args.outdir}/*.fna")

        add_to_library(fna_files, args.db)

    # ===== 4. BUILD =====
    if not args.skip_build:
        print("[4] build")
        build_db(args.db, args.build_threads)

    print("\n[DONE]")


if __name__ == "__main__":
    main()