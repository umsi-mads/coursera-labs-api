"""An object for grouping credential info."""

from dataclasses import dataclass


@dataclass
class Credentials:
    """Credentials object for use with OAuth initializer."""

    client_id: str
    client_secret: str
    scopes: str
    refresh_token: str
