import socket
import threading
import time
import webbrowser
import signal
import sys
from contextlib import closing

import uvicorn

from .app import app


def find_free_port() -> int:
    """Find a free TCP port on localhost."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def wait_for_server(port: int, timeout: float = 30.0) -> bool:
    """Poll the health endpoint until the server is ready."""
    import urllib.request

    url = f"http://127.0.0.1:{port}/health"
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def open_browser(url: str) -> None:
    """Open the default web browser."""
    webbrowser.open(url, new=2)  # new=2 opens in a new tab


def run_server(port: int) -> None:
    """Run the uvicorn server. This blocks until the server stops."""
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def main() -> None:
    """Main entry point: find port, start server, open browser, wait."""
    port = find_free_port()
    url = f"http://127.0.0.1:{port}"

    print(f"\n  Starting MarkItDown GUI on {url}")
    print("  Press Ctrl+C to stop\n")

    # Start server in a background thread
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    # Wait for server to be ready
    if not wait_for_server(port, timeout=30.0):
        print("  ERROR: Server failed to start within 30 seconds.")
        sys.exit(1)

    # Open browser
    open_browser(url)

    # Keep main thread alive until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
