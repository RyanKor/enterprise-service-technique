from queue import Queue
from collections import defaultdict
from typing import List


class Node(dict):

    def __init__(self):
        super().__init__()
        self.final: bool = False
        self.out: set = set()
        self.fail: Node = None

    def addout(self, out: set) -> None:
        if type(out) is set:
            self.out = self.out.union(out)
        else:
            self.out.add(out)


    def addchild(self, alphabet: str, node=None) -> None:
        self[alphabet] = Node() if node is None else node


class AC:

    def __init__(self, patterns):
        self.patterns: List[str] = patterns
        self.head: Node = Node()

        self.maketrie()
        self.constructfail()

    def search(self, sentence: str) -> List[str]:
        crr: Node = self.head
        ret: List[str] = []
        for idx, c in enumerate(sentence):
            while crr is not self.head and c not in crr:
                crr = crr.fail
            if c in crr:
                crr = crr[c]
            if crr.final:
                ret.extend(list(crr.out))
        return ret

    def maketrie(self) -> None:
        for pattern in self.patterns:
            crr = self.head
            for c in pattern:
                if c not in crr:
                    crr.addchild(c)
                crr = crr[c]
            crr.final = True
            crr.addout(pattern)

    def constructfail(self) -> None:
        queue: Queue = Queue()
        self.head.fail = self.head
        queue.put(self.head)
        while not queue.empty():
            crr = queue.get()
            for nextc in crr:
                child = crr[nextc]

                if crr is self.head:
                    child.fail = self.head
                else:
                    f = crr.fail
                    while f is not self.head and nextc not in f:
                        f = f.fail
                    if nextc in f:
                        f = f[nextc]
                    child.fail = f

                child.addout(child.fail.out)
                child.final |= child.fail.final

                queue.put(child)


if __name__ == "__main__":
    patterns: List[str] = ["he", "she", "hers", "his"]

    text: str = "a his hoge hershe"

    aho_Corasick = AC(patterns)

    print(aho_Corasick.search(text))
