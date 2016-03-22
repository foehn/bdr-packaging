# Conventions for PostgreSQL Global Development Group RPM releases:

# Official PostgreSQL Development Group RPMS have a PGDG after the release number.
# Integer releases are stable -- 0.1.x releases are Pre-releases, and x.y are
# test releases.

# Pre-releases are those that are built from CVS snapshots or pre-release
# tarballs from postgresql.org.  Official beta releases are not
# considered pre-releases, nor are release candidates, as their beta or
# release candidate status is reflected in the version of the tarball. Pre-
# releases' versions do not change -- the pre-release tarball of 7.0.3, for
# example, has the same tarball version as the final official release of 7.0.3:
# but the tarball is different.

# Test releases are where PostgreSQL itself is not in beta, but certain parts of
# the RPM packaging (such as the spec file, the initscript, etc) are in beta.

# Pre-release RPM's should not be put up on the public ftp.postgresql.org server
# -- only test releases or full releases should be.
# This is the PostgreSQL Global Development Group Official RPMset spec file,
# or a derivative thereof.
# Copyright 2003-2014 Devrim GÜNDÜZ <devrim@gunduz.org>
# and others listed.

# Major Contributors:
# ---------------
# Lamar Owen
# Tom Lane
# Jeff Frost
# Peter Eisentraut
# Alvaro Herrera
# David Fetter
# Greg Smith
# Craig Ringer
# and others in the Changelog....

# This spec file and ancilliary files are licensed in accordance with 
# The PostgreSQL license.

# In this file you can find the default build package list macros.  These can be overridden by defining
# on the rpm command line:
# rpm --define 'packagename 1' .... to force the package to build.
# rpm --define 'packagename 0' .... to force the package NOT to build.
# The base package, the lib package, the devel package, and the server package always get built.

# If this is a beta or test build, we don't strip debuginfo and will
# pass extra cflags to configure.
%define beta 0
%{?beta:%define __os_install_post /usr/lib/rpm/brp-compress}


# Version and name
# ----------------

# Release identifier for the BDR patchset revision on top of this PostgreSQL
# release. Corresponds to the tag, e.g. bdr-pg/REL9_4_1-2 has pgbdrrelease 2.
%define pgbdrrelease 1

# If building a tagged release, set % gittag to the full tag name. If building
# a git snapshot, set % githash. One of the two MUST be set.
#
%define gittag bdr-pg/REL9_4_6-1

# packagename sets the name of the package. Unsurprisingly.
#
# Don't define files that depend on the 'name' or 'packagename' macros, they're
# exclusively for use in requires/depends declarations and package metadata.
%{!?%packagename:%define packagename postgresql-bdr}

# These values control locations and names of installed components - the
# default datadir, unit names, base installation directory, etc; see the
# scripts for details of usage.
#
# Note that the 'name' macro uses packagename, not longname, so it should
# not be used for file naming. Use {longname}{shortmajorversion} instead.
#
%{!?longname:%define longname postgresql}
%{!?shortname:%define shortname pgsql}
%{!?%majorversion:%define majorversion 9.4}
%{!?%shortmajorversion:%define shortmajorversion 94}

# If set, prevmajorversion is used when running pg_upgrade in the setup script.
# If it's the empty string or unset the user will have to specify what to
# upgrade from when running the setup script.
#
# Commenting this out won't work, you must set it to % {null} (without the space)
# if you want it empty.
#
%{!?prevmajorversion:%define prevmajorversion %{null}}

# The short description appears in initscripts etc
%{!?shortserverdescription:%define shortserverdescription PostgreSQL %{majorversion} database server with BDR}

# File locations
# --------------

# Install root for executables, plugins, etc. Pg doesn't follow the FHS
# for a number of reasons - parallel installs of different versions,
# avoiding conflict with plugin installs, etc.
%{!?pgbaseinstdir:%define pgbaseinstdir /usr/%{shortname}-%{majorversion}}

# BDR: OVERRIDE pgvarlib location to ensure datadir doesn't conflict
%define pgvarlib %{_sharedstatedir}/%{shortname}/%{majorversion}-bdr

# The dir within which all this Pg install's data files live - main datadir,
# backup files, etc. Usually /var/lib/pgsql/9.4 or similar.
%{!?pgvarlib:%define pgvarlib %{_sharedstatedir}/%{shortname}/%{majorversion}}

# The main datadir location and 'backups' dir location
%{!?pgdatadir:%define pgdatadir %{pgvarlib}/data}
%{!?pgbackupsdir:%define pgbackupsdir %{pgvarlib}/backups}

# The unit name for systemd and the initscript name
# By default:
#   postgresql-x.y.service (systemd)
#   /etc/init.d/postgresql-x.y (sysvinit)
#
%{!?unitname:%define unitname %{longname}-%{majorversion}}

# postgres user and group IDs, homedir, etc. You usually don't want to change these
# even when rebuilding. They're defined as macros mostly so it's obvious when the code
# refers to the postgres user homedir and when it refers to pgdatadir.
#
# Note that these definitions intentionally ignore {shortname} because the user is
# shared across multiple packages which should have the same definition of the user.
#
# They should all be the same as the default RPM packages. If you change any of these
# you must change them all.
%define pguser postgres
%define pggroup postgres
%define pguserhome %{_sharedstatedir}/pgsql
%define pggroupid 26
%define pguserid 26


# Note: Do NOT set dist yourself.
# It should be supplied externally from mock/koji, rpmbuild macros, etc.
#% define dist donotuse

# Distro difference handling macros
# ---------------------------------

# RHEL5 has a bizarre default for the _sharedstatedir macro
# See https://bugzilla.redhat.com/show_bug.cgi?id=894903
%if "%{_sharedstatedir}" == "/usr/com"
%define _sharedstatedir /var/lib
%endif

%if  0%{?rhel} >= 7 || 0%{?fedora} >= 19
# SEPostgreSQL is built by default on RHEL 7 and on Fedora 19+
%{!?selinux:%define selinux 1}
%else
# SEPostgreSQL requirements are not met on RHEL5 or 6.
%{!?selinux:%define selinux 0}
%endif

# Are we using systemd based init?
%if 0%{?rhel} >= 7 || 0%{?fedora} >= 15
%{!?systemd:%define systemd 1}
%else
%{!?systemd:%define systemd 0}
%endif

# Optional features
# -----------------

%{!?test:%define test 1}
%{!?plpython:%define plpython 1}
%{!?pltcl:%define pltcl 1}
%{!?plperl:%define plperl 1}
%{!?ssl:%define ssl 1}
%{!?intdatetimes:%define intdatetimes 1}
%{!?kerberos:%define kerberos 1}
%{!?nls:%define nls 1}
%{!?xml:%define xml 1}
%{!?pam:%define pam 1}
%{!?disablepgfts:%define disablepgfts 0}
%{!?runselftest:%define runselftest 0}
%{!?ldap:%define ldap 1}

# Allow rebuilders to override the Release tag
# Used to set Release: in the style of 3PGDG{dist} by default
%{!?releasever:%define releasever 1}
%{!?releasetag:%define releasetag _2ndQuadrant}

# If you set the githash macro, adds it to the Release field:
%{?githash:%define releasegitsuffix _git%{githash}}

# Sanity checks
#-----------------------

# Enforce that you must set gittag or githash
%if "%{?gittag}" != "" && "%{?githash}" != ""
  %{error:Both %%gittag and %%githash set, bad spec file configuration. See README.md}
%else
  %if "%{?gittag}" == "" && "%{?githash}" == ""
    %{error:No %%gittag or %%githash set, bad spec file configuration. See README.md}
  %endif
%endif

# Top level package info
# ----------------------

Summary:	PostgreSQL client programs and libraries
Name:		%{packagename}%{shortmajorversion}
Version:	9.4.6_bdr%{pgbdrrelease}
Release:	%{releasever}%{releasetag}%{?releasegitsuffix}%{?dist}

License:	PostgreSQL
Group:		Applications/Databases
Url:		http://www.postgresql.org/

# Note: if these files are already in the local srcdir they won't be downloaded.
Source0:	http://packages.2ndquadrant.com/postgresql-bdr94-2ndquadrant/tarballs/%{packagename}-%{version}%{?githash:-git%{githash}}.tar.bz2
Source1:    http://packages.2ndquadrant.com/postgresql-bdr94-2ndquadrant/tarballs/%{packagename}-%{version}%{?githash:-git%{githash}}.tar.bz2.md5
# SysV Init script for !systemd
Source3:	postgresql.init
Source4:	Makefile.regress
Source5:	pg_config.h
Source6:	README.rpm-dist
Source7:	ecpg_config.h
Source10:	postgresql-check-db-dir
# We don't use longname here, as it's hosted on Pg's site and we're just bundling
# the generic PDF for now:
Source12:   http://www.postgresql.org/files/documentation/pdf/%{majorversion}/postgresql-%{majorversion}-A4.pdf
Source14:	postgresql.pam
Source16:	filter-requires-perl-Pg.sh
# systemd control files
Source17:	postgresql-setup
Source18:	postgresql.service

Patch1:		rpm-pgsql.patch
Patch3:		postgresql-logging.patch
Patch6:		postgresql-perl-rpath.patch
# Only used on older Fedora and RHEL undergoing removal of libtermcap
Patch8:		postgresql-prefer-ncurses.patch

Buildrequires:	perl glibc-devel bison
Requires:	/sbin/ldconfig

# RHEL 5.10 only has flex 2.5.4a; 6.5 has 2.5.35, but older rels may not
# so only build-requires a higher flex on RHEL 7
%if 0%{?rhel} >= 7
Buildrequires: flex >= 2.5.31
%else
Buildrequires: flex
%endif

%if ! %systemd
Requires:	initscripts
%else
Requires:	systemd
BuildRequires:	systemd-units
%endif

BuildRequires:	readline-devel
%define zlibver 1.0.4
BuildRequires:	zlib-devel >= %zlibver

%if %ssl
BuildRequires:	openssl-devel
%endif

%if %kerberos
BuildRequires:	krb5-devel
BuildRequires:	e2fsprogs-devel
%endif

%if %nls
%define nlsver 0.10.35
BuildRequires:	gettext >= %nlsver
%endif

%if %xml
BuildRequires:	libxml2-devel libxslt-devel
%endif

%if %pam
BuildRequires:	pam-devel
%endif

%if %ldap
BuildRequires:	openldap-devel
%endif

%if %selinux
BuildRequires: libselinux >= 2.0.93
BuildRequires: selinux-policy >= 3.9.13
%endif

# Over time the package containing this has varied.  If in doubt use:
#   yum whatprovides /usr/lib64/libuuid.so
# to find out.
%if 0%{?rhel} == 5
BuildRequires: e2fsprogs-devel
%else
BuildRequires: libuuid-devel
%endif

# docs requirements
BuildRequires: openjade
BuildRequires: opensp
BuildRequires: docbook-dtds
BuildRequires: docbook-style-dsssl
BuildRequires: libxslt

Requires:	%{name}-libs = %{version}-%{release}
Requires(post):	%{_sbindir}/update-alternatives
Requires(postun):	%{_sbindir}/update-alternatives

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# For compatibility with RHEL/Fedora RPMs
Provides:	postgresql = %{version}-%{release}
Provides:	postgresql%{?_isa} = %{version}-%{release}

# If the package name isn't the default, Provide the base name, so we remain
# compatible with PGDG PostgreSQL packages.
%if "%{packagename}" != "postgresql"
Provides:   postgresql%{shortmajorversion} = %{version}-%{release}
Provides:   postgresql%{shortmajorversion}%{?_isa} = %{version}-%{release}
%endif

%description
PostgreSQL is an advanced Object-Relational database management system (DBMS).
The base postgresql package contains the client programs that you'll need to
access a PostgreSQL DBMS server, as well as HTML documentation for the whole
system.  These client programs can be located on the same machine as the
PostgreSQL server, or on a remote machine that accesses a PostgreSQL server
over a network connection.  The PostgreSQL server can be found in the
%{packagename}%{shortmajorversion}-server sub-package.

If you want to manipulate a PostgreSQL database on a local or remote PostgreSQL
server, you need this package. You also need to install this package
if you are installing the %{packagename}%{shortmajorversion}-server package.

# Subpackages
# -----------


%package libs
Summary:	The shared libraries required for any PostgreSQL clients
Group:		Applications/Databases
# For compatibility with Fedora/CentOS RPMs:
Provides:	postgresql-libs = %{version}-%{release}
Provides:	postgresql-libs%{?_isa} = %{version}-%{release}
%if "%{packagename}" != "postgresql"
# To be compatible with PGDG when package is renamed:
Provides:   postgresql%{shortmajorversion}-libs = %{version}-%{release}
Provides:   postgresql%{shortmajorversion}-libs%{?_isa} = %{version}-%{release}
%endif

%description libs
The %{packagename}%{shortmajorversion}-libs package provides the essential shared libraries for any
PostgreSQL client program or interface. You will need to install this package
to use any other PostgreSQL package or any clients that need to connect to a
PostgreSQL server.


%package server
Summary:	The programs needed to create and run a PostgreSQL server
Group:		Applications/Databases
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
Requires(pre):	/usr/sbin/useradd
# for /sbin/ldconfig
Requires(post):		glibc
Requires(postun):	glibc
# pre/post stuff needs systemd too
%if %systemd
Requires(post):		systemd-units
Requires(preun):	systemd-units
Requires(postun):	systemd-units
%endif
Requires:	%{name} = %{version}-%{release}
Requires:	%{name}-libs = %{version}-%{release}
# For compatibility with RHEL/Fedora:
Provides:	postgresql-server = %{version}-%{release}
Provides:	postgresql-server%{?_isa} = %{version}-%{release}
%if "%{packagename}" != "postgresql"
# To be compatible with PGDG stock RPMs
Provides:   postgresql%{shortmajorversion}-server = %{version}-%{release}
Provides:   postgresql%{shortmajorversion}-server%{?_isa} = %{version}-%{release}
%endif

%description server
PostgreSQL is an advanced Object-Relational database management system (DBMS).
The %{packagename}%{shortmajorversion}-server package contains the programs needed to create
and run a PostgreSQL server, which will in turn allow you to create
and maintain PostgreSQL databases.


%package docs
Summary:	Extra documentation for PostgreSQL
Group:		Applications/Databases
# For compatibility with RHEL/Fedora:
Provides:	postgresql-docs = %{version}-%{release}
Provides:	postgresql-docs%{?_isa} = %{version}-%{release}
%if "%{packagename}" != "postgresql"
# To be compatible with PGDG stock RPMs
# (The docs aren't noarch, even though they contain no arch binaries)
Provides:   postgresql%{shortmajorversion}-docs = %{version}-%{release}
Provides:   postgresql%{shortmajorversion}-docs%{?_isa} = %{version}-%{release}
%endif

%description docs
The %{packagename}%{shortmajorversion}-docs package includes the SGML source for the documentation
as well as the documentation in PDF format and some extra documentation.
Install this package if you want to help with the PostgreSQL documentation
project, or if you want to generate printed documentation. This package also
includes HTML version of the documentation.


%package contrib
Summary:	Contributed source and binaries distributed with PostgreSQL
Group:		Applications/Databases
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
# For compatibility with RHEL/Fedora:
Provides:	postgresql-contrib = %{version}-%{release}
Provides:	postgresql-contri%{?_isa}b = %{version}-%{release}
%if "%{packagename}" != "postgresql"
# To be compatible with PGDG stock RPMs
Provides:   postgresql%{shortmajorversion}-contrib = %{version}-%{release}
Provides:   postgresql%{shortmajorversion}-contrib%{?_isa} = %{version}-%{release}
%endif


%description contrib
The %{packagename}%{shortmajorversion}-contrib package contains various extension modules that are
included in the PostgreSQL distribution.


%package devel
Summary:	PostgreSQL development header files and libraries
Group:		Development/Libraries
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
# For compatibility with RHEL/Fedora:
Provides:	postgresql-devel = %{version}-%{release}
Provides:	postgresql-devel%{?_isa} = %{version}-%{release}
%if "%{packagename}" != "postgresql"
# To be compatible with PGDG stock RPMs
Provides:   postgresql%{shortmajorversion}-devel = %{version}-%{release}
Provides:   postgresql%{shortmajorversion}-devel%{?_isa} = %{version}-%{release}
%endif
# Libraries included via public PostgreSQL headers, or those that pg_config
# emits linker flags for, should be Requires: entries for the -devel package.
Requires:	readline-devel
Requires:	zlib-devel >= %zlibver
%if %ssl
Requires:	openssl-devel
%endif
%if %nls
Requires:	gettext >= %nlsver
%endif
%if %xml
Requires:	libxml2-devel libxslt-devel
%endif
%if %pam
Requires:	pam-devel
%endif

%description devel
The %{packagename}%{shortmajorversion}-devel package contains the header files and libraries
needed to compile C or C++ applications which will directly interact
with a PostgreSQL database management server.  It also contains the ecpg
Embedded C Postgres preprocessor. You need to install this package if you want
to develop applications which will interact with a PostgreSQL server.


%if %plperl
%package plperl
Summary:	The Perl procedural language for PostgreSQL
Group:		Applications/Databases
Requires:	%{name}-server%{?_isa} = %{version}-%{release}
# See http://fedoraproject.org/wiki/Packaging:Perl
Requires:	perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
BuildRequires:	perl(ExtUtils::Embed)
BuildRequires:	perl(ExtUtils::MakeMaker)
%if 0%{?rhel} == 5
# CentOS 5 didn't have perl-devel or perl-libs, just "perl"
Requires: perl
%else
Requires: perl-libs
BuildRequires:	perl-devel%{?_isa}
%endif
# For compatibility with RHEL/Fedora:
Provides:	postgresql-plperl = %{version}-%{release}
Provides:	postgresql-plperl%{?_isa} = %{version}-%{release}
%if "%{packagename}" != "postgresql"
# To be compatible with PGDG stock RPMs
Provides:   postgresql%{shortmajorversion}-plperl = %{version}-%{release}
Provides:   postgresql%{shortmajorversion}-plperl%{?_isa} = %{version}-%{release}
%endif

%description plperl
The %{packagename}%{shortmajorversion}-plperl package contains the PL/Perl procedural language,
which is an extension to the PostgreSQL database server.
Install this if you want to write database functions in Perl.

%endif


%if %plpython
%package plpython
Summary:	The Python procedural language for PostgreSQL
Group:		Applications/Databases
BuildRequires:	python-devel%{?_isa}
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	%{name}-server%{?_isa} = %{version}-%{release}
# For compatibility with RHEL/Fedora:
Provides:	postgresql-plpython = %{version}-%{release}
Provides:	postgresql-plpython%{?_isa} = %{version}-%{release}
%if "%{packagename}" != "postgresql"
# To be compatible with PGDG stock RPMs
Provides:   postgresql%{shortmajorversion}-plpython = %{version}-%{release}
Provides:   postgresql%{shortmajorversion}-plpython%{?_isa} = %{version}-%{release}
%endif

%description plpython
The %{packagename}%{shortmajorversion}-plpython package contains the PL/Python procedural language,
which is an extension to the PostgreSQL database server.
Install this if you want to write database functions in Python.

%endif

%if %pltcl
%package pltcl
Summary:	The Tcl procedural language for PostgreSQL
Group:		Applications/Databases
BuildRequires:	tcl-devel%{?_isa}
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	%{name}-server%{?_isa} = %{version}-%{release}
# For compatibility with RHEL/Fedora:
Provides:	postgresql-pltcl = %{version}-%{release}
Provides:	postgresql-pltcl%{?_isa} = %{version}-%{release}
%if "%{packagename}" != "postgresql"
# To be compatible with PGDG stock RPMs
Provides:   postgresql%{shortmajorversion}-pltcl = %{version}-%{release}
Provides:   postgresql%{shortmajorversion}-pltcl%{?_isa} = %{version}-%{release}
%endif

%description pltcl
PostgreSQL is an advanced Object-Relational database management
system. The %{name}-pltcl package contains the PL/Tcl language
for the backend.
%endif

%if %test
%package test
Summary:	The test suite distributed with PostgreSQL
Group:		Applications/Databases
Requires:	%{name}-server%{?_isa} = %{version}-%{release}
Requires:	%{name}-devel%{?_isa} = %{version}-%{release}
# For compatibility with RHEL/Fedora:
Provides:	postgresql-test = %{version}-%{release}
Provides:	postgresql-test%{?_isa} = %{version}-%{release}
%if "%{packagename}" != "postgresql"
# To be compatible with PGDG stock RPMs
Provides:   postgresql%{shortmajorversion}-test = %{version}-%{release}
Provides:   postgresql%{shortmajorversion}-test%{?_isa} = %{version}-%{release}
%endif

%description test
The %{packagename}%{shortmajorversion}-test package contains files needed for various tests for the
PostgreSQL database management system, including regression tests and
benchmarks.
%endif

# Build scripts, install scripts, pre/post scripts, etc
# -----------------------------------------------------

%define __perl_requires %{SOURCE16}

%prep

# Check the md5. In release builds it's checked into git, not downloaded from
# the source.
pushd %{_sourcedir}
if ! md5sum --check %{SOURCE1}; then
	echo "md5sum --check %{SOURCE1} failed, check %{SOURCE0}"
	exit 1

fi
popd

# You must prepare the dist tarball to match this format by overriding distdir,
# or the RPM build will fail because it won't find the correct contained
# directory. For a tagged release:
#
#   make distdir='postgresql-bdr-$(VERSION)-bdr${pgbdrrelease}
#
# and for test/interim releases based on git snapshots include the git rev:
#
#   make distdir='postgresql-bdr-$(VERSION)-bdr${pgbdrrelease}-git'$(git rev-parse --short HEAD)
#
%setup -q -n %{packagename}-%{version}%{?githash:-git%{githash}}
%patch1 -p1
%patch3 -p1
%patch6 -p1

#patch8 is only needed on RHEL6 and older
%if 0%{?rhel} && 0%{?rhel} < 7
%patch8 -p1
%endif

cp -p %{SOURCE12} .

%build

# fail quickly and obviously if user tries to build as root
%if %runselftest
	if [ x"`id -u`" = x0 ]; then
		echo "postgresql's regression tests fail if run as root."
		echo "If you really need to build the RPM as root, use"
		echo "--define='runselftest 0' to skip the regression tests."
		exit 1
	fi
%endif

CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS

# Strip out -ffast-math from CFLAGS....
CFLAGS=`echo $CFLAGS|xargs -n 1|grep -v ffast-math|xargs -n 100`
# Add LINUX_OOM_ADJ=0 to ensure child processes reset postmaster's oom_adj
CFLAGS="$CFLAGS -DLINUX_OOM_ADJ=0"

export LIBNAME=%{_lib}
# We don't use the "configure" macro here because we don't install in /usr or
# put libs in /usr/lib64 etc.
./configure --enable-rpath \
	--prefix=%{pgbaseinstdir} \
	--includedir=%{pgbaseinstdir}/include \
	--mandir=%{pgbaseinstdir}/share/man \
	--datadir=%{pgbaseinstdir}/share \
%if %beta
	--enable-debug \
	--enable-cassert \
%endif
%if %plperl
	--with-perl \
%endif
%if %plpython
	--with-python \
%endif
%if %pltcl
	--with-tcl \
	--with-tclconfig=%{_libdir} \
%endif
%if %ssl
	--with-openssl \
%endif
%if %pam
	--with-pam \
%endif
%if %kerberos
	--with-gssapi \
	--with-includes=%{_includedir} \
	--with-libraries=%{_libdir} \
%endif
%if %nls
	--enable-nls \
%endif
%if !%intdatetimes
	--disable-integer-datetimes \
%endif
%if %disablepgfts
	--disable-thread-safety \
%endif
	--with-uuid=e2fs \
%if %xml
	--with-libxml \
	--with-libxslt \
%endif
%if %ldap
	--with-ldap \
%endif
%if %selinux
	--with-selinux \
%endif
	--with-system-tzdata=%{_datadir}/zoneinfo \
	--sysconfdir=/etc/sysconfig/${shortname} \
	--docdir=%{_docdir}

make %{?_smp_mflags} all
make %{?_smp_mflags} -C contrib all
make %{?_smp_mflags} -C contrib/uuid-ossp all

# Have to hack makefile to put correct path into tutorial scripts
sed "s|C=\`pwd\`;|C=%{pgbaseinstdir}/lib/tutorial;|" < src/tutorial/Makefile > src/tutorial/GNUmakefile
make %{?_smp_mflags} -C src/tutorial NO_PGXS=1 all
rm -f src/tutorial/GNUmakefile

%if %runselftest
	pushd src/test/regress
	make all
	cp ../../../contrib/spi/refint.so .
	cp ../../../contrib/spi/autoinc.so .
	make MAX_CONNECTIONS=5 check
	make clean
	popd
	pushd src/pl
	make MAX_CONNECTIONS=5 check
	popd
	pushd contrib
	make MAX_CONNECTIONS=5 check
	popd
%endif

%if %test
	pushd src/test/regress
	make all
	popd
%endif

%install
rm -rf %{buildroot}

make DESTDIR=%{buildroot} install

mkdir -p %{buildroot}%{pgbaseinstdir}/share/extensions/
make -C contrib DESTDIR=%{buildroot} install
make -C contrib/uuid-ossp DESTDIR=%{buildroot} install

# multilib header hack; note pg_config.h is installed in two places!
# we only apply this to known Red Hat multilib arches, per bug #177564
case `uname -i` in
	i386 | x86_64 | ppc | ppc64 | s390 | s390x)
		mv %{buildroot}%{pgbaseinstdir}/include/pg_config.h %{buildroot}%{pgbaseinstdir}/include/pg_config_`uname -i`.h
		install -m 644 %{SOURCE5} %{buildroot}%{pgbaseinstdir}/include/
		mv %{buildroot}%{pgbaseinstdir}/include/server/pg_config.h %{buildroot}%{pgbaseinstdir}/include/server/pg_config_`uname -i`.h
		install -m 644 %{SOURCE5} %{buildroot}%{pgbaseinstdir}/include/server/
		mv %{buildroot}%{pgbaseinstdir}/include/ecpg_config.h %{buildroot}%{pgbaseinstdir}/include/ecpg_config_`uname -i`.h
		install -m 644 %{SOURCE7} %{buildroot}%{pgbaseinstdir}/include/
		;;
	*)
	;;
esac

substitute_vars() {
	# Insert RPM variables into scripts wherever a placeholder of the form
	# __RPM__[varname]__ is found.
	sed -e 's|__RPM_PGVERSION__|%{version}|g' \
		-e 's|__RPM_PGENGINE__|%{pgbaseinstdir}/bin|g' \
		-e 's|__RPM_PGUNITNAME__|%{unitname}|g' \
		-e 's|__RPM_PGMAJORVERSION__|%{majorversion}|g' \
		-e 's|__RPM_PGSHORTMAJORVERSION__|%{shortmajorversion}|g' \
		-e 's|__RPM_PREVMAJORVERSION__|%{?prevmajorversion}|g' \
		-e 's|__RPM_PGPACKAGENAME__|%{name}|g' \
		-e 's|__RPM_PGLONGNAME__|%{longname}|g' \
		-e 's|__RPM_PGSHORTNAME__|%{shortname}|g' \
		-e 's|__RPM_PGDOCDIR__|%{_pkgdocdir}|g' \
		-e 's|__RPM_PGVARLIB__|%{pgvarlib}|g' \
		-e 's|__RPM_PGDATA__|%{pgdatadir}|g' \
		-e 's|__RPM_SHORTSERVERDESCRIPTION__|%{shortserverdescription}|g' \
		-e 's|__RPM_INITDIR__|%{_initrddir}|g' \
		-e 's|__RPM_PGUSER__|%{pguser}|g' \
		-e 's|__RPM_PGGROUP__|%{pggroup}|g' \
		-e 's|__RPM_SYSTEMD__|%{systemd}|g' \
		< "$1" > "$2"
}

# prep the setup script, including insertion of some values it needs
substitute_vars "%{SOURCE17}" "%{longname}%{shortmajorversion}-setup"
touch -r "%{SOURCE17}" "%{longname}%{shortmajorversion}-setup"
install -m 755 "%{longname}%{shortmajorversion}-setup" "%{buildroot}%{pgbaseinstdir}/bin/%{longname}%{shortmajorversion}-setup"

# prep the startup check script, including insertion of some values it needs
substitute_vars "%{SOURCE10}" "%{longname}%{shortmajorversion}-check-db-dir"
touch -r "%{SOURCE10}" "%{longname}%{shortmajorversion}-check-db-dir"
install -m 755 "%{longname}%{shortmajorversion}-check-db-dir" "%{buildroot}%{pgbaseinstdir}/bin/%{longname}%{shortmajorversion}-check-db-dir"

%if %systemd
# ... and the systemd unit file
install -d %{buildroot}%{_unitdir}
substitute_vars "%{SOURCE18}" "%{unitname}.service"
touch -r "%{SOURCE18}" "%{unitname}.service"
install -m 644 "%{unitname}.service" "%{buildroot}%{_unitdir}/%{unitname}.service"
%else
# ... or the sysvinit script
install -d %{buildroot}/%{_initrddir}
substitute_vars "%{SOURCE3}" "%{longname}.init"
touch -r "%{SOURCE3}" "%{longname}.init"
install -m 755 %{longname}.init %{buildroot}/%{_initrddir}/%{unitname}
%endif

%if %pam
install -d %{buildroot}/etc/pam.d
install -m 644 %{SOURCE14} %{buildroot}/etc/pam.d/%{longname}%{shortmajorversion}
%endif

# PGDATA needs removal of group and world permissions due to pg_pwd hole.
install -d -m 700 %{buildroot}%{pgdatadir}

# backups of data go here...
install -d -m 700 %{buildroot}%{pgbackupsdir}

# Create the multiple postmaster startup directory
install -d -m 700 %{buildroot}/etc/sysconfig/pgsql/%{majorversion}

# Install linker conf file under postgresql installation directory.
# We will install the latest version via alternatives.
cat > %{_builddir}/%{longname}-%{majorversion}-libs.conf <<__END__
%{pgbaseinstdir}/lib
__END__

install -d -m 755 %{buildroot}%{pgbaseinstdir}/share/
install -m 700 %{_builddir}/%{longname}-%{majorversion}-libs.conf %{buildroot}%{pgbaseinstdir}/share/

%if %test
	# tests. There are many files included here that are unnecessary,
	# but include them anyway for completeness.  We replace the original
	# Makefiles, however.
	mkdir -p %{buildroot}%{pgbaseinstdir}/lib/test
	cp -a src/test/regress %{buildroot}%{pgbaseinstdir}/lib/test
	install -m 0755 contrib/spi/refint.so %{buildroot}%{pgbaseinstdir}/lib/test/regress
	install -m 0755 contrib/spi/autoinc.so %{buildroot}%{pgbaseinstdir}/lib/test/regress
	pushd  %{buildroot}%{pgbaseinstdir}/lib/test/regress
	strip *.so
	rm -f GNUmakefile Makefile *.o
	chmod 0755 pg_regress regress.so
	popd
	cp %{SOURCE4} %{buildroot}%{pgbaseinstdir}/lib/test/regress/Makefile
	chmod 0644 %{buildroot}%{pgbaseinstdir}/lib/test/regress/Makefile
%endif

# Fix some more documentation
# gzip doc/internals.ps
cp %{SOURCE6} README.rpm-dist
mkdir -p %{buildroot}%{pgbaseinstdir}/share/doc/html
mv doc/src/sgml/html doc
mkdir -p %{buildroot}%{pgbaseinstdir}/share/man/
mv doc/src/sgml/man1 doc/src/sgml/man3 doc/src/sgml/man7  %{buildroot}%{pgbaseinstdir}/share/man/
rm -rf %{buildroot}%{_docdir}/pgsql

# initialize file lists
cp /dev/null main.lst
cp /dev/null libs.lst
cp /dev/null server.lst
cp /dev/null devel.lst
cp /dev/null plperl.lst
cp /dev/null pltcl.lst
cp /dev/null plpython.lst

# initialize file lists
cp /dev/null main.lst
cp /dev/null libs.lst
cp /dev/null server.lst
cp /dev/null devel.lst
cp /dev/null plperl.lst
cp /dev/null pltcl.lst
cp /dev/null plpython.lst

%if %nls
%find_lang ecpg-%{majorversion}
%find_lang ecpglib6-%{majorversion}
%find_lang initdb-%{majorversion}
%find_lang libpq5-%{majorversion}
%find_lang pg_basebackup-%{majorversion}
%find_lang pg_config-%{majorversion}
%find_lang pg_controldata-%{majorversion}
%find_lang pg_ctl-%{majorversion}
%find_lang pg_dump-%{majorversion}
%find_lang pg_resetxlog-%{majorversion}
%find_lang pgscripts-%{majorversion}
%if %plperl
%find_lang plperl-%{majorversion}
cat plperl-%{majorversion}.lang > pg_plperl.lst
%endif
%find_lang plpgsql-%{majorversion}
%if %plpython
%find_lang plpython-%{majorversion}
cat plpython-%{majorversion}.lang > pg_plpython.lst
%endif
%if %pltcl
%find_lang pltcl-%{majorversion}
cat pltcl-%{majorversion}.lang > pg_pltcl.lst
%endif
%find_lang postgres-%{majorversion}
%find_lang psql-%{majorversion}
%endif

cat libpq5-%{majorversion}.lang > pg_libpq5.lst
cat pg_config-%{majorversion}.lang ecpg-%{majorversion}.lang ecpglib6-%{majorversion}.lang > pg_devel.lst
cat initdb-%{majorversion}.lang pg_ctl-%{majorversion}.lang psql-%{majorversion}.lang pg_dump-%{majorversion}.lang pg_basebackup-%{majorversion}.lang pgscripts-%{majorversion}.lang > pg_main.lst
cat postgres-%{majorversion}.lang pg_resetxlog-%{majorversion}.lang pg_controldata-%{majorversion}.lang plpgsql-%{majorversion}.lang > pg_server.lst

# Ensure that the PG user homedir exists so rpm can package it
mkdir -p %{buildroot}%{pguserhome}

%check
# Run post-install checks for the packages, after the install section has run
# This is run by rpmbuild, not on the host after installation like the post
# sections, and is intended for build sanity checks or running of regression
# tests etc.
echo "Running RPM %%check section"

%if %systemd
    if grep __RPM "%{buildroot}%{_unitdir}/%{unitname}.service"; then
		echo "Found unsubstituted __RPM vars in unit file"
		exit 1
	fi
%else
	if grep __RPM "%{buildroot}/%{_initrddir}/%{unitname}"; then
		echo "Found unsubstituted _RPM vars in initscript"
		exit 1
	fi
%endif

if grep __RPM "%{buildroot}%{pgbaseinstdir}/bin/%{longname}%{shortmajorversion}-setup"; then
	echo "Found unsubstituted __RPM vars in %{longname}%{shortmajorversion}-setup"
	exit 1
fi

if grep __RPM "%{buildroot}%{pgbaseinstdir}/bin/%{longname}%{shortmajorversion}-check-db-dir"; then
	echo "Found unsubstitued __RPM vars in %{longname}%{shortmajorversion}-check-db-dir"
	exit 1
fi

echo "Done with %%check"

%pre server
groupadd -g %{pggroupid} -o -r %{pggroup} >/dev/null 2>&1 || :
useradd -M -n -g postgres -o -r -d %{pguserhome} -s /bin/bash \
	-c "PostgreSQL Server" -u %{pguserid} %{pguser} >/dev/null 2>&1 || :

%post server
/sbin/ldconfig
if [ $1 -eq 1 ] ; then
    # Initial installation
%if %systemd
    /usr/bin/systemctl daemon-reload >/dev/null 2>&1 || :
%else
    chkconfig --add %{unitname}
%endif
fi
# postgres' .bash_profile.
# We now don't install .bash_profile as we used to in pre 9.0. Instead, use cat,
# so that package manager will be happy during upgrade to new major version. Multiple
# packages can stomp on this file.
echo "[ -f /etc/profile ] && source /etc/profile
PGDATA=%{pgdatadir}
export PGDATA" >  %{pguserhome}/.bash_profile
chown postgres: %{pguserhome}/.bash_profile

%preun server
if [ $1 -eq 0 ] ; then
	# Package removal, not upgrade
%if %systemd
	/usr/bin/systemctl --no-reload disable %{unitname}.service >/dev/null 2>&1 || :
	/usr/bin/systemctl stop %{unitname}.service >/dev/null 2>&1 || :
%else
	/sbin/service %{unitname} condstop >/dev/null 2>&1
	chkconfig --del %{unitname}
%endif
fi

%postun server
/sbin/ldconfig 
%if %systemd
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 || :
%endif
if [ $1 -ge 1 ] ; then
	# Package upgrade, not uninstall
%if %systemd
	/usr/bin/systemctl try-restart %{unitname}.service >/dev/null 2>&1 || :
%else
	/sbin/service %{unitname} condrestart >/dev/null 2>&1
%endif
fi

%if %plperl
%post 	-p /sbin/ldconfig	plperl
%postun	-p /sbin/ldconfig 	plperl
%endif

%if %plpython
%post 	-p /sbin/ldconfig	plpython
%postun	-p /sbin/ldconfig 	plpython
%endif

%if %pltcl
%post 	-p /sbin/ldconfig	pltcl
%postun	-p /sbin/ldconfig 	pltcl
%endif

%if %test
%post test
chown -R %{pguser}:%{pggroup} /usr/share/pgsql/test >/dev/null 2>&1 || :
%endif

%post
# Create alternatives entries for common binaries and man files
#
# The Red Hat RPMs use "pgsql" for these alternatives, so we must follow that;
# you don't want {shortname} here.
%{_sbindir}/update-alternatives	--install	/usr/bin/psql	pgsql-psql	%{pgbaseinstdir}/bin/psql	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/clusterdb	pgsql-clusterdb	%{pgbaseinstdir}/bin/clusterdb	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/createdb	pgsql-createdb	%{pgbaseinstdir}/bin/createdb	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/createlang	pgsql-createlang	%{pgbaseinstdir}/bin/createlang	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/createuser	pgsql-createuser	%{pgbaseinstdir}/bin/createuser	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/dropdb	pgsql-dropdb	%{pgbaseinstdir}/bin/dropdb	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/droplang	pgsql-droplang	%{pgbaseinstdir}/bin/droplang	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/dropuser	pgsql-dropuser	%{pgbaseinstdir}/bin/dropuser	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/pg_basebackup	pgsql-pg_basebackup	%{pgbaseinstdir}/bin/pg_basebackup	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/pg_dump	pgsql-pg_dump	%{pgbaseinstdir}/bin/pg_dump	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/pg_dumpall	pgsql-pg_dumpall	%{pgbaseinstdir}/bin/pg_dumpall	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/pg_restore	pgsql-pg_restore	%{pgbaseinstdir}/bin/pg_restore	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/reindexdb	pgsql-reindexdb	%{pgbaseinstdir}/bin/reindexdb	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/bin/vacuumdb	pgsql-vacuumdb	%{pgbaseinstdir}/bin/vacuumdb	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/clusterdb.1	pgsql-clusterdbman	%{pgbaseinstdir}/share/man/man1/clusterdb.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/createdb.1	pgsql-createdbman	%{pgbaseinstdir}/share/man/man1/createdb.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/createlang.1	pgsql-createlangman	%{pgbaseinstdir}/share/man/man1/createlang.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/createuser.1	pgsql-createuserman	%{pgbaseinstdir}/share/man/man1/createuser.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/dropdb.1	pgsql-dropdbman	%{pgbaseinstdir}/share/man/man1/dropdb.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/droplang.1	pgsql-droplangman	%{pgbaseinstdir}/share/man/man1/droplang.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/dropuser.1	pgsql-dropuserman	%{pgbaseinstdir}/share/man/man1/dropuser.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/pg_basebackup.1	pgsql-pg_basebackupman	%{pgbaseinstdir}/share/man/man1/pg_basebackup.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/pg_dump.1	pgsql-pg_dumpman	%{pgbaseinstdir}/share/man/man1/pg_dump.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/pg_dumpall.1	pgsql-pg_dumpallman	%{pgbaseinstdir}/share/man/man1/pg_dumpall.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/pg_restore.1	pgsql-pg_restoreman	%{pgbaseinstdir}/share/man/man1/pg_restore.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/psql.1	pgsql-psqlman	%{pgbaseinstdir}/share/man/man1/psql.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/reindexdb.1	pgsql-reindexdbman	%{pgbaseinstdir}/share/man/man1/reindexdb.1	%{shortmajorversion}0
%{_sbindir}/update-alternatives	--install	/usr/share/man/man1/vacuumdb.1	pgsql-vacuumdbman	%{pgbaseinstdir}/share/man/man1/vacuumdb.1	%{shortmajorversion}0

%post libs
# Make sure ld.so can find the libs for Pg
%{_sbindir}/update-alternatives --install /etc/ld.so.conf.d/postgresql-libs.conf pgsql-ld-conf %{pgbaseinstdir}/share/%{longname}-%{majorversion}-libs.conf %{shortmajorversion}0
/sbin/ldconfig

# Drop alternatives entries for common binaries and man files
%postun
if [ "$1" -eq 0 ]
then
	# Only remove these links if the package is completely removed from the system (vs.just being upgraded)
	%{_sbindir}/update-alternatives --remove pgsql-psql		%{pgbaseinstdir}/bin/psql
	%{_sbindir}/update-alternatives --remove pgsql-clusterdb	%{pgbaseinstdir}/bin/clusterdb
	%{_sbindir}/update-alternatives --remove pgsql-clusterdbman	%{pgbaseinstdir}/share/man/man1/clusterdb.1
	%{_sbindir}/update-alternatives --remove pgsql-createdb		%{pgbaseinstdir}/bin/createdb
	%{_sbindir}/update-alternatives --remove pgsql-createdbman	%{pgbaseinstdir}/share/man/man1/createdb.1
	%{_sbindir}/update-alternatives --remove pgsql-createlang	%{pgbaseinstdir}/bin/createlang
	%{_sbindir}/update-alternatives --remove pgsql-createlangman	%{pgbaseinstdir}/share/man/man1/createlang.1
	%{_sbindir}/update-alternatives --remove pgsql-createuser	%{pgbaseinstdir}/bin/createuser
	%{_sbindir}/update-alternatives --remove pgsql-createuserman	%{pgbaseinstdir}/share/man/man1/createuser.1
	%{_sbindir}/update-alternatives --remove pgsql-dropdb		%{pgbaseinstdir}/bin/dropdb
	%{_sbindir}/update-alternatives --remove pgsql-dropdbman	%{pgbaseinstdir}/share/man/man1/dropdb.1
	%{_sbindir}/update-alternatives --remove pgsql-droplang		%{pgbaseinstdir}/bin/droplang
	%{_sbindir}/update-alternatives --remove pgsql-droplangman	%{pgbaseinstdir}/share/man/man1/droplang.1
	%{_sbindir}/update-alternatives --remove pgsql-dropuser		%{pgbaseinstdir}/bin/dropuser
	%{_sbindir}/update-alternatives --remove pgsql-dropuserman	%{pgbaseinstdir}/share/man/man1/dropuser.1
	%{_sbindir}/update-alternatives --remove pgsql-pg_basebackup	%{pgbaseinstdir}/bin/pg_basebackup
	%{_sbindir}/update-alternatives --remove pgsql-pg_dump		%{pgbaseinstdir}/bin/pg_dump
	%{_sbindir}/update-alternatives --remove pgsql-pg_dumpall	%{pgbaseinstdir}/bin/pg_dumpall
	%{_sbindir}/update-alternatives --remove pgsql-pg_dumpallman	%{pgbaseinstdir}/share/man/man1/pg_dumpall.1
	%{_sbindir}/update-alternatives --remove pgsql-pg_basebackupman	%{pgbaseinstdir}/share/man/man1/pg_basebackup.1
	%{_sbindir}/update-alternatives --remove pgsql-pg_dumpman	%{pgbaseinstdir}/share/man/man1/pg_dump.1
	%{_sbindir}/update-alternatives --remove pgsql-pg_restore	%{pgbaseinstdir}/bin/pg_restore
	%{_sbindir}/update-alternatives --remove pgsql-pg_restoreman	%{pgbaseinstdir}/share/man/man1/pg_restore.1
	%{_sbindir}/update-alternatives --remove pgsql-psqlman		%{pgbaseinstdir}/share/man/man1/psql.1
	%{_sbindir}/update-alternatives --remove pgsql-reindexdb	%{pgbaseinstdir}/bin/reindexdb
	%{_sbindir}/update-alternatives --remove pgsql-reindexdbman	%{pgbaseinstdir}/share/man/man1/reindexdb.1
	%{_sbindir}/update-alternatives --remove pgsql-vacuumdb		%{pgbaseinstdir}/bin/vacuumdb
	%{_sbindir}/update-alternatives --remove pgsql-vacuumdbman	%{pgbaseinstdir}/share/man/man1/vacuumdb.1
fi

%postun libs
if [ "$1" -eq 0 ]
then
	%{_sbindir}/update-alternatives --remove pgsql-ld-conf %{pgbaseinstdir}/share/%{longname}-%{majorversion}-libs.conf
	/sbin/ldconfig
fi

%clean
rm -rf %{buildroot}

# FILES section
# -------------

%files -f pg_main.lst
%defattr(-,root,root)
%doc doc/KNOWN_BUGS doc/MISSING_FEATURES
%doc COPYRIGHT doc/bug.template
%doc README.rpm-dist
%{pgbaseinstdir}/bin/clusterdb
%{pgbaseinstdir}/bin/createdb
%{pgbaseinstdir}/bin/createlang
%{pgbaseinstdir}/bin/createuser
%{pgbaseinstdir}/bin/dropdb
%{pgbaseinstdir}/bin/droplang
%{pgbaseinstdir}/bin/dropuser
%{pgbaseinstdir}/bin/pg_basebackup
%{pgbaseinstdir}/bin/pg_config
%{pgbaseinstdir}/bin/pg_dump
%{pgbaseinstdir}/bin/pg_dumpall
%{pgbaseinstdir}/bin/pg_isready
%{pgbaseinstdir}/bin/pg_restore
%{pgbaseinstdir}/bin/pg_test_fsync
%{pgbaseinstdir}/bin/pg_receivexlog
%{pgbaseinstdir}/bin/psql
%{pgbaseinstdir}/bin/reindexdb
%{pgbaseinstdir}/bin/vacuumdb
%{pgbaseinstdir}/share/man/man1/clusterdb.*
%{pgbaseinstdir}/share/man/man1/createdb.*
%{pgbaseinstdir}/share/man/man1/createlang.*
%{pgbaseinstdir}/share/man/man1/createuser.*
%{pgbaseinstdir}/share/man/man1/dropdb.*
%{pgbaseinstdir}/share/man/man1/droplang.*
%{pgbaseinstdir}/share/man/man1/dropuser.*
%{pgbaseinstdir}/share/man/man1/pg_basebackup.*
%{pgbaseinstdir}/share/man/man1/pg_config.*
%{pgbaseinstdir}/share/man/man1/pg_dump.*
%{pgbaseinstdir}/share/man/man1/pg_dumpall.*
%{pgbaseinstdir}/share/man/man1/pg_isready.*
%{pgbaseinstdir}/share/man/man1/pg_receivexlog.*
%{pgbaseinstdir}/share/man/man1/pg_restore.*
%{pgbaseinstdir}/share/man/man1/psql.*
%{pgbaseinstdir}/share/man/man1/reindexdb.*
%{pgbaseinstdir}/share/man/man1/vacuumdb.*
%{pgbaseinstdir}/share/man/man3/*
%{pgbaseinstdir}/share/man/man7/*

%files docs
%defattr(-,root,root)
%doc doc/src/*
%doc *-A4.pdf
%doc src/tutorial
%doc doc/html

%files contrib
%defattr(-,root,root)
%{pgbaseinstdir}/lib/_int.so
%{pgbaseinstdir}/lib/adminpack.so
%{pgbaseinstdir}/lib/auth_delay.so
%{pgbaseinstdir}/lib/autoinc.so
%{pgbaseinstdir}/lib/auto_explain.so
%{pgbaseinstdir}/lib/btree_gin.so
%{pgbaseinstdir}/lib/btree_gist.so
%{pgbaseinstdir}/lib/chkpass.so
%{pgbaseinstdir}/lib/citext.so
%{pgbaseinstdir}/lib/cube.so
%{pgbaseinstdir}/lib/dblink.so
%{pgbaseinstdir}/lib/dummy_seclabel.so
%{pgbaseinstdir}/lib/earthdistance.so
%{pgbaseinstdir}/lib/file_fdw.so*
%{pgbaseinstdir}/lib/fuzzystrmatch.so
%{pgbaseinstdir}/lib/insert_username.so
%{pgbaseinstdir}/lib/isn.so
%{pgbaseinstdir}/lib/hstore.so
%{pgbaseinstdir}/lib/passwordcheck.so
%{pgbaseinstdir}/lib/pg_freespacemap.so
%{pgbaseinstdir}/lib/pg_stat_statements.so
%{pgbaseinstdir}/lib/pgrowlocks.so
%{pgbaseinstdir}/lib/sslinfo.so
%{pgbaseinstdir}/lib/lo.so
%{pgbaseinstdir}/lib/ltree.so
%{pgbaseinstdir}/lib/moddatetime.so
%{pgbaseinstdir}/lib/pageinspect.so
%{pgbaseinstdir}/lib/pgcrypto.so
%{pgbaseinstdir}/lib/pgstattuple.so
%{pgbaseinstdir}/lib/pg_buffercache.so
%{pgbaseinstdir}/lib/pg_prewarm.so
%{pgbaseinstdir}/lib/pg_trgm.so
%{pgbaseinstdir}/lib/pg_upgrade_support.so
%{pgbaseinstdir}/lib/postgres_fdw.so
%{pgbaseinstdir}/lib/refint.so
%{pgbaseinstdir}/lib/seg.so
%if %selinux
%{pgbaseinstdir}/lib/sepgsql.so
%{pgbaseinstdir}/share/contrib/sepgsql.sql
%endif
%{pgbaseinstdir}/lib/tablefunc.so
%{pgbaseinstdir}/lib/tcn.so
%{pgbaseinstdir}/lib/test_decoding.so
%{pgbaseinstdir}/lib/test_shm_mq.so
%{pgbaseinstdir}/lib/timetravel.so
%{pgbaseinstdir}/lib/unaccent.so
%{pgbaseinstdir}/lib/worker_spi.so
%if %xml
%{pgbaseinstdir}/lib/pgxml.so
%endif
%{pgbaseinstdir}/lib/uuid-ossp.so
%{pgbaseinstdir}/share/extension/adminpack*
%{pgbaseinstdir}/share/extension/autoinc*
%{pgbaseinstdir}/share/extension/btree_gin*
%{pgbaseinstdir}/share/extension/btree_gist*
%{pgbaseinstdir}/share/extension/chkpass*
%{pgbaseinstdir}/share/extension/citext*
%{pgbaseinstdir}/share/extension/cube*
%{pgbaseinstdir}/share/extension/dblink*
%{pgbaseinstdir}/share/extension/dict_int*
%{pgbaseinstdir}/share/extension/dict_xsyn*
%{pgbaseinstdir}/share/extension/earthdistance*
%{pgbaseinstdir}/share/extension/file_fdw*
%{pgbaseinstdir}/share/extension/fuzzystrmatch*
%{pgbaseinstdir}/share/extension/hstore*
%{pgbaseinstdir}/share/extension/insert_username*
%{pgbaseinstdir}/share/extension/intagg*
%{pgbaseinstdir}/share/extension/intarray*
%{pgbaseinstdir}/share/extension/isn*
%{pgbaseinstdir}/share/extension/lo*
%{pgbaseinstdir}/share/extension/ltree*
%{pgbaseinstdir}/share/extension/moddatetime*
%{pgbaseinstdir}/share/extension/pageinspect*
%{pgbaseinstdir}/share/extension/pg_buffercache*
%{pgbaseinstdir}/share/extension/pg_freespacemap*
%{pgbaseinstdir}/share/extension/pg_prewarm*
%{pgbaseinstdir}/share/extension/pg_stat_statements*
%{pgbaseinstdir}/share/extension/pg_trgm*
%{pgbaseinstdir}/share/extension/pgcrypto*
%{pgbaseinstdir}/share/extension/pgrowlocks*
%{pgbaseinstdir}/share/extension/pgstattuple*
%{pgbaseinstdir}/share/extension/postgres_fdw*
%{pgbaseinstdir}/share/extension/refint*
%{pgbaseinstdir}/share/extension/seg*
%{pgbaseinstdir}/share/extension/sslinfo*
%{pgbaseinstdir}/share/extension/tablefunc*
%{pgbaseinstdir}/share/extension/tcn*
%{pgbaseinstdir}/share/extension/test_parser*
%{pgbaseinstdir}/share/extension/test_shm_mq*
%{pgbaseinstdir}/share/extension/timetravel*
%{pgbaseinstdir}/share/extension/tsearch2*
%{pgbaseinstdir}/share/extension/unaccent*
%{pgbaseinstdir}/share/extension/uuid-ossp*
%{pgbaseinstdir}/share/extension/worker_spi*
%{pgbaseinstdir}/share/extension/xml2*
%{pgbaseinstdir}/bin/oid2name
%{pgbaseinstdir}/bin/pgbench
%{pgbaseinstdir}/bin/vacuumlo
%{pgbaseinstdir}/bin/pg_archivecleanup
%{pgbaseinstdir}/bin/pg_recvlogical
%{pgbaseinstdir}/bin/pg_standby
%{pgbaseinstdir}/bin/pg_test_timing
%{pgbaseinstdir}/bin/pg_upgrade
%{pgbaseinstdir}/bin/pg_xlogdump
%{pgbaseinstdir}/share/man/man1/oid2name.1
%{pgbaseinstdir}/share/man/man1/pg_archivecleanup.1
%{pgbaseinstdir}/share/man/man1/pg_recvlogical.1
%{pgbaseinstdir}/share/man/man1/pg_standby.1
%{pgbaseinstdir}/share/man/man1/pg_test_fsync.1
%{pgbaseinstdir}/share/man/man1/pg_test_timing.1
%{pgbaseinstdir}/share/man/man1/pg_upgrade.1
%{pgbaseinstdir}/share/man/man1/pg_xlogdump.1
%{pgbaseinstdir}/share/man/man1/pgbench.1
%{pgbaseinstdir}/share/man/man1/vacuumlo.1

%files libs -f pg_libpq5.lst
%defattr(-,root,root)
%{pgbaseinstdir}/lib/libpq.so.*
%{pgbaseinstdir}/lib/libecpg.so*
%{pgbaseinstdir}/lib/libpgtypes.so.*
%{pgbaseinstdir}/lib/libecpg_compat.so.*
%{pgbaseinstdir}/lib/libpqwalreceiver.so
%config(noreplace) %{pgbaseinstdir}/share/%{longname}-%{majorversion}-libs.conf

%files server -f pg_server.lst
%defattr(-,root,root)
%{pgbaseinstdir}/bin/%{longname}%{shortmajorversion}-setup
%if %systemd
%{_unitdir}/%{unitname}.service
%else
%config(noreplace) %{_initrddir}/%{unitname}
%endif
%{pgbaseinstdir}/bin/%{longname}%{shortmajorversion}-check-db-dir
%if %pam
%config(noreplace) /etc/pam.d/%{longname}%{shortmajorversion}
%endif
%attr (755,root,root) %dir /etc/sysconfig/pgsql
%{pgbaseinstdir}/bin/initdb
%{pgbaseinstdir}/bin/pg_controldata
%{pgbaseinstdir}/bin/pg_ctl
%{pgbaseinstdir}/bin/pg_resetxlog
%{pgbaseinstdir}/bin/postgres
%{pgbaseinstdir}/bin/postmaster
%{pgbaseinstdir}/share/man/man1/initdb.*
%{pgbaseinstdir}/share/man/man1/pg_controldata.*
%{pgbaseinstdir}/share/man/man1/pg_ctl.*
%{pgbaseinstdir}/share/man/man1/pg_resetxlog.*
%{pgbaseinstdir}/share/man/man1/postgres.*
%{pgbaseinstdir}/share/man/man1/postmaster.*
%{pgbaseinstdir}/share/postgres.bki
%{pgbaseinstdir}/share/postgres.description
%{pgbaseinstdir}/share/postgres.shdescription
%{pgbaseinstdir}/share/system_views.sql
%{pgbaseinstdir}/share/*.sample
%{pgbaseinstdir}/share/timezonesets/*
%{pgbaseinstdir}/share/tsearch_data/*.affix
%{pgbaseinstdir}/share/tsearch_data/*.dict
%{pgbaseinstdir}/share/tsearch_data/*.ths
%{pgbaseinstdir}/share/tsearch_data/*.rules
%{pgbaseinstdir}/share/tsearch_data/*.stop
%{pgbaseinstdir}/share/tsearch_data/*.syn
%{pgbaseinstdir}/lib/dict_int.so
%{pgbaseinstdir}/lib/dict_snowball.so
%{pgbaseinstdir}/lib/dict_xsyn.so
%{pgbaseinstdir}/lib/euc2004_sjis2004.so
%{pgbaseinstdir}/lib/plpgsql.so
%dir %{pgbaseinstdir}/share/extension
%{pgbaseinstdir}/share/extension/plpgsql*
%{pgbaseinstdir}/lib/test_parser.so
%{pgbaseinstdir}/lib/tsearch2.so

%dir %{pgbaseinstdir}/lib
%dir %{pgbaseinstdir}/share
%attr(700,postgres,postgres) %dir %{pguserhome}
%attr(700,postgres,postgres) %dir %{pgvarlib}
%attr(700,postgres,postgres) %dir %{pgdatadir}
%attr(700,postgres,postgres) %dir %{pgbackupsdir}
%{pgbaseinstdir}/lib/*_and_*.so
%{pgbaseinstdir}/share/conversion_create.sql
%{pgbaseinstdir}/share/information_schema.sql
%{pgbaseinstdir}/share/snowball_create.sql
%{pgbaseinstdir}/share/sql_features.txt

%files devel -f pg_devel.lst
%defattr(-,root,root)
%{pgbaseinstdir}/include/*
%{pgbaseinstdir}/bin/ecpg
%{pgbaseinstdir}/lib/libpq.so
%{pgbaseinstdir}/lib/libecpg.so
%{pgbaseinstdir}/lib/libpq.a
%{pgbaseinstdir}/lib/libecpg.a
%{pgbaseinstdir}/lib/libecpg_compat.so
%{pgbaseinstdir}/lib/libecpg_compat.a
%{pgbaseinstdir}/lib/libpgcommon.a
%{pgbaseinstdir}/lib/libpgport.a
%{pgbaseinstdir}/lib/libpgtypes.so
%{pgbaseinstdir}/lib/libpgtypes.a
%{pgbaseinstdir}/lib/pgxs/*
%{pgbaseinstdir}/lib/pkgconfig/*
%{pgbaseinstdir}/share/man/man1/ecpg.*

%if %plperl
%files plperl -f pg_plperl.lst
%defattr(-,root,root)
%{pgbaseinstdir}/lib/plperl.so
%{pgbaseinstdir}/share/extension/plperl*
%endif

%if %pltcl
%files pltcl -f pg_pltcl.lst
%defattr(-,root,root)
%{pgbaseinstdir}/lib/pltcl.so
%{pgbaseinstdir}/bin/pltcl_delmod
%{pgbaseinstdir}/bin/pltcl_listmod
%{pgbaseinstdir}/bin/pltcl_loadmod
%{pgbaseinstdir}/share/unknown.pltcl
%{pgbaseinstdir}/share/extension/pltcl*
%endif

%if %plpython
%files plpython -f pg_plpython.lst
%defattr(-,root,root)
%{pgbaseinstdir}/lib/plpython*.so
%{pgbaseinstdir}/share/extension/plpython2u*
%{pgbaseinstdir}/share/extension/plpythonu*
%endif

%if %test
%files test
%defattr(-,postgres,postgres)
%attr(-,postgres,postgres) %{pgbaseinstdir}/lib/test/*
%attr(-,postgres,postgres) %dir %{pgbaseinstdir}/lib/test
%endif

# Revision history (changelog)
# ----------------------------

%changelog

* Tue Mar 22 2016 Craig Ringer <craig@2ndquadrant.com> 9.4.6_bdr1-1_2ndQuadrant
- Update to 9.4.6
- Remove -fno-omit-frame-pointer (suspected binary compat issues with PGDG)

* Tue Oct 20 2015 Craig Ringer <craig@2ndquadrant.com> 9.4.5_bdr1-1_2ndQuadrant
- Release for BDR 0.9.3
- Update to 9.4.5

* Mon Jul 6 2015 Craig Ringer <craig@2ndquadrant.com> 9.4.4_bdr1-1_2ndQuadrant
- Release for bDR 0.9.2
- Update to 9.4.4
- Remove Conflicts: with self due to issues with rpm vs yum handling differences

* Tue May 26 2015 Craig Ringer <craig@2ndquadrant.com> 9.4.2_bdr1-1_2ndQuadrant
- Release for BDR 0.9.1
- Update to 9.4.2
- pg_dump changes for global sequences

* Tue Mar 24 2015 Craig Ringer <craig@2ndquadrant.com> 9.4.1_bdr2-1_2ndQuadrant
- Release for BDR 0.9.0
- Deparse fixes
- Fix DoNotReplicateRepNodeId

* Mon Feb 9 2015 Craig Ringer <craig@2ndquadrant.com> 9.4.1_bdr1-1_2ndQuadrant
- Update to 9.4.1

* Sun Feb 8 2015 Craig Ringer <craig@2ndquadrant.com> 9.4.0_bdr2-1_2ndQuadrant
- Update to 9.4.0 STABLE plus recent fixes from REL9_4_STABLE on top

* Wed Dec 24 2014 Craig Ringer <craig@2ndquadrant.com> 9.4.0_bdr1-1_2ndQuadrant
- Update to 9.4.0

* Fri Nov 28 2014 Craig Ringer <craig@2ndquadrant.com> 9.4rc1_bdr1-1_2ndQuadrant
- Update to 9.4rc1

* Fri Sep 19 2014 Craig Ringer <craig@2ndquadrant.com> 9.4beta2_bdr1-1_2ndQuadrant
- Publish the first release of Pg with BDR patches that doesn't contain the BDR
  extension its self.
- Move BDR extension into separate postgresql-bdr94-bdr package

* Tue Sep 2 2014 Craig Ringer <craig@2ndquadrant.com> bdr0.7.1_1_2ndQuadrant
- BDR 0.7.1 release (tag bdr/0.7.1) based on PostgreSQL 9.4beta2 at
  rev 364f7cd4b6d2bb89be55c8915fcd08b69b5eb84e
- Fix a bug that caused large volumes of data to be logged unnecessarily by
  conflict logging
- Fix a leak in conflict logging code
- Deparse support for COMMENT ON
- Permit ALTER TABLE ... DISABLE/ENABLE TRIGGER commands
- Add pg_replication_identifier_drop interface and use it from within
  bdr_init_copy and init_replica
- Disable function body checks during apply
- Ensure conflict history sequence is always created as a local sequence
- Don't show sequence amdata in psql \d output
- Bug fixes in deparse
- Bug fixes in commit timestamps
- More regression tests

* Thu Aug 28 2014 Craig Ringer <craig@2ndquadrant.com> bdr0.7.0_1_2ndquadrant
- BDR 0.7.0 release (tag bdr/0.7.0) based on PostgreSQL 9.4beta2 at
  rev 364f7cd4b6d2bb89be55c8915fcd08b69b5eb84e
- Add postgresql-bdr94-bdr package
- Unified spec file for RHEL 5/6/7 and Fedora 19/20 with build with distro
  conditionals instead of separate specs for each distro, compatibility with
  the PGDG repository
- Change datadir to /var/lib/pgsql/9.4-bdr
- Always compile with -fno-omit-frame-pointer so we can use perf on x64
- Conflict with PGDG 9.4 RPMs and provide postgresql94, so BDR can be used
  in place of PGDG and PGDG won't replace BDR on yum update.
- Use libuuid instead of ossp-uuid (improvement from PGDG)
- Fixed Perl dependency error (fix for PGDG RPM)
- Removed some obsolete files and macros from PGDG spec
- Used consistent Perl Requires: form (fix for PGDG RPM)
- Fixed missing Group field (fix for PGDG RPM)
- Don't use of-Wl,--as-needed as it breaks RHEL5 (fix for PGDG RPM)
