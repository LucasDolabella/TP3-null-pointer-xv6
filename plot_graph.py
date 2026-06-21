#!/usr/bin/env python3
"""
Boots xv6 in QEMU, runs the 'graph' program, captures tick data
for 3 processes (30/20/10 tickets), and saves a PNG graph.
"""

import subprocess, os, time, select, re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

print("Booting xv6...")

q = subprocess.Popen(
    ["qemu-system-riscv64", "-machine", "virt", "-bios", "none",
     "-kernel", "kernel/kernel", "-m", "128M", "-smp", "1", "-nographic",
     "-global", "virtio-mmio.force-legacy=false",
     "-drive", "file=fs.img,if=none,format=raw,id=x0",
     "-device", "virtio-blk-device,drive=x0,bus=virtio-mmio-bus.0"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
)

def drain(timeout=2):
    out = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        r, _, _ = select.select([q.stdout], [], [], 0.2)
        if r:
            chunk = os.read(q.stdout.fileno(), 4096)
            if chunk:
                out += chunk
    return out.decode("utf-8", "replace")

time.sleep(8)
drain()

print("Running graph inside xv6...")
q.stdin.write(b"graph\n")
q.stdin.flush()

time.sleep(90)
raw = drain(5)
q.terminate()

print("Raw output from xv6:")
print(raw)

samples_a, samples_b, samples_c = [], [], []
total_a = total_b = total_c = 0

for line in raw.splitlines():
    m = re.match(r'^(\d+)\t(\d+)\t(\d+)\t(\d+)$', line.strip())
    if m:
        samples_a.append(int(m.group(2)))
        samples_b.append(int(m.group(3)))
        samples_c.append(int(m.group(4)))

    m2 = re.match(r'^total\t(\d+)\t(\d+)\t(\d+)$', line.strip())
    if m2:
        total_a, total_b, total_c = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))

if not samples_a:
    print("ERROR: could not parse any data from xv6 output.")
    exit(1)

print(f"\nParsed {len(samples_a)} samples.")
print(f"Totals — A: {total_a}, B: {total_b}, C: {total_c}")

# ---------------------------------------------------------------------------
# Step 3: plot
# ---------------------------------------------------------------------------

x = list(range(1, len(samples_a) + 1))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("xv6 Lottery Scheduler — Proportional CPU Share", fontsize=14, fontweight='bold')

ax1.plot(x, samples_a, 'o-', color='steelblue',  label='A (30 tickets)', linewidth=2, markersize=6)
ax1.plot(x, samples_b, 's-', color='darkorange', label='B (20 tickets)', linewidth=2, markersize=6)
ax1.plot(x, samples_c, '^-', color='green',      label='C (10 tickets)', linewidth=2, markersize=6)
ax1.set_title("Ticks per Sample Interval")
ax1.set_xlabel("Sample")
ax1.set_ylabel("Ticks gained")
ax1.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax1.legend()
ax1.grid(True, alpha=0.3)

avg_c = sum(samples_c) / len(samples_c)
ax1.axhline(avg_c * 3, color='steelblue',  linestyle='--', alpha=0.4, label='expected A')
ax1.axhline(avg_c * 2, color='darkorange', linestyle='--', alpha=0.4, label='expected B')
ax1.axhline(avg_c * 1, color='green',      linestyle='--', alpha=0.4, label='expected C')

labels = ['A\n(30 tickets)', 'B\n(20 tickets)', 'C\n(10 tickets)']
totals = [total_a, total_b, total_c]
colors = ['steelblue', 'darkorange', 'green']
bars = ax2.bar(labels, totals, color=colors, alpha=0.85, edgecolor='black')

for bar, val in zip(bars, totals):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
             str(val), ha='center', va='bottom', fontsize=11, fontweight='bold')

expected_unit = (total_a + total_b + total_c) / 6  # 3+2+1 = 6 parts
ax2.axhline(expected_unit * 3, color='steelblue',  linestyle='--', alpha=0.5, label='expected A (3x)')
ax2.axhline(expected_unit * 2, color='darkorange', linestyle='--', alpha=0.5, label='expected B (2x)')
ax2.axhline(expected_unit * 1, color='green',      linestyle='--', alpha=0.5, label='expected C (1x)')
ax2.legend(fontsize=8)
ax2.set_title("Total Ticks Accumulated")
ax2.set_ylabel("Total ticks")
ax2.grid(True, axis='y', alpha=0.3)

plt.tight_layout()
outfile = "lottery_graph.png"
plt.savefig(outfile, dpi=150, bbox_inches='tight')
print(f"\nGraph saved to: {outfile}")