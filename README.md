This tree contains the spec files, init scripts, etc for BDR, BDR-pg, and UDR
packages. Tags named `rpm/bdr-[xxx]` contain releases of the RPMs.

The extension and PostgreSQL sources are not present here, and should be
placed at an appropriate public download location then downloaded with
`spectool`. Do *not* check source tarballs in here.

# One-time setup

To build packages you'll need mock and you'll probably want some related tools:

    # Install tools
    yum install yum-utils rpmdevtools repoview createrepo rpm-sign mock

You *must* use Mock 1.2.7 or newer. It's packaged in Fedora 21. If you're on
something older, rebuild the Fedora 21 srpm, or just build packages for your OS
using mock on Fedora 21.

If you're going to prepare release or snapshot tarballs you'll also need to:

    yum groupinstall "Development Tools"
    yum-builddep postgresql
    yum install openjade jadetex docbook-dtds docbook5-schemas docbook-style-dsssl docbook-style-xsl


# Versioning

The principle followed by these packages is:

* The Version changes only when the BDR source code changes, resulting in a new
  source tarball;

* The Release number is incremented when the BDR RPMs are modified without a
  new source tarball. This might be the addition of RPM-specific patches, fixes
  to the specfile, etc.

# Building from spec files

You can't use the spec files in the main `rpm/bdr` branch un-edited.
You must copy `bdr.spec.in` to `bdr.spec` and then edit it to define either
`%githash` (for a snapshot build) or `%gittag` (for a build of a tagged
upstream release). You'll also have to prepare the sources using specific
commands so that their contents and filenames are what the packages expect.
See "RELEASES" and "SNAPSHOTS" below for details on how to prepare the spec
files and sources.

Assuming that you've checked out a tag (which will already contain prepared
spec files, etc) or you've followed the snapshot or release process, you're
ready to build the packages.

Build the RPMs using `mock` 1.2.7 or newer. You should not need to install
dependencies manually; just use `mock` to build the packages for your target
OS/version in a chroot.

For official BDR releases, packages for all target RHEL, CentOS and Fedora
releases are built on Fedora 21 using `mock`.

It should be possible to directly `rpmbuild` these packages on the target host
by building a srpm with `rpmbuild -bs`, using `yum-builddep` from `yum-utils`
to install build depends, then `rpmbuild -ba` the srpm to produce RPMs. That's
what `mock` does behind the scenes, so it should work.

The official BDR RPM releases (see "Preparing official releases") use automation
for reproducible builds. For ad-hoc builds of patched RPMs or snapshots, you
can just run some manual `mock` commands, specifying any valid target from
`/etc/mock/targets` where called for with `-r`.

## Building bdr-pg and bdr from specs

    (cd rpm && spectool -g postgresql94.spec )
    mock -r fedora-21-x86_64 --buildsrpm --spec rpm/postgresql94.spec --sources rpm/ --resultdir fedora-21
    mock -r fedora-21-x86_64 --rebuild fedora-21/postgresql-bdr94-*.src.rpm --resultdir fedora-21

    (cd rpm && spectool -g bdr.spec)
    mock -r fedora-21-x86_64 --buildsrpm --spec rpm/bdr.spec --sources rpm/ --resultdir fedora-21
    mock -r fedora-21-x86_64 --init
    mock -r fedora-21-x86_64 --install fedora-21/postgresql-bdr94-*.rpm
    mock -r fedora-21-x86_64 --no-clean --rebuild fedora-21/postgresql-bdr94-bdr-*.src.rpm --resultdir fedora-21/


## Building udr from specs

To build UDR, you need to copy the mock target(s) you want to build from
`/etc/mock/targets` to a temporary path, then add the PGDG yum repository for
that target to the target definition file so that `mock` knows where to get
the stock PostgreSQL RPMs.

Alternately, you can use the same approach as in "building bdr-pg and bdr from
specs", manually installing the RPMs into the `mock` chroot before performing
the UDR build.  You will find `yumdownloader` useful for this.

    (cd rpm && spectool -g udr.spec)
    mock -r fedora-21-x86_64 --buildsrpm --spec rpm/udr.spec --sources rpm/ --resultdir fedora-21

 then either:

    yumdownloader postgresql...[xxx]
    mock --init
    mock --install [xxx]
    mock -r fedora-21-x86_64 --no-clean --rebuild fedora-21/postgresql94-udr-*.src.rpm --resultdir fedora-21

or invoke `mock --rebuild` with `mock -r /path/to/my/custom/fedora-21-x86_64.cfg`, where the custom
config has the PGDG PostgreSQL repository configured:

    mock -r ./my-fedora-21-with-pgdg_x86_64.cfg --rebuild fedora-21/postgresql94-udr-*.src.rpm --resultdir fedora-21



# Snapshots

A snapshot RPM is an RPM that's built from an arbitrary git ref, not from
a tagged upstream release.

You'll be building a snapshot if you've customised BDR or you're doing a hotfix
build.

Official BDR RPMs built from tagged upstream sources require a somewhat
different process; see `README-releases.md` for details on that.

To build a snapshot of an arbitrary BDR git ref, you need to make a dist
tarball of the patched PostgreSQL sources produce SRPMs and RPMs from that,
then produce a dist tarball of the bdr extension git tree and make SRPMs and
RPMs for that.

## Building dist tarballs for snapshot RPMs

If you're not compiling a final tagged release package, you need to prep
a dist tarball for BDR and for the patched PostgreSQL. (The latter isn't
required for UDR).

Skip this step if you're building a package for a tagged release (where there's
a %bdrtag value set in the spec file), as in that case you MUST use the tarball
produced for the release and uploaded to the package server and it'll be
downloaded for you.

The snapshot dist tarball name must match the pattern in the BDR specfile, as
shown on the "make dist" line below. The content path must match, not just the
filename, which is why we override `distdir` rather than renaming the file:

    # Grab the repository
    git clone --bare \
        git://git.postgresql.org/git/2ndquadrant_bdr.git \
        2ndquadrant_bdr.git

    # check out a workspace for the patched PostgreSQL
    git clone --reference 2ndquadrant_bdr.git \
        --branch bdr-pg/REL9_4_STABLE \
        git://git.postgresql.org/git/2ndquadrant_bdr.git \
        postgresql-bdr
    
    # Make a dist tarball
    pushd postgresql-bdr
    # We apply a simple revision number on top of the PostgreSQL version
    # for bdr-patched PostgreSQL. Whatever you use here should match
    # the %define bdrrev line in postgresql94.spec
    pgbdrrelease=1
    git checkout bdr-pg/REL9_4_STABLE
    # No need for any options, it's only to create the makefiles
    # for "make dist".
    ./configure
    BDR_PG_GITHASH=$(git rev-parse --short HEAD)
    make -s distdir='postgresql-bdr-$(VERSION)_'"bdr${pgbdrrelease}-git${BDR_PG_GITHASH}" dist
    popd

You'll also need a dist tarball of the BDR extension, so prepare that now.
(This extension tarball is also used for UDR builds).

For the purpose of making a dist tarball it does not matter if you configure
against unpatched 9.4 or against BDR 9.4, you just need a valid Makefile.

Assuming you already cloned the repository as given above:

    git clone --reference 2ndquadrant_bdr.git \
        --branch bdr-plugin/next \
        git://git.postgresql.org/git/2ndquadrant_bdr.git \
        postgresql-bdr-extension

    pushd postgresql-bdr-extension
    ./autogen.sh
    PATH=/path/to/some/postgresql/9.4/bin:$PATH ./configure
    BDR_EXT_GITHASH=$(git rev-parse --short HEAD)
    make distdir='bdr-$(BDR_VERSION)-git'${BDR_EXT_GITHASH} git-dist
    popd postgresql-bdr-extension

to prepare a tarball of a snapshot of git.

## Building the snapshot SRPMs and RPMs

Build RPMs of a git snapshot of the BDR-patched PostgreSQL for just `fedora 20 x86_64`:

    pushd packaging
    pushd rpm
    # Copy the dist tarball to the cwd
    cp /path/to/postgresql-*.bz2 .
    # Create a checksum file, required by the package script
    md5sum postgresql-*.bz2 > $(echo postgresql-*.bz2).md5
    # Edit the specfile to add the %githash and update %pgbdrrelease
    sed \
        -e "s/^#% define githash.*\$/%define githash ${BDR_PG_GITHASH}/" \
        -e "s/^%define pgbdrrelease .*\$/%define pgbdrrelease ${pgbdrrelease}/" \
        postgresql94.spec.in > postgresql94.spec
    # Download the docs PDF
    spectool --gf postgresql94.spec
    popd
    # If needed, edit rpm/postgresql94.spec to change other settings (Version, etc), then:
    ./mock-build-all.sh

It's a similar process to build the BDR extension RPM against the patched
PostgreSQL sources:

    pushd rpm
    cp /path/to/postgresql-bdr-extension/bdr-*.bz2
    md5sum bdr-*.bz2 > $(echo bdr-*.bz2).md5
    # Edit the specfile to add the %githash
    sed \
        -e "s/^#% define githash.*\$/%define githash ${BDR_EXT_GITHASH}/" \
        bdr.spec.in > bdr.spec
    popd
    # Edit the specfile to set any other params like version, then:
    SPECFILE=rpm/bdr.spec ./mock-buildall.sh

The first run will take longer because it has to set up and cache the mock
chroots.

# Preparing official releases

Additional steps are required to prepare an official BDR RPM release. The
documentation is in the private packaging tree along with information about
the correct signing keys to use, repository locations, etc.
