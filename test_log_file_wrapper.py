import logging

from jaraco.logging import LogFileWrapper


def test_wrapper_logs_complete_lines_and_retains_partial(caplog):
    wrapper = LogFileWrapper('test.wrapper', logging.WARNING)
    with caplog.at_level(logging.WARNING, logger='test.wrapper'):
        wrapper.write('first')
        assert caplog.messages == []
        wrapper.write(' line\nsecond line\npartial')
        assert caplog.messages == ['first line', 'second line']
        assert wrapper.queued == 'partial'
        wrapper.write('\n')
        assert caplog.messages == ['first line', 'second line', 'partial']
        assert wrapper.queued == ''


def test_wrapper_accepts_empty_write(caplog):
    wrapper = LogFileWrapper('test.wrapper', logging.WARNING)
    wrapper.write('')
    assert wrapper.queued == ''
    assert caplog.messages == []
