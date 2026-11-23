"""Trusted local provisioning. Run python -m app.cli --help."""

import argparse
from getpass import getpass

from pydantic import TypeAdapter, ValidationError

from ledger_api.auth import Email, Registration, configured_service
from ledger_api.domain.errors import LedgerError
from ledger_api.repositories.users import UserRepository


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-admin")
    create.add_argument("--email", required=True)
    create.add_argument("--name", required=True)
    commands.add_parser("grant-admin").add_argument("--email", required=True)
    args = parser.parse_args(argv)
    try:
        email = TypeAdapter(Email).validate_python(args.email)
        service = configured_service()
        if args.command == "create-admin":
            data = Registration(
                email=email, name=args.name, password=getpass("New admin password: ")
            )
            service.register(data, role="ADMIN")
        else:
            with service.db.write_transaction() as conn:
                UserRepository(conn).grant_admin(email)
    except ValidationError:
        parser.exit(
            1,
            "Invalid email, name or password. Passwords must be 12 to 128 characters.\n",
        )
    except LedgerError as exc:
        parser.exit(1, f"{exc.code}: {exc}\n")
    print("Administrator provisioned.")


if __name__ == "__main__":
    main()
