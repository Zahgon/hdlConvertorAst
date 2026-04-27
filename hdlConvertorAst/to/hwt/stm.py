from hdlConvertorAst.hdlAst import HdlOp, HdlStmIf, HdlStmWhile, HdlStmBlock, HdlStmAssign, HdlStmCaseType
from hdlConvertorAst.to.hdlUtils import Indent, iter_with_last
from hdlConvertorAst.to.hwt.expr import ToHwtExpr
from hdlConvertorAst.to.basic_hdl_sim_model import ToBasicHdlSimModel


class ToHwtStm(ToHwtExpr):

    def visit_HdlStmProcess(self, o):
        """
        :type o: HdlStmProcess
        """
        w = self.out.write
        if o.labels:
            w("# ")
            if o.labels:
                w(o.labels[0])
                # w(", ")
        # w("sens: ")
        # if o.sensitivity:
        #    for last, s in iter_with_last(o.sensitivity):
        #        if isinstance(s, HdlOp):
        #            w(str(s.fn))
        #            w(" ")
        #            self.visit_iHdlExpr(s.ops[0])
        #        else:
        #            self.visit_iHdlExpr(s)
        #        if not last:
        #            w(", ")
        w("\n")
        self.visit_doc(o)
        if o.trigger_constrain is not None:
            raise NotImplementedError()
        self.visit_iHdlStatement(o.body)
        # w("\n")

    def visit_HdlStmBlock(self, o):
        """
        :type o: HdlStmBlock
        """
        self.visit_doc(o)
        w = self.out.write
        for is_last, i in iter_with_last(o.body):
            self.visit_iHdlStatement(i)
            if not is_last:
                if o.in_preproc:
                    w("\n")
                else:
                    w(",\n")

    def visit_HdlStmIf(self, o):
        """
        :type stm: HdlStmIf
        """
        self.visit_doc(o)
        w = self.out.write

        in_preproc = o.in_preproc
        if in_preproc:
            w("if ")
        else:
            w("If(")
        self.visit_iHdlExpr(o.cond)
        if in_preproc:
            w(":\n")
        else:
            w(",\n")
        with Indent(self.out):
            self.visit_iHdlStatement(o.if_true)
            w("\n")
        if not in_preproc:
            w(")")
        for (c, _stm) in o.elifs:
            if in_preproc:
                w("elif ")
            else:
                w(".Elif(")
            self.visit_iHdlExpr(c)
            if in_preproc:
                w(":\n")
            else:
                w(",\n")
            with Indent(self.out):
                self.visit_iHdlStatement(_stm)
            w("\n")
            if not in_preproc:
                w(")")

        ifFalse = o.if_false
        if ifFalse is not None:
            if in_preproc:
                w("else:\n")
            else:
                w(".Else(\n")
            with Indent(self.out):
                self.visit_iHdlStatement(ifFalse)
                w("\n")
            if not in_preproc:
                w(")")

    def visit_HdlStmAssign(self, o):
        """
        :type o: HdlStmAssign
        """
        self.visit_doc(o)
        w = self.out.write
        self.visit_iHdlExpr(o.dst)
        if o.is_blocking:
            raise NotImplementedError(o)
        if o.time_delay is not None:
            raise NotImplementedError()
        if o.event_delay is not None:
            raise NotImplementedError()
        if o.in_preproc:
            w(" = ")
            self.visit_iHdlExpr(o.src)
        else:
            w("(")
            self.visit_iHdlExpr(o.src)
            w(")")

    def visit_HdlStmCase(self, o):
        """
        :type o: HdlStmCase
        """
        pass

    def visit_HdlStmFor(self, o):
        """
        :type o: HdlStmFor
        """
        pass

    def visit_HdlStmWhile(self, o):
        """
        :type o: HdlStmWhile
        """
        pass

    def visit_HdlStmBreak(self, o):
        """
        :type o: HdlStmBreak
        """
        pass
    
    def visit_HdlStmContinue(self, o):
        """
        :type o: HdlStmContinue
        """
        pass
    
    def visit_HdlStmThrow(self, o):
        pass

    def visit_HdlStmWait(self, o):
        pass

    def visit_HdlStmNop(self, o):
        ToBasicHdlSimModel.visit_HdlStmNop(self, o)
