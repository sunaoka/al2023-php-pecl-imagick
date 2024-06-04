# syntax=docker/dockerfile:1.4
ARG PLATFORM
FROM --platform=$PLATFORM public.ecr.aws/amazonlinux/amazonlinux:2023 as base

ARG PHP_VER

RUN <<EOT
  dnf install -y rpm-build
  dnf install -y php${PHP_VER}-devel php-pear
  dnf install -y ImageMagick-devel
EOT

FROM base

ARG PHP_VER
ENV PHP_VER ${PHP_VER}

CMD rpmbuild -ba --clean --define "_smp_mflags %{nil}" --define "php_ver ${PHP_VER}" /root/rpmbuild/SPECS/php-pecl-imagick.spec
