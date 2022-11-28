# coding=utf-8
import http.client, json, requests, time
from azure.storage.blob import BlobClient
from string import Template

class SubmitPackage(object):
    def __init__(self, tenantId: str, clientId: str, clientSecret: str) -> None:
        self._ingestionConnection = http.client.HTTPSConnection("manage.devcenter.microsoft.com")
        #self._tokenEndpoint = "https://login.microsoftonline.com/{0}/oauth2/token"
        tokenResource = "https://manage.devcenter.microsoft.com"
        tokenRequestBody = "grant_type=client_credentials&client_id={0}&client_secret={1}&resource={2}".format(clientId, clientSecret, tokenResource)
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        tokenConnection = http.client.HTTPSConnection("login.microsoftonline.com")
        tokenConnection.request("POST", "/{0}/oauth2/token".format(tenantId), tokenRequestBody, headers=headers)
        tokenResponse = tokenConnection.getresponse()
        print(tokenResponse.status)
        tokenJson = json.loads(tokenResponse.read().decode())
        print(tokenJson["access_token"])
        self._acess_token = tokenJson["access_token"]
        tokenConnection.close()
        self._init = True

    #def make_submit_body(self, release, version, desc_en, desc_zh, copyright_en, copyright_zh, upload_file, image, releaseNotes_en, releaseNotes_zh, friendlyName):
    def make_submit_body(self, **kargs):
        data = dict(**kargs)
        with open("template.json") as template:
            content = ''.join(template.readlines())
            t = Template(content)
            config = t.substitute(data)
            print(config)
        return config

    def get_app_info(self, applicationId: str):
        if not self._init:
            return
        headers = {"Authorization": "Bearer " + self._acess_token,
                "Content-type": "application/json",
                "User-Agent": "Python"}
        #self._ingestionConnection = http.client.HTTPSConnection("manage.devcenter.microsoft.com")

        # Get application
        self._ingestionConnection.request("GET", "/v1.0/my/applications/{0}".format(applicationId), "", headers)
        appResponse = self._ingestionConnection.getresponse()
        print(appResponse.status)
        print(appResponse.headers["MS-CorrelationId"])  # Log correlation ID
        #print(json.loads(appResponse.read().decode()))
        return appResponse

    def delete_exist_submission(self, applicationId: str):
        if not self._init:
            return
        appResponse = self.get_app_info(applicationId)
        #self._ingestionConnection = http.client.HTTPSConnection("manage.devcenter.microsoft.com")
        headers = {"Authorization": "Bearer " + self._acess_token,
                "Content-type": "application/json",
                "User-Agent": "Python"}

        # Delete existing in-progress submission
        appJsonObject = json.loads(appResponse.read().decode())
        if "pendingApplicationSubmission" in appJsonObject :
            submissionToRemove = appJsonObject["pendingApplicationSubmission"]["resourceLocation"]
            self._ingestionConnection.request("DELETE", "/v1.0/my/{}".format(submissionToRemove), "", headers)
            deleteSubmissionResponse = self._ingestionConnection.getresponse()
            print('delete pending submit status: {}'.format(deleteSubmissionResponse.status))
            print(deleteSubmissionResponse.read().decode())
            print(deleteSubmissionResponse.headers["MS-CorrelationId"])  # Log correlation ID
            deleteSubmissionResponse.read()
        else:
            print("no pending submission")

    def create_submit(self, applicationId: str, appSubmissionRequestJson: str, zipFilePath: str):
        headers = {"Authorization": "Bearer " + self._acess_token,
                "Content-type": "application/json",
                "User-Agent": "Python"}

        # Create submission
        self._ingestionConnection.request("POST", "/v1.0/my/applications/{0}/submissions".format(applicationId), "", headers)
        createSubmissionResponse = self._ingestionConnection.getresponse()
        print(createSubmissionResponse.status)
        print(createSubmissionResponse.headers["MS-CorrelationId"])  # Log correlation ID

        submissionJsonObject = json.loads(createSubmissionResponse.read().decode())
        submissionId = submissionJsonObject["id"]
        fileUploadUrl = submissionJsonObject["fileUploadUrl"]
        print(submissionId)
        print(fileUploadUrl)

        # Update submission
        self._ingestionConnection.request("PUT", "/v1.0/my/applications/{0}/submissions/{1}".format(applicationId, submissionId), appSubmissionRequestJson.encode('utf-8'), headers)
        updateSubmissionResponse = self._ingestionConnection.getresponse()
        print('update submission status: {}'.format(updateSubmissionResponse.status))
        print(updateSubmissionResponse.read().decode())
        print(updateSubmissionResponse.headers["MS-CorrelationId"])  # Log correlation ID
        updateSubmissionResponse.read()

        return 
        # Upload images and packages in a zip file.
        blob_client = BlobClient.from_blob_url(fileUploadUrl)
        with open(zipFilePath, "rb") as data:
            blob_client.upload_blob(data, blob_type="BlockBlob")

        # Commit submission
        self._ingestionConnection.request("POST", "/v1.0/my/applications/{0}/submissions/{1}/commit".format(applicationId, submissionId), "", headers)
        commitResponse = self._ingestionConnection.getresponse()
        print(commitResponse.status)
        print(commitResponse.headers["MS-CorrelationId"])  # Log correlation ID
        print(commitResponse.read())

        # Pull submission status until commit process is completed
        self._ingestionConnection.request("GET", "/v1.0/my/applications/{0}/submissions/{1}/status".format(applicationId, submissionId), "", headers)
        getSubmissionStatusResponse = self._ingestionConnection.getresponse()
        submissionJsonObject = json.loads(getSubmissionStatusResponse.read().decode())
        while submissionJsonObject["status"] == "CommitStarted":
            time.sleep(60)
            self._ingestionConnection.request("GET", "/v1.0/my/applications/{0}/submissions/{1}/status".format(applicationId, submissionId), "", headers)
            getSubmissionStatusResponse = self._ingestionConnection.getresponse()
            submissionJsonObject = json.loads(getSubmissionStatusResponse.read().decode())
            print(submissionJsonObject["status"])

        print(submissionJsonObject["status"])
        print(submissionJsonObject)

        self._ingestionConnection.close()

if __name__ == '__main__':
    sp = SubmitPackage("36717d49-ab65-4442-954e-cf268f4099ed", "533545a1-0544-4558-b133-9bc20a5a9dd9", "WEd8Q~IDDcxpnCKLKislMmWrmJ5fBRezcXCv2aL7")
    #origin(sp._acess_token, "9P9RSPJDKX9G")
    #resp2003 = sp.get_app_info("9NWB78L1MPS2")
    #resp2203 = sp.get_app_info("9P9RSPJDKX9G")
    sp.delete_exist_submission("9P9RSPJDKX9G")
    req = sp.make_submit_body(release="openEuler 22.03", version="1.0.0.0", desc_en="test desc", desc_zh="测试描述", image="screen.png", upload_file="test.appxupload", copyright_en="test copyright", copyright_zh="测试授权", releasenote_en="test releasenote", releasenote_zh="中文发布纪要")
    sp.create_submit("9P9RSPJDKX9G", req, "test.zip")
    