from hdlConvertorAst.hdlAst._statements import HdlStmIf, HdlStmBlock


def elifs_to_if_then_else(stm):
    """
    Optionally create if-then-else without else-ifs from this if-then-else statement

    :type stm: HdlStmIf
    :note: non recursive
    """
    pass
