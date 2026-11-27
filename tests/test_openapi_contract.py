from pathlib import Path

import yaml

from ledger_api.main import app


def test_documented_api_operations_match_implementation():
    specification = yaml.safe_load(
        Path("docs/openapi.yaml").read_text(encoding="utf-8")
    )

    methods = {"get", "post", "put", "patch", "delete"}

    documented = {
        (path, method)
        for path, operations in specification["paths"].items()
        for method, operation in operations.items()
        if method in methods
        and operation.get("x-implementation-status") != "planned"
        and path != "/app/"
    }

    implemented = {
        (path, method)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
        if method in methods
    }

    assert documented == implemented


def test_reconciliation_remains_planned():
    specification = yaml.safe_load(
        Path("docs/openapi.yaml").read_text(encoding="utf-8")
    )

    operation = specification["paths"]["/admin/reconciliation"]["get"]

    assert operation["x-implementation-status"] == "planned"