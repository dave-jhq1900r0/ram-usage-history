import psutil

def collect_ram_metrics(top_n=10):
    """Fetch current memory state and top RAM-consuming processes."""
    vm = psutil.virtual_memory()
    processes = []
    
    # We fetch all processes. On Windows, some system processes will raise
    # AccessDenied. We just skip them since we can't measure them anyway.
    for proc in psutil.process_iter():
        try:
            mem_info = proc.memory_info()
            name = proc.name()
            if not name:
                name = "Unknown"
            
            # print(f"DEBUG: {name} ({proc.pid}) using {mem_info.rss} bytes")
            
            processes.append({
                'pid': proc.pid,
                'name': name,
                'rss': mem_info.rss
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # FIXME: Some svchost.exe instances share memory. We report them individually for now.
    processes.sort(key=lambda x: x['rss'], reverse=True)

    return {
        'total_bytes': vm.total,
        'available_bytes': vm.available,
        'percent_used': vm.percent,
        'top_processes': processes[:top_n]
    }
