#!/usr/bin/env python3
"""
Launch a background Waypipe client on Linux hosts.

Steps:
1. Ensure running on Linux.
2. Check that `waypipe` is in the PATH.
3. Check if waypipe client is already running.
4. Remove any pre-existing /tmp/waypipe/waypipe.sock.
5. Start the client detached from the terminal, logging output to
    /tmp/waypipe/waypipe_client.log.
"""

import sys
import shutil
import os
import subprocess
import pathlib

SOCKET_PATH = "/tmp/waypipe/waypipe.sock"
LOG_PATH = "/tmp/waypipe/waypipe_client.log"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def waypipe_available() -> bool:
    return shutil.which("waypipe") is not None


def is_waypipe_running() -> bool:
    """Check if waypipe client is already running"""
    try:
        # Run ps aux and grep for waypipe client process
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Look for waypipe client process in the output
        for line in result.stdout.splitlines():
            if "waypipe" in line and "client" in line and "--socket" in line:
                print(f"Found running waypipe process: {line.strip()}")
                return True
        return False
    except subprocess.CalledProcessError:
        # If ps command fails, assume waypipe is not running
        return False


def remove_socket() -> None:
    if os.path.exists(SOCKET_PATH):
        print(f"Removing existing socket {SOCKET_PATH}")
        os.remove(SOCKET_PATH)


def run_client() -> None:
    cmd = [
        "waypipe",
        "--compress",
        "zstd=3",
        "--socket",
        SOCKET_PATH,
        "client",
    ]

    # Ensure the directory for the socket exists
    pathlib.Path("/tmp/waypipe").mkdir(parents=True, exist_ok=True)

    with open(LOG_PATH, "ab", buffering=0) as log:
        print(f"Starting Waypipe client; logging to {LOG_PATH}")
        # Detach: close stdin, redirect stdout/stderr to log, run in new session
        subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )
    print("Waypipe client started in background.")


def main() -> None:
    if not is_linux():
        print("❌ This script is intended for Linux hosts only.")
        sys.exit(1)

    if not waypipe_available():
        print("❌ `waypipe` was not found in your PATH. Please install it first.")
        sys.exit(1)

    if is_waypipe_running():
        print("✅ Waypipe client is already running.")
        return

    remove_socket()
    run_client()


if __name__ == "__main__":
    main()
