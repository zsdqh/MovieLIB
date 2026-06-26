#!/bin/sh
set -e

mc alias set local http://minio:9000 "$MINIO_USER" "$MINIO_PASSWORD"
mc mb local/"$MINIO_AVATAR_BUCKET_NAME" | true
mc mb local/"$MINIO_MOVIE_BUCKET_NAME" | true
