%{!?_with_teamcity: %define version 3.3.0}
%{!?_with_teamcity: %define release 1}

# git archive --format=tar --prefix="alerta-contrib-3.3.0/" HEAD | gzip > ~/rpmbuild/SOURCES/alerta-contrib-3.3.0.tar.gz

Name: alerta-contrib
Summary: Alerta monitoring contributions
Version: %{version}
Release: %{release}
Source0: alerta-contrib-%{version}.tar.gz
License: Apache License 2.0
Group: Utilities/System
BuildRoot: %{_tmppath}/alerta-contrib-%{version}-%{release}-buildroot
Prefix: /opt
BuildArch: x86_64
Vendor: Nick Satterly <nick.satterly@theguardian.com>
Url: https://github.com/alerta/alerta-contrib
BuildRequires: python-devel, python-setuptools, python-virtualenv
Requires: supervisor

%description
Alerta is a monitoring framework that consolidates alerts
from multiple sources like syslog, SNMP, Nagios, Riemann,
Zabbix, and displays them on an alert console.

%prep
%setup

%build
/usr/bin/virtualenv --no-site-packages alerta
alerta/bin/pip install -r requirements.txt --upgrade

alerta/bin/python monitors/dynect/setup.py install --single-version-externally-managed --root=/
alerta/bin/python monitors/pinger/setup.py install --single-version-externally-managed --root=/
alerta/bin/python monitors/snmptrap/setup.py install --single-version-externally-managed --root=/
alerta/bin/python monitors/syslog/setup.py install --single-version-externally-managed --root=/
alerta/bin/python monitors/urlmon/setup.py install --single-version-externally-managed --root=/

/usr/bin/virtualenv --relocatable alerta

%install
%__mkdir_p %{buildroot}/opt/alerta/bin
cp %{_builddir}/alerta-contrib-%{version}/alerta/bin/alerta* %{buildroot}/opt/alerta/bin/
cp %{_builddir}/alerta-contrib-%{version}/alerta/bin/python* %{buildroot}/opt/alerta/bin/
cp %{_builddir}/alerta-contrib-%{version}/alerta/bin/activate* %{buildroot}/opt/alerta/bin/
cp -r %{_builddir}/alerta-contrib-%{version}/alerta/lib %{buildroot}/opt/alerta/
%__install -m 0444 etc/alerta.conf.example %{buildroot}%{_sysconfdir}/alerta.conf
%__install -m 0444 etc/supervisord.conf.example %{buildroot}%{_sysconfdir}/supervisord.conf

prelink -u %{buildroot}/opt/alerta/bin/python

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/alerta.conf
%defattr(-,alerta,alerta)
/opt/alerta/bin/alerta*
%config(noreplace) %{_sysconfdir}/supervisord.conf
/opt/alerta/bin/python*
/opt/alerta/bin/activate*
/opt/alerta/lib/*

%pre
getent group alerta >/dev/null || groupadd -r alerta
getent passwd alerta >/dev/null || \
    useradd -r -g alerta -d /var/lib/alerta -s /sbin/nologin \
    -c "Alerta monitoring tool" alerta
exit 0

%changelog
* Wed Oct 14 2014 Nick Satterly <nick.satterly@theguardian.com> - 3.3.0-1
- Release 3.3