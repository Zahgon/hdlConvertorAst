from typing import Optional

from hdlConvertorAst.hdlAst._expr import HdlValueInt


class Indent(object):
    """
    indentation context
    """

    def __init__(self, autoIndentStream):
        self.s = autoIndentStream
        self.original_indent = None

    def __enter__(self):
        s = self.s
        self.original_indent = s.indent_str
        s.indent_cnt += 1
        s.indent_str = s.indent_str + s.INDENT_STEP

    def __exit__(self, exception_type, exception_value, traceback):
        s = self.s
        s.indent_cnt -= 1
        s.indent_str = self.original_indent


class UnIndent():
    """
    unindentation context
    """

    def __init__(self, autoIndentStream):
        self.s = autoIndentStream
        self.original_indent = None

    def __enter__(self):
        s = self.s
        self.original_indent = s.indent_str
        assert s.indent_cnt > 0
        s.indent_cnt -= 1
        s.indent_str = s.indent_str[0:len(s.indent_str) - len(s.INDENT_STEP)]

    def __exit__(self, exception_type, exception_value, traceback):
        s = self.s
        s.indent_cnt += 1
        s.indent_str = self.original_indent


class AutoIndentingStream():

    def __init__(self, stream, indent_step):
        """
        :param stream: output stream
        :param indent_step: string of indent
        """

        self.INDENT_STEP = indent_step
        self.stream = stream
        self.requires_indent = True
        self.indent_cnt = 0
        self.indent_str = ""

    def write(self, s):
        w = self.stream.write
        if self.requires_indent and s != "\n":
            w(self.indent_str)
        w(s)
        self.requires_indent = s.endswith("\n")

    def close(self):
        pass


def iter_with_last(it):
    # Ensure it's an iterator and get the first field
    it = iter(it)
    try:
        prev = next(it)
    except StopIteration:
        return
    for item in it:
        # Lag by one item so I know I'm not at the end
        yield False, prev
        prev = item

    # Last item
    yield True, prev


def to_unsigned(val: int, width: int) -> int:
    pass


def _mask_fits_hex(width: int, vld_mask: Optional[int]):
    # check bits for hex digit have all same value
    pass


def bit_string(v: int, width: int, vld_mask:Optional[int]=None):
    """
    :param v: integer value of bitstring
    :param width: number of bits in value
    :param vld_mask: mask which has 1 for every valid bit in value
    :return: HdlValueInt
    """
    pass
