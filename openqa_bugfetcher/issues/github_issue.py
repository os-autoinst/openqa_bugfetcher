"""Issue fetcher for GitHub issues via the GitHub REST API."""

from http import HTTPStatus

import requests

from openqa_bugfetcher.issues import BaseIssue


class GitHubIssue(BaseIssue):
    """Fetch issue status from the GitHub REST API."""

    prefixes = {"gh"}

    def fetch(self, conf):
        """Fetch issue status from api.github.com, using client credentials if configured."""
        try:
            repo, issue_id = self.bugid.split("#")[1:]
            url = f"https://api.github.com/repos/{repo}/issues/{issue_id}"
            auth = None
            if "client_id" in conf["github"] and "client_secret" in conf["github"]:
                auth = (conf["github"]["client_id"], conf["github"]["client_secret"])
            req = requests.get(url, auth=auth, timeout=60)
            assert req.status_code != HTTPStatus.FORBIDDEN, "Github ratelimiting"
            if req.ok:
                data = req.json()
                self.title = data["title"]
                self.assigned = bool(data["assignee"])
                self.assignee = data["assignee"]["login"] if self.assigned else None
                self.status = data["state"]
                self.open = self.status != "closed"
            else:
                self.existing = False
        except ValueError:
            self.existing = False
