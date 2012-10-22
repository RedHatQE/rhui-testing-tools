Name:		rhui-testing-tools
Version:	0.1
Release:	1%{?dist}
Summary:	RHUI Testing library

Group:		Development/Python
License:	GPLv3+
URL:		https://github.com/RedHatQE/rhui-testing-tools
Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:  noarch

BuildRequires:	python-devel
Requires:	python-paramiko

%description

%prep
%setup -q

%build

%install
%{__python} setup.py install -O1 --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc LICENSE README.md
%attr(0755, root, root) %{_bindir}/*.py
%attr(0755, root, root) %{_bindir}/*.sh
%{python_sitelib}/*.egg-info
%{python_sitelib}/rhuilib/*.py
%{python_sitelib}/rhuilib/*.pyc
%{python_sitelib}/rhuilib/*.pyo
%{_datadir}/%name/cfn
%{_datadir}/%name/testing-data

%changelog
* Mon Oct 22 2012 Vitaly Kuznetsov <vitty@redhat.com> 0.1-1
- new package built with tito

