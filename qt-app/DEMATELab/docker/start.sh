#!/bin/bash
# Starts a virtual X display, a VNC server, the noVNC web client, and DEMATELab.
# The GUI is then reachable in a browser at http://<host>:<published port>/.
#
# APP_MODE=dev  -> restart the GUI whenever Python files under /app/DEMATELab change
# APP_MODE=prod -> require VNC_PASSWORD and restart the GUI if it is closed or crashes
#
# Started as root: it matches the app user to the owner of exports/, then drops to that user.
# (Rootless Docker/Podman, where exports/ shows up as root-owned and is only writable by
# root, keeps running as the container's root user, which is the host user there.)
set -euo pipefail

APP_MODE="${APP_MODE:-prod}"
DISPLAY="${DISPLAY:-:99}"
SCREEN_GEOMETRY="${SCREEN_GEOMETRY:-1600x1000x24}"
VNC_PORT="${VNC_PORT:-5900}"
VNC_PASSWORD="${VNC_PASSWORD:-}"
WORKSPACE="${WORKSPACE:-/workspace}"
export DISPLAY

log() { echo "[dematelab] $*"; }

if [[ "$APP_MODE" == "prod" && -z "$VNC_PASSWORD" ]]; then
    log "VNC_PASSWORD must be set in production (see DEMATELab/.env.example). Not starting." >&2
    log "Set it, then recreate the container (make prod)." >&2
    # Wait instead of exiting so the restart policy doesn't loop; the healthcheck reports
    # the container as unhealthy.
    exec sleep infinity
fi

# Remove a stale display lock left behind by a container restart. Done before dropping
# privileges: /tmp is sticky, so only root can remove a lock left by a different UID.
display_number="${DISPLAY#:}"
rm -f "/tmp/.X${display_number}-lock" "/tmp/.X11-unix/X${display_number}"

# The container starts as root only to run the app as the owner of the exports folder
# (on Linux, the host user who owns the bind-mounted ./exports), then drops privileges.
if [[ "$(id -u)" == 0 ]]; then
    exports_dir="$WORKSPACE/exports"
    mkdir -p "$exports_dir"
    owner_uid="$(stat -c %u "$exports_dir")"
    owner_gid="$(stat -c %g "$exports_dir")"
    as_app=(setpriv --reuid=app --regid=app --init-groups)
    if [[ "$owner_uid" != 0 ]]; then
        # Never give app the root group, even if the folder's group is root.
        if [[ "$owner_gid" != 0 && "$owner_gid" != "$(id -g app)" ]]; then
            groupmod --non-unique --gid "$owner_gid" app
        fi
        if [[ "$owner_uid" != "$(id -u app)" ]]; then
            log "Running as UID ${owner_uid}:$(id -g app) (owner of exports/)"
            usermod --non-unique --uid "$owner_uid" app
        fi
    elif ! "${as_app[@]}" sh -c 'f="$(mktemp -p "$1")" && rm -f "$f"' sh "$exports_dir" 2>/dev/null; then
        # Root-owned and only writable by root: rootless Docker/Podman (root here is the host
        # user) or a folder Docker created itself. Stay root rather than change its owner.
        log "exports/ is only writable by root; running as root" >&2
        as_app=()
    fi
    # Root-owned but writable folders (Docker Desktop/OrbStack/Windows mounts) keep app.
    if (( ${#as_app[@]} )); then
        chown -R app:app /home/app
        chown app:app "$WORKSPACE"
        export HOME=/home/app USER=app LOGNAME=app
        exec "${as_app[@]}" "$0" "$@"
    fi
fi

if (( ${#VNC_PASSWORD} > 8 )); then
    log "Note: VNC passwords are limited to 8 characters; only the first 8 are checked." >&2
fi

log "Starting virtual display ${DISPLAY} (${SCREEN_GEOMETRY})"
Xvfb "$DISPLAY" -screen 0 "$SCREEN_GEOMETRY" -nolisten tcp &

for _ in $(seq 1 50); do
    [[ -S "/tmp/.X11-unix/X${display_number}" ]] && break
    sleep 0.1
done

openbox &

vnc_auth=(-nopw)
if [[ -n "$VNC_PASSWORD" ]]; then
    mkdir -p "$HOME/.vnc"
    x11vnc -storepasswd "$VNC_PASSWORD" "$HOME/.vnc/passwd" >/dev/null
    vnc_auth=(-rfbauth "$HOME/.vnc/passwd")
fi

# VNC only listens inside the container; browsers connect through websockify/noVNC.
x11vnc -display "$DISPLAY" -localhost -rfbport "$VNC_PORT" -forever -shared -quiet "${vnc_auth[@]}" &

log "Serving noVNC on container port 6080"
websockify --web /usr/share/novnc "0.0.0.0:6080" "localhost:${VNC_PORT}" >/dev/null 2>&1 &

# Run from the workspace so file dialogs default to it; it links back to /app/assets
# so the app's relative "assets/icons/..." stylesheet paths still resolve.
mkdir -p "$WORKSPACE/exports"
cd "$WORKSPACE"

if [[ "$APP_MODE" == "dev" ]]; then
    log "Starting DEMATELab in dev mode (reloads on changes in /app/DEMATELab)"
    # Qt's event loop ignores SIGINT, so don't wait the default 5s before force-stopping it.
    watchfiles --filter python --sigint-timeout 1 "python -m DEMATELab" /app/DEMATELab &
else
    log "Starting DEMATELab"
    (while true; do python -m DEMATELab || true; log "DEMATELab exited; restarting"; sleep 1; done) &
fi

# If any of the services above dies, exit so Docker's restart policy recovers the container.
wait -n
log "A service exited; stopping container" >&2
exit 1
