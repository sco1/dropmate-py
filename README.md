# Dropmate-py
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
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
  audit       Audit a consolidated Dropmate log.
  audit-bulk  Audit a directory of consolidated Dropmate logs.
```
<!-- [[[end]]] -->

## Usage
### Environment Variables
The following environment variables are provided to help customize pipeline behaviors.

| Variable Name      | Description                       | Default      |
|--------------------|-----------------------------------|--------------|
| `PROMPT_START_DIR` | Start path for UI file/dir prompt | `'.'`        |

### `dropmate audit`
Process a consolidated Dropmate log CSV.
#### Input Parameters
| Parameter              | Description                                   | Type         | Default    |
|------------------------|-----------------------------------------------|--------------|------------|
| `--log-filepath`       | Path to Dropmate log CSV to parse.            | `Path\|None` | GUI Prompt |
| `--min-alt-loss`       | Threshold altitude delta.                     | `int`        | `200`      |
| `--min-firmware`       | Threshold firmware version.                   | `int\|float` | `5`        |
| `--time-delta-minutes` | Dropmate internal clock delta from real-time. | `int`        | `60`       |

### `dropmate audit-bulk`
Batch process a directory of consolidated Dropmate log CSVs.
#### Input Parameters
| Parameter              | Description                                   | Type         | Default    |
|------------------------|-----------------------------------------------|--------------|------------|
| `--log-dir`            | Path to Dropmate log directory to parse.      | `Path\|None` | GUI Prompt |
| `--log-pattern`        | Dropmate log file glob pattern.<sup>1,2</sup> | `str`        | `"*.csv"`  |
| `--min-alt-loss`       | Threshold altitude delta.                     | `int`        | `200`      |
| `--min-firmware`       | Threshold firmware version.                   | `int\|float` | `5`        |
| `--time-delta-minutes` | Dropmate internal clock delta from real-time. | `int`        | `60`       |

1. Case sensitivity is deferred to the host OS
2. Recursive globbing requires manual specification (e.g. `**/*.csv`)

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
