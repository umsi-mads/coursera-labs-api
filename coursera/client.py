"""Coursera API Client."""

import os
import logging
import requests

from coursera_autograder.commands import oauth2
from coursera.credentials import Credentials
from coursera.refresher_auth import RefresherAuth
from coursera import API_ROOT


def filter_params(params, keys):
    """Raise if the params include extra invalid keys."""

    for key in params.keys():
        if key not in keys:
            raise ValueError(
                "{} is not a valid parameter for this function.".format(key)
            )


class Coursera:
    """Coursera API client."""

    def __init__(self):
        creds = Credentials(
            client_id=os.environ.get("COURSERA_CLIENT_ID"),
            client_secret=os.environ.get("COURSERA_CLIENT_SECRET"),
            scopes="view_profile access_course_authoring_api",
            refresh_token=os.environ.get("COURSERA_REFRESH_TOKEN_XXX"),
        )

        if creds.refresh_token:
            logging.info("Refresh token detected. Using CourseraRefresherAuth.")
            self.auth = RefresherAuth(creds)
        else:
            logging.info("Refresh token not detected. Using Coursera's OAuth server.")
            self.auth = oauth2.build_oauth2(creds).build_authorizer()

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
            "POST", "/v1/courses/{}/assets".format(course_id), body=params,
        )

    def get_asset(self, course_id, asset_id):
        """Get an asset for a course."""

        return self._authed_request(
            "GET", "/v1/courses/{}/assets/{}".format(course_id, asset_id),
        )

    def get_course(self, course_slug):
        """Get details of a course from its slug."""

        return self._authed_request(
            "GET", "/onDemandCourses.v1", params={"q": "slug", "slug": course_slug}
        )

    def get_images(self, course_id):
        """Get a list of images for a course."""

        return self._authed_request("GET", "/v1/courses/{}/labImages".format(course_id))

    def get_labs(self, course_id, image_id):
        """Get a list of labs using an image for a course."""

        return self._authed_request(
            "GET", "/v1/courses/{}/labImages/{}/labs".format(course_id, image_id),
        )

    def update_lab(self, course_id, image_id, lab_id, params=None):
        """Update the details of a lab."""

        if not params:
            params = {}

        filter_params(params, ["name", "description"])

        return self._authed_request(
            "UPDATE",
            "/v1/courses/{}/labImages/{}/labs/{}".format(course_id, image_id, lab_id),
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
            "/v1/courses/{}/labImages/{}/labs".format(course_id, image_id),
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
            "/v1/courses/{}/labImages/{}/labs".format(course_id, image_id),
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
            "/v1/courses/{}/labImages/{}/labs".format(course_id, image_id),
            body=params,
            params={"action": "asyncPublish", "labId": lab_id},
        )

    def get_lab_items(self, course_id, image_id, lab_id):
        """Get a list of items using a lab."""

        return self._authed_request(
            "GET",
            "/v1/courses/{}/labImages/{}/labs/{}/itemsUsingLab".format(
                course_id, image_id, lab_id
            ),
        )

    def _authed_request(self, method, path, *args, **kwargs):
        """Send a request with Coursera auth headers."""

        # Prefix all relative paths with the API_ROOT
        path = API_ROOT + path

        # Attach the auth argument to our request
        kwdict = dict(kwargs)
        kwdict["auth"] = self.auth

        # Convert our arguments into a request object
        req = requests.Request(method, path, *args, **kwdict).prepare()

        logging.debug(req.headers)

        # If we're submitting a body, it needs the application/json header.
        if "body" in kwargs:
            req.headers["Content-Type"] = "application/json"

        # Send the request!
        resp = requests.Session().send(req)

        if resp.status_code != 200:
            raise RuntimeError(
                "{} Error: {}".format(resp.status_code, resp.json()["message"])
            )

        return resp.json()["elements"]
