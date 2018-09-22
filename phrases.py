import re


def a_necessary_and_not_sufficient(phrase):
    match = re.search(r"\s*necessary (and|but) not sufficient\s*", phrase)
    if match is not None:
        [P, Q] = [
            re.sub(r"[,.\ ]+", " ", sentence.strip())
            for sentence in phrase.split(match.group(0))
        ]

        return {
            'P': {
                'P': P,
                'Q': Q,
                'relation': '->'
            },
            'Q': {
                'P': None,
                'Q': {
                    'P': Q,
                    'Q': P,
                    'relation': '->'
                },
                'relation': '!'
            },
            'relation': "&"
        }


def will_if(phrase):
    match = re.search(r"will(?P<first>.*)if(?P<second>.*)", phrase)
    if match is not None:
        [P, Q] = [
            item.strip()
            for item in match.groups()
        ]
        return {
            'P': Q,
            'Q': P,
            'relation': '->'
        }

def a_given(phrase):
    match = re.search(r"given(?P<given>[^,]+),(?P<then>[^,]+),?(?P<rest>.*)?", phrase)
    if match is not None:
        return {
            'P': match.group('given'),
            'QR': match.group('then'),
            'R': match.group('rest'),
            'relation': '->'
        }


def unless(phrase):
    if 'unless' in phrase:
        sentences = phrase.split('unless')
        [P, Q] = [sentence.strip() for sentence in sentences]
        return {
            'P': "not " + P,
            'Q': Q,
            'relation': "|"
        }


def suppose(phrase):
    if 'suppose' in phrase:
        phrase = re.sub(
            r"\s*suppose\s*(?:(?:that|also)\s*){0,2}",
            "",
            phrase
        ).strip()

        [P, Q] = [None, None]
        if "then" in phrase:
            sentences = phrase.split("then")
            [P, Q] = [
                sentence.strip()
                for sentence in sentences
            ]

        verbs = list(filter(
            lambda x: x in phrase,
            ['when', 'if']
        ))

        if len(verbs) == 1:
            sentences = phrase.split(verbs[0] + ' ')
            [P, Q] = [
                sentence.strip()
                for sentence in sentences
            ]

        if P is not None and Q is not None:
            return {
                'P': P,
                'Q': Q,
                'relation': "->"
            }


def assume(phrase):
    if 'assume' in phrase:
        phrase = re.sub(r"\s*(assume)\s+(?:that\s*)?", "", phrase)
        return {
            'P': "INPUT",
            'Q': phrase,
            'relation': "->"
        }


def if_and_only_if(phrase):
    ifs = list(filter(
        lambda x: x in phrase,
        ['if and only if', 'iff']
    ))
    if len(ifs) == 1:
        sentences = phrase.split(ifs[0])
        [P, Q] = [
            sentence.strip()
            for sentence in sentences
        ]
        return {
            'P': P,
            'Q': Q,
            'relation': "<->"
        }


def only_if(phrase):
    if 'only if' in phrase:
        sentences = phrase.split('only if')
        [Q, P] = [
            sentence.strip()
            for sentence in sentences
        ]
        return {
            'P': P,
            'Q': Q,
            'relation': "<->"
        }


def respectively(phrase):
    respective = re.search(r"\s*(and\s*)?\s*respectively\s*", phrase)
    if respective is not None:
        sentences = phrase.split(respective.group(0))
        [P, Q] = [
            sentence.strip()
            for sentence in sentences
        ]
        return {
            'P': P,
            'Q': Q,
            'relation': "&"
        }

def __make_dict_from_list(list, relation = '->'):
    if len(list) > 1:
        return {
            'P': list[0],
            'Q': __make_dict_from_list(list[1:], relation),
            'relation': relation
        }

    return list[0]


def comma_separated(phrase):
    if ',' in phrase:
        sentences = phrase.split(',')
        sentences = [
            sentence.strip()
            for sentence in sentences
        ]

        if len(sentences) == 2:
            return {
                'P': sentences[0],
                'Q': sentences[1],
                'relation': "->"
            }

        return __make_dict_from_list(sentences)
