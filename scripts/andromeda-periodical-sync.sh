#!/bin/bash

# How long (in seconds) to keep Andromeda OPEN
OPEN_DURATION=60

# How long (in seconds) to wait before opening it again
CLOSED_INTERVAL=300

# true  = Only run this cycle if the screen is LOCKED.
# false = Run this cycle regardless of lock status.
ONLY_RUN_WHEN_LOCKED=true


# Check if the session is currently locked
check_if_locked() {

    SESSION_ID=$(loginctl list-sessions | grep $(whoami) | awk 'NR==2 {print $1}')
    
    LOCK_STATUS=$(loginctl show-session "$SESSION_ID" -p LockedHint)

    if [[ "$LOCK_STATUS" == *"yes"* ]]; then
        return 0
    else
        return 1
    fi
}

start_cycle() {
    echo "[$(date +'%T')] Starting Andromeda session..."
        andromeda session start & 
    
    sleep "$OPEN_DURATION"
    
    echo "[$(date +'%T')] Stopping Andromeda session..."
    andromeda session stop
}

echo "Starting Andromeda Cycle Script."
echo "Config: Open for ${OPEN_DURATION}s, Closed for ${CLOSED_INTERVAL}s."

while true; do
    if [ "$ONLY_RUN_WHEN_LOCKED" = true ]; then
        if check_if_locked; then

            start_cycle
        else
            echo "[$(date +'%T')] Screen unlocked. Skipping cycle."
        fi
    else
        start_cycle
    fi

    sleep "$CLOSED_INTERVAL"
done