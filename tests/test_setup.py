"""Reject a corrupt tool archive before extraction, including optimized Python."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class SetupIntegrityTests(unittest.TestCase):
    def check_rejection(self, optimized):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'scripts').mkdir()
            shutil.copy2(Path(__file__).resolve().parents[1] / 'scripts/setup-john.sh',
                         root / 'scripts/setup-john.sh')
            commands = root / 'commands'
            commands.mkdir()
            # No network access or real extraction/build is used by this test.
            (commands / 'curl').write_text(
                '#!/usr/bin/env python3\n'
                'import sys\nfrom pathlib import Path\n'
                "Path(sys.argv[sys.argv.index('--output')+1]).write_bytes(b'corrupt archive')\n")
            for command in ('tar', 'make'):
                (commands / command).write_text(
                    '#!/usr/bin/env python3\nimport os\nfrom pathlib import Path\n'
                    "Path(os.environ['SETUP_EXECUTED_MARKER']).touch()\nraise SystemExit(99)\n")
            for command in commands.iterdir():
                command.chmod(0o755)
            marker = root / 'extraction-or-build-started'
            env = dict(os.environ, PATH=str(commands) + os.pathsep + os.environ['PATH'],
                       SETUP_EXECUTED_MARKER=str(marker), PYTHONOPTIMIZE=str(optimized))
            result = subprocess.run(['bash', str(root / 'scripts/setup-john.sh')],
                                    env=env, capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Source checksum mismatch', result.stderr)
            self.assertFalse(marker.exists(), 'Unverified archive reached extraction or build')

    def test_corrupt_download_stops_before_extraction(self):
        self.check_rejection(0)

    def test_corrupt_download_stops_with_optimized_python(self):
        self.check_rejection(1)


if __name__ == '__main__':
    unittest.main()
