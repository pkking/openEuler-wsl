# coding=utf-8
import http.client, json, requests, time
from azure.storage.blob import BlobClient
from string import Template
import argparse
import sys
import datetime
from typing import Optional
import humanize

class SubmitPackage(object):
    def __init__(self, tenantId: str, clientId: str, clientSecret: str) -> None:
        self._ingestionConnection = http.client.HTTPSConnection("manage.devcenter.microsoft.com")
        tokenResource = "https://manage.devcenter.microsoft.com"
        tokenRequestBody = "grant_type=client_credentials&client_id={0}&client_secret={1}&resource={2}".format(clientId, clientSecret, tokenResource)
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        tokenConnection = http.client.HTTPSConnection("login.microsoftonline.com")
        tokenConnection.request("POST", "/{0}/oauth2/token".format(tenantId), tokenRequestBody, headers=headers)
        tokenResponse = tokenConnection.getresponse()
        print('get access token status: {}'.format(tokenResponse.status))
        tokenJson = json.loads(tokenResponse.read().decode())
        self._acess_token = tokenJson["access_token"]
        tokenConnection.close()
        self._init = True

    def make_submit_body(self, metapath: str, templatepath: str):
        with open(metapath, encoding='utf-8') as meta:
            metadata = json.loads(meta.read())
            metadata['year'] = datetime.date.today().year
        with open(templatepath, encoding='utf-8') as template:
            content = ''.join(template.readlines())
            t = Template(content)
            config = t.substitute(metadata)
        return json.loads(config)

    def get_app_info(self, release: str):
        if not self._init:
            sys.exit(1)
        headers = {"Authorization": "Bearer " + self._acess_token,
                "Content-type": "application/json",
                "User-Agent": "Python"}

        self._ingestionConnection.request("GET", "/v1.0/my/applications", "", headers)
        appResponse = self._ingestionConnection.getresponse()
        print('get app info status: {}'.format(appResponse.status))
        print(appResponse.headers["MS-CorrelationId"])  # Log correlation ID
        data = json.loads(appResponse.read().decode())
        for app in data['value']:
            if app['primaryName'] == 'openEuler {}'.format(release):
                return app
        raise ValueError("no {} found".format(release))

    def delete_exist_submission(self, submissionToRemove: str):
        if not self._init:
            sys.exit(1)
        headers = {"Authorization": "Bearer " + self._acess_token,
                "Content-type": "application/json",
                "User-Agent": "Python"}
        self._ingestionConnection.request("DELETE", "/v1.0/my/{}".format(submissionToRemove), "", headers)
        deleteSubmissionResponse = self._ingestionConnection.getresponse()
        print('delete pending submit status: {}'.format(deleteSubmissionResponse.status))
        print(deleteSubmissionResponse.headers["MS-CorrelationId"])  # Log correlation ID
        deleteSubmissionResponse.read()

    def create_submit(self, applicationId: str, appSubmissionRequestJson, zipFilePath: str):
        headers = {"Authorization": "Bearer " + self._acess_token,
                "Content-type": "application/json",
                "User-Agent": "Python"}

        # Create submission
        self._ingestionConnection.request("POST", "/v1.0/my/applications/{0}/submissions".format(applicationId), "", headers)
        createSubmissionResponse = self._ingestionConnection.getresponse()
        print('create submission status: {} {}'.format(createSubmissionResponse.status, createSubmissionResponse.reason))
        print(createSubmissionResponse.headers["MS-CorrelationId"])  # Log correlation ID
        submissionJsonObject = json.loads(createSubmissionResponse.read().decode())
        if int(createSubmissionResponse.status) >= 400:
            print(submissionJsonObject)
            sys.exit(1) 
        submissionId = submissionJsonObject["id"]
        fileUploadUrl = submissionJsonObject["fileUploadUrl"]

        if len(submissionJsonObject['applicationPackages']) > 0:
            for package in submissionJsonObject['applicationPackages']:
                print('package {} {} {} will be replaced'.format(package['fileName'], package['fileStatus'], package['version']))
                package['fileStatus'] = 'PendingDelete'

        appSubmissionRequestJson['applicationPackages'].extend(submissionJsonObject['applicationPackages'])

        # Update submission
        self._ingestionConnection.request("PUT", "/v1.0/my/applications/{0}/submissions/{1}".format(applicationId, submissionId), json.dumps(appSubmissionRequestJson).encode('utf-8'), headers)
        updateSubmissionResponse = self._ingestionConnection.getresponse()
        print('update submission status: {} {}'.format(updateSubmissionResponse.status, updateSubmissionResponse.reason))
        print(updateSubmissionResponse.headers["MS-CorrelationId"])  # Log correlation ID
        updateSubmissionObject = json.loads(updateSubmissionResponse.read().decode())
        if updateSubmissionResponse.status >= 400:
            print(updateSubmissionObject)
            sys.exit(1)

        # Upload images and packages in a zip file.
        blob_client = BlobClient.from_blob_url(fileUploadUrl)
        with open(zipFilePath, "rb") as data:
            blob_client.upload_blob(data, blob_type="BlockBlob", progress_hook=progress)

        # Commit submission
        self._ingestionConnection.request("POST", "/v1.0/my/applications/{0}/submissions/{1}/commit".format(applicationId, submissionId), "", headers)
        commitResponse = self._ingestionConnection.getresponse()
        print('commit submission status: {}'.format(commitResponse.status))
        print(commitResponse.headers["MS-CorrelationId"])  # Log correlation ID
        commitResponseObject = json.loads(commitResponse.read().decode())
        if commitResponse.status >= 400:
            print(commitResponseObject)
            sys.exit(1)

        # Pull submission status until commit process is completed
        self._ingestionConnection.request("GET", "/v1.0/my/applications/{0}/submissions/{1}/status".format(applicationId, submissionId), "", headers)
        getSubmissionStatusResponse = self._ingestionConnection.getresponse()
        submissionJsonObject = json.loads(getSubmissionStatusResponse.read().decode())
        while submissionJsonObject["status"] == "CommitStarted":
            time.sleep(60)
            self._ingestionConnection.request("GET", "/v1.0/my/applications/{0}/submissions/{1}/status".format(applicationId, submissionId), "", headers)
            getSubmissionStatusResponse = self._ingestionConnection.getresponse()
            submissionJsonObject = json.loads(getSubmissionStatusResponse.read().decode())
            print('get commit status: {}'.format(submissionJsonObject["status"]))

        print('get commit status finished, final status: {}'.format(submissionJsonObject["status"]))
        print(submissionJsonObject)

        self._ingestionConnection.close()

def progress(current: int, total: Optional[int]):
    t = total if total else '0'
    print('{}/{}'.format(humanize.naturalsize(current), humanize.naturalsize(t)))

def init_parser():
    parser = argparse.ArgumentParser(
        prog = 'submit.py',
        description= 'automate create a UWP app submission',
    )

    parser.add_argument('-c', '--client_id', help="azure AD applicaion client id")
    parser.add_argument('-t', '--tenant_id', help="azure AD user id")
    parser.add_argument('-k', '--client_secret', help="azure AD application key secret")
    parser.add_argument('-r', '--release', help="release number")
    parser.add_argument('-m', '--meta', help="meta data file for submission request template")
    parser.add_argument('--template', default="template.json", help="submission request template, default to ./template.json")
    parser.add_argument('-f', '--zipfile', help="zip file path which contains intro images name as `release` and a appxupload bundle")
    return parser

if __name__ == '__main__':
    parser = init_parser()
    args = parser.parse_args()

    if not args.client_id or not args.tenant_id or not args.client_secret or not args.release or not args.zipfile:
        parser.print_help()
        sys.exit(1)

    if not args.meta:
        args.meta = 'meta/{}/meta.json'.format(args.release)
    
    sp = SubmitPackage(args.tenant_id, args.client_id, args.client_secret)
    
    data = sp.get_app_info(args.release)

    if data and "pendingApplicationSubmission" in data :
        submissionToRemove = data["pendingApplicationSubmission"]["resourceLocation"]
        sp.delete_exist_submission(submissionToRemove)

    requestBody = sp.make_submit_body(args.meta, args.template)
    sp.create_submit(data['id'], requestBody, args.zipfile)
    