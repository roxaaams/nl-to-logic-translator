import re


def get_predicates(symbol):
    predicates = []
    if hasattr(symbol, 'is_null'):
        return predicates
    if isinstance(symbol, PropositionSymbol):
        predicates.append(symbol.id)
    else:
        predicates += symbol.predicates
    return predicates


def map_predicate(symbol, predicates):
    if hasattr(symbol, 'is_null'):
        return ''

    if isinstance(symbol, Phrase):
        return symbol.predicate_set(predicates)
    else:
        for (predicate, symb) in predicates.items():
            if predicate == symbol.id:
                ret = symb
                if symbol.is_not:
                    ret = "!" + symb
                return ret


class Phrase:
    def __init__(self, dict):
        self.P = dict["P"]
        self.Q = dict["Q"]
        if isinstance(self.P, type(dict)):
            self.P = Phrase(self.P)
        else:
            self.P = PropositionSymbol(self.P)
        if isinstance(self.Q, type(dict)):
            self.Q = Phrase(self.Q)
        else:
            self.Q = PropositionSymbol(self.Q)
        self.relation = dict["relation"]
        self.predicates = [] + get_predicates(self.P) + get_predicates(self.Q)

    def predicate_set(self, predicates):
        return {
            'P': map_predicate(self.P, predicates) or self.P.raw,
            'Q': map_predicate(self.Q, predicates) or self.Q.raw,
            'relation': self.relation
        }

    def __str__(self):
        return "(" + str(self.P) + " " + self.relation + " " + str(self.Q) + ")"


class PropositionSymbol:
    def __init__(self, inpt):
        self.raw = inpt

        if inpt is None:
            self.is_null = True
            return inpt

        subject = re.search(r"^\w+", inpt)
        inpt = inpt[subject.end():].strip()
        self.subject = subject.group(0).strip()

        has_not = re.search(r"\s*not\s+", inpt)
        self.is_not = False
        if has_not is not None:
            self.is_not = True
            inpt = (inpt[:has_not.start()] + ' ' + inpt[has_not.end():]).strip()

        self.id = inpt.strip()

    def __str__(self):
        if hasattr(self, 'is_null'):
            return ''

        str = self.subject + " "
        if self.is_not:
            str += "not "
        str += self.id
        return str
