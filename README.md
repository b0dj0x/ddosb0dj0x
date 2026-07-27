![DDOSB0DJ0X](https://img.shields.io/badge/DDOSB0DJ0X-v1.0-red?style=for-the-badge&logo=python&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![OSINT](https://img.shields.io/badge/OSINT-Tool-orange?style=for-the-badge)
![Made By](https://img.shields.io/badge/Made%20By-b0dj0x-purple?style=for-the-badge&logo=github&logoColor=white)

<div align="center">

```
ASCII = [
    "██████╗ ███████╗ ██████╗ █████╗ ███████╗ ██████╗  █████╗ ███████╗████████╗",
    "██╔══██╗██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔════╝╚══██╔══╝",
    "██║  ██║█████╗  ██║     ███████║█████╗  ██║  ███╗███████║█████╗     ██║   ",
    "██║  ██║██╔══╝  ██║     ██╔══██║██╔══╝  ██║   ██║██╔══██║██╔══╝     ██║   ",
    "██████╔╝███████╗╚██████╗██║  ██║██║     ╚██████╔╝██║  ██║███████╗   ██║   ",
    "╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ",
]
```

**DDoS simulation and stress testing tool for authorized testing of any target**

*Free APIs · No API Keys Required · Zero Config*

[![Twitter](https://img.shields.io/badge/Twitter-b0dj0x-1DA1F2?style=flat-square&logo=twitter&logoColor=white)](https://x.com/b0dj0x)
[![GitHub](https://img.shields.io/badge/GitHub-b0dj0x-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/b0dj0x)
[![Website](https://img.shields.io/badge/Website-b0dj0x.cc-00ff88?style=flat-square)](https://b0dj0x.cc)
[![Telegram](https://img.shields.io/badge/Telegram-b0dj0x-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/b0dj0x)
[![TryHackMe](https://img.shields.io/badge/TryHackMe-b0dj0x-88cc14?style=flat-square&logo=tryhackme&logoColor=white)](https://tryhackme.com/p/b0dj0x)
[![HackTheBox](https://img.shields.io/badge/HackTheBox-b0dj0x-9FEF00?style=flat-square&logo=hackthebox&logoColor=white)](https://app.hackthebox.com/profile/b0dj0x)

</div>

---

## What is DDOSB0DJ0X?

DDoS simulation and stress testing tool for authorized testing of any target

## Features

- 5 attack modes (HTTP, Slowloris, random path, POST, connection)
- 7 HTTP methods (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD)
- 5 payload sizes (tiny to huge: 100B to 1MB)
- 7 rotating User-Agents
- Slowloris persistent connections
- Live stats panel (RPS, success/fail, data sent/recv, response times, status codes)
- Tor proxy support
- Custom headers
- Authorization gate (must type YES)
- JSON report export
- For authorized testing only
- Zero config, no API keys needed

## Installation

```bash
git clone https://github.com/b0dj0x/DDOSB0DJ0X.git
cd DDOSB0DJ0X
pip install -r requirements.txt
```

## Usage

```bash
python3 ddosb0dj0x.py http://yourserver.com
python3 ddosb0dj0x.py http://yourserver.com --mode slowloris
python3 ddosb0dj0x.py http://yourserver.com --threads 100 --duration 60
python3 ddosb0dj0x.py http://yourserver.com --tor -o report.json
```

## Disclaimer

**For authorized security testing and educational purposes only.** The developer assumes no liability for misuse of this tool. Only use against targets you own or have written authorization to test.

---

## Author

**b0dj0x** - [https://b0dj0x.cc](https://b0dj0x.cc)

[![Twitter](https://img.shields.io/badge/Twitter-b0dj0x-1DA1F2?style=flat-square&logo=twitter&logoColor=white)](https://x.com/b0dj0x)
[![GitHub](https://img.shields.io/badge/GitHub-b0dj0x-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/b0dj0x)
[![Website](https://img.shields.io/badge/Website-b0dj0x.cc-00ff88?style=flat-square)](https://b0dj0x.cc)
[![Telegram](https://img.shields.io/badge/Telegram-b0dj0x-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/b0dj0x)
[![TryHackMe](https://img.shields.io/badge/TryHackMe-b0dj0x-88cc14?style=flat-square&logo=tryhackme&logoColor=white)](https://tryhackme.com/p/b0dj0x)
[![HackTheBox](https://img.shields.io/badge/HackTheBox-b0dj0x-9FEF00?style=flat-square&logo=hackthebox&logoColor=white)](https://app.hackthebox.com/profile/b0dj0x)
[![HackerOne](https://img.shields.io/badge/HackerOne-b0dj0x-50413C?style=flat-square&logo=hackerone&logoColor=white)](https://hackerone.com/b0dj0x)
[![Medium](https://img.shields.io/badge/Medium-b0dj0x-000000?style=flat-square&logo=medium&logoColor=white)](https://medium.com/@b0dj0x)

---

*Made with ❤ by b0dj0x*
