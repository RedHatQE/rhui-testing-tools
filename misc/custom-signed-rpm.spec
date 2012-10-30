Name:           custom-signed-rpm
Version:        1
Release:        0.1%{?dist}
Summary:        Custom signed RPM

Group:          System Environment/Base
License:        GPLv3
URL:            http://www.redhat.com
BuildArch:      noarch

%description
custom signed rpm

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
touch $RPM_BUILD_ROOT/custom-signed-rpm

%files
/custom-signed-rpm

%changelog
