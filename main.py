from sets import LogicSet

with open('./input') as f:
    sets = list(
        filter(
            lambda x: len(x) > 0,
            [x.strip() for x in f.readlines()]
        )
    )
    phrases = [LogicSet(set) for set in sets]
    print("\n".join(list(map(lambda x: str(x), phrases))))
