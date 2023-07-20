import os
from pathlib import Path

import typer
from dotenv import load_dotenv
from sco1_misc.prompts import prompt_for_dir, prompt_for_file

MIN_ALT_LOSS = 200
MIN_FIRMWARE = 5
MIN_TIME_DELTA_MINUTES = 60

load_dotenv()
start_dir = os.environ.get("PROMPT_START_DIR", ".")
PROMPT_START_DIR = Path(start_dir)

dropmate_cli = typer.Typer(add_completion=False)


@dropmate_cli.command()
def audit(
    log_filepath: Path = typer.Option(exists=True, file_okay=True, dir_okay=False),
    min_alt_loss: int = typer.Option(default=MIN_ALT_LOSS),
    min_firmware: float = typer.Option(default=MIN_FIRMWARE),
    time_delta_minutes: int = typer.Option(default=MIN_TIME_DELTA_MINUTES),
) -> None:
    """Audit a consolidated Dropmate log."""
    if log_filepath is None:
        log_filepath = prompt_for_file(
            title="Select Flight Log",
            start_dir=PROMPT_START_DIR,
            filetypes=[
                ("Compiled Dropmate Logs", "*.csv"),
                ("All Files", "*.*"),
            ],
        )

    raise NotImplementedError


@dropmate_cli.command()
def audit_bulk(
    log_dir: Path = typer.Option(exists=True, file_okay=False, dir_okay=True),
    log_pattern: str = typer.Option("*.csv"),
    min_alt_loss: int = typer.Option(default=MIN_ALT_LOSS),
    min_firmware: float = typer.Option(default=MIN_FIRMWARE),
    time_delta_minutes: int = typer.Option(default=MIN_TIME_DELTA_MINUTES),
) -> None:
    """Audit a directory of consolidated Dropmate logs."""
    if log_dir is None:
        log_dir = prompt_for_dir(
            title="Select directory for batch processing", start_dir=PROMPT_START_DIR
        )

    raise NotImplementedError


if __name__ == "__main__":
    dropmate_cli()
