-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

Format: 3.0 (quilt)
Source: libyang2
Binary: libyang2, libyang2-dev, libyang2-tools, libyang-tools
Architecture: any all
Version: 2.0.112-6
Maintainer: Ondřej Surý <ondrej@debian.org>
Homepage: https://github.com/CESNET/libyang/
Standards-Version: 4.5.0
Vcs-Browser: https://github.com/CESNET/libyang/tree/libyang2
Vcs-Git: https://github.com/CESNET/libyang.git -b libyang2
Testsuite: autopkgtest
Testsuite-Triggers: gzip
Build-Depends: cmake, debhelper (>= 10), libcmocka-dev <!nocheck>, libpcre2-dev, pkg-config
Package-List:
 libyang-tools deb oldlibs optional arch=all
 libyang2 deb libs optional arch=any
 libyang2-dev deb libdevel optional arch=any
 libyang2-tools deb devel optional arch=any
Checksums-Sha1:
 4ab1637a95510b0558452d8cb2c998b04212ceb0 1075307 libyang2_2.0.112.orig.tar.gz
 050fad7a46ce6562806dda271f76bbf4166a1f4c 11468 libyang2_2.0.112-6.debian.tar.xz
Checksums-Sha256:
 909d7706185e2e7f85c1d6cb94c299c2c0a22b68363dde010981333f662ceac8 1075307 libyang2_2.0.112.orig.tar.gz
 6c78b291560488e59a7a845ff949ec700581148d1eef93e0bb96ab5562af6d70 11468 libyang2_2.0.112-6.debian.tar.xz
Files:
 4ac414ef27f3c4d14f96c2f49c58c2be 1075307 libyang2_2.0.112.orig.tar.gz
 aa798a069f506a243d337c18600477e5 11468 libyang2_2.0.112-6.debian.tar.xz

-----BEGIN PGP SIGNATURE-----

iQKTBAEBCgB9FiEEw2Gx4wKVQ+vGJel9g3Kkd++uWcIFAmGfUqdfFIAAAAAALgAo
aXNzdWVyLWZwckBub3RhdGlvbnMub3BlbnBncC5maWZ0aGhvcnNlbWFuLm5ldEMz
NjFCMUUzMDI5NTQzRUJDNjI1RTk3RDgzNzJBNDc3RUZBRTU5QzIACgkQg3Kkd++u
WcJEug//cLqrDm+XrWNnIs3Qr+VQVu9kFJ+RNhAhnXNqflN8Matcq6OUxc8Pnsk2
ODzX33Nl7vDpixWlkmbSWhPMk7z6+nzKkMPrqJ1pmQX/HaKLJudUdJ3W2oySL1M4
t6BVhnnBt/AyqbkOHSUxsLqgNF5Hwkyr5k0NxOsvpDUoQfMbDZbtscJyNyOC1ljv
8bqO6sk/c+mdeNxzWpX2J2rEh5zqPKLspWlCg2ub76Yff+koHPh+K4e4wlP3WxLn
T6+vsDgYkmOLxxjuL1DgPfo6id3h7ndkcJDvRG9gFbyxqKBwuhEyvqH7Q/xxBECM
yFIt9WvhJg+aH/3lYGgwP9M0BQRN5dz8EGWv9BR14+rN9Qt19oXZBckb17r7CZiM
Ld5VKrIM1QtfGY0dVoqYmbQ1Fl+fZTeoHSh7hlKX6VMS2XPCuWRM4iO8SXg0pxGw
i1YBD50JQgp7i09QXbjkOQRsGh+oa5YRsD41OnBSlA8ey5TUi2Iq/+KOLqKyQ/+2
lg1OzrGVi+goL2uGjz3FvbLOie4zM+XSrAx2h9z25h+taPcOQ8i+5FhfjPP9ztZi
mVkHd0IuFb3H+PCczCUxbWE3nfatEKx0vDeQcdNGt4Lyf1XGBhO+w36k0khYuJY6
GFki3FP05KGT2GM8vzyyKMdlheB8dN24C8IcNQaedvUmOEZdoEs=
=BsL+
-----END PGP SIGNATURE-----
