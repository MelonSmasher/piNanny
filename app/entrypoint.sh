#!/usr/bin/env bash

rm -rf /tmp/resin/images /usr/src/app/pi-nanny/public/images/stream;

mkdir -p /tmp/resin/images && \
    mkdir -p /usr/src/app/pi-nanny/public/images && \
    ln -s /tmp/resin/images /usr/src/app/pi-nanny/public/images/stream

# Fire up the kernel mods
modprobe bcm2835-v4l2;
#modprobe v4l2_common;
v4l2-ctl --overlay=1;

# Set mic volume
amixer -c 1 sset Mic 100%;

# Run Supervisor
/usr/bin/supervisord