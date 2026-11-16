"""Small, repeatable compatibility patches to the pinned native framework."""
from pathlib import Path
import sys

def apply(engine):
    # Stock macOS Bash 3.2 supports all remaining constructs in these scripts.
    for name in ('setup.sh', 'port.sh'):
        path = Path(engine)/'scripts'/name
        text = path.read_text(encoding='utf-8')
        text = text.replace('[ "${BASH_VERSINFO:-0}" -lt 4 ]', '[ "${BASH_VERSINFO:-0}" -lt 3 ]')
        text = text.replace('${source_path,,}', '$(printf \'%s\' "$source_path" | tr \'[:upper:]\' \'[:lower:]\')')
        # Bash <=4.3 treats expansion of an empty array as unset under -u.
        # Use its defined-array idiom rather than disabling fail-fast checks.
        for array in ('pnach', 'wide', 'setup', 'modules', 'overlays', 'toggles', 'patches', 'presses'):
            original = '"${' + array + '[@]}"'
            guarded = '${' + array + '[@]+' + original + '}'
            if guarded not in text: text = text.replace(original, guarded)
        text = text.replace('this script needs bash 4 or newer', 'this script needs bash 3 or newer')
        path.write_text(text, encoding='utf-8')
    # ARM64 can fuse arithmetic even without x86 AVX/FMA. Preserve PS2 rounding.
    path = Path(engine)/'scripts/cxx.sh'
    text = path.read_text(encoding='utf-8')
    marker = 'cxx_all="${CXXFLAGS:-} $cxx_stdlib $cxx_extra"'
    text = text.replace(marker, 'cxx_extra="$cxx_extra -ffp-contract=off"\n' + marker) if 'cxx_extra="$cxx_extra -ffp-contract=off"' not in text else text
    path.write_text(text, encoding='utf-8')
    if sys.platform.startswith('linux'):
        # Keep pacing, sound and title statistics on the same steady timebase
        # as scheduling. Do not change guest clocks or the 60/50 Hz targets.
        header = Path(__file__).with_name('host_clock.hpp').read_text(encoding='utf-8')
        (Path(engine)/'host/mojo_host_clock.hpp').write_text(header,encoding='utf-8')
        path = Path(engine)/'host/window.cpp'
        text = path.read_text(encoding='utf-8')
        if '#include "mojo_host_clock.hpp"' not in text:
            text = text.replace('#include "window.hpp"', '#include "window.hpp"\n#include "mojo_host_clock.hpp"',1)
        text = text.replace('SDL_GetPerformanceCounter()', 'mojo::host_clock::counter()')
        text = text.replace('SDL_GetPerformanceFrequency()', 'mojo::host_clock::frequency()')
        path.write_text(text,encoding='utf-8')
