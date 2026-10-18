# The torguapi Lambda layer: src/torguapi/*.py, packaged as python/torguapi/
# (the layout Lambda puts on sys.path, and the one consumers' unit tests
# unpack, e.g. njmunicipalities-api/scripts/fetch_torguapi.sh).
#
# Layer versions are immutable, and consumers pin a version number. Any change
# to the sources or to the package version in setup.cfg replaces the resource,
# which publishes a new version; skip_destroy keeps every old version (as
# RetentionPolicy: Retain did under SAM).
#
# The zip is built by scripts/build_layer.py (make layer), not archive_file:
# archive_file gives entries added from content no Unix file mode at all.

locals {
  src_dir   = "${path.module}/../src/torguapi"
  src_files = sort(fileset(local.src_dir, "*.py"))

  package_version = regex("(?m)^version\\s*=\\s*(\\S+)", file("${path.module}/../setup.cfg"))[0]

  # Hash of the sources rather than of the zip, so nothing about how the zip
  # is written (timestamps, compression) can publish a version by itself
  source_hash = sha256(join("\n", [
    for f in local.src_files : "${f} ${filesha256("${local.src_dir}/${f}")}"
  ]))

  layer_zip = "${path.module}/build/layer_torguapi.zip"
}

resource "aws_lambda_layer_version" "layer" {
  layer_name          = var.layer_name
  description         = "torguapi ${local.package_version}"
  filename            = local.layer_zip
  source_code_hash    = local.source_hash
  compatible_runtimes = ["python3.12"]
  skip_destroy        = true

  lifecycle {
    precondition {
      condition     = fileexists(local.layer_zip)
      error_message = "${local.layer_zip} is missing: run make layer first."
    }
  }
}
