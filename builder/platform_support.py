"""Small, repeatable compatibility patches to the pinned native framework."""
from pathlib import Path

def apply(engine):
    # Stock macOS Bash 3.2 supports all remaining constructs in these scripts.
    for name in ('setup.sh', 'port.sh'):
        path = Path(engine)/'scripts'/name
        text = path.read_text(encoding='utf-8')
        text = text.replace('[ "${BASH_VERSINFO:-0}" -lt 4 ]', '[ "${BASH_VERSINFO:-0}" -lt 3 ]')
        text = text.replace('${source_path,,}', '$(printf \'%s\' "$source_path" | tr \'[:upper:]\' \'[:lower:]\')')
        path.write_text(text, encoding='utf-8')
    # ARM64 can fuse arithmetic even without x86 AVX/FMA. Preserve PS2 rounding.
    path = Path(engine)/'scripts/cxx.sh'
    text = path.read_text(encoding='utf-8')
    marker = 'cxx_all="${CXXFLAGS:-} $cxx_stdlib $cxx_extra"'
    text = text.replace(marker, 'cxx_extra="$cxx_extra -ffp-contract=off"\n' + marker) if 'cxx_extra="$cxx_extra -ffp-contract=off"' not in text else text
    path.write_text(text, encoding='utf-8')
