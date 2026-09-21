# ram-usage-history

I needed a simple, no-overhead way to track what was eating my memory on Windows over long work sessions without leaving heavy monitoring GUIs open. This tool logs overall RAM state and the top memory-consuming processes to a local SQLite database. It includes a built-in ASCII chart renderer to visualize usage spikes directly in the terminal.

## Installation

Clone the repository and install the dependencies. I recommend using a virtual environment.

```cmd
pip install -r requirements.txt
```

## How to run

### 1. Collect data
To log a single snapshot of your current RAM usage:
```cmd
python ram_history.py collect
```

To run it as a daemon/background loop logging every 60 seconds:
```cmd
python ram_history.py collect --loop --interval 60
```
(You can also register it as a Windows Task Scheduler basic task to run on startup/login without a terminal window).

### 2. View usage history
To see a summary of peak usage and the worst memory-offending processes:
```cmd
python ram_history.py summary
```

To render an ASCII trend chart of the last 24 hours:
```cmd
python ram_history.py chart --hours 24
```

<!-- verified: 2026-09-21 -->
