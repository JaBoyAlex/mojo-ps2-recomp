"""Preserve queue semantics while avoiding division for power-of-two rings."""
import importlib.util
from pathlib import Path


def apply(engine):
    spec = importlib.util.spec_from_file_location(
        'display_labels', Path(__file__).with_name('display_labels.py'))
    labels = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(labels)
    replace_once = labels.replace_once
    header = engine / 'runtime/src/gs/queue.hpp'
    source = engine / 'runtime/src/gs/queue.cpp'
    replace_once(header, '    std::uint64_t capacity_ = 0;', '''    std::uint64_t capacity_ = 0;
    std::uint64_t offset_mask_ = 0;
    // Equivalent to modulo for power-of-two capacities. Keep the original
    // operation for other capacities; no queue sizing or ordering changes.
    std::uint64_t offset(std::uint64_t cursor) const {
        return offset_mask_ ? cursor & offset_mask_ : cursor % capacity_;
    }''')
    replace_once(source, '    capacity_ = capacity;', '''    capacity_ = capacity;
    offset_mask_ = capacity && !(capacity & (capacity - 1)) ? capacity - 1 : 0;''')
    replace_once(source, 'const std::uint64_t pos = head % capacity_;',
                 'const std::uint64_t pos = offset(head);')
    replace_once(source, 'buffer_.get() + head % capacity_;',
                 'buffer_.get() + offset(head);')
    replace_once(source, 'const std::uint64_t pos = tail % capacity_;',
                 'const std::uint64_t pos = offset(tail);')
