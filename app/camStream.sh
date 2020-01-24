#!/bin/bash

base="/tmp/resin/images"

set -x

cd $base;
rm -rf $base/*

# fifos seem to work more reliably than pipes - and the fact that the
# fifo can be named helps ffmpeg guess the format correctly.
mkfifo live.h264
raspivid -w ${v4l2_WIDTH} -h ${v4l2_HEIGHT} -fps ${v4l2_FRAME_RATE} -t 86400000 -b ${v4l2_BIT_RATE} -o --inline > live.h264 &

# Letting the buffer fill a little seems to help ffmpeg to id the stream
sleep 2

ffmpeg -y \
  -i live.h264 \
  -f ${v4l2_MIC_FORMAT} -r:a ${v4l2_MIC_FREQ} -ac ${v4l2_MIC_CHAN} -itsoffset ${v4l2_AUDIO_OFFSET} -i ${v4l2_MIC_DEV} \
  -c:v copy \
  -c:a aac -strict -2  -b:a 128k \
  -tune zerolatency \
  -map 0:0 -map 1:0 \
  -f hls \
  -hls_flags delete_segments+append_list+split_by_time \
  -hls_list_size 6 \
  -hls_segment_type mpegts \
  -hls_segment_filename "%08d.ts" \
  live.m3u8

# ffmpeg -i rtsp://127.0.0.1:%(ENV_v4l2_RTSP_PORT)s/unicast -codec:a aac -ac %(ENV_v4l2_MIC_CHAN)s -ar %(ENV_v4l2_MIC_FREQ)s -c:v h264 -b:v 2000k -f dash -window_size 4 -extra_window_size 0 -min_seg_duration 2000000 -remove_at_exit 1 manifest.mpd
# vim:ts=2:sw=2:sts=2:et:ft=sh