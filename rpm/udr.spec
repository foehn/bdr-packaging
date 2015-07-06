# These must be the same as in the PostgreSQL RPM:
%{!?%packagename:%define packagename postgresql}
%{!?longname:%define longname postgresql}
%{!?shortname:%define shortname pgsql}
%{!?%majorversion:%define majorversion 9.4}
%{!?%shortmajorversion:%define shortmajorversion 94}

%{!?pgbaseinstdir:%define pgbaseinstdir /usr/%{shortname}-%{majorversion}}

# The version of the underlying PostgreSQL release we require, coresponding to
# Version: in the Pg RPM, and optionally the Release too.
%{!?required_pg:%define required_pg 9.4.2}

%define gittag bdr-plugin/0.9.2

# If you --define a githash or set it in a macro, adds it to the Release field:
%{?githash:%define releasegitsuffix _git%{githash}}

Name:		%{packagename}%{shortmajorversion}-udr
Version:	0.9.2
Release:	1_2ndQuadrant%{?releasegitsuffix}%{?dist}
Summary:	UDR - Uni-Directional Logical Replication for PostgreSQL

Group:		Applications/Databases
License:	PostgreSQL
URL:		http://2ndquadrant.com/bdr
Source0:	http://packages.2ndquadrant.com/postgresql-bdr94-2ndquadrant/tarballs/bdr-%{version}%{?githash:-git%{githash}}.tar.bz2
Source1:	http://packages.2ndquadrant.com/postgresql-bdr94-2ndquadrant/tarballs/bdr-%{version}%{?githash:-git%{githash}}.tar.bz2.md5

BuildRequires:	%{packagename}%{shortmajorversion}-devel%{?_isa} >= %{required_pg}
Requires:		%{packagename}%{shortmajorversion}%{?_isa} >= %{required_pg}
Requires:		%{packagename}%{shortmajorversion}-server%{?_isa} >= %{required_pg}
Requires:		%{packagename}%{shortmajorversion}-contrib%{?_isa} >= %{required_pg}
Conflicts:      %{packagename}%{shortmajorversion}-bdr

BuildRequires:	autoconf
BuildRequires:  automake

# These should match those in the PostgreSQL spec, as they're headers
# PostgreSQL exposes via includes in its own public headers, and/or or that
# pg_config will emit linker options to link to.
#
# These should actually be Requires: dependencies of postgresql94-devel, but
# they aren't; see http://www.postgresql.org/message-id/547C0032.7040309@2ndquadrant.com
#
BuildRequires:  openssl-devel
BuildRequires:  gettext >= 0.10.35
BuildRequires:  libxml2-devel libxslt-devel
BuildRequires:  pam-devel
BuildRequires:  readline-devel
BuildRequires:  zlib-devel >= 1.0.4

%description
%{packagename}%{shortmajorversion}-udr installs a unidirectional-only version of the 'bdr' extension,
called 'udr'.

This package contains UDR %{version} built with PostgreSQL %{packagename}%{shortmajorversion}.

%prep
# Enforce that you must set gittag or githash
%if "%{?gittag}" != "" && "%{?githash}" != ""
  %{error:Both %%gittag and %%githash set, bad spec file configuration. See README.md}
%else
  %if "%{?gittag}" == "" && "%{?githash}" == ""
    %{error:No %%gittag or %%githash set, bad spec file configuration. See README.md}
  %endif
%endif

%setup -q -n bdr-%{version}%{?releasegitsuffix}

%build
./autogen.sh
export PATH=%{pgbaseinstdir}/bin:$PATH
./configure --enable-bdr=no
make -s %{?_smp_mflags}

%install
export PATH=%{pgbaseinstdir}/bin:$PATH
make -s %{?_smp_mflags} DESTDIR=%{buildroot} install

%files
%{pgbaseinstdir}/bin/bdr_init_copy
%{pgbaseinstdir}/bin/bdr_initial_load
%{pgbaseinstdir}/bin/bdr_dump
%{pgbaseinstdir}/bin/bdr_resetxlog
%{pgbaseinstdir}/lib/bdr.so
%{pgbaseinstdir}/share/extension/bdr*
%doc %{_docdir}/%{shortname}/extension/README.bdr
%doc %{_docdir}/%{shortname}/extension/bdr.conf.sample

%changelog
* Mon Jul 6 2015 Craig Ringer <craig@2ndquadrant.com> 0.9.2-1_2ndQuadrant
- Release 0.9.2
- Bugfixes per release notes

* Tue May 26 2015 Craig Ringer <craig@2ndquadrant.com> 0.9.1-1_2ndQuadrant
- Release 0.9.1, requiring Pg 9.4.2_bdr1
- Bugfixes per release notes

* Tue Mar 24 2015 Craig Ringer <craig@2ndquadrant.com> 0.9.0-1_2ndQuadrant
- Release 0.9.0

* Mon Feb 9 2015 Craig Ringer <craig@2ndquadrant.com> 0.8.0-2_2ndQuadrant
- Re-package with PostgreSQL 9.4.1 as a requirement

* Sun Feb 8 2015 Craig Ringer <craig@2ndquadrant.com> 0.8.0-1_2ndQuadrant
- Update to BDR 0.8.0 final

* Wed Dec 24 2014 Craig Ringer <craig@2ndquadrant.com> 0.8.0beta1-1_2ndQuadrant
- First cut UDR package
