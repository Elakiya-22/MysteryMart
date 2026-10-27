import subprocess
import time
import sys

def main():
    while True:
        print("[TunnelKeeper] Starting localtunnel on port 5000 (subdomain: two-toes-shave)...", flush=True)
        try:
            proc = subprocess.Popen(
                ["npx.cmd", "-y", "localtunnel", "--port", "5000", "--subdomain", "two-toes-shave"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in proc.stdout:
                print(f"[localtunnel] {line.strip()}", flush=True)
            proc.wait()
            print(f"[TunnelKeeper] localtunnel exited with code {proc.returncode}. Restarting in 3s...", flush=True)
        except Exception as e:
            print(f"[TunnelKeeper] Error: {e}. Retrying in 3s...", flush=True)
        time.sleep(3)

if __name__ == '__main__':
    main()
