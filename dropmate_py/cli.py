import os
from pathlib import Path

import click
import typer
from dotenv import load_dotenv
from sco1_misc.prompts import prompt_for_dir, prompt_for_file

from dropmate_py.audits import audit_pipeline
from dropmate_py.log_utils import consolidate_drop_records
from dropmate_py.parser import log_parse_pipeline, merge_dropmates

MIN_ALT_LOSS = 200  # feet
MIN_FIRMWARE = 5
MIN_TIME_DELTA_MINUTES = 60
MIN_DELTA_BETWEEN_MINUTES = 10

load_dotenv()
start_dir = os.environ.get("PROMPT_START_DIR", ".")
PROMPT_START_DIR = Path(start_dir)

dropmate_cli = typer.Typer(add_completion=False)


@dropmate_cli.command()
def audit(
    log_filepath: Path = typer.Option(None, exists=True, file_okay=True, dir_okay=False),
    min_alt_loss_ft: int = typer.Option(default=MIN_ALT_LOSS),
    min_firmware: float = typer.Option(default=MIN_FIRMWARE),
    internal_time_delta_minutes: int = typer.Option(default=MIN_TIME_DELTA_MINUTES),
    time_delta_between_minutes: int = typer.Option(default=MIN_DELTA_BETWEEN_MINUTES),
) -> None:
    """Audit a consolidated Dropmate log."""
    if log_filepath is None:
        try:
            log_filepath = prompt_for_file(
                title="Select Flight Log",
                start_dir=PROMPT_START_DIR,
                filetypes=[
                    ("Compiled Dropmate Logs", ("*.csv", ".txt")),
                    ("All Files", "*.*"),
                ],
            )
        except ValueError:
            raise click.ClickException("No file selected for processing, aborting.")

    conslidated_log = log_parse_pipeline(log_filepath)
    found_errs = audit_pipeline(
        consolidated_log=conslidated_log,
        min_alt_loss_ft=min_alt_loss_ft,
        min_firmware=min_firmware,
        max_scanned_time_delta_sec=internal_time_delta_minutes * 60,
        min_delta_to_next_sec=time_delta_between_minutes * 60,
    )

    print(f"Found {len(found_errs)} errors.")
    if found_errs:
        for err in found_errs:
            print(err)


@dropmate_cli.command()
def audit_bulk(
    log_dir: Path = typer.Option(None, exists=True, file_okay=False, dir_okay=True),
    log_pattern: str = typer.Option("*.csv"),
    min_alt_loss_ft: int = typer.Option(default=MIN_ALT_LOSS),
    min_firmware: float = typer.Option(default=MIN_FIRMWARE),
    internal_time_delta_minutes: int = typer.Option(default=MIN_TIME_DELTA_MINUTES),
    time_delta_between_minutes: int = typer.Option(default=MIN_DELTA_BETWEEN_MINUTES),
) -> None:
    """Audit a directory of consolidated Dropmate logs."""
    if log_dir is None:
        try:
            log_dir = prompt_for_dir(
                title="Select directory for batch processing", start_dir=PROMPT_START_DIR
            )
        except ValueError:
            raise click.ClickException("No directory selected for processing, aborting.")

    log_files = list(log_dir.glob(log_pattern))
    print(f"Found {len(log_files)} log files to process.")

    compiled_logs = log_parse_pipeline(log_files[0])
    for log_filepath in log_files[1:]:
        compiled_logs.extend(log_parse_pipeline(log_filepath))

    compiled_logs = merge_dropmates(compiled_logs)
    found_errs = audit_pipeline(
        consolidated_log=compiled_logs,
        min_alt_loss_ft=min_alt_loss_ft,
        min_firmware=min_firmware,
        max_scanned_time_delta_sec=internal_time_delta_minutes * 60,
        min_delta_to_next_sec=time_delta_between_minutes * 60,
    )

    print(f"Found {len(found_errs)} errors.")
    if found_errs:
        for err in found_errs:
            print(err)


@dropmate_cli.command()
def consolidate(
    log_dir: Path = typer.Option(None, exists=True, file_okay=False, dir_okay=True),
    log_pattern: str = typer.Option("dropmate_records_*"),
    out_filename: str = typer.Option("consolidated_dropmate_records.csv"),
) -> None:
    """Merge a directory of logs into a simplified drop record."""
    if log_dir is None:
        try:
            log_dir = prompt_for_dir(
                title="Select directory for batch processing", start_dir=PROMPT_START_DIR
            )
        except ValueError:
            raise click.ClickException("No directory selected for processing, aborting.")

    log_files = list(log_dir.glob(log_pattern))
    print(f"Found {len(log_files)} log files to consolidate.")

    out_filepath = log_dir / out_filename
    consolidated_records = consolidate_drop_records(
        log_dir=log_dir, log_pattern=log_pattern, out_filepath=out_filepath
    )

    print(f"Identified {len(consolidated_records)} unique drop records.")


if __name__ == "__main__":
    dropmate_cli()
