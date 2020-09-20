class ComparableLine:
    def __init__(self, line):
        self.line = line

    def __gt__(self, other):
        if self.line['chromo'] != other.line['chromo']:
            return self.line['chromo'] > other.line['chromo']
        else:
            return int(self.line['pos']) > int(other.line['pos'])

    def __eq__(self, other):
        if self.line['chromo'] != other.line['chromo']:
            return self.line['chromo'] == other.line['chromo']
        else:
            return self.line['pos'] == other.line['pos']
