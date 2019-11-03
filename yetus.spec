%global debug_package %{nil}

Name:    yetus
Version: 0.11.0
Release: 1%{?dist}
Summary: Libraries and tools for contributing and release processes for software projects
License: ASL 2.0 and MIT and OFL
URL:     https://yetus.apache.org/

ExclusiveArch: x86_64

Source0: https://archive.apache.org/dist/%{name}/%{version}/apache-%{name}-%{version}-src.tar.gz
Source1: audience-annotations-pom-template.xml
Source2: audience-annotations-jdiff-pom-template.xml

Patch1: disable-modules-%{version}.patch 

BuildRequires: apache-parent
BuildRequires: maven-local
BuildRequires: maven-assembly-plugin
BuildRequires: jdiff

%description
Apache Yetus is a collection of libraries and tools that enable contribution 
and release processes for software projects.

Yetus helps community driven software projects improve their contribution and 
release processes by providing: A robust system for automatically checking new 
contributions against a variety of community accepted requirements. The means 
to document a well defined supported interface for downstream projects tooling 
to help release managers generate release documentation based on the information
provided by community issue trackers and source repositories

%package javadoc
Summary: Javadoc for %{name}

%description javadoc
This package contains javadoc for %{name}.

%prep
%autosetup -p1 -n %{name}-project-%{version}

%build
export MAVEN_HOME=/usr/share/xmvn
%mvn_build --skip-install

%install
%mvn_install

mkdir -p %{buildroot}%{_javadir}
install -pm 644 \
	audience-annotations-component/audience-annotations/target/audience-annotations-%{version}.jar \
	%{buildroot}%{_javadir}/audience-annotations.jar
install -pm 644 \
        audience-annotations-component/audience-annotations-jdiff/target/audience-annotations-jdiff-%{version}.jar \
	%{buildroot}%{_javadir}/audience-annotations-jdiff.jar

mkdir -p %{buildroot}%{_mavenpomdir}
install -pm 644 %{SOURCE1} %{buildroot}%{_mavenpomdir}/JPP-audience-annotations.pom
install -pm 644 %{SOURCE2} %{buildroot}%{_mavenpomdir}/JPP-audience-annotations-jdiff.pom
sed -i "s|@version@|%{version}|" %{buildroot}%{_mavenpomdir}/JPP-audience-annotations.pom
sed -i "s|@version@|%{version}|" %{buildroot}%{_mavenpomdir}/JPP-audience-annotations-jdiff.pom
%add_maven_depmap JPP-audience-annotations.pom audience-annotations.jar
%add_maven_depmap JPP-audience-annotations-jdiff.pom audience-annotations-jdiff.jar

%files
%license LICENSE
%doc NOTICE
%{_javadir}/*.jar
%{_mavenpomdir}/*
%{_datadir}/maven-metadata/*

%files javadoc
%{_javadocdir}/%{name}

%changelog
* Sun Nov 03 2019 Javi Roman <javiroman@apache.org> - 0.11.0-1
- New Apache Yetus package

