"""Coursera API Client."""

import os
from dataclasses import dataclass
import logging
import requests
from coursera_autograder.commands import oauth2


@dataclass
class Credentials:
    """Credentials object for use with OAuth initializer."""

    client_id: str
    client_secret: str
    scopes: str


def filter_params(params, keys):
    """Raise if the params include extra invalid keys."""

    for key in params.keys():
        if key not in keys:
            raise ValueError(
                "{} is not a valid parameter for this function.".format(key)
            )


class Coursera:
    """Coursera API client."""

    API_ROOT = "https://api.coursera.org/api/v1"

    def __init__(self):
        self.creds = Credentials(
            client_id=os.environ.get("COURSERA_CLIENT_ID"),
            client_secret=os.environ.get("COURSERA_CLIENT_SECRET"),
            scopes="view_profile access_course_authoring_api",
        )
        self.auth = oauth2.build_oauth2(self.creds).build_authorizer()

    def create_asset(self, course_id, params=None):
        """Create an asset for a course."""

        if not params:
            params = {}

        filter_params(
            params,
            [
                "filename",
                "url",
                "type",
                "languageCode",
                "videoTemplate",
                "runAsync",
                "callbackUrl",
                "callbackUrlToken",
            ],
        )

        return self._authed_request(
            "POST", "/courses/{}/assets".format(course_id), body=params,
        )

    def get_asset(self, course_id, asset_id):
        """Get an asset for a course."""

        return self._authed_request(
            "GET", "/courses/{}/assets/{}".format(course_id, asset_id),
        )

    def get_images(self, course_id):
        """Get a list of images for a course."""

        return self._authed_request("GET", "/courses/{}/labImages".format(course_id))

    def get_labs(self, course_id, image_id):
        """Get a list of labs using an image for a course."""

        return self._authed_request(
            "GET", "/courses/{}/labImages/{}/labs".format(course_id, image_id),
        )

    def update_lab(self, course_id, image_id, lab_id, params=None):
        """Update the details of a lab."""

        if not params:
            params = {}

        filter_params(params, ["name", "description"])

        return self._authed_request(
            "UPDATE",
            "/courses/{}/labImages/{}/labs/{}".format(course_id, image_id, lab_id),
            body=params,
        )

    def create_mount_point(self, course_id, image_id, lab_id, params=None):
        """Create or update a mount point for a lab."""

        if not params:
            params = {}

        filter_params(
            params, ["mountPath", "type", "newMountPath", "volumeArchiveAssetId"]
        )

        return self._authed_request(
            "POST",
            "/courses/{}/labImages/{}/labs".format(course_id, image_id),
            body=params,
            params={"action": "createOrPatchMountPoint", "labId": lab_id},
        )

    def delete_mount_point(self, course_id, image_id, lab_id, params=None):
        """Delete a mount point for a lab."""

        if not params:
            params = {}

        filter_params(params, ["mountPath"])

        return self._authed_request(
            "POST",
            "/courses/{}/labImages/{}/labs".format(course_id, image_id),
            body=params,
            params={"action": "deleteMountPoint", "labId": lab_id},
        )

    def async_publish_lab(self, course_id, image_id, lab_id, params=None):
        """Start publishing a lab asynchronously."""

        if not params:
            params = {}

        filter_params(params, ["publishType", "publishSummary"])

        return self._authed_request(
            "POST",
            "/courses/{}/labImages/{}/labs".format(course_id, image_id),
            body=params,
            params={"action": "asyncPublish", "labId": lab_id},
        )

    def get_lab_items(self, course_id, image_id, lab_id):
        """Get a list of items using a lab."""

        return self._authed_request(
            "GET",
            "/courses/{}/labImages/{}/labs/{}/itemsUsingLab".format(
                course_id, image_id, lab_id
            ),
        )

    def _authed_request(self, method, path, *args, **kwargs):
        """Send a request with Coursera auth headers."""

        # Prefix all relative paths with the API_ROOT
        path = self.API_ROOT + path

        # Attach the auth argument to our request
        kwdict = dict(kwargs)
        kwdict["auth"] = self.auth

        # Convert our arguments into a request object
        req = requests.Request(method, path, *args, **kwdict).prepare()

        # If we're submitting a body, it needs the application/json header.
        if "body" in kwargs:
            req.headers["Content-Type"] = "application/json"

        # Send the request!
        return requests.Session().send(req)


def main():
    logging.basicConfig(level=logging.DEBUG)
    resp = Coursera().get_images("cv72QmJBEeuSOhJSWorwXw")
    print(resp)
    print(resp.json())
    # Coursera().get_images("ZQnMj8N9EemFBg6_bG2HQg")


if __name__ == "__main__":
    main()
