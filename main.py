"""Coursera API Client."""

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

    creds = Credentials(
        # These credentials are published in the coursera_autograder repo.
        client_id="NS8qaSX18X_Eu0pyNbLsnA",
        client_secret="bUqKqGywnGXEJPFrcd4Jpw",
        scopes="view_profile manage_graders access_course_authoring_api",
    )
    auth = oauth2.build_oauth2(creds).build_authorizer()

    API_ROOT = "https://api.coursera.org/api/v1"

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

        resp = self._authed_request(
            "POST", "/courses/{}/assets".format(course_id), body=params,
        )

        return resp

    def get_asset(self, course_id, asset_id):
        """Get an asset for a course."""

        resp = self._authed_request(
            "GET", "/courses/{}/assets/{}".format(course_id, asset_id),
        )

        return resp

    def get_images(self, course_id):
        """Get a list of images for a course."""

        resp = self._authed_request("GET", "/courses/{}/labImages".format(course_id),)

        return resp

    def get_labs(self, course_id, image_id):
        """Get a list of labs using an image for a course."""

        resp = self._authed_request(
            "GET", "/courses/{}/labImages/{}/labs".format(course_id, image_id),
        )

        return resp

    def update_lab(self, course_id, image_id, lab_id, params=None):
        """Update the details of a lab."""

        if not params:
            params = {}

        filter_params(params, ["name", "description"])

        resp = self._authed_request(
            "UPDATE",
            "/courses/{}/labImages/{}/labs/{}".format(course_id, image_id, lab_id),
            body=params,
        )

        return resp

    def create_mount_point(self, course_id, image_id, lab_id, params=None):
        """Create or update a mount point for a lab."""

        if not params:
            params = {}

        filter_params(
            params, ["mountPath", "type", "newMountPath", "volumeArchiveAssetId"]
        )

        resp = self._authed_request(
            "POST",
            "/courses/{}/labImages/{}/labs".format(course_id, image_id),
            body=params,
            params={"action": "createOrPatchMountPoint", "labId": lab_id},
        )

        return resp

    def delete_mount_point(self, course_id, image_id, lab_id, params=None):
        """Delete a mount point for a lab."""

        if not params:
            params = {}

        filter_params(params, ["mountPath"])

        resp = self._authed_request(
            "POST",
            "/courses/{}/labImages/{}/labs".format(course_id, image_id),
            body=params,
            params={"action": "deleteMountPoint", "labId": lab_id},
        )

        return resp

    def async_publish_lab(self, course_id, image_id, lab_id, params=None):
        """Start publishing a lab asynchronously."""

        if not params:
            params = {}

        filter_params(params, ["publishType", "publishSummary"])

        resp = self._authed_request(
            "POST",
            "/courses/{}/labImages/{}/labs".format(course_id, image_id),
            body=params,
            params={"action": "asyncPublish", "labId": lab_id},
        )

        return resp

    def get_lab_items(self, course_id, image_id, lab_id):
        """Get a list of items using a lab."""

        resp = self._authed_request(
            "GET",
            "/courses/{}/labImages/{}/labs/{}/itemsUsingLab".format(
                course_id, image_id, lab_id
            ),
        )

        return resp

    def _authed_request(self, *args, **kwargs):
        """Send a request with Coursera auth headers."""

        arglist = list(args)
        arglist[1] = self.API_ROOT + arglist[1]
        kwdict = dict(kwargs)
        kwdict["auth"] = self.auth
        req = requests.Request(*arglist, **kwdict).prepare()
        return requests.Session().send(req)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    Coursera().get_images("ZQnMj8N9EemFBg6_bG2HQg")
