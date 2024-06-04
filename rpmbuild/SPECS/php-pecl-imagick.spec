%global php_name   php

%global pecl_name  imagick

# we don't want -z defs linker flag
%undefine _strict_symbol_defs_build

%global with_zts   0%{!?_without_zts:%{?__zts%{php_name}:1}}
%global ini_name   40-%{pecl_name}.ini

%global have_devel 1

Summary:       Provides a wrapper to the ImageMagick library.
Name:          %{php_name}%{?php_ver}-pecl-%{pecl_name}
Version:       3.7.0
Release:       1%{?dist}.0.1
License:       PHP
Group:         Development/Languages
URL:           http://pecl.php.net/package/%{pecl_name}

Source:        https://pecl.php.net/get/imagick-3.7.0.tgz

BuildRequires: %{php_name}-devel
BuildRequires: php%{?pear_ver}-pear
BuildRequires: ImageMagick-devel >= 6.9.0

Requires:      php(zend-abi) = %{expand:%{%{php_name}_zend_api}}
Requires:      php(api) = %{expand:%{%{php_name}_core_api}}

Provides:      %{php_name}-pecl(%{pecl_name}) = %{version}
Provides:      %{php_name}-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:      %{php_name}-%{pecl_name} = %{version}-%{release}
Provides:      %{php_name}-%{pecl_name}%{?isa} = %{version}-%{release}

%description
Imagick is a native php extension to create and modify images using
the ImageMagick API.

This extension requires ImageMagick version 6.9.0 and PHP 8.1.0+.

%if 0%{?have_devel}
%package devel
Summary:       Development files for %{name}
Group:         Development/Languages
BuildArch:     noarch

Requires:      %{php_name}-devel
Requires:      %{name} = %{version}

%description devel
Development files for building against the PECL %{pecl_name} module.
%endif

%prep
%setup -qc

%{?_licensedir:sed -e '/LICENSE/s/role="doc"/role="src"/' -i package.xml}

mv %{pecl_name}-%{version} NTS
cd NTS

# Some packages provide their license in the file 'COPYING'; we expect
# to find it in 'LICENSE'
if [ ! -f LICENSE ] && [ -f COPYING ]
then
  cp COPYING LICENSE
fi

# Perform package-specific operations

cd ..

# Some packages come with their own .ini files, so we'll try to use them
if [ -f NTS/%{pecl_name}.php.ini ]
then
  cp NTS/%{pecl_name}.php.ini %{ini_name}
elif [ -f NTS/%{pecl_name}.ini ]
then
  cp NTS/%{pecl_name}.ini %{ini_name}
else
  cat >%{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF
fi
# Some packages' .ini files don't actually load the extension
if ! grep -q 'extension=%{pecl_name}' %{ini_name}
then
  sed -i '1iextension=%{pecl_name}.so\n' %{ini_name}
fi

%if %{with_zts}
# Duplicate sources tree for ZTS build
cp -pr NTS ZTS
%endif

%build
cd NTS
%if 0%{?__phpize%{?php_ver}}
%{expand:%{__phpize%{?php_ver}}}
%else
%{_bindir}/phpize
%endif
%configure \
    --enable-%{pecl_name} \
%if 0%{?__phpconfig%{?php_ver}}
    --with-php-config=%{expand:%{__phpconfig%{?php_ver}}}
%else
    --with-php-config=%{_bindir}/php-config
%endif
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%if 0%{?__ztsphpize%{?php_ver}}
%{expand:%{__ztsphpize%{?php_ver}}}
%else
%{_bindir}/zts-phpize
%endif
%configure \
    --enable-%{pecl_name} \
%if 0%{?__ztsphpconfig%{?php_ver}}
    --with-php-config=%{expand:%{__ztsphpconfig%{?php_ver}}}
%else
    --with-php-config=%{_bindir}/zts-php-config
%endif
make %{?_smp_mflags}
%endif

%install
make -C NTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{expand:%{%{php_name}_inidir}}/%{ini_name}

install -D -m 644 package.xml %{buildroot}%{expand:%{pecl%{?pear_ver}_xmldir}}/%{name}.xml

%if %{with_zts}
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{expand:%{%{php_name}_ztsinidir}}/%{ini_name}
%endif

# Documentation
cd NTS
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do
    install -Dpm 644 $i %{buildroot}%{expand:%{pecl%{?pear_ver}_docdir}}/%{pecl_name}/$i
done

%check
if [ "$(rpm -q --qf '%%{version}' ImageMagick)" = "6.7.8.9" ]
then
  # https://bugzilla.redhat.com/show_bug.cgi?id=1228034
  rm ?TS/tests/bug20636.phpt
  rm ?TS/tests/151_Imagick_subImageMatch_basic.phpt
fi

cd NTS
# minimal load test of NTS extension
%if 0%{?__%{php_name}}
%{expand:%{__%{php_name}}} \
%else
%{_bindir}/php \
%endif
    --define extension=./modules/%{pecl_name}.so \
    --modules | grep -i '^%{pecl_name}$'

# upstream test suite for NTS extension
NO_INTERACTION=true make test

%if %{with_zts}
cd ../ZTS
# minimal load test of ZTS extension
%if 0%{?__zts%{php_name}}
%{expand:%{__zts%{php_name}}} \
%else
%{_bindir}/zts-php \
%endif
    --define extension=./modules/%{pecl_name}.so \
    --modules | grep -i '^%{pecl_name}$'

# upstream test suite for ZTS extension
NO_INTERACTION=true make test
%endif

%files
%license NTS/LICENSE
%{expand:%{pecl%{?pear_ver}_xmldir}}/%{name}.xml

%config(noreplace) %{expand:%{%{php_name}_inidir}}/%{ini_name}
%{expand:%{%{php_name}_extdir}}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{expand:%{%{php_name}_ztsinidir}}/%{ini_name}
%{expand:%{%{php_name}_ztsextdir}}/%{pecl_name}.so
%endif

%{_datadir}/doc/pecl%{?pear_ver}/%{pecl_name}

%if 0%{?have_devel}
%files devel
%{_includedir}/%{php_name}/ext/%{pecl_name}
%endif

%changelog
* Tue Jun 04 2024 SUNAOKA Norifumi <sunaoka@pocari.org> - 3.7.0-1
- Update 3.7.0

* Mon Jun 10 2019 Trinity Quirk <tquirk@amazon.com> - 3.4.4-1
- Package updated to 3.4.4.

* Mon Oct 08 2018 Trinity Quirk <tquirk@amazon.com> - 3.4.3-3
- Removed arch-specific requirement for -devel subpackage

* Mon Oct 08 2018 Trinity Quirk <tquirk@amazon.com> - 3.4.3-2
- Made ini snippets pre-7.2 friendly

* Tue Sep 11 2018 Trinity Quirk <tquirk@amazon.com> - 3.4.3-1
- Package created via download from pecl.php.net.
