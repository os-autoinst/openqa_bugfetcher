#!/usr/bin/python3

from distutils.core import setup

setup(
    name="openqa_bugfetcher",
    version="0.7.0",
    license="GPLv3",
    description="Tool to update the openqa bug status cache",
    author="Dominik Heidler",
    author_email="dheidler@suse.de",
    requires=["openqa_client", "requests"],
    packages=["openqa_bugfetcher", "openqa_bugfetcher.issues"],
    scripts=["bin/fetch_openqa_bugs"],
    data_files=[
        ("/etc/openqa", ["bugfetcher.conf"]),
    ],
)
