import io
import logging
import sys

from jaraco.logging import TimestampFileHandler


def test_unused_handler_does_not_close_stderr(tmp_path, monkeypatch):
    stderr = io.StringIO()
    monkeypatch.setattr(sys, 'stderr', stderr)
    handler = TimestampFileHandler(str(tmp_path / 'log.txt'))
    handler.close()
    assert not stderr.closed
    stderr.write('still usable')


def test_rotation_closes_previous_file(tmp_path, monkeypatch):
    stderr = io.StringIO()
    monkeypatch.setattr(sys, 'stderr', stderr)
    paths = iter([str(tmp_path / 'first.log'), str(tmp_path / 'second.log')])
    handler = TimestampFileHandler(str(tmp_path / 'log.txt'))
    monkeypatch.setattr(handler, 'get_filename', lambda timestamp: next(paths))
    record = logging.LogRecord('test', logging.INFO, __file__, 1, 'message', (), None)
    try:
        handler.emit(record)
        previous = handler.stream
        handler.emit(record)
        assert previous.closed
        assert not handler.stream.closed
        assert not stderr.closed
        current = handler.stream
    finally:
        handler.close()
    assert current.closed
    handler.close()
    assert not stderr.closed
