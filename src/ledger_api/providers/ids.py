"""Production UUID provider."""

from uuid import uuid4


class UUIDProvider:
    def new_id(self) -> str:
        return str(uuid4())
