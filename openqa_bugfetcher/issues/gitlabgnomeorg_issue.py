import html
import requests

from openqa_bugfetcher.issues import BaseIssue


class GitlabGnomeOrgIssue(BaseIssue):
    # Example: ggo#GNOME/gtk#6766
    prefixes = {"ggo"}

    def fetch(self, conf):
        repo, issue_id = self.bugid.split("#")[1:]
        if "personal_access_token" in conf["gitlab.gnome.org"]:

            url = f"https://gitlab.gnome.org/api/v4/issues?iids[]={issue_id}"
            cfg = conf["gitlab.gnome.org"]
            # curl --header "PRIVATE-TOKEN: <MY_PRIVATE_TOKEN>" https://gitlab.gnome.org/api/v4/issues?iids[]=6766
            headers = {"PRIVATE-TOKEN": cfg["personal_access_token"]}
            req = requests.get(url, headers=headers, timeout=60)
            data = req.json()
            assert data, "Empty JSON Object"
            bug = data[0]
            self.title = bug["title"]
            self.status = bug["state"]
            self.open = self.status in [
                "opened",
            ]
        else:
            # https://gitlab.gnome.org/GNOME/gtk/-/issues/6766
            url = f"https://gitlab.gnome.org/{repo}/-/issues/{issue_id}"
            req = requests.get(url, timeout=60)
            title = req.text.split("<title>", 1)[1].split("</title>", 1)[0]
            # Feature request: If there is only one printer, make it the default printer (#6766) · Issues · GNOME / gtk · GitLab # noqa: E501
            if title in ("Invalid Bug ID", "Search by bug number"):
                self.existing = False
            else:
                self.title = html.unescape(title.split(f" (#{issue_id}", 1)[0])
                # Can't find the status
                self.status = "UNKNOWN"
                self.open = True
