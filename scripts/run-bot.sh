#!/usr/bin/env bash
set -eo pipefail

if [ -z "$APP_COMPONENT" ]; then
    echo "Please set APP_COMPONENT"
    exit 1
fi

cd /srv/root

case $APP_COMPONENT in
    "bot")
        exec app/main.py
    ;;

    *)
        echo "'$APP_COMPONENT' isn't a known value for APP_COMPONENT"
    ;;
esac
