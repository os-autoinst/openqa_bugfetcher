"""Issue fetcher for SUSE Jira (jira.suse.com)."""

from http import HTTPStatus

import requests

from openqa_bugfetcher.issues import BaseIssue


class JiraIssue(BaseIssue):
    """Fetch issue status from jira.suse.com via the Jira REST API."""

    prefixes = {"jsc"}

    def fetch(self, conf):
        """Fetch issue status using basic auth credentials from config."""
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
            assert req.status_code != HTTPStatus.UNAUTHORIZED, "Wrong auth for Jira"
            self.existing = False
