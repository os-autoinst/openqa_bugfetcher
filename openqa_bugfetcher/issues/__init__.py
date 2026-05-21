"""Base classes and issue fetcher registry for openqa_bugfetcher."""

import inspect
import json
import os
from abc import ABC, abstractmethod
from collections import OrderedDict
from http import HTTPStatus
from importlib import import_module

import requests

BUGZILLA_ERR_INVALID_BUG_ID = 101


class BaseIssue(ABC):
    """Abstract base class for all issue tracker implementations."""

    prefixes = set()

    def __init__(self, conf, bugid):
        """Initialize the issue and fetch its current status."""
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
        """Return the issue fields as a dict suitable for the openQA API."""
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
        """Fetch the issue status from the remote tracker and populate instance attributes."""
        pass


class BugzillaBaseIssue(BaseIssue):
    """Base class for Bugzilla-based issue trackers using the JSON-RPC API."""

    disabled_assigne = ""
    url = ""

    def fetch(self, conf):
        """Fetch bug status via the Bugzilla JSON-RPC API."""

        def json_rpc_get(url, method, params):
            get_params = OrderedDict({"method": method, "params": json.dumps([params])})
            return requests.get(url, params=get_params, timeout=60)

        issue_id = self.bugid.split("#")[1]
        req = json_rpc_get(self.url, "Bug.get", {"ids": [issue_id]})
        assert req.status_code != HTTPStatus.UNAUTHORIZED, "Wrong auth for Bugzilla"
        assert req.status_code != HTTPStatus.FORBIDDEN, "Insufficient permission to access this bug"
        assert req.ok
        data = req.json()
        if data["error"] and data["error"]["code"] == BUGZILLA_ERR_INVALID_BUG_ID:
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
    """Discovers and dispatches to the correct issue tracker implementation by bug ID prefix."""

    def __init__(self, conf):
        """Load all issue tracker plugins and build the prefix dispatch table."""
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
        """Return a populated issue object for the given bug ID."""
        assert "#" in bugid, f"Bad bugid format: {bugid}"
        prefix = bugid.split("#")[0].lower()
        assert prefix in self.prefix_table, f"No implementation found for {bugid}"
        return self.prefix_table[prefix](self.conf, bugid)
