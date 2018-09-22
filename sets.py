import re
import phrases
from phrase import Phrase

processors = list(
    map(
        lambda name: getattr(phrases, name),
        filter(
            lambda x: not x.startswith("__") and not x == "re" and not x.startswith('__'),
            dir(phrases)
        )
    )
)

def apply_processors(line):
    results = list(
        filter(
            lambda x: x is not None,
            map(
                lambda proc: proc(line),
                processors
            )
        )
    )
    if len(results) >= 1:
        result = results[0]
        if 'PR' in result:
            result['P'] = apply_processors(result['PR'])
        if 'QR' in result:
            result['Q'] = apply_processors(result['QR'])
        print(result)
        return result

    return {
        'P': "INPUT",
        'Q': line,
        'relation': "->"
    }


def clean(sentence):
    if sentence is None:
        return sentence

    sentence = re.sub(
        r"\s*(if|would|will|were|should|be|could|to|do|does|is|was|for|on|it)\s+",
        " ",
        sentence
    ).strip()
    sentence = re.sub(r"\s+", " ", sentence).strip()
    sentence = re.sub(r"dn't", "d not", sentence).strip()
    sentence = re.sub(r"sn't", "s not", sentence).strip()
    sentence = re.sub(r"n't", "n not", sentence).strip()
    sentence = re.sub(r"un(\w+)", r"not \1", sentence).strip()
    sentence = re.sub(r"neither (\w+) nor", r"not \1 and not", sentence).strip()
    return sentence


and_or_regex = r"(?P<left>.*(?:not\s+)?\w+)\s+(?P<modifier>and|or)\s+(?P<right>(?:not\s+)?\w+.*)"


def postprocess(sentence):
    if isinstance(sentence, dict):
        return apply_postprocessing(sentence)

    if sentence is None:
        return sentence

    sentence = clean(sentence)

    ret = sentence

    subject = re.search(r"^(?:not\s+)?(?P<word>\w+)", sentence)
    if subject is not None:
        sentence = clean(sentence[:subject.start('word')].strip() + ' ' + sentence[subject.end('word'):].strip())
        subject = subject.group('word')
    else:
        subject = ''

    and_or = re.search(and_or_regex, sentence)
    if and_or is not None:
        if and_or.group('modifier') == 'and':
            relation = '&'
        else:
            relation = '|'

        left_side = and_or.group('left')
        right_side = and_or.group('right')
        should_chain = re.search(r"^\w+\s*$", and_or.group('left'))
        if should_chain is not None:
            rest_right_side = re.search(r"^\w+\s*(?P<rest>.*)$", right_side)
            left_side += " " + rest_right_side.group('rest')

        ret = {
            "P": clean(subject + ' ' + (sentence[:and_or.start()] + ' ' + left_side + ' ' + postprocess(sentence[and_or.end():])).strip()),
            "Q": clean(subject + ' ' + (sentence[:and_or.start()] + ' ' + right_side + ' ' + postprocess(sentence[and_or.end():])).strip()),
            'relation': relation
        }

    return ret

def apply_postprocessing(dict):
    dict["Q"] = postprocess(dict["Q"])
    dict["P"] = postprocess(dict["P"])
    return dict

def find_subject_in_sentence(sentence):
    if isinstance(sentence, dict):
        ret = find_subject_in_phrase(sentence)
        if ret is not None:
            return ret
    else:
        first = re.search(r"^(?:not\s+)?(?P<word>\w+)", sentence).group('word')
        if "he" not in first:
            return first

def find_subject_in_phrase(phrase):
    [P, Q] = [phrase["P"], phrase["Q"]]
    if P is not "INPUT":
        ret = find_subject_in_sentence(P)
        if ret is not None:
            return ret
    ret = find_subject_in_sentence(Q)
    if ret is not None:
        return ret

def find_subject(phrases):
    for phrase in phrases:
        ret = find_subject_in_phrase(phrase)
        if ret is not None:
            return ret

def replace_subject_in_sentence(sentence, subject):
    if isinstance(sentence, dict):
        return replace_subject_in_phrase(sentence, subject)
    if sentence is None:
        return sentence
    first = re.search(r"^(?:not\s+)?(?P<word>\w+)", sentence)
    return clean(subject + ' ' + sentence[:first.start('word')] + ' ' + sentence[first.end('word'):])

def replace_subject_in_phrase(phrase, subject):
    [P, Q] = [phrase["P"], phrase["Q"]]
    if P is not "INPUT":
        phrase["P"] = replace_subject_in_sentence(P, subject)
    phrase["Q"] = replace_subject_in_sentence(Q, subject)
    return phrase

def replace_subjects(phrases, subject):
    for phrase in phrases:
        replace_subject_in_phrase(phrase, subject)

def find_predicates(phrases):
    predicates = []
    for phrase in phrases:
        predicates += phrase.predicates
    predicates = list(filter(lambda x: len(x) > 0, predicates))
    return predicates

def print_predicate_set_item(item):
    if isinstance(item, dict):
        return print_predicate_set(item)
    else:
        if item is None:
            return ''
        return item

def print_predicate_set(pset):
    return "(" + print_predicate_set_item(pset["P"]) + " " + pset["relation"] + " " + print_predicate_set_item(pset["Q"]) + ")"


def check_and_re_analyse(D):
    if 'R' in D:
        print("Rechecking")
        print(D['R'].strip())
        print(apply_processors(D['R'].strip()))
        return apply_processors(D['R'].strip())

class LogicSet:
    def __init__(self, line):
        self.line = line.strip()
        self.phrases = list(
            map(
                lambda x:
                apply_processors(x.strip().lower()),
                re.findall(r"[^.;]+", self.line)
            )
        )
        self.phrases += list(
            filter(
                lambda x: x is not None,
                map(
                    lambda x: check_and_re_analyse(x),
                    self.phrases
                )
            )
        )
        self.phrases = list(
            map(
                lambda x: apply_postprocessing(x),
                self.phrases
            )
        )
        replace_subjects(self.phrases, find_subject(self.phrases))
        self.phrases = [Phrase(phrase) for phrase in self.phrases]
        predicates = list(set(find_predicates(self.phrases)))
        self.predicates = {}
        index = 0
        for predicate in predicates:
            self.predicates[predicate] = chr(ord("A") + index)
            index += 1


    def __str__(self):
        ret = "Line: " + self.line + "\n"
        ret += "==========\n"
        for phrase in self.phrases:
            ret += str(phrase) + '\n'
        ret += "==========\n"
        predicate_set = list(map(lambda phrase: phrase.predicate_set(self.predicates), self.phrases))
        ret += "\n".join([key + ': ' + value for (key, value) in self.predicates.items()]) + "\n\n"
        ret += "\n".join(list(map(lambda pset: print_predicate_set(pset), predicate_set))) + "\n"
        ret += "==========\n"
        return ret
