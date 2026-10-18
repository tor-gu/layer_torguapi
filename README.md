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

## Deployment

The layer is published by GitHub Actions (`.github/workflows/deploy.yml`) with
Terraform (`infra/`):

- Push to `dev`: runs the unit tests and a `terraform plan`, which is shown in
  the run's summary. Nothing is published.
- Merge to `main`: the same, then waits for approval in the GitHub `prod`
  environment. After approval, `terraform apply` publishes a new layer version.

The layer zip is built by `make layer` (`scripts/build_layer.py`), which the
workflow runs before Terraform. Run it yourself before a local
`terraform plan` in `infra/`.

A new version is published only when a file in `src/torguapi/` or the version
in `setup.cfg` changes. Old versions are never deleted. Each version's
description shows the package version (e.g. `torguapi 0.3.0`), so to find the
layer version for a release:

```sh
aws lambda list-layer-versions --layer-name layer_torguapi \
    --query 'LayerVersions[].[Version,Description]' --output text
```

Consumers pin a version (`arn:aws:lambda:us-east-1:490461464130:layer:layer_torguapi:<version>`)
and move to a new one deliberately.

The workflow's AWS roles are in `infra/github/`, which is applied by hand:

```sh
cd infra/github
terraform init -backend-config=backend.hcl
terraform apply
```
