%global skiptests   1

Name:    yetus
Version: 0.11.0
Release: 1%{?dist}
Summary: Libraries and tools for contributing and release processes for software projects
License: ASL 2.0 and MIT and OFL
URL:     https://yetus.apache.org/

ExclusiveArch: x86_64

Source0: https://archive.apache.org/dist/%{name}/%{version}/apache-%{name}-%{version}-src.tar.gz

Patch1: disable-modules-%{version}.patch 

BuildRequires: apache-parent
BuildRequires: maven-local
BuildRequires: maven-assembly-plugin
BuildRequires: maven-plugin-plugin
BuildRequires: jdiff
BuildRequires: maven-antrun-plugin

%description
Apache Yetus is a collection of libraries and tools that enable contribution 
and release processes for software projects.

Yetus helps community driven software projects improve their contribution and 
release processes by providing: A robust system for automatically checking new 
contributions against a variety of community accepted requirements. The means 
to document a well defined supported interface for downstream projects tooling 
to help release managers generate release documentation based on the information
provided by community issue trackers and source repositories

%package devel
Summary:       Development files for the %{name} library
Requires:      %{name}%{?_isa} = %{version}-%{release}
 
%description devel
Development files for the Apache Yetus library.

%prep
%autosetup -p1 -n %{name}-project-%{version}

%build
export MAVEN_HOME=/usr/share/xmvn
%mvn_build

%install

%make_install
# fedora guidelines no .a|.la
find %{buildroot} -name '*.a' -o -name '*.la' -delete

# Remove help scripts based on Python2
rm -f %{buildroot}%{_bindir}/mesos-cat
rm -f %{buildroot}%{_bindir}/mesos-ps
rm -f %{buildroot}%{_bindir}/mesos-scp
rm -f %{buildroot}%{_bindir}/mesos-tail

mkdir -p -m0755 %{buildroot}%{_bindir}
mkdir -p -m0755 %{buildroot}%{_sysconfdir}/default
mkdir -p -m0755 %{buildroot}%{_sysconfdir}/%{name}
mkdir -p -m0755 %{buildroot}%{_sysconfdir}/%{name}-master
mkdir -p -m0755 %{buildroot}%{_sysconfdir}/%{name}-agent
mkdir -p -m0755 %{buildroot}%{_tmpfilesdir}
mkdir -p -m0755 %{buildroot}/%{_localstatedir}/log/%{name}
mkdir -p -m0755 %{buildroot}/%{_sharedstatedir}/%{name}
mkdir -p -m0755 %{buildroot}%{_unitdir}/
mkdir -p -m0755 %{buildroot}%{_datadir}/java

echo zk://localhost:2181/mesos > %{buildroot}%{_sysconfdir}/mesos/zk
echo %{_var}/lib/%{name}       > %{buildroot}%{_sysconfdir}/mesos-master/work_dir
echo %{_var}/lib/%{name}       > %{buildroot}%{_sysconfdir}/mesos-agent/work_dir
echo 1                         > %{buildroot}%{_sysconfdir}/mesos-master/quorum

install -p -m 0755 %{SOURCE7} %{buildroot}%{_bindir}/
install -p -m 0644 %{SOURCE4} %{SOURCE5} %{SOURCE6} %{buildroot}%{_sysconfdir}/default
install -p -m 0644 %{SOURCE1} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -p -m 0644 %{SOURCE2} %{SOURCE3} %{buildroot}%{_unitdir}/
install -p -m 0644 src/java/target/mesos-*.jar %{buildroot}%{_datadir}/java/

make clean
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -raf src/examples/ %{buildroot}%{_datadir}/%{name}

# Remove examples based on Python2
find %{buildroot} -name '*.py' -delete

# Some files got mangling shebang, we fix them after everything else is done
for i in $(find %{buildroot} -type f -exec grep -Iq . {} \; -print);do
    for j in $(grep -l '^#!/usr/bin/env bash' $i);do 
        pathfix.py -pni "/usr/bin/bash" $j
    done
done

# remove shebang as in other template files.
sed -i 1d %{buildroot}/%{_sysconfdir}/%{name}/mesos-deploy-env.sh.template 

# remove zero length files
find %{buildroot} -size 0 -delete

# remove build time templates
find %{buildroot} -name '*.in' -delete

%files
%license LICENSE
%doc NOTICE
%{_libdir}/*.so
%{_libdir}/%{name}/modules/*.so
%{_bindir}/mesos*
%{_sbindir}/mesos-*
%{_datadir}/%{name}/
%exclude %{_datadir}/%{name}/examples
%{_libexecdir}/%{name}/
%{_tmpfilesdir}/%{name}.conf
%attr(0755,%{mesos_user},%{mesos_group}) %{_var}/log/%{name}/
%attr(0755,%{mesos_user},%{mesos_group}) %{_var}/lib/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}*
%config(noreplace) %{_sysconfdir}/default/%{name}*
%{_unitdir}/%{name}*.service

%files devel
%{_includedir}/%{name}
%{_includedir}/stout
%{_includedir}/process
%{_includedir}/csi
%{_libdir}/pkgconfig/%{name}.pc
%{_datadir}/java/%{name}-*.jar
%{_datadir}/%{name}/examples/*

%pre
getent group %{mesos_group} >/dev/null || groupadd -r %{mesos_group}
getent passwd %{mesos_user} >/dev/null || \
    useradd -r -g %{mesos_group} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
    -c "%{name} daemon account" %{mesos_user}
exit 0

%post
%systemd_post %{name}-slave.service %{name}-master.service

%preun
%systemd_preun %{name}-slave.service %{name}-master.service

%postun
%systemd_postun_with_restart %{name}-slave.service %{name}-master.service

%changelog
* Fri Sep 27 2019 Javi Roman <javiroman@apache.org> - 1.8.1-5
- Properly named mesos-generate-tarball ouput, and updated comment
  for noticing non-free code.

* Thu Sep 26 2019 Javi Roman <javiroman@apache.org> - 1.8.1-4
- Patent code sanity clean up with mesos-generate-tarball.sh helper

* Wed Sep 25 2019 Javi Roman <javiroman@apache.org> - 1.8.1-3
- Disable nvml.h usage according MESOS-9978

* Tue Sep 24 2019 Javi Roman <javiroman@apache.org> - 1.8.1-2
- Remove obsolete maven plugins: site and pgp

* Sat Sep 21 2019 Javi Roman <javiroman@apache.org> - 1.8.1-1
- Rebuilt for latest release, and rebooting the package with Apache Mesos
  Release based on ASF's official release infrastructure.

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.0-0.4ce5475.11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 0.23.0-0.4ce5475.10
- Rebuilt for switch to libxcrypt
