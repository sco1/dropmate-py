# Dropmate-py
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dropmate-py/1.0.0?logo=python&logoColor=FFD43B)](https://pypi.org/project/dropmate-py/)
[![PyPI](https://img.shields.io/pypi/v/dropmate-py?logo=Python&logoColor=FFD43B)](https://pypi.org/project/dropmate-py/)
[![PyPI - License](https://img.shields.io/pypi/l/dropmate-py?color=magenta)](https://github.com/sco1/dropmate-py/blob/main/LICENSE)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sco1/dropmate-py/main.svg)](https://results.pre-commit.ci/latest/github/sco1/dropmate-py/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

Python helpers for the [EDC Dropmate](https://earthlydynamics.com/dropmate/).

## Installation
Install by cloning this repository and installing into a virtual environment:

```bash
$ pip install .
```

You can confirm proper installation via the `dropmate` CLI:
<!-- [[[cog
import cog
from subprocess import PIPE, run
out = run(["dropmate", "--help"], stdout=PIPE, encoding="ascii")
cog.out(
    f"```bash\n$ dropmate --help\n{out.stdout.rstrip()}\n```"
)
]]] -->
```bash
$ dropmate --help
Usage: dropmate [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  audit        Audit a consolidated Dropmate log.
  audit-bulk   Audit a directory of consolidated Dropmate logs.
  consolidate  Merge a directory of logs into a simplified drop record.
```
<!-- [[[end]]] -->

## Usage
**NOTE:** All functionality assumes that log records have been provided by Dropmate app version 1.5.16 or newer. Prior versions may not contain all the necessary data columns to conduct the data audit, and there may also be column naming discrepancies between the iOS and Android apps.

### Supported Audits
The following audits are supported:

* Empty Drop Record
* Minimum Altitude Loss
* Minimum Time Between Drop Records
  * Time delta between the end of the previous drop record and the beginning of the next.
  * Short deltas may indicate that the previous drop record ended prematurely & restarted mid-air
* Minimum Dropmate Firmware Version
* Dropmate Internal Clock Drift
  * Measured as the delta between the scanning device's clock at scan time and the Dropmate's internal clock

### Environment Variables
The following environment variables are provided to help customize pipeline behaviors.

| Variable Name      | Description                       | Default      |
|--------------------|-----------------------------------|--------------|
| `PROMPT_START_DIR` | Start path for UI file/dir prompt | `'.'`        |

### `dropmate audit`
Process a consolidated Dropmate log CSV.
#### Input Parameters
| Parameter                       | Description                                                      | Type         | Default    |
|---------------------------------|------------------------------------------------------------------|--------------|------------|
| `--log-filepath`                | Path to Dropmate log CSV to parse.                               | `Path\|None` | GUI Prompt |
| `--min-alt-loss-ft`             | Threshold altitude delta, feet.                                  | `int`        | `200`      |
| `--min-firmware`                | Threshold firmware version.                                      | `int\|float` | `5`        |
| `--internal-time-delta-minutes` | Dropmate internal clock delta from real-time.                    | `int`        | `60`       |
| `--time-between-delta-minutes`  | Delta between the start of a drop record and end of the previous | `int`        | `10`       |

### `dropmate audit-bulk`
Batch process a directory of consolidated Dropmate log CSVs.
#### Input Parameters
| Parameter                       | Description                                                      | Type         | Default    |
|---------------------------------|------------------------------------------------------------------|--------------|------------|
| `--log-dir`                     | Path to Dropmate log directory to parse.                         | `Path\|None` | GUI Prompt |
| `--log-pattern`                 | Dropmate log file glob pattern.<sup>1,2</sup>                    | `str`        | `"*.csv"`  |
| `--min-alt-loss-ft`             | Threshold altitude delta, feet.                                  | `int`        | `200`      |
| `--min-firmware`                | Threshold firmware version.                                      | `int\|float` | `5`        |
| `--internal-time-delta-minutes` | Dropmate internal clock delta from real-time.                    | `int`        | `60`       |
| `--time-between-delta-minutes`  | Delta between the start of a drop record and end of the previous | `int`        | `10`       |

1. Case sensitivity is deferred to the host OS
2. Recursive globbing requires manual specification (e.g. `**/*.csv`)

### `dropmate consolidate`
Merge a directory of Dropmate app outputs into a deduplicated, simplified drop record.
#### Input Parameters
| Parameter        | Description                                   | Type         | Default                             |
|----------------- |-----------------------------------------------|--------------|-------------------------------------|
| `--log-dir`      | Path to Dropmate log directory to parse.      | `Path\|None` | GUI Prompt                          |
| `--log-pattern`  | Dropmate log file glob pattern.<sup>1,2</sup> | `str`        | `"dropmate_records_*"`              |
| `--out-filename` | Consolidated log filename.<sup>3</sup>        | `str`        | `consolidated_dropmate_records.csv` |

1. Case sensitivity is deferred to the host OS
2. Recursive globbing requires manual specification (e.g. `**/dropmate_records_*`)
3. Consolidate log will be written into the specified log directory; any existing file of the same name will be overwritten

## Contributing
**NOTE:** Due to deployment environment restrictions preventing the use of compiled libraries (e.g. Polars, Pandas/Numpy), tooling is intentionally limited to pure-Python implementations.
### Development Environment
This project uses [Poetry](https://python-poetry.org/) to manage dependencies. With your fork cloned to your local machine, you can install the project and its dependencies to create a development environment using:

```bash
$ poetry install
```

A [pre-commit](https://pre-commit.com) configuration is also provided to create a pre-commit hook so linting errors aren't committed:

```bash
$ pre-commit install
```

### Testing & Coverage
A [pytest](https://docs.pytest.org/en/latest/) suite is provided, with coverage reporting from [pytest-cov](https://github.com/pytest-dev/pytest-cov). A [tox](https://github.com/tox-dev/tox/) configuration is provided to test across all supported versions of Python. Testing will be skipped for Python versions that cannot be found.

```bash
$ tox
```

Details on missing coverage, including in the test suite, is provided in the report to allow the user to generate additional tests for full coverage.
