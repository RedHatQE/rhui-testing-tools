Name:		rhui-testing-tools
Version:	0.1
Release:	7%{?dist}
Summary:	RHUI Testing library

Group:		Development/Python
License:	GPLv3+
URL:		https://github.com/RedHatQE/rhui-testing-tools
Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:  noarch

BuildRequires:	python-devel
Requires:	python-paramiko python-nose PyYAML

%description

%prep
%setup -q

%build

%install
%{__python} setup.py install -O1 --root $RPM_BUILD_ROOT
%{__mkdir_p} $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc LICENSE README.md
%attr(0755, root, root) %{_bindir}/*.py
%attr(0755, root, root) %{_bindir}/*.sh
%config(noreplace) %attr(0600, root, root) %{_sysconfdir}/rhui_ec2.yaml
%{python_sitelib}/*.egg-info
%{python_sitelib}/rhuilib/*.py
%{python_sitelib}/rhuilib/*.pyc
%{python_sitelib}/rhuilib/*.pyo
%dir %{_datadir}/%name/rhui-tests
%{_datadir}/%name/testplans
%exclude %{_datadir}/%name/testplans/*/*.py?
%attr(0644, root, root) %{_datadir}/%name/rhui-tests/*.py
%exclude %{_datadir}/%name/rhui-tests/*.py?
%{_datadir}/%name/testing-data
%{_sharedstatedir}/%{name}

%changelog
* Tue Feb 19 2013 Vitaly Kuznetsov <vitty@redhat.com> 0.1-7
- RHUI-2.1.1

* Fri Nov 23 2012 Vitaly Kuznetsov <vitty@redhat.com> 0.1-6
- new tests (vitty@redhat.com)
- testplans (vitty@redhat.com)
- nitrate reporting (mkovacik@redhat.com)
- bugfixes and library improvements

* Tue Nov 13 2012 Vitaly Kuznetsov <vitty@redhat.com> 0.1-5
- new version

* Mon Nov 05 2012 Vitaly Kuznetsov <vitty@redhat.com> 0.1-4
- new tests and library improvements

* Thu Oct 25 2012 Vitaly Kuznetsov <vitty@redhat.com> 0.1-3
- use nose testing framework (vitty@redhat.com)

* Tue Oct 23 2012 Vitaly Kuznetsov <vitty@redhat.com> 0.1-2
- packaging: hot fixes (vitty@redhat.com)

* Mon Oct 22 2012 Vitaly Kuznetsov <vitty@redhat.com> 0.1-1
- new package built with tito
