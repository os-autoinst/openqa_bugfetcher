import html
import requests

from openqa_bugfetcher.issues import BaseIssue


class DebianIssue(BaseIssue):
    prefixes = {"deb"}

    def fetch(self, conf):
        issue_id = self.bugid.split("#")[1]
        print(f"issue_id: {issue_id}")
        if issue_id == "0":
            self.title = "Dummy bug report, for automatic carry-over"
            self.priority = None
            self.assignee = None
            self.assigned = False
            self.open = False
            self.status = "dummy"
            self.resolution = None
            self.existing = True
        else:
            # Debian bug scraping using the URL
            url = f"https://bugs.debian.org/cgi-bin/bugreport.cgi?bug={issue_id}"
            req = requests.get(url, timeout=60)
            title = req.text.split("<h1>", 1)[1].split("<br>\n", 1)[1].split("</h1>", 1)[0]
            buginfo = req.text.split('<div class="buginfo">', 1)[1].split("</div>", 1)[0]
            if "Bug is archived." in buginfo:
                self.status = "archived"
            elif "<strong>Done:</strong>" in buginfo:
                self.status = "fixed"
            else:
                self.status = "open"
            if "There is no record of Bug" in req.text:
                self.existing = False
            else:
                self.title = html.unescape(title)
                self.open = self.status not in [
                    "archived",
                    "fixed",
                ]
