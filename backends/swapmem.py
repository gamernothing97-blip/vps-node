"""Host RAM + swap detection, shared by every backend.

A node with little RAM but a big swap file (e.g. 7 GB RAM + 32 GB swap) is treated as having RAM+swap
(39 GB) of capacity. Each VPS gets swap equal to its RAM, limited to the swap the host really has.
"""


def host_ram_swap():
    """(ram_bytes, swap_bytes, swap_free_bytes) from /proc/meminfo. Zeros if it cannot be read."""
    ram = swap = free = 0
    try:
        for line in open("/proc/meminfo"):
            k, _, v = line.partition(":")
            kb = int(v.split()[0]) * 1024 if v.split() else 0
            if k == "MemTotal":
                ram = kb
            elif k == "SwapTotal":
                swap = kb
            elif k == "SwapFree":
                free = kb
    except Exception:
        pass
    return ram, swap, free


def capacity_gb():
    """(ram_gb, swap_gb) as whole numbers - what the node reports to the bot."""
    ram, swap, _ = host_ram_swap()
    return int(ram // 1024 ** 3), int(swap // 1024 ** 3)


def vps_swap_gb(ram_gb):
    """Swap for one VPS: same size as its RAM, but never more than the host's swap. 0 = host has no swap."""
    _, swap, _ = host_ram_swap()
    return int(min(int(ram_gb), swap // 1024 ** 3))


def check_fits(ram_gb):
    """Raise if the plan's RAM does not fit into host RAM + swap."""
    ram, swap, _ = host_ram_swap()
    if ram and int(ram_gb) * 1024 ** 3 > ram + swap:
        raise RuntimeError(f"this node has {ram / 1024 ** 3:.1f}GB RAM + {swap / 1024 ** 3:.0f}GB swap - "
                           f"cannot create a {int(ram_gb)}GB VPS here")
