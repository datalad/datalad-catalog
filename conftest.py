import platform

if platform.system() == "Windows":
    collect_ignore_glob = ["*workflow.py", "*workflows.py"]
