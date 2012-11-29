%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name:           python-iomock
Version:        0.1
Release:        1%{?dist}
Summary:        Python library for unit testing code that works with files

License:        GPLv2+
URL:            https://github.com/MarSik/python-iomock

# get the current source file using the following two commands
# git clone https://github.com/MarSik/python-iomock
# cd python-di; python setup.py sdist
# it will be in the dist directory
Source0:        http://pypi.python.org/packages/source/d/iomock/iomock-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-setuptools-devel
BuildRequires:  python-nose
BuildRequires:  python-di
Requires:       python-di
BuildArch:      noarch

%description
This python package provides an "iomock" module. 
It is intended to be used in unit testing environments.

%prep
%setup -q -n iomock-%{version}

# remove upstream egg-info
rm -rf *.egg-info


%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
rm -rf ${buildroot}%{python_sitelib}/setuptools/tests

%check
%{__python} setup.py nosetests

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{python_sitelib}/iomock
%{python_sitelib}/iomock-*.egg-info

%doc



%changelog
* Tue Nov 27 2012 Martin Sivak <msivak@euryale.brq.redhat.com> - 0.1-1
- Inital release

