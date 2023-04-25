# coding=utf-8
"""
This script try to submit the zipped WSL app to Windows Store
Using the [API](https://learn.microsoft.com/en-us/windows/uwp/monetize/manage-app-submissions)
"""
import argparse
import datetime
import json
import logging
import os
import sys
import time
from string import Template
from typing import Optional

import humanize
import requests
from azure.storage.blob import BlobClient

# setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fmter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
ch.setFormatter(fmt=fmter)
logger.addHandler(ch)

REQUEST_TIMEOUT = 60


class SubmitPackage:
    """
    submit the wsl app
    """

    def __init__(self, tenantId: str, clientId: str, clientSecret: str) -> None:
        self.baseurl = tokenResource = "https://manage.devcenter.microsoft.com"
        tokenRequestBody = (
            f"grant_type=client_credentials&client_id={clientId}&"
            f"client_secret={clientSecret}&resource={tokenResource}"
        )
        tokenHeaders = {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        tokenResponse = requests.post(
            f"https://login.microsoftonline.com/{tenantId}/oauth2/token",
            data=tokenRequestBody,
            headers=tokenHeaders,
            timeout=REQUEST_TIMEOUT,
        )

        logger.info(
            f"get access token status: {tokenResponse.status_code} {tokenResponse.reason}"
        )
        tokenJson = tokenResponse.json()
        self._acess_token = tokenJson["access_token"]
        self._init = True

    def make_submit_body(self, metapath: str, templatepath: str):
        with open(metapath, encoding="utf-8") as meta:
            metadata = json.loads(meta.read())
            metadata["year"] = datetime.date.today().year
        with open(templatepath, encoding="utf-8") as template:
            content = "".join(template.readlines())
            t = Template(content)
            config = t.substitute(metadata)
        return json.loads(config)

    def get_app_info(self, release: str):
        if not self._init:
            sys.exit(1)
        headers = {
            "Authorization": "Bearer " + self._acess_token,
            "Content-type": "application/json",
            "User-Agent": "Python",
        }
        api = f"/v1.0/my/applications"
        appResponse = requests.get(
            f"{self.baseurl}{api}", headers=headers, timeout=REQUEST_TIMEOUT
        )

        logger.info(
            f"get {api} to get app info, status: {appResponse.status_code} {appResponse.reason}"
        )
        # Log correlation ID
        logger.info(appResponse.headers["MS-CorrelationId"])
        data = appResponse.json()
        for app in data["value"]:
            if app["primaryName"] == f"openEuler {release}":
                return app
        raise ValueError(f"no {release} found")

    def delete_exist_submission(self, submissionToRemove: str):
        if not self._init:
            sys.exit(1)
        headers = {
            "Authorization": "Bearer " + self._acess_token,
            "Content-type": "application/json",
            "User-Agent": "Python",
        }
        api = f"/v1.0/my/{submissionToRemove}"
        deleteSubmissionResponse = requests.delete(
            f"{self.baseurl}{api}", headers=headers, timeout=REQUEST_TIMEOUT
        )

        logger.info(
            f"delete {api} to delete pending submit, status: {deleteSubmissionResponse.status_code} {deleteSubmissionResponse.reason}",
        )
        # Log correlation ID
        logger.info(deleteSubmissionResponse.headers["MS-CorrelationId"])

    def create_submit(
        self, applicationId: str, appSubmissionRequestJson, zipFilePath: str
    ):
        """
        Do the submit process:
        1. create a submission
        2. fill the submission metadata
        3. upload blob file
        4. commit the submission
        5. wait the submission accepted/denied by server
        """
        headers = {
            "Authorization": "Bearer " + self._acess_token,
            "Content-type": "application/json",
            "User-Agent": "Python",
        }
        api = f"/v1.0/my/applications/{applicationId}/submissions"
        # Create submission
        createSubmissionResponse = requests.post(
            f"{self.baseurl}{api}", headers=headers, timeout=REQUEST_TIMEOUT
        )

        logger.info(
            f"post {api} to create submission, status: {createSubmissionResponse.status_code} {createSubmissionResponse.reason}"
        )
        # Log correlation ID
        logger.info(createSubmissionResponse.headers["MS-CorrelationId"])

        submissionJsonObject = createSubmissionResponse.json()
        if createSubmissionResponse.status_code >= 400:
            logger.error(submissionJsonObject)
            sys.exit(1)

        submissionId = submissionJsonObject["id"]
        fileUploadUrl = submissionJsonObject["fileUploadUrl"]

        if len(submissionJsonObject["applicationPackages"]) > 0:
            for package in submissionJsonObject["applicationPackages"]:
                logger.info(
                    f"package {package['fileName']} {package['fileStatus']} {package['version']} will be replaced"
                )
                package["fileStatus"] = "PendingDelete"

        appSubmissionRequestJson["applicationPackages"].extend(
            submissionJsonObject["applicationPackages"]
        )

        api = f"/v1.0/my/applications/{applicationId}/submissions/{submissionId}"
        # Update submission
        updateSubmissionResponse = requests.put(
            f"{self.baseurl}{api}",
            json.dumps(appSubmissionRequestJson).encode("utf-8"),
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        logger.info(
            f"put {api} to update submission, status: {updateSubmissionResponse.status_code} {updateSubmissionResponse.reason}"
        )
        # Log correlation ID
        logger.info(updateSubmissionResponse.headers["MS-CorrelationId"])

        updateSubmissionObject = updateSubmissionResponse.json()
        if updateSubmissionResponse.status_code >= 400:
            logger.error(updateSubmissionObject)
            sys.exit(1)

        size = os.stat(zipFilePath).st_size
        logger.info(
            f"begin to upload zip file({humanize.naturalsize(size)}): {zipFilePath} to {fileUploadUrl}"
        )
        # Upload images and packages in a zip file.
        blob_client = BlobClient.from_blob_url(fileUploadUrl)
        with open(zipFilePath, "rb") as data:
            blob_client.upload_blob(
                data, blob_type="BlockBlob", progress_hook=progress, length=size
            )

        logger.info("upload end")
        api = f"/v1.0/my/applications/{applicationId}/submissions/{submissionId}/commit"
        # Commit submission
        commitResponse = requests.post(
            f"{self.baseurl}{api}", headers=headers, timeout=REQUEST_TIMEOUT
        )

        logger.info(
            f"post {api} to commit submission, status: {commitResponse.status_code} {commitResponse.reason}"
        )
        # Log correlation ID
        logger.info(commitResponse.headers["MS-CorrelationId"])
        commitResponseObject = commitResponse.json()
        if commitResponse.status_code >= 400:
            logger.error(commitResponseObject)
            sys.exit(1)

        api = f"/v1.0/my/applications/{applicationId}/submissions/{submissionId}/status"
        # Pull submission status until commit process is completed
        getSubmissionStatusResponse = requests.get(
            f"{self.baseurl}{api}", headers=headers, timeout=REQUEST_TIMEOUT
        )

        submissionJsonObject = getSubmissionStatusResponse.json()
        while submissionJsonObject["status"] == "CommitStarted":
            time.sleep(60)
            getSubmissionStatusResponse = requests.get(
                f"{self.baseurl}{api}", headers=headers, timeout=REQUEST_TIMEOUT
            )
            submissionJsonObject = getSubmissionStatusResponse.json()
            logger.info(
                f"get {api} to grab commit status: {submissionJsonObject['status']}"
            )

        exitCode = 0
        logger.info(
            f"get commit status finished, final status: {submissionJsonObject['status']}"
        )
        if submissionJsonObject["statusDetails"]["errors"]:
            logger.error(submissionJsonObject)
            exitCode = 1

        return exitCode


def progress(current: int, total: Optional[int]):
    t = total if total else "0"
    logger.info(f"{humanize.naturalsize(current)}/{humanize.naturalsize(t)}")


def init_parser():
    new_parser = argparse.ArgumentParser(
        prog="submit.py",
        description="automate create a UWP app submission",
    )

    new_parser.add_argument("-c", "--client_id", help="azure AD applicaion client id")
    new_parser.add_argument("-t", "--tenant_id", help="azure AD user id")
    new_parser.add_argument(
        "-k", "--client_secret", help="azure AD application key secret"
    )
    new_parser.add_argument("-r", "--release", help="release number")
    new_parser.add_argument(
        "-m",
        "--meta",
        help="submission request template file, default to ./meta/{RELEASE}/meta.json",
    )
    new_parser.add_argument(
        "--template",
        default="template.json",
        help="submission request template, default to ./template.json",
    )
    new_parser.add_argument(
        "-f",
        "--zipfile",
        help="zip file path which contains intro images name as `release` and a appxupload bundle",
    )
    return new_parser


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args()

    if (
        not args.client_id
        or not args.tenant_id
        or not args.client_secret
        or not args.release
        or not args.zipfile
    ):
        parser.print_help()
        sys.exit(1)

    if not args.meta:
        args.meta = f"meta/{args.release}/meta.json"

    sp = SubmitPackage(args.tenant_id, args.client_id, args.client_secret)

    release_data = sp.get_app_info(args.release)

    if release_data and "pendingApplicationSubmission" in release_data:
        submissionToRemove = release_data["pendingApplicationSubmission"][
            "resourceLocation"
        ]
        sp.delete_exist_submission(submissionToRemove)

    requestBody = sp.make_submit_body(args.meta, args.template)
    sys.exit(sp.create_submit(release_data["id"], requestBody, args.zipfile))
