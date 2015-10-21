%global libname tracemalloc

Name:		python-%{libname}
Version:        1.2
Release:	1%{?dist}
Summary:	Debug tool to trace memory blocks allocated by Python.

Group:		python
License:	MIT
URL:		http://pytracemalloc.readthedocs.org/
Source0:	https://github.com/haypo/pytracemalloc/archive/pytracemalloc-1.2.tar.gz

BuildRequires:	python2-devel >= 2.7
Requires:	python2 >= 2.7

%description
The tracemalloc module is a debug tool to trace memory blocks allocated
 by Python. It provides the following information:

* Traceback where an object was allocated
* Statistics on allocated memory blocks per filename and per line number:
  total size, number and average size of allocated memory blocks
* Compute the differences between two snapshots to detect memory leaks

To trace most memory blocks allocated by Python, the module should be started as early
as possible by setting the PYTHONTRACEMALLOC environment variable to 1.
The tracemalloc.start() function can be called at runtime to start tracing Python memory
allocations.

The tracemalloc module has been integrated in Python 3.4.
This package provides backport to python 2.7.

%prep
%setup -q -n py%{libname}-py%{libname}-%{version}

%build
%{__python} setup.py build


%install
%{__python} setup.py install --root $RPM_BUILD_ROOT


%files
%{python_sitearch}/%{libname}.py*
%{python_sitearch}/py%{libname}-*-py*.egg-info
%attr(755, root, root) %{python_sitearch}/_%{libname}.so*

%changelog
* Wed Oct 21 2015 Francesco Romani <fromani@redhat.com> - 1.2
- Initial rpm release

