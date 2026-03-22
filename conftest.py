"""
pytest configuration — adds the project root to sys.path so that
all modules (config, riot_api, stats, formatter, …) are importable
without a package install step.
"""

import sys
from pathlib import Path

# Insert the lolnotifier root so `import riot_api` etc. work in tests
sys.path.insert(0, str(Path(__file__).parent))
