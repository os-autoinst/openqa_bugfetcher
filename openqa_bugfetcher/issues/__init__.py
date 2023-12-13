from abc import ABC, abstractmethod
from collections import OrderedDict
from importlib import import_module
import inspect
import json
import os

import requests


class BaseIssue(ABC):
    prefixes = set()

    def __init__(self, conf, bugid):
        self.bugid = bugid
        self.title = None
        self.priority = None
        self.assigned = False
        self.assignee = None
        self.open = False
        self.status = None
        self.resolution = None
        self.existing = True
        self.fetch(conf)

    def get_dict(self):
        return {
            "title": self.title,
            "priority": self.priority,
            "assigned": int(self.assigned),
            "assignee": self.assignee,
            "open": int(self.open),
            "status": self.status,
            "resolution": self.resolution,
            "existing": int(self.existing),
        }

    @abstractmethod
    def fetch(self, conf):
        pass


class BugzillaBaseIssue(BaseIssue):
    disabled_assigne = ""
    url = ""

    def fetch(self, conf):
        def json_rpc_get(url, method, params):
            get_params = OrderedDict({"method": method, "params": json.dumps([params])})
            return requests.get(url, params=get_params, timeout=60)

        issue_id = self.bugid.split("#")[1]
        req = json_rpc_get(self.url, "Bug.get", {"ids": [issue_id]})
        assert req.status_code != 401, "Wrong auth for Bugzilla"
        assert req.status_code != 403, "Insufficient permission to access this bug"
        assert req.ok
        data = req.json()
        if data["error"] and data["error"]["code"] == 101:
            self.existing = False
        else:
            bug = data["result"]["bugs"][0]
            self.title = bug["summary"]
            self.priority = bug["priority"]
            self.assignee = bug["assigned_to"]
            self.assigned = not self.assignee.endswith(self.disabled_assigne)
            self.open = bool(bug["is_open"])
            self.status = bug["status"]
            self.resolution = bug.get("resolution")


class IssueFetcher:
    def __init__(self, conf):
        self.conf = conf
        self.prefix_table = {}
        for module in os.listdir(os.path.dirname(__file__)):
            if module == "__init__.py" or module[-3:] != ".py" or module == "__pycache__":
                continue
            plugin = import_module(f"openqa_bugfetcher.issues.{module[:-3]}")
            for _, obj in inspect.getmembers(plugin):
                if inspect.isclass(obj) and issubclass(obj, BaseIssue) and obj is not BaseIssue:
                    for prefix in obj.prefixes:
                        self.prefix_table[prefix] = obj

    def get_issue(self, bugid):
        assert "#" in bugid, f"Bad bugid format: {bugid}"
        prefix = bugid.split("#")[0].lower()
        assert prefix in self.prefix_table, f"No implementation found for {bugid}"
        return self.prefix_table[prefix](self.conf, bugid)
