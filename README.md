# layer_torguapi

This is an AWS Lambda layer containing common code for APIs deployed at
`api.tor-gu.com`.

## Development

The layer itself has no third-party dependencies. To run the tests and the
`make` targets locally, create a virtual environment and install the
development requirements:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Then:

- `make test` runs the unit tests
- `make style` formats the code with isort and black
- `make build` builds the package
