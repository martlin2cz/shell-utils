#!/bin/bash -x

DEV_DIR=$(dirname $0)
APP_DIR=~/apps/tmate-assistant-app
SYSTEMD_DIR=~/.config/systemd/user

echo "make sure the app dir exist"
mkdir -p $APP_DIR

echo "copy the actual assistant script"
cp $DEV_DIR/assist-tmate.sh $APP_DIR

echo "prepare the systemd files"
mkdir -p $SYSTEMD_DIR
cp $DEV_DIR/tmate-assistant.service $SYSTEMD_DIR
cp $DEV_DIR/tmate-assistant.timer $SYSTEMD_DIR

echo "reload the systemd service"
systemctl --user daemon-reload
systemctl --user stop tmate-assistant.timer
systemctl --user disable tmate-assistant.timer
systemctl --user enable tmate-assistant.timer
systemctl --user start tmate-assistant.timer

