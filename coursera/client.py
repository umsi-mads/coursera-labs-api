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
            **self.__request(
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

        return self.__request("POST", f"/v1/courses/{course_id}/assets", body=params)

    def get_asset(self, course_id, asset_id):
        """Get an asset for a course."""

        return self.__request("GET", f"/v1/courses/{course_id}/assets/{asset_id}")

    def get_course(self, course_slug):
        """Get details of a course from its slug."""

        raise UnsupportedError(f"get_course({course_slug!r}) not currently supported")
        return self.__request(
            "GET", "/onDemandCourses.v1", params={"q": "slug", "slug": course_slug}
        )[0]

    def get_images(self, course_id) -> [LabImage]:
        """Get a list of images for a course."""

        resp = self.__request("GET", f"/v1/courses/{course_id}/labImages")

        return [LabImage(id=x["id"], **x["labImage"]) for x in resp]

    def get_labs(self, course_id, image_id) -> [Lab]:
        """Get a list of labs using an image for a course."""

        resp = self.__request(
            "GET", f"/v1/courses/{course_id}/labImages/{image_id}/labs"
        )

        return [Lab(id=x["id"], **x["lab"]) for x in resp]

    def update_lab(self, course_id, image_id, lab_id, params=None):
        """Update the details of a lab."""

        if not params:
            params = {}

        filter_params(params, ["name", "description"])

        return self.__request(
            "UPDATE",
            f"/v1/courses/{course_id}/labImages/{image_id}/labs/{lab_id}",
            body=params,
        )

    def get_lab_items(self, course_id, image_id, lab_id) -> [ItemReference]:
        """Get a list of items using a lab."""

        resp = self.__request(
            "GET",
            f"/v1/courses/{course_id}/labImages/{image_id}/labs/{lab_id}/itemsUsingLab",
        )

        if resp:
            print(resp[0])
        return [ItemReference(**x) for x in resp]

    def create_mount_point(self, course_id, image_id, lab_id, params=None):
        """Create or update a mount point for a lab."""

        if not params:
            params = {}

        filter_params(
            params, ["mountPath", "type", "newMountPath", "volumeArchiveAssetId"]
        )

        return self.__request(
            "POST",
            f"/v1/courses/{course_id}/labImages/{image_id}/labs",
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
            f"/v1/courses/{course_id}/labImages/{image_id}/labs",
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
            f"/v1/courses/{course_id}/labImages/{image_id}/labs",
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
        logging.debug("[%s] %s ? %s", method, path, args)
        resp = self.session.request(method, path, *args, **kwargs)

        # TODO: Try to figure out how to more intelligently deal with this.
        # Sometimes I get a strange 400 error that suggests that it's a bad request,
        # but the details sound like it's an infra problem on Coursera's side:
        # HTTP/1.1 400 None
        #
        # {"errorCode":"Bad request.","message":"Course Authoring API:\nDownstream gRPC
        # error in coursera.proto.caapi.lab.v1beta1.CaLabAPI/GetLabs, RequestID:
        # Dze9K7abEeyAOQ6cF2Gznw, Reason: INVALID_ARGUMENT: httpStatus=400,
        # responseHeaders={content-length=[102], content-type=[application/json],
        # date=[Thu, 07 Apr 2022 17:49:23 GMT], server=[envoy],
        # x-coursera-envoy-path-routing-matched=[learningItems],
        # x-envoy-upstream-service-time=[469]},
        # responseBody='{\"errorCode\":null,\"message\":\"Workspace template  doesn't
        # have a instructor workspace.\",\"details\":null}', Source:
        # Instance[application: ca-api-application, image: ami-0c2103524b27197aa,
        # instance: i-0b86419af043a83d2, ip: 10.1.22.38, asg:
        # ca-api-application-vpcprod-55, env: vpcprod]","details":null}
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.error(
                "Recieved a bad response from Coursera: %s",
                resp.content.decode("utf-8"),
            )
            return []

        return resp.json()["elements"]
