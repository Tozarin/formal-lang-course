from pathlib import Path

from antlr4 import ParserRuleContext

from project.interpret.LenguageVisitor import LenguageVisitor
from project.interpret.LenguageParser import LenguageParser 
from project.interpret.types import LSet, LPair, LTriple, LCFG, LFiniteAutoma
from project.interpret.patterns import PAny, PName, PPair, PTriple, match


class InterpretVisitor(LenguageVisitor):
    def __init__(self):
        self.envs = [{}]
        self.is_print = True

    def set_var(self, var_name: str, value):
        self.envs[-1][var_name] = value

    def get_var(self, var_name: str):
        for env in reversed(self.envs):
            if var_name in env:
                return env[var_name]

        raise RuntimeError(f"Unknown variable name: {var_name}")

    def add_env(self, env: dict):
        self.envs.append(env)

    def pop_env(self):
        if len(self.envs) < 2:
            raise RuntimeError("Cant pop global env")

        self.envs.pop()

    def visitProgramm(self, contex: ParserRuleContext):
        return self.visitChildren(contex)

    def visitBind(self, contex: LenguageParser.BindContext):
        var_name = contex.VAR().getText()
        value = self.visit(contex.expr())
        self.set_var(var_name, value)

    def visitPrint(self, contex: LenguageParser.PrintContext):
        argument = self.visit(contex.expr())
        if self.is_print:
            print(str(argument) + "\n")
        return argument

    def visitVar(self, contex: LenguageParser.VarContext):
        return self.get_var(contex.VAR().getText())

    def visitInt(self, contex: LenguageParser.IntContext):
        return int(contex.INT().getText())

    def visitString(self, contex: LenguageParser.StringContext):
        return contex.STRING().getText()[1:-1]

    def visitBool(self, contex: LenguageParser.BoolContext):
        return contex.BOOL().getText() == "true"

    def visitRegex(self, contex: LenguageParser.RegexContext):
        return LFiniteAutoma.from_string(contex.REGEX().getText()[2:-1])

    def visitCfg(self, contex: LenguageParser.CfgContext):
        return LCFG.from_string(contex.CFG().getText()[2:-1])

    def visitPair(self, contex: LenguageParser.PairContext):
        return LPair(self.visit(contex.expr(0)), self.visit(contex.expr(1)))

    def visitTriple(self, contex: LenguageParser.TripleContext):
        return LTriple(self.visit(contex.expr(0)), self.visit(contex.expr(1)), self.visit(contex.expr(2)))

    def visitIn(self, contex: LenguageParser.InContext):
        elem = self.visit(contex.expr(0))
        elems = self.visit(contex.expr(1))

        if not isinstance(elems, LSet):
            raise TypeError(f"Expected set type at left argument of \"in\", not: {type(elems)}")

        return elem in elems

    def visitNot(self, contex: LenguageParser.NotContext):
        value = self.visit(contex.expr())
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool type at argument of \"not\", not: {type(value)}")

        return not value

    def visitOr(self, contex: LenguageParser.OrContext):
        left_value = self.visit(contex.expr(0))
        right_value = self.visit(contex.expr(1))

        if not isinstance(left_value, bool):
            raise TypeError(f"Expected bool type at left argument of \"or\", not: {type(value)}")
        if not isinstance(right_value, bool):
            raise TypeError(f"Expected bool type at right argument of \"or\", not: {type(value)}")

        return left_value or right_value

    def visitAnd(self, contex: LenguageParser.AndContext):
        left_value = self.visit(contex.expr(0))
        right_value = self.visit(contex.expr(1))

        if not isinstance(left_value, bool):
            raise TypeError(f"Expected bool type at left argument of \"and\", not: {type(value)}")
        if not isinstance(right_value, bool):
            raise TypeError(f"Expected bool type at right argument of \"and\", not: {type(value)}")

        return left_value and right_value        

    def visitSet(self, contex: LenguageParser.SetContext):
        return LSet({self.visit(elem) for elem in contex.expr()})

    def visitRange(self, contex: LenguageParser.RangeContext):
        return LSet(range(int(contex.INT(0).getText()), int(contex.INT(1).getText()) + 1))

    def visitStarting(self, contex: LenguageParser.StartingContext):
        return self.visit(contex.expr()).starting()

    def visitFinal(self, contex: LenguageParser.FinalContext):
        return self.visit(contex.expr()).final()

    def visitNodes(self, contex: LenguageParser.NodesContext):
        return self.visit(contex.expr()).nodes()

    def visitEdges(self, contex: LenguageParser.EdgesContext):
        return self.visit(contex.expr()).edges()

    def visitMarks(self, contex: LenguageParser.MarksContext):
        return self.visit(contex.expr()).marks()

    def visitReachables(self, contex: LenguageParser.ReachablesContext):
        return self.visit(contex.expr()).reachables()

    def visitMap(self, contex: LenguageParser.MapContext):
        pattern = self.visit(contex.pattern())
        elems = self.visit(contex.expr(0))

        def action():
            return self.visit(contex.expr(1))

        if not isinstance(elems, LSet):
            raise TypeError(f"To \"map\" first argument must be set, not {type(elems)}")

        mapped = set()
        for elem in elems.set:
            if isinstance(elem, LPair) or isinstance(elem, LTriple):
                elem = elem.to_tuple()
            self.add_env(match(pattern, elem))
            mapped.add(action())
            self.pop_env()

        return LSet(mapped)

    def visitFilter(self, contex: LenguageParser.FilterContext):
        pattern = self.visit(contex.pattern())
        elems = self.visit(contex.expr(0))

        def action():
            return self.visit(contex.expr(1))

        if not isinstance(elems, LSet):
            raise TypeError(f"To \"filter\" first argument must be set, not {type(elems)}")

        filtred = set()
        for elem in elems.set:
            if isinstance(elem, LPair) or isinstance(elem, LTriple):
                elem = elem.to_tuple()
            self.add_env(match(pattern, elem))
            result = action()

            if not isinstance(result, bool):
                TypeError(f"Lambda filter result type must be bool, not {type(result)}")

            if result:
                filtred.add(elem)
            
            self.pop_env()

        return LSet(filtred)

    def visitSet_starting(self, contex: LenguageParser.Set_startingContext):
        return self.visit(contex.expr(0)).set_starting(self.visit(contex.expr(1)))

    def visitSet_final(self, contex: LenguageParser.Set_finalContext):
        return self.visit(contex.expr(0)).set_final(self.visit(contex.expr(1)))

    def visitAdd_starting(self, contex: LenguageParser.Add_startingContext):
        return self.visit(contex.expr(0)).add_starting(self.visit(contex.expr(1)))

    def visitAdd_final(self, contex: LenguageParser.Add_finalContext):
        return self.visit(contex.expr(0)).add_final(self.visit(contex.expr(1)))

    def visitLoad_dot(self, contex: LenguageParser.Load_dotContext):
        name = contex.STRING().getText()[1:-1]
        if not isinstance(name, str):
            raise TypeError(f"To \"load_dot\" argument must be string type, not {type(name)}")

        path = Path(name)
        if path.name.startswith("cfg"):
            return LCFG.from_file(path)
        else:
            return LFiniteAutoma.from_file(path)

    def visitLoad_graph(self, contex: LenguageParser.Load_graphContext):
        name = contex.STRING().getText()[1:-1]
        if not isinstance(name, str):
            raise TypeError(f"To \"load_graph\" argument must be string type, not {type(name)}")

        return LFiniteAutoma.from_data(name)

    def visitInter(self, contex: LenguageParser.InterContext):
        return self.visit(contex.expr(0)).intersect(self.visit(contex.expr(1)))

    def visitUnion(self, contex: LenguageParser.UnionContext):
        return self.visit(contex.expr(0)).union(self.visit(contex.expr(1)))

    def visitConcat(self, contex: LenguageParser.ConcatContext):
        return self.visit(contex.expr(0)).concat(self.visit(contex.expr(1)))

    def visitStar(self, contex: LenguageParser.StarContext):
        automa = self.visit(contex.expr())
        if not isinstance(automa, LFiniteAutoma):
            raise TypeError(f"Argument of \"*\" must be FiniteAutoma type, not {type(automa)}")

        return automa.star()

    def visitParents(self, contex: LenguageParser.ParentsContext):
        return self.visit(contex.expr())
    
    def visitAny(self, contex: LenguageParser.AnyContext):
        return PAny()

    def visitUnvar(self, contex: LenguageParser.UnvarContext):
        return PName(contex.VAR().getText())

    def visitUnpair(self, contex: LenguageParser.UnpairContext):
        return PPair(self.visit(contex.pattern(0)), self.visit(contex.pattern(1)))

    def visitUntriple(self, contex: LenguageParser.UntripleContext):
        return PTriple(self.visit(contex.pattern(0)), self.visit(contex.pattern(1)), self.visit(contex.pattern(2)))
