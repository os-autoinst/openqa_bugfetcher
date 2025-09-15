# spec file for package openqa_bugfetcher
#
# Copyright (c) 2025 SUSE LLC and contributors
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           openqa_bugfetcher
Version:        0.6.7
Release:        0
Summary:        Tool to update the openqa bug status cache
License:        GPL-3.0-only
Group:          Development/Languages/Python
URL:            https://github.com/os-autoinst/openqa_bugfetcher
Source:         %{name}-%{version}.tar.xz
BuildRequires:  python-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3-openqa_client
Requires:       python3-requests
Requires:       python3-simplejson
BuildArch:      noarch

%description
Python tool that will get a list of referenced bugs from openQA,
fetch the bug status of each bug from the corresponding bugtracker
and push the bug status back to openQA.

%prep
%setup -q -n openqa_bugfetcher-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot}

%files
%license LICENSE
%doc README.md
# You may have to add additional files here (documentation and binaries mostly)
%{_bindir}/fetch_openqa_bugs
%config(noreplace) %{_sysconfdir}/openqa/bugfetcher.conf
%dir %{_sysconfdir}/openqa
%{python3_sitelib}/openqa_bugfetcher/
%{python3_sitelib}/openqa_bugfetcher-*

%changelog
