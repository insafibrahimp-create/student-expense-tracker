"""
Run the database tests and print a colored summary.
This wrapper invokes the test file directly so the environment (.env) is respected.
"""
import subprocess
import sys
from colorama import init, Fore, Style

init(autoreset=True)

cmd = [sys.executable, 'database\test_expenses.py']
print('Running tests:', ' '.join(cmd))
proc = subprocess.run(cmd)

if proc.returncode == 0:
    print(Fore.GREEN + '\nAll tests passed (0 failures)')
else:
    print(Fore.RED + f'\nTests finished with return code {proc.returncode}')

sys.exit(proc.returncode)
