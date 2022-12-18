from pcfg import PCFG
from nltk.grammar import Nonterminal, ProbabilisticProduction
from multipledispatch import dispatch
from schenkComposer.utility import productionsDictFromJSON
from schenkComposer.contour.contour import Contour


class ContourPCFG:
    """
    Probabilistic context-free grammar for contours
    """
    @dispatch(str, str)
    def __init__(self, filepath, urlinieContour: str):
        startProduction = ProbabilisticProduction(
            Nonterminal("S"),
            [Nonterminal(urlinieContour)],
            prob=1
        )
        self.__init__(
            productionsDictFromJSON(filepath),
            startProduction
        )

    @dispatch(dict, ProbabilisticProduction)
    def __init__(
            self,
            productionsDict: dict,
            startProduction: ProbabilisticProduction = ProbabilisticProduction(Nonterminal("S"), ["0"], prob=1)
    ):
        """
        :param productionsDict: (k)'contour->contours' (v)probability, using the ascii version of the contours
        :param startProduction: The production from which the PCFG starts with probability 1
        """
        productions = [startProduction]
        for prodStr, prob in productionsDict.items():
            # Divide the entire production string into its left- and right-hand sides
            lhs, rhs = prodStr.replace(" ", "").split("->")
            # Divide the right-hand side into its series of terminals and/or nonterminals
            rhs = rhs.split("-")
            # Wrap the left-hand side in a Nonterminal object
            lhs = Nonterminal(lhs)
            # Wrap the right-hand side in Nonterminal objects if nonterminal, keep as is otherwise
            rhs = [r if (r[1:] in ["1", "1_"]) else Nonterminal(r) for r in rhs]
            # Add the ProbabilisticProduction to the list of productions
            productions.append(ProbabilisticProduction(lhs, rhs, prob=prob))

        self.productions = productions
        self.pcfg = PCFG(Nonterminal("S"), productions)

    def newStartProduction(self, contour: str):
        startProduction = ProbabilisticProduction(
            Nonterminal("S"),
            [Nonterminal(contour)],
            prob=1
        )
        self.productions = [startProduction] + self.productions[1:]
        self.pcfg = PCFG(Nonterminal("S"), self.productions)

    def generate(self, num: int):
        """Generate `num` examples from the grammar"""
        generations = []
        for _ in range(num):
            generation = [s for s in self.pcfg.generate(1)][0]
            generation = [Contour(c) for c in generation.split(" ")]
            generations.append(generation)
        return generations

    def printGenerated(self, generated):
        print("".join([str(c) for c in generated]))


if __name__ == "__main__":
    from schenkComposer.utility import productionsDictFromJSON
    from schenkComposer.config import PRODUCTIONS_JSON_PATH

    pcfg = ContourPCFG(PRODUCTIONS_JSON_PATH, "d31")
    generated = pcfg.generate(3)
    for g in generated:
        pcfg.printGenerated(g)