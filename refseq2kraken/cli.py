import typer
import glob

from refseq2kraken.download import download_pipeline
from refseq2kraken.kraken import init_db, add_to_library, build_db
from refseq2kraken.utils import ensure_dir

app = typer.Typer(
    help="RefSeq → Kraken2 pipeline",
    context_settings={"help_option_names": ["-h", "--help"]}
)

@app.command()
def run(
    group: str = typer.Option(..., help="RefSeq group (ex: plant, fungi)"),
    db: str = typer.Option(..., help="Kraken DB path"),
    outdir: str = typer.Option(..., help="Output directory"),
    download_threads: int = typer.Option(6, help="Download threads"),
    build_threads: int = typer.Option(32, help="Build threads"),
    skip_init: bool = typer.Option(False, help="Skip taxonomy download"),
    skip_download: bool = typer.Option(False, help="Skip download"),
    skip_add: bool = typer.Option(False, help="Skip add-to-library"),
    skip_build: bool = typer.Option(False, help="Skip build"),
):

    ensure_dir(outdir)

    fna_files = []

    # 1. INIT
    if not skip_init:
        init_db(db)

    # 2. DOWNLOAD
    if not skip_download:
        fna_files = download_pipeline(
            group,
            download_threads,
            outdir
        )

    # 3. ADD
    if not skip_add:
        if not fna_files:
            fna_files = glob.glob(f"{outdir}/*.fna")

        add_to_library(fna_files, db)

    # 4. BUILD
    if not skip_build:
        build_db(db, build_threads)

    print("[DONE]")