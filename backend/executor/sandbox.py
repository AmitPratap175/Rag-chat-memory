import subprocess
import sys


class Sandbox:
    def execute(self, code: str, timeout: int = 5):
        """Executes Python code in a sandboxed environment."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,  # Do not raise CalledProcessError
            )
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return "", "Execution timed out."
        except Exception as e:
            return "", f"An unexpected error occurred: {e}"
