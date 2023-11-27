import time
import sys


def simple_progress_bar(total):
    for i in range(total):
        percent = (i + 1) / total
        bar_length = 20
        bar = "=" * int(bar_length * percent) + "-" * (
            bar_length - int(bar_length * percent)
        )
        sys.stdout.write(f"\r[{bar}] {int(percent * 100)}%")
        sys.stdout.flush()
        time.sleep(0.1)


simple_progress_bar(100)
