"""Coursera API Client."""

import os
import logging
import requests

from coursera_autograder.commands import oauth2

from . import API_ROOT
from .credentials import Credentials
from .refresher_auth import RefresherAuth
from .models import User, LabImage, Lab, ItemReference


def filter_params(params, keys):
    """Raise if the params include extra invalid keys."""

    for key in params.keys():
        if key not in keys:
            raise ValueError(
                "{} is not a valid parameter for this function.".format(key)
            )


class UnsupportedError(Exception):
    """This method is not currently supported, but is expected to be in the future."""


class Coursera:
    """Coursera API client."""

    def __init__(self):
        creds = Credentials(
            client_id=os.environ.get("COURSERA_CLIENT_ID"),
            client_secret=os.environ.get("COURSERA_CLIENT_SECRET"),
            refresh_token=os.environ.get("COURSERA_REFRESH_TOKEN"),
            scopes=os.environ.get(
                "COURSERA_SCOPES", "view_profile access_course_authoring_api"
            ),
        )

        if creds.refresh_token:
            logging.info("Refresh token detected. Using CourseraRefresherAuth.")
            auth = RefresherAuth(creds)
        else:
            logging.info("Refresh token not detected. Using Coursera's OAuth server.")
            auth = oauth2.build_oauth2(creds).build_authorizer()

        self.session = requests.Session()
        self.session.auth = auth

    def whoami(self) -> User:
        """Get your user profile."""

        return User(
            self.__request(
                "GET",
                "/externalBasicProfiles.v1",
                params={"q": "me", "fields": "name,timezone,locale,privacy"},
            )[0]
        )

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

        return self.__request(
            "POST", "/v1/courses/{}/assets".format(course_id), body=params,
        )

    def get_asset(self, course_id, asset_id):
        """Get an asset for a course."""

        return self.__request(
            "GET", "/v1/courses/{}/assets/{}".format(course_id, asset_id),
        )

    def get_course(self, course_slug):
        """Get details of a course from its slug."""

        raise UnsupportedError(
            "get_course({!r}) not currently supported".format(course_slug)
        )
        return self.__request(
            "GET", "/onDemandCourses.v1", params={"q": "slug", "slug": course_slug}
        )[0]

    def get_images(self, course_id) -> [LabImage]:
        """Get a list of images for a course."""

        resp = self.__request("GET", "/v1/courses/{}/labImages".format(course_id))

        return [LabImage(x) for x in resp]

    def get_labs(self, course_id, image_id) -> [Lab]:
        """Get a list of labs using an image for a course."""

        resp = self.__request(
            "GET", "/v1/courses/{}/labImages/{}/labs".format(course_id, image_id),
        )

        return [Lab(x) for x in resp]

    def update_lab(self, course_id, image_id, lab_id, params=None):
        """Update the details of a lab."""

        if not params:
            params = {}

        filter_params(params, ["name", "description"])

        return self.__request(
            "UPDATE",
            "/v1/courses/{}/labImages/{}/labs/{}".format(course_id, image_id, lab_id),
            body=params,
        )

    def get_lab_items(self, course_id, image_id, lab_id) -> [ItemReference]:
        """Get a list of items using a lab."""

        resp = self.__request(
            "GET",
            "/v1/courses/{}/labImages/{}/labs/{}/itemsUsingLab".format(
                course_id, image_id, lab_id
            ),
        )

        return [ItemReference(x) for x in resp]

    def create_mount_point(self, course_id, image_id, lab_id, params=None):
        """Create or update a mount point for a lab."""

        if not params:
            params = {}

        filter_params(
            params, ["mountPath", "type", "newMountPath", "volumeArchiveAssetId"]
        )

        return self.__request(
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

        return self.__request(
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

        return self.__request(
            "POST",
            "/v1/courses/{}/labImages/{}/labs".format(course_id, image_id),
            body=params,
            params={"action": "asyncPublish", "labId": lab_id},
        )

    def __request(self, method, path, *args, **kwargs):
        """Send a request with Coursera auth headers."""

        # Prefix all relative paths with the API_ROOT
        path = API_ROOT + path

        # If we're submitting a body, it needs the application/json header.
        if "body" in kwargs:
            kwargs["headers"]["Content-Type"] = "application/json"

        # Send the request!
        resp = self.session.request(method, path, *args, **kwargs)

        resp.raise_for_status()

        return resp.json()["elements"]
