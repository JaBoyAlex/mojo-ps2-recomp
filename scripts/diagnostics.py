"""Print status only; never collect paths, environment, hardware IDs or raw logs."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
state=root/'userdata'
print(json.dumps({'builder':'1.0.0-rc.1','prepared':(state/'active.json').is_file(),
                  'disc_present':(state/'disc.iso').is_file(),
                  'memory_card_present':(state/'saves/mojo.ps2').is_file()},indent=2))
