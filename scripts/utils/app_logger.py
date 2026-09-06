"""Central application logger.

Every action logged via `print_time`/`log_action` across the codebase, as well as
the parameters and per-run output produced by the genotype/microtype/machine
learning workflows, is persisted to a single rotating log file so the full
history of commands, parameters and software output can be reviewed later.
"""
import atexit
import datetime
import logging
import logging.handlers
import os
import platform
import shutil
import threading
import time
from contextlib import contextmanager

_LOGGER_NAME = "smartyper"
_logger = None
_log_path = None
_app_start_time = time.time()
_active_seconds = 0.0
_active_lock = threading.Lock()


def _default_log_dir():
    # scripts/utils/app_logger.py -> project root/log
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, "log")


def get_logger():
    global _logger, _log_path
    if _logger is not None:
        return _logger

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    log_dir = _default_log_dir()
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        log_dir = os.getcwd()

    _log_path = os.path.join(log_dir, f"smartyper_{datetime.datetime.fromtimestamp(_app_start_time).strftime('%Y%m%d_%H%M%S')}.log")

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.handlers.RotatingFileHandler(_log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    _logger = logger
    return _logger


def get_log_file_path():
    get_logger()
    return _log_path


def log_action(msg, level="info"):
    logger = get_logger()
    getattr(logger, level, logger.info)(str(msg))


def log_parameters(params, context=""):
    """Log every attribute of a parameter object (or dict) to the log file."""
    logger = get_logger()
    header = f"Parameters snapshot{(' - ' + context) if context else ''}"
    logger.info(header)
    if isinstance(params, dict):
        items = params.items()
    elif hasattr(params, "__dict__"):
        items = vars(params).items()
    else:
        logger.info(f"  {params}")
        return
    for key, value in items:
        logger.info(f"  {str(key).lstrip('_')} = {value}")


def get_peak_memory_mb():
    """Return the process's peak (max) resident memory usage in MB, or None if unavailable."""
    try:
        import resource
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # ru_maxrss is KB on Linux but bytes on macOS
        return peak / (1024 * 1024) if platform.system() == "Darwin" else peak / 1024
    except Exception:
        try:
            import psutil
            return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        except Exception:
            return None


def get_hardware_info():
    """Return a dict describing CPU model/speed/threads, OS, system memory and disk space of the log's drive."""
    info = {}
    info["os"] = platform.platform()
    info["os_name"] = _get_os_name()
    info["machine"] = platform.machine()
    info["python_version"] = platform.python_version()

    try:
        info["cpu_threads"] = os.cpu_count()
    except Exception:
        info["cpu_threads"] = None

    info["cpu_name"] = _get_cpu_name()
    info["cpu_speed_mhz"] = _get_cpu_speed_mhz()

    try:
        import psutil
        vm = psutil.virtual_memory()
        info["total_memory_gb"] = round(vm.total / (1024 ** 3), 2)
        info["available_memory_gb"] = round(vm.available / (1024 ** 3), 2)
    except Exception:
        try:
            # Fallback for Linux without psutil
            with open("/proc/meminfo") as f:
                meminfo = dict(
                    (line.split(":")[0], int(line.split(":")[1].strip().split()[0]))
                    for line in f if ":" in line
                )
            info["total_memory_gb"] = round(meminfo.get("MemTotal", 0) / (1024 ** 2), 2)
            info["available_memory_gb"] = round(meminfo.get("MemAvailable", 0) / (1024 ** 2), 2)
        except Exception:
            info["total_memory_gb"] = None
            info["available_memory_gb"] = None

    try:
        usage = shutil.disk_usage(_default_log_dir())
        info["disk_total_gb"] = round(usage.total / (1024 ** 3), 2)
        info["disk_free_gb"] = round(usage.free / (1024 ** 3), 2)
    except Exception:
        info["disk_total_gb"] = None
        info["disk_free_gb"] = None

    info.update(_get_memory_hardware_info())
    info.update(_get_disk_hardware_info(_default_log_dir()))
    info["memory_bandwidth_mbps"] = _measure_memory_bandwidth_mbps()
    info["disk_write_speed_mbps"] = _measure_disk_write_speed_mbps(_default_log_dir())

    return info


def _get_cpu_name():
    """Best-effort lookup of the CPU model name across platforms."""
    try:
        if platform.system() == "Linux":
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
        elif platform.system() == "Darwin":
            import subprocess
            return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
        elif platform.system() == "Windows":
            return platform.processor()
    except Exception:
        pass
    return platform.processor() or None


def _get_cpu_speed_mhz():
    """Best-effort CPU speed lookup. psutil.cpu_freq() is often None under WSL2/containers."""
    try:
        import psutil
        freq = psutil.cpu_freq()
        if freq and (freq.max or freq.current):
            return round(freq.max or freq.current, 0)
    except Exception:
        pass
    try:
        if platform.system() == "Linux":
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.lower().startswith("cpu mhz"):
                        return round(float(line.split(":", 1)[1].strip()), 0)
    except Exception:
        pass
    return None


def _get_os_name():
    """Best-effort human-readable OS distribution/version name across platforms."""
    try:
        if platform.system() == "Linux":
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        elif platform.system() == "Darwin":
            return f"macOS {platform.mac_ver()[0]}"
        elif platform.system() == "Windows":
            win_ver = platform.win32_ver()
            return f"Windows {win_ver[0]} {win_ver[1]}".strip()
    except Exception:
        pass
    return f"{platform.system()} {platform.release()}"


def _get_memory_hardware_info():
    """Best-effort RAM speed/manufacturer/model via dmidecode. Usually requires root; falls back to None."""
    info = {"memory_speed_mhz": None, "memory_manufacturer": None, "memory_model": None}
    if platform.system() != "Linux":
        return info
    try:
        import subprocess
        result = subprocess.run(["dmidecode", "--type", "17"], capture_output=True, text=True, timeout=3)
        if result.returncode != 0:
            return info
        speeds = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("Speed:") and "Unknown" not in line:
                try:
                    speeds.append(int(line.split(":")[1].strip().split()[0]))
                except Exception:
                    pass
            elif line.startswith("Manufacturer:") and "Unknown" not in line and info["memory_manufacturer"] is None:
                info["memory_manufacturer"] = line.split(":", 1)[1].strip()
            elif line.startswith("Part Number:") and "Unknown" not in line and info["memory_model"] is None:
                info["memory_model"] = line.split(":", 1)[1].strip()
        if speeds:
            info["memory_speed_mhz"] = max(speeds)
    except Exception:
        pass
    return info


def _get_disk_hardware_info(path):
    """Best-effort local drive vendor/model lookup via Linux sysfs; no root required."""
    info = {"disk_vendor": None, "disk_model": None}
    if platform.system() != "Linux":
        return info
    try:
        st_dev = os.stat(path).st_dev
        link = f"/sys/dev/block/{os.major(st_dev)}:{os.minor(st_dev)}"
        dev_dir = os.path.realpath(link)
        # Walk up from the partition to the parent disk device that exposes model/vendor files
        while dev_dir != "/sys" and not os.path.exists(os.path.join(dev_dir, "device", "model")):
            parent = os.path.dirname(dev_dir)
            if parent == dev_dir:
                break
            dev_dir = parent
        model_path = os.path.join(dev_dir, "device", "model")
        vendor_path = os.path.join(dev_dir, "device", "vendor")
        if os.path.exists(model_path):
            with open(model_path) as f:
                info["disk_model"] = f.read().strip()
        if os.path.exists(vendor_path):
            with open(vendor_path) as f:
                info["disk_vendor"] = f.read().strip()
    except Exception:
        pass
    return info


def _measure_memory_bandwidth_mbps():
    """Best-effort measured RAM copy throughput (MB/s); not the DIMM's rated MT/s speed, which needs root/dmidecode."""
    try:
        size = 64 * 1024 * 1024  # 64 MB
        src = bytearray(size)
        start = time.time()
        _ = bytearray(src)
        elapsed = time.time() - start
        if elapsed > 0:
            return round((size / (1024 * 1024)) / elapsed, 1)
    except Exception:
        pass
    return None


def _measure_disk_write_speed_mbps(path, size_mb=20):
    """Best-effort measured sequential write throughput (MB/s) to the log's drive; no root required."""
    try:
        test_file = os.path.join(path, ".smartyper_disk_speed_test.tmp")
        chunk = os.urandom(1024 * 1024)
        start = time.time()
        with open(test_file, "wb") as f:
            for _ in range(size_mb):
                f.write(chunk)
            f.flush()
            os.fsync(f.fileno())
        elapsed = time.time() - start
        os.remove(test_file)
        if elapsed > 0:
            return round(size_mb / elapsed, 1)
    except Exception:
        pass
    return None


def log_hardware_info():
    """Log the machine's OS, CPU model/speed/threads, memory, and disk info to the log file."""
    logger = get_logger()
    info = get_hardware_info()
    mem_speed = f"{info['memory_speed_mhz']} MHz" if info['memory_speed_mhz'] else "unavailable (requires root/dmidecode)"
    mem_vendor = f"{info['memory_manufacturer']} {info['memory_model']}".strip() if info['memory_manufacturer'] or info['memory_model'] else "unavailable (requires root/dmidecode)"
    disk_vendor = f"{info['disk_vendor']} {info['disk_model']}".strip() if info['disk_vendor'] or info['disk_model'] else "unavailable"
    mem_bw = f"{info['memory_bandwidth_mbps']} MB/s (measured copy throughput)" if info['memory_bandwidth_mbps'] else "unavailable"
    disk_speed = f"{info['disk_write_speed_mbps']} MB/s (measured write throughput)" if info['disk_write_speed_mbps'] else "unavailable"
    logger.info(
        "Hardware: "
        f"OS = {info['os_name']} ({info['os']}, {info['machine']}), "
        f"Python = {info['python_version']}, "
        f"CPU = {info['cpu_name']}, "
        f"CPU speed = {info['cpu_speed_mhz']} MHz, "
        f"CPU threads = {info['cpu_threads']}, "
        f"total memory = {info['total_memory_gb']} GB, "
        f"available memory = {info['available_memory_gb']} GB, "
        f"memory speed = {mem_speed}, "
        f"memory = {mem_vendor}, "
        f"memory bandwidth = {mem_bw}, "
        f"disk total = {info['disk_total_gb']} GB, "
        f"disk free = {info['disk_free_gb']} GB, "
        f"disk drive = {disk_vendor}, "
        f"disk speed = {disk_speed}"
    )


def log_run_summary(start_time, context="", accumulate=True):
    """Log elapsed time since `start_time` alongside the two whole-session timers and peak memory.

    `start_time` may be a `time.time()` float or a `datetime.datetime` instance.
    When `accumulate` is True (default), the elapsed time is added to the
    session-wide "active" time counter reported when the application exits.
    """
    if isinstance(start_time, datetime.datetime):
        elapsed = (datetime.datetime.now() - start_time).total_seconds()
    else:
        elapsed = time.time() - start_time

    if accumulate:
        global _active_seconds
        with _active_lock:
            _active_seconds += elapsed

    total_session_elapsed = time.time() - _app_start_time
    active_elapsed = get_active_seconds()
    peak_mb = get_peak_memory_mb()
    mem_str = f"{peak_mb:.2f} MB" if peak_mb is not None else "unavailable"
    logger = get_logger()
    header = f"Run summary{(' - ' + context) if context else ''}"
    logger.info(
        f"{header}: step elapsed time = {elapsed:.2f}s, "
        f"total session time so far = {total_session_elapsed:.2f}s, "
        f"total active time so far = {active_elapsed:.2f}s, "
        f"peak memory = {mem_str}"
    )


@contextmanager
def track_run(context=""):
    """Context manager that logs a run summary (elapsed time + peak memory) on exit."""
    start_time = time.time()
    try:
        yield
    finally:
        log_run_summary(start_time, context=context)


def log_app_start():
    """Mark the application start in the log; pairs with the automatic exit summary below."""
    log_action("SmarTyper application started")
    log_hardware_info()


def get_active_seconds():
    """Return the total time accumulated so far by tracked runs (via `log_run_summary`/`track_run`)."""
    with _active_lock:
        return _active_seconds


def _log_app_shutdown():
    total_elapsed = time.time() - _app_start_time
    active_elapsed = get_active_seconds()
    idle_elapsed = max(0.0, total_elapsed - active_elapsed)
    peak_mb = get_peak_memory_mb()
    mem_str = f"{peak_mb:.2f} MB" if peak_mb is not None else "unavailable"
    hw = get_hardware_info()
    mem_speed = f"{hw['memory_speed_mhz']} MHz" if hw['memory_speed_mhz'] else "unavailable (requires root/dmidecode)"
    mem_vendor = f"{hw['memory_manufacturer']} {hw['memory_model']}".strip() if hw['memory_manufacturer'] or hw['memory_model'] else "unavailable (requires root/dmidecode)"
    disk_vendor = f"{hw['disk_vendor']} {hw['disk_model']}".strip() if hw['disk_vendor'] or hw['disk_model'] else "unavailable"
    mem_bw = f"{hw['memory_bandwidth_mbps']} MB/s (measured)" if hw['memory_bandwidth_mbps'] else "unavailable"
    disk_speed = f"{hw['disk_write_speed_mbps']} MB/s (measured)" if hw['disk_write_speed_mbps'] else "unavailable"
    logger = get_logger()
    logger.info(
        "Application session summary: "
        f"total elapsed time = {total_elapsed:.2f}s, "
        f"active (running) time = {active_elapsed:.2f}s, "
        f"idle time = {idle_elapsed:.2f}s, "
        f"peak memory = {mem_str}, "
        f"OS = {hw['os_name']} ({hw['machine']}), "
        f"CPU = {hw['cpu_name']} @ {hw['cpu_speed_mhz']} MHz, "
        f"CPU threads = {hw['cpu_threads']}, "
        f"total memory = {hw['total_memory_gb']} GB, "
        f"memory speed = {mem_speed}, "
        f"memory = {mem_vendor}, "
        f"memory bandwidth = {mem_bw}, "
        f"disk free = {hw['disk_free_gb']} / {hw['disk_total_gb']} GB, "
        f"disk drive = {disk_vendor}, "
        f"disk speed = {disk_speed}"
    )


# Ensures the whole-project runtime and peak memory are recorded even if the
# app is closed via the window manager rather than an explicit code path.
atexit.register(_log_app_shutdown)
