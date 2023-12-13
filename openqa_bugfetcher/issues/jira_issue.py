import requests

from openqa_bugfetcher.issues import BaseIssue


class JiraIssue(BaseIssue):
    prefixes = {"jsc"}

    def fetch(self, conf):
        issue_id = self.bugid.split("#")[1]
        url = f"https://jira.suse.com/rest/api/2/issue/{issue_id}"
        cred = conf["jira"]
        req = requests.get(url, auth=(cred["user"], cred["pass"]), timeout=60)
        if req.ok:
            data = req.json()["fields"]
            self.title = data["summary"]
            self.priority = data["priority"]["name"]
            self.status = data["status"]["name"]
            self.open = self.status not in ("Rejected", "Resolved", "Closed")
        else:
            assert req.status_code != 401, "Wrong auth for Jira"
            self.existing = False
