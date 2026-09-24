"""Issue fetcher for GNOME Bugzilla (bugzilla.gnome.org)."""

from typing import ClassVar

from openqa_bugfetcher.issues import BugzillaBaseIssue


class BugzillaGnomeIssue(BugzillaBaseIssue):
    """Fetch bug status from bugzilla.gnome.org."""

    prefixes: ClassVar[set] = {"bgo"}
    disabled_assigne = "@gnome.bugs"
    url = "https://bugzilla.gnome.org/jsonrpc.cgi"
