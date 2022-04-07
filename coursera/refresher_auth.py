"""An authentication mechanism that only needs a refresh token."""

import logging
from datetime import datetime, timedelta

import requests

from coursera import ACCOUNT_ROOT


class RefresherAuth(requests.auth.AuthBase):
    """Authenticate requests based on your client account creds and a refresh token."""

    def __init__(self, creds):
        self.creds = creds
        self.access_token = None
        self.expires_at = 0

    def is_valid(self):
        """Do we have a valid access token?"""
        return self.access_token and datetime.now() < self.expires_at

    def refresh(self):
        """Fetch a fresh access token."""
        data = {
            "refresh_token": self.creds.refresh_token,
            "grant_type": "refresh_token",
            "client_id": self.creds.client_id,
            "client_secret": self.creds.client_secret,
            "redirect_uri": "http://localhost:9876/callback",
        }
        logging.debug("[POST] %s ? %s", ACCOUNT_ROOT + "/token", data)
        resp = requests.post(ACCOUNT_ROOT + "/token", data=data)
        if resp.status_code != 200:
            raise RuntimeError(
                "Unable to get a access token based on the supplied refresh token: [{}] {}".format(
                    resp.status_code, resp.json()["msg"]
                )
            )

        value = resp.json()
        self.access_token = value["access_token"]
        self.expires_at = datetime.now() + timedelta(seconds=value["expires_in"])
        return True

    def __call__(self, request):
        if not self.is_valid():
            self.refresh()

        request.headers["Authorization"] = "Bearer {}".format(self.access_token)
        return request

    def __repr__(self):
        return "<RefresherAuth token={} expires_at={}>".format(
            self.access_token, self.expires_at
        )
