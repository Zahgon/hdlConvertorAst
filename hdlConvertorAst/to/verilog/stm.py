from hdlConvertorAst.hdlAst import HdlOpType, HdlStmWait, HdlStmBlock,\
    HdlStmProcessTriggerConstrain
from hdlConvertorAst.to.hdlUtils import Indent, iter_with_last
from hdlConvertorAst.to.verilog.expr import ToVerilog2005Expr


class ToVerilog2005Stm(ToVerilog2005Expr):
    ASSIGN_OPS = {
        HdlOpType.ASSIGN: '=',
        HdlOpType.PLUS_ASSIGN: '+=',
        HdlOpType.MINUS_ASSIGN: '-=',
        HdlOpType.MUL_ASSIGN: '*=',
        HdlOpType.DIV_ASSIGN: '/=',
        HdlOpType.MOD_ASSIGN: '%=',
        HdlOpType.AND_ASSIGN: '&=',
        HdlOpType.OR_ASSIGN: '|=',
        HdlOpType.XOR_ASSIGN: '^=',
        HdlOpType.SHIFT_LEFT_ASSIGN: '<<=',
        HdlOpType.SHIFT_RIGHT_ASSIGN: '>>=',
        HdlOpType.ARITH_SHIFT_LEFT_ASSIGN: '<<<=',
        HdlOpType.ARITH_SHIFT_RIGHT_ASSIGN: '>>>=',
    }

    def __init__(self, out_stream):
        super(ToVerilog2005Stm, self).__init__(out_stream)
        self.top_stm = None
        self.is_in_loop_spec = False
    
    def visit_hdlAttributes(self, o):
        """
        :type o: List[Tuple[str, Optional[iHdlExpr]]]
        """
        if not o:
            return
        w = self.out.write
        w("(* ")
        for last, (aId, aVal) in iter_with_last(o):
            w(aId)
            if aVal is not None:
                w("=")
                self.visit_iHdlExpr(aVal)

            if not last:
                w(", ")
        w(" *)")

    def visit_iHdlStatement(self, stm):
        """
        :type stm: iHdlStatement
        """
        if stm.hdlAttributes:
            self.visit_hdlAttributes(stm.hdlAttributes)
            self.out.write("\n")

        if self.top_stm is None:
            self.top_stm = stm
            try:
                return ToVerilog2005Expr.visit_iHdlStatement(self, stm)
            finally:
                self.top_stm = None
        else:
            return ToVerilog2005Expr.visit_iHdlStatement(self, stm)

    def visit_HdlStmProcess(self, proc):
        """
        :type proc: HdlStmProcess
        """
        self.visit_doc(proc)
        sens = proc.sensitivity
        body = proc.body
        w = self.out.write
        skip_body = False
        if sens is None and proc.trigger_constrain is None:
            if isinstance(body, HdlStmWait):
                skip_body = True
                wait = body
                body = []
            elif (isinstance(body, HdlStmBlock)
                    and body.body
                    and isinstance(body.body[0], HdlStmWait)):
                wait = body.body[0]
                body = body.body[1:]
            else:
                wait = None

            if wait is None:
                assert self.top_stm is proc
                assert isinstance(body, HdlStmBlock), body
                body = body.body
                wait = body[-1]
                assert isinstance(wait, HdlStmWait), wait
                assert len(wait.val) == 0
                body = body[:-1]
                w("initial")
            else:
                if self.top_stm is proc:
                    w("always ")
                w("#")
                assert len(wait.val) == 1
                self.visit_iHdlExpr(wait.val[0])
            _body = HdlStmBlock()
            _body.body = body
            body = _body
        else:
            tr = proc.trigger_constrain
            if self.top_stm is proc:
                if tr is None:
                    w("always ")
                elif tr is HdlStmProcessTriggerConstrain.FF:
                    w("always_ff ")
                elif tr is HdlStmProcessTriggerConstrain.COMB:
                    w("always_comb ")
                elif tr is HdlStmProcessTriggerConstrain.LATCH:
                    w("always_latch ")
                else:
                    raise ValueError(proc.trigger_constrain)
            if tr is None:
                w("@(")
                for last, item in iter_with_last(sens):
                    self.visit_iHdlExpr(item)
                    if not last:
                        w(", ")
                w(")")
            else:
                assert not sens

        # to prevent useless newline for empty always/time waits
        if skip_body:
            return True
        else:
            return self.visit_iHdlStatement_in_statement(body)

    def visit_iHdlStatement_in_statement(self, stm):
        """
        Print statement which is body of other statement
        e.g. body of process, branch of if-then-else or case of case stememnt
        """
        w = self.out.write
        if isinstance(stm, HdlStmBlock):
            if len(stm.body) == 1 and not stm.labels:
                stm = stm.body[0]
            else:
                w(" ")
                return self.visit_HdlStmBlock(stm)

        w("\n")
        with Indent(self.out):
            return self.visit_iHdlStatement(stm)

    def visit_HdlStmBlock(self, o):
        """
        :type o: HdlStmBlock
        """
        self.visit_doc(o)
        w = self.out.write
        if o.in_preproc:
            w("generate ")

        w("begin")
        if o.labels:
            w(": ")
            w(o.labels[0])
        w("\n")
        with Indent(self.out):
            for s in o.body:
                need_semi = self.visit_iHdlStatement(s)
                if need_semi:
                    w(";\n")
                else:
                    w("\n")
        w("end")
        if o.in_preproc:
            w(" endgenerate")
        return False

    def visit_HdlStmIf(self, o):
        """
        :type o: HdlStmIf
        """
        self.visit_doc(o)
        w = self.out.write
        if o.in_preproc:
            w("generate ")
        w("if (")
        self.visit_iHdlExpr(o.cond)
        w(")")
        need_semi = self.visit_iHdlStatement_in_statement(o.if_true)

        for cond, stms in o.elifs:
            if need_semi:
                w(";\n")
            else:
                w(" ")
            w("else if (")
            self.visit_iHdlExpr(cond)
            w(")")
            need_semi = self.visit_iHdlStatement_in_statement(stms)

        ifFalse = o.if_false
        if ifFalse is not None:
            if need_semi:
                w(";\n")
            else:
                w(" ")
            w("else")
            need_semi = self.visit_iHdlStatement_in_statement(ifFalse)

        if o.in_preproc:
            if need_semi:
                w(";\n")
            else:
                w("\n")
            w("endgenerate")
            return False
        else:
            return need_semi

    def visit_HdlStmAssign(self, o):
        """
        :type o: HdlStmAssign
        :return: True if requires ;\\n after end
        """
        self.visit_doc(o)
        w = self.out.write
        ts = self.top_stm
        if not self.is_in_loop_spec and (ts is o or (ts is not None and ts.in_preproc)):
            w("assign ")
            self.visit_iHdlExpr(o.dst)
            w(" = ")
        else:
            self.visit_iHdlExpr(o.dst)
            if o.is_blocking:
                w(" = ")
            else:
                w(" <= ")

        if o.time_delay is not None:
            w("#")
            self.visit_iHdlExpr(o.time_delay)
            w(" ")
        if o.event_delay is not None:
            w("@")
            if len(o.event_delay) > 1:
                w("(")
            for is_last, e in iter_with_last(o.event_delay):
                self.visit_iHdlExpr(e)
                if not is_last:
                    w(", ")
            if len(o.event_delay) > 1:
                w(")")
            w(" ")

        self.visit_iHdlExpr(o.src)
        return True

    def visit_HdlStmCase(self, o):
        """
        :type o: HdlStmCase

        :return: True if requires ;\\n after end
        """
        pass

    def visit_HdlStmWait(self, o):
        """
        :type o: HdlStmWait

        :return: True if requires ;\\n after end
        """
        pass

    def visit_HdlStmFor(self, o):
        """
        :type o: HdlStmFor

        :return: True if requires ;\\n after end
        """
        pass

    def visit_HdlStmForIn(self, o):
        """
        :type o: HdlStmForIn
        :return: True if requires ;\\n after end
        """
        pass

    def visit_HdlStmWhile(self, o):
        """
        :type o: HdlStmWhile
        :return: True if requires ;\\n after end
        """
        pass

    def visit_HdlStmRepeat(self, o):
        """
        :type o: HdlStmRepeat
        :return: True if requires ;\\n after end
        """
        pass

    def visit_HdlStmReturn(self, o):
        """
        :type o: HdlStmReturn
        """
        pass

    def visit_HdlStmContinue(self, o):
        """
        :type o: HdlStmContinue
        """
        pass

    def visit_HdlStmBreak(self, o):
        """
        :type o: HdlStmBreak
        """
        pass

    def visit_HdlStmThrow(self, o):
        """
        :type o: HdlStmThrow
        """
        raise ValueError("SystemVerilog does not have exceptions")

    # [TODO] SV only
    def visit_HdlImport(self, o):
        """
        :type o: HdlImport
        """
        pass
