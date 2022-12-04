from random import sample


def generatePhrase():
    return sample([
        ["a", "a'", "b", "[HC]", "c", "c'", "d", "[AC]"],
        ["a", "[HC]", "b", "[AC]"],
        ["a", "b", "[AC]", "c", "b", "[AC]"],
        ["a", "b", "[AC]", "a'", "b'", "[AC]"],
        ["a", "[AC]"],
        ["a", "b", "[AC]"]
    ], 1)[0]


if __name__ == "__main__":
    phrase = generatePhrase()
    print(phrase)









