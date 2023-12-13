import requests

from openqa_bugfetcher.issues import BaseIssue


class ProgressIssue(BaseIssue):
    prefixes = {"poo"}

    def fetch(self, conf):
        issue_id = self.bugid.split("#")[1]
        url = f"https://progress.opensuse.org/issues/{issue_id}.json"
        req = requests.get(url, headers={"X-Redmine-API-Key": conf["progress"]["api_key"]}, timeout=60)
        if req.ok:
            data = req.json()["issue"]
            self.title = data["subject"]
            self.priority = data["priority"]["name"]
            self.assigned = "assigned_to" in data
            self.assignee = data["assigned_to"]["name"] if self.assigned else None
            self.status = data["status"]["name"]
            self.open = self.status not in ("Rejected", "Resolved", "Closed")
        else:
            assert req.status_code != 401, "Wrong auth for Progress"
            self.existing = False
