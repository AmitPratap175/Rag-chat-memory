from .sandbox import Sandbox


class Tester:
    def __init__(self):
        self.sandbox = Sandbox()

    def run_tests(self, user_code: str, test_code: str):
        """Runs tests against the user's code in the sandbox."""
        full_code = f"{user_code}\n\n{test_code}"
        stdout, stderr = self.sandbox.execute(full_code)

        if stderr:
            return False, stderr

        # A simple way to check for test success is the absence of "FAILED"
