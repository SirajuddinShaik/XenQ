# system_manager.py for client/src/xenq_client/components/system_manager.py

import asyncio
from fastapi.responses import StreamingResponse
import psutil
import platform
from tabulate import tabulate
import subprocess
from collections import defaultdict
from fastapi import APIRouter, Request
from pydantic import BaseModel

# Create the router
router = APIRouter(
    prefix="/system_manager",
    tags=["System Manager"]
)

SHARED_FOLDER = "../xenq_shared_folder"

@router.get("/get_config")
def get_system_info():
    system_info = []
    # OS Info
    uname = platform.uname()
    system_info.append(["Node Name", uname.node])
    system_info.append(["System", f"{uname.system} {uname.release}"])
    
    # CPU Info
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_freq = psutil.cpu_freq()
    cpu_usage = psutil.cpu_percent(interval=1)

    system_info.append(["CPU Physical Cores", cpu_cores])
    system_info.append(["CPU Frequency (MHz)", f"{cpu_freq.current:.2f}"])
    system_info.append(["CPU Usage (%)", cpu_usage])

    # RAM Info
    virtual_mem = psutil.virtual_memory()
    system_info.append(["Available RAM (GB)", f"{virtual_mem.available / (1024**3):.2f}/{virtual_mem.total / (1024**3):.2f}"])
    system_info.append(["RAM Usage (%)", virtual_mem.percent])

    # Disk Info
    disk = psutil.disk_usage('/')
    system_info.append(["Free Disk (GB)", f"{disk.free / (1024**3):.2f}/{disk.total / (1024**3):.2f}"])
    system_info.append(["Disk Usage (%)", disk.percent])

    # OS Info
    system_info.append(["Machine", uname.machine])
    system_info.append(["Processor", uname.processor])

    table =  tabulate(system_info, headers=["Component", "Details"], tablefmt="github")
    return {"response": table, "success": True}


# List of known internal Windows processes to exclude
windows_internal_processes = [
    "System", "svchost.exe", "wininit.exe", "smss.exe", "csrss.exe", "fontdrvhost.exe", "Registry",
    "sdxhelper.exe", "lsass.exe", "explorer.exe", "services.exe", "taskhostw.exe", "spoolsv.exe",
    "systemsettings.exe", "audiodg.exe", "taskhostw.exe", "dwm.exe", "OneApp.IGCC.WinService.exe",
    "dllhost.exe", "sihost.exe", "searchindexer.exe", "svchost.exe", "backgroundtaskhost.exe",
    "presentationfontcache.exe", "widgets.exe", "ctfmon.exe", "shellexperiencehost.exe"
]

# Function to get exposed ports of a process (if any)
def get_exposed_ports(pid):
    ports = set()
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.pid == pid:
                # Skip ports with 5 digits
                if conn.laddr.port >= 10000 and conn.laddr.port <= 65535:
                    continue
                ports.add(conn.laddr.port)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return list(ports)

# Function to list user applications and servers, excluding Windows internal processes
@router.get("/list_process")
def list_user_processes():  
    process_details = defaultdict(lambda: {"count": 0, "ram_usage": 0, "ports": set()})

    for process in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            process_name = process.info['name']
            pid = process.info['pid']

            # Exclude internal Windows processes
            if process_name.lower() in (name.lower() for name in windows_internal_processes):
                continue

            # Get RAM usage in MB
            ram_usage = process.info['memory_info'].rss / (1024 * 1024)  # Convert to MB

            # Get exposed ports for the process
            ports = get_exposed_ports(pid)

            # Update the process details
            process_details[process_name]["count"] += 1
            process_details[process_name]["ram_usage"] += ram_usage
            process_details[process_name]["ports"].update(ports)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Prepare data for display
    rows = []
    for name, details in process_details.items():
        row = [
            name,
            details["count"],
            round(details["ram_usage"], 2),
            ", ".join(map(str, sorted(details["ports"])))
        ]
        rows.append(row)
    rows.sort(key=lambda x: x[2], reverse=True)
    # Display results in a table
    column_names = ["Name", "Instance Count", "RAM Usage (MB)", "Ports"]
    table =  tabulate(rows, headers=column_names, tablefmt="github")
    return {"response": table, "success": True}

class KillProcessRequest(BaseModel):
    name: str = None
    port: int = None    

@router.post("/kill_process")
async def kill_processes_by_name_or_port(request: Request):
    body = await request.json()
    name = body.get("name", None)
    port = body.get("port", None)
    print(name, port)
    killed_pids = []

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.info['pid']
            proc_name = proc.info['name']

            # Kill by name
            if name and proc_name.lower() == name.lower():
                psutil.Process(pid).kill()
                killed_pids.append(pid)

            # Kill by port
            elif port:
                for conn in proc.connections(kind='inet'):
                    if conn.laddr.port == port:
                        psutil.Process(pid).kill()
                        killed_pids.append(pid)
                        break  # No need to check more connections once matched

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed_pids:
        msg = f"Killed processes with PIDs: {killed_pids}"
    else:
        msg = "No matching processes found."
    return {"response": msg, "success": True}

@router.post("/run_command")
async def start_process(request: Request):
    body = await request.json()
    command = body.get("command")
    stream = body.get("stream", False)

    if not command:
        return {"response": "No command provided.", "success": False}

    try:
        if not stream:
            # Normal mode: just start the process without streaming
            process = subprocess.Popen(command, shell=True, cwd=SHARED_FOLDER)
            return {"response": f"Process started with PID {process.pid}", "success": True}
        else:
            # Stream mode: stream stdout line-by-line
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                cwd=SHARED_FOLDER
            )

            async def stream_output():
                try:
                    while True:
                        line = await asyncio.to_thread(process.stdout.readline)
                        if not line:
                            break
                        yield line.rstrip() + "\n"
                finally:
                    process.terminate()
                    await asyncio.to_thread(process.wait)

            return StreamingResponse(stream_output(), media_type="text/plain")

    except Exception as e:
        return {"response": f"Error starting process: {str(e)}", "success": False}