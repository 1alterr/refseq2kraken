import argparse
import glob

from refseq2kraken.download import download_pipeline
from refseq2kraken.kraken import init_db, add_to_library, build_db
from refseq2kraken.utils import ensure_dir


def main():
    parser = argparse.ArgumentParser(
        prog="refseq2kraken",
        description="Download Taxonomy → RefSeq → Kraken2 Build",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("--group", required=True, help="RefSeq group (ex: plant, fungi)")
    parser.add_argument("--db", required=True, help="Kraken DB path")
    parser.add_argument("--outdir", required=True, help="Output directory")

    parser.add_argument("--download-threads", type=int, default=6)
    parser.add_argument("--build-threads", type=int, default=32)

    parser.add_argument("--skip-init", action="store_true")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-add", action="store_true")
    parser.add_argument("--skip-build", action="store_true")

    args = parser.parse_args()

    ensure_dir(args.outdir)

    fna_files = []

    if not args.skip_init:
        init_db(args.db)

    if not args.skip_download:
        fna_files = download_pipeline(
            args.group,
            args.download_threads,
            args.outdir
        )

    if not args.skip_add:
        if not fna_files:
            fna_files = glob.glob(f"{args.outdir}/*.fna")

        add_to_library(fna_files, args.db)

    if not args.skip_build:
        build_db(args.db, args.build_threads)

    print("[DONE]")


if __name__ == "__main__":
    main()