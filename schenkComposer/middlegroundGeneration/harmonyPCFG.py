from pcfg import PCFG
from nltk.grammar import Nonterminal, ProbabilisticProduction
from multipledispatch import dispatch
from schenkComposer.utility import makeRomans


class HarmonyPCFG:
    """
    Probabilistic context-free grammar for harmonies
    """
    def __init__(
            self,
            productionsDict: dict,
            terminalStrings: list[str],
            startProduction: str
    ):
        """
        :param productionsDict: (k)'harmony->h1-h2-...-hn' (v)probability, using ascii roman numerals and variables
        :param terminalStrings: List of strings comprising the set of terminals
        :param startProduction: The production from which the PCFG starts with probability 1
        """
        productions = [ProbabilisticProduction(
            Nonterminal("S"),
            [f if (f in terminalStrings) else Nonterminal(f) for f in startProduction.split("-")],
            prob=1
        )]
        for prodStr, prob in productionsDict.items():
            lhs, rhs = prodStr.replace(" ", "").split("->")
            rhs = rhs.split("-")
            lhs = Nonterminal(lhs)
            rhs = [r if (r in terminalStrings) else Nonterminal(r) for r in rhs]
            productions.append(ProbabilisticProduction(lhs, rhs, prob=prob))

        self.productions = productions
        self.pcfg = PCFG(Nonterminal("S"), productions)

    def newStartProduction(self, harmonyVariable: str):
        startProduction = ProbabilisticProduction(
            Nonterminal("S"),
            [Nonterminal(harmonyVariable)],
            prob=1
        )
        self.productions = [startProduction] + self.productions[1:]
        self.pcfg = PCFG(Nonterminal("S"), self.productions)

    def generate(self, num: int):
        generations = []
        for _ in range(num):
            generation = [s for s in self.pcfg.generate(1)][0]
            generation = makeRomans(generation.split(" "))
            generations.append(generation)
        return generations


if __name__ == "__main__":
    from pprint import pprint
    
    pcfg = HarmonyPCFG(
        {
            "T4->I-IV-V-I6": 0.5,
            "T4->I-ii6-V-I6": 0.5,
            "PD2->IV-ii6": 0.8,
            "PD2->IV-ii": 0.2,
            "D2->Cad64-V": 1
        },
        "I-ii-iii-IV-V-vi-viio-I6-ii6-Cad64".split("-"),
        "T4-PD2-D2-I"
    )
    generated = pcfg.generate(3)
    pprint(generated)
