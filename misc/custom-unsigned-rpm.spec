Name:           custom-unsigned-rpm
Version:        1
Release:        0.1%{?dist}
Summary:        Custom unsigned RPM

Group:          System Environment/Base
License:        GPLv3
URL:            http://www.redhat.com
BuildArch:      noarch

%description
custom unsigned rpm

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
touch $RPM_BUILD_ROOT/custom-unsigned-rpm

%files
/custom-unsigned-rpm

%changelog
