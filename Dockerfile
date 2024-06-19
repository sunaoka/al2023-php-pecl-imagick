# syntax=docker/dockerfile:1.4
ARG PLATFORM
FROM --platform=$PLATFORM public.ecr.aws/amazonlinux/amazonlinux:2023 as base

ARG PHP_VER

RUN <<EOT bash -ex
  dnf install -y rpm-build
  if [ "${PHP_VER}" = "8.3" ]; then
    ARCH=$(uname -m)
    dnf install -y \
      https://github.com/sunaoka/al2023-php83/releases/download/8.3.8-1.\${ARCH}/php8.3-devel-8.3.8-1.amzn2023.0.1.\${ARCH}.rpm \
      https://github.com/sunaoka/al2023-php83/releases/download/8.3.8-1.\${ARCH}/php8.3-cli-8.3.8-1.amzn2023.0.1.\${ARCH}.rpm \
      https://github.com/sunaoka/al2023-php83/releases/download/8.3.8-1.\${ARCH}/php8.3-common-8.3.8-1.amzn2023.0.1.\${ARCH}.rpm \
      https://github.com/sunaoka/al2023-php83/releases/download/8.3.8-1.\${ARCH}/php8.3-xml-8.3.8-1.amzn2023.0.1.\${ARCH}.rpm \
      https://github.com/sunaoka/al2023-php83/releases/download/8.3.8-1.\${ARCH}/php8.3-process-8.3.8-1.amzn2023.0.1.\${ARCH}.rpm
  else
    dnf install -y php${PHP_VER}-devel
  fi
  dnf install -y php-pear
  dnf install -y ImageMagick-devel
EOT

FROM base

ARG PHP_VER
ENV PHP_VER ${PHP_VER}

CMD rpmbuild -ba --clean --define "_smp_mflags %{nil}" --define "php_ver ${PHP_VER}" /root/rpmbuild/SPECS/php-pecl-imagick.spec
