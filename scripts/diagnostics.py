"""Print status only; never collect paths, environment, hardware IDs or raw logs."""
import json
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'builder'))
from build import VERSION
state=Path.home()/'Library/Application Support/MOJO Recomp' if sys.platform=='darwin' else root/'userdata'
print(json.dumps({'builder':VERSION,'prepared':(state/'active.json').is_file(),
                  'disc_present':(state/'disc.iso').is_file(),
                  'memory_card_present':(state/'saves/mojo.ps2').is_file()},indent=2))
