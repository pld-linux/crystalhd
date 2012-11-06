#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_with	kernel		# kernel module (already in 3.6 staging)
%bcond_without	userspace	# userspace
%bcond_without	gstreamer	# gstreamer 0.10 module
#
%if %{without kernel}
%undefine	with_dist_kernel
%endif
Summary:	Linux Crystal HD drivers
Summary(pl.UTF-8):	Sterowniki Crystal HD dla Linuksa
Name:		crystalhd
Version:	3.10.0
%define	snap	20121105
%define		rel	0.%{snap}.1
Release:	%{rel}
License:	LGPL v2.1 (libcrystalhd), GPL v2 (driver), Broadcom (firmware)
Group:		Libraries
# http://git.linuxtv.org/jarod/crystalhd.git
# git clone git://linuxtv.org/jarod/crystalhd.git
Source0:	%{name}.tar.xz
# Source0-md5:	e7f8cc40c698de485fdb2d76580ea808
URL:		http://www.broadcom.com/support/crystal_hd/
BuildRequires:	autoconf >= 2.50
%if %{with kernel}
BuildRequires:	kernel-module-build >= 3:2.6.20}
%endif
%if %{with userspace}
BuildRequires:	libstdc++-devel
%if %{with gstreamer}
BuildRequires:	automake
BuildRequires:	gstreamer0.10-devel >= 0.10.0
BuildRequires:	gstreamer0.10-plugins-base-devel >= 0.10.0
BuildRequires:	libtool
BuildRequires:	pkgconfig
%endif
%endif
ExclusiveArch:	i686 pentium4 athlon %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Linux Crystal HD drivers.

%description -l pl.UTF-8
Sterowniki Crystal HD dla Linuksa.

%package -n kernel-video-crystalhd
Summary:	Linux kernel driver for Broadcom Crystal HD devices
Summary(pl.UTF-8):	Sterownik jądra Linuksa dla urządzeń Broadcom Crystal HD
Release:	%{rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
%endif

%description -n kernel-video-crystalhd
Linux kernel driver for Broadcom Crystal HD devices.

%description -n kernel-video-crystalhd -l pl.UTF-8
Sterownik jądra Linuksa dla urządzeń Broadcom Crystal HD.

%package firmware
Summary:	Firmware for Broadcom Crystal HD devices
Summary(pl.UTF-8):	Firmware dla urządzeń Broadcom Crystal HD
Release:	%{rel}
License:	Broadcom
Group:		Base

%description firmware
Firmware for Broadcom Crystal HD devices.

%description firmware -l pl.UTF-8
Firmware dla urządzeń Broadcom Crystal HD.

%package -n libcrystalhd
Summary:	Crystal HD device interface library
Summary(pl.UTF-8):	Biblioteka interfejsu do urządzeń Crystal HD
Release:	%{rel}
License:	LGPL v2.1
Group:		Libraries
#Requires:	cpuinfo(sse2)

%description -n libcrystalhd
Crystal HD device interface library.

%description -n libcrystalhd -l pl.UTF-8
Biblioteka interfejsu do urządzeń Crystal HD.

%package -n libcrystalhd-devel
Summary:	Header files for Crystal HD library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki Crystal HD
Release:	%{rel}
License:	LGPL v2.1
Group:		Development/Libraries
Requires:	libcrystalhd = %{version}-%{rel}

%description -n libcrystalhd-devel
Header files for Crystal HD library.

%description -n libcrystalhd-devel -l pl.UTF-8
Pliki nagłówkowe biblioteki Crystal HD.

%package -n gstreamer0.10-bcmdec
Summary:	Broadcom video decoder plugin for GStreamer
Summary(pl.UTF-8):	Wtyczka dekodera obrazu Broadcoma dla GStreamera
Release:	%{rel}
License:	LGPL v2.1
Group:		Libraries
Requires:	libcrystalhd = %{version}-%{rel}

%description -n gstreamer0.10-bcmdec
Broadcom video decoder plugin for GStreamer.

%description -n gstreamer0.10-bcmdec -l pl.UTF-8
Wtyczka dekodera obrazu Broadcoma dla GStreamera.

%prep
%setup -q -n %{name}

%build
cd driver/linux
%{__autoconf}
%configure \
	--with-kernel=%{_kernelsrcdir}
%if %{with kernel}
%{__make}
%endif
cd ../..

%if %{with userspace}
%{__make} -C linux_lib/libcrystalhd \
	CXX="%{__cxx}" \
	BCGCC="%{__cxx}" \
	CPPFLAGS='$(INCLUDES) %{rpmcxxflags} -D__LINUX_USER__ -Wall -fPIC -shared -fstrict-aliasing -msse2'

%if %{with gstreamer}
cd filters/gst/gst-plugin
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-static
%{__make} \
	CC="%{__cxx}" \
	CPP="%{__cxx}" \
	BCMDEC_CFLAGS="-I. -I../../../../linux_lib/libcrystalhd -I../../../../include -D__LINUX_USER__ -DWMV_FILE_HANDLING" \
	BCMDEC_LDFLAGS="-L../../../../linux_lib/libcrystalhd -lcrystalhd"
%endif
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -D driver/linux/crystalhd.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kerenl/drivers/video/crystalhd.ko
%endif

%if %{with userspace}
install -D driver/linux/20-crystalhd.rules $RPM_BUILD_ROOT/lib/udev/rules.d/20-crystalhd.rules

%{__make} -C linux_lib/libcrystalhd install \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{_libdir}

%if %{with gstreamer}
%{__make} -C filters/gst/gst-plugin install \
	DESTDIR=$RPM_BUILD_ROOT
%{__rm} $RPM_BUILD_ROOT%{_libdir}/gstreamer-0.10/libgst*.la
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-video-crystalhd
%depmod %{_kernel_ver}

%postun	-n kernel-video-crystalhd
%depmod %{_kernel_ver}

%post	-n libcrystalhd -p /sbin/ldconfig
%postun	-n libcrystalhd -p /sbin/ldconfig

%if %{with kernel}
%files -n kernel-video-crystalhd
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/video/crystalhd.ko*
%endif

%if %{with userspace}
%files firmware
%defattr(644,root,root,755)
/lib/firmware/bcm70012fw.bin
/lib/firmware/bcm70015fw.bin
/lib/udev/rules.d/20-crystalhd.rules

%files -n libcrystalhd
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcrystalhd.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libcrystalhd.so.3

%files -n libcrystalhd-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcrystalhd.so
%{_includedir}/libcrystalhd

%files -n gstreamer0.10-bcmdec
%defattr(644,root,root,755)
%doc filters/gst/gst-plugin/AUTHORS
%attr(755,root,root) %{_libdir}/gstreamer-0.10/libgstbcmdec.so
%endif
