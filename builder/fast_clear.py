"""Exact, guarded GS page clears; retain the general renderer as fallback."""
import importlib.util
from pathlib import Path


def apply(engine):
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location('display_labels', here/'display_labels.py')
    labels = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(labels)
    replace = labels.replace_once
    folder = engine/'runtime/src/gs/gpu'
    gpu, shader = folder/'gpu.cpp', folder/'gs.wgsl'
    helper = (here/'fast_clear.inc').read_bytes()
    target = folder/'mojo_fast_clear.inc'
    if not target.exists() or target.read_bytes() != helper:
        target.write_bytes(helper)
    replace(gpu, 'kDecode, kPipelines };', 'kDecode, kFastClear, kPipelines };')
    replace(gpu, '"resolve", "snapshot", "decode"};',
            '"resolve", "snapshot", "decode", "fast_clear"};')
    replace(gpu, 'bool g_live = false;',
            'bool g_fast_clear = false;\nstd::uint64_t g_fast_clears = 0;\nbool g_live = false;')
    replace(gpu, 'void flush_batch() {', '#include "mojo_fast_clear.inc"\n\nvoid flush_batch() {')
    replace(gpu, '    const std::uint32_t prims = static_cast<std::uint32_t>(b.prims.size() / kPrimWords);',
            '    if (try_fast_clear()) return;\n    const std::uint32_t prims = static_cast<std::uint32_t>(b.prims.size() / kPrimWords);')
    replace(gpu, '    auto make_pipeline = [=](int entry, bool mip) {', '''    const bool has_clear = shader_text.empty() || shader_text.find("fn fast_clear") != std::string::npos;
    g_fast_clear = has_clear && os::env("PS2_FAST_CLEAR") != "0";
    auto make_pipeline = [=](int entry, bool mip) {''')
    replace(gpu, '    for (int i = 0; i < kPipelines; ++i) {\n        g_pipelines[i] = make_pipeline(i, false);',
            '    for (int i = 0; i < kPipelines; ++i) {\n        if (i == kFastClear && !has_clear) continue;\n        g_pipelines[i] = make_pipeline(i, false);')
    line = '    for (int i = 0; i < kPipelines; ++i) std::fprintf(stderr, " %s %llu", kEntryPoints[i], static_cast<unsigned long long>(g_dispatches[i]));'
    replace(gpu, line, line+'\n    std::fprintf(stderr, " [fast-clear %llu]", static_cast<unsigned long long>(g_fast_clears));')
    kernel = (here/'fast_clear.wgsl').read_text(encoding='utf-8')
    text = shader.read_text(encoding='utf-8')
    if kernel not in text:
        if 'fn fast_clear(' in text:
            raise ValueError('Unexpected fast-clear shader implementation')
        shader.write_text(text.rstrip()+'\n\n'+kernel, encoding='utf-8', newline='\n')
