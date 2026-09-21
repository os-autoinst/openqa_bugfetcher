"""Issue fetcher for KDE Bugzilla (bugs.kde.org)."""

from typing import ClassVar

from openqa_bugfetcher.issues import BugzillaBaseIssue


class BugzillaKDEIssue(BugzillaBaseIssue):
    """Fetch bug status from bugs.kde.org."""

    prefixes: ClassVar[set] = {"kde"}
    disabled_assigne = "@kde.org"
    url = "https://bugs.kde.org/jsonrpc.cgi"
