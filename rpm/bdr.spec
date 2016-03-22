#These must be the same as in the PostgreSQL RPM:
%{!?%packagename:%define packagename postgresql-bdr}
%{!?longname:%define longname postgresql}
%{!?shortname:%define shortname pgsql}
%{!?%majorversion:%define majorversion 9.4}
%{!?%shortmajorversion:%define shortmajorversion 94}

%{!?pgbaseinstdir:%define pgbaseinstdir /usr/%{shortname}-%{majorversion}}

# The version of the underlying PostgreSQL release we require, coresponding to
# Version: in the Pg RPM, and optionally the Release too.
%{!?required_pg:%define required_pg 9.4.6_bdr1}

# If you're building a git snapshot, you must set the githash macro so that
# the spec file will locate the correct tarball. If you're building a tagged
# final release you must instead set the gittag macro.
#
%define gittag bdr-plugin/0.9.3-2

# If you --define a githash or set it in a macro, adds it to the Release field:
%{?githash:%define releasegitsuffix _git%{githash}}

Name:		%{packagename}%{shortmajorversion}-bdr
Version:	0.9.3
Release:	2_2ndQuadrant%{?releasegitsuffix}%{?dist}
Summary:	BDR - Bi-Directional Replication for PostgreSQL

Group:		Applications/Databases
License:	PostgreSQL
URL:		http://2ndquadrant.com/bdr
Source0:	http://packages.2ndquadrant.com/postgresql-bdr94-2ndquadrant/tarballs/bdr-%{version}%{?githash:-git%{githash}}.tar.bz2
Source1:	http://packages.2ndquadrant.com/postgresql-bdr94-2ndquadrant/tarballs/bdr-%{version}%{?githash:-git%{githash}}.tar.bz2.md5

BuildRequires:	%{packagename}%{shortmajorversion}-devel%{?_isa} >= %{required_pg}
Requires:		%{packagename}%{shortmajorversion}%{?_isa} >= %{required_pg}
Requires:		%{packagename}%{shortmajorversion}-server%{?_isa} >= %{required_pg}
Requires:		%{packagename}%{shortmajorversion}-contrib%{?_isa} >= %{required_pg}
Conflicts:      %{packagename}%{shortmajorversion}-udr

BuildRequires:	autoconf
BuildRequires:  automake

# Unlike the UDR RPM, we don't need to Requires: postgresql-bdr94-devel's
# dependencies because they're properly declared by the package its self.

%description
%{packagename}%{shortmajorversion}-bdr installs the 'bdr' extension for bi-directional
asynchronous multi-master replication in PostgreSQL.

This package contains BDR %{version} built with PostgreSQL %{packagename}%{shortmajorversion} plus BDR support patches.

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
./configure --enable-bdr=yes
make -s %{?_smp_mflags} USE_PGXS=1

%install
export PATH=%{pgbaseinstdir}/bin:$PATH
make -s %{?_smp_mflags} USE_PGXS=1 DESTDIR=%{buildroot} install

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
* Tue Mar 22 2016 Craig Ringer <craig@2ndquadrant.com> 0.9.3-2_2ndQuadrant
- Rebuild for BDR-pg 9.4.6-1

* Tue Oct 20 2015 Craig Ringer <craig@2ndquadrant.com> 0.9.3-1_2ndQuadrant
- Release 0.9.3, requiring Pg 9.4.5_bdr1
- Bugfixes per release notes

* Mon Jul 6 2015 Craig Ringer <craig@2ndquadrant.com> 0.9.2-1_2ndQuadrant
- Release 0.9.2, requiring Pg 9.4.4_bdr1
- Bugfixes per release notes

* Tue May 26 2015 Craig Ringer <craig@2ndquadrant.com> 0.9.1-1_2ndQuadrant
- Release 0.9.1, requiring Pg 9.4.2_bdr1
- Bugfixes per release notes

* Tue Mar 24 2015 Craig Ringer <craig@2ndquadrant.com> 0.9.0-1_2ndQuadrant
- Release 0.9.0, requiring Pg 9.4.1_bdr2
- Dynamic configuration support in BDR

* Mon Feb 9 2015 Craig Ringer <craig@2ndquadrant.com> 0.8.0-2_2ndQuadrant
- Repackage with Pg 9.4.1_bdr1 as a requirement

* Sun Feb 8 2015 Craig Ringer <craig@2ndquadrant.com> 0.8.0-1_2ndQuadrant
- Update to BDR 0.8.0 final

* Wed Dec 24 2014 Craig Ringer <craig@2ndquadrant.com> 0.8.0beta1-1_2ndQuadrant
- Use configure script and autogen.sh
- Update to handle bundled bdr_dump, bdr_resetxlog
- Use bdr-%{version} filename pattern
- Large number of changes to BDR code its self, see the git logs

* Mon Sep 22 2014 Craig Ringer <craig@2ndquadrant.com> 0.7.2-1_2ndQuadrant
- Extract postgresql-bdr94-bdr into its own package after repository split.
