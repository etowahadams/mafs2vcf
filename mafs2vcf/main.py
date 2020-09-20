from queue import PriorityQueue
from mafs2vcf.constants import constants as c
from mafs2vcf.comparable_line.comparable_line import ComparableLine


class MafsConverter:
    """
    Convert .mafs file to a vcf
    """

    def __init__(self, target_filename=None, div_filename=None, anc_filename=None):
        """
        Initialize converter. Filename must be provided.
        :param target_filename: String, a path to .mafs file for target species
        :param div_filename: String, a path to .mafs file for divergent species
        :param anc_filename: String, a path to .mafs file for ancestral species
        """
        self.target_filename = target_filename
        self.div_filename = div_filename
        self.anc_filename = anc_filename
        self.pq = PriorityQueue()

        # open files
        try:
            self.target_file = open(target_filename, 'r')
        except IOError:
            print("Target file could not be opened")

        try:
            self.div_file = open(div_filename, 'r')
        except IOError:
            print("Divergent file could not be opened")

        if anc_filename:
            try:
                self.anc_file = open(anc_filename, 'r')
            except IOError:
                print("Ancestral file could not be opened")
        else:
            self.anc_file = None;

    @staticmethod
    def process_line(line, line_source="target"):
        """
        Process a line from the target mafs file
        :param line: string with tabs. ex "NW_018734359.1	1006208	C	T	C	1.000000	0.000000e+00	10"
        :param line_source: target, divergent, or ancestral
        :return: object containing chromo, position, knownEM, and the first part of the corresponding vcf line
        """
        chromo = position = major = minor = knownEM = unknownEM = nInd = None
        cols = line.split('\t')
        if len(cols) == 7:
            chromo, position, major, minor, knownEM, unknownEM, nInd = cols
        if len(cols) == 8:  # some files have an extra ref column
            chromo, position, major, minor, ref, knownEM, unknownEM, nInd = cols
        nInd = nInd[:-1]  # get rid of the new line at the end

        return {'chromo': chromo,
                'pos': position,
                'knownEM': knownEM,
                'type': line_source,
                'row': f"{chromo}\t{position}\t{c.VAR_ID}\t{major}\t{minor}\t{c.VAR_QUAL}\t{c.VAR_FILTER}\tKEM={knownEM};PKEM={unknownEM};NI={nInd}\tGT"
                }

    def convert_to_VCF(self, output_filename):
        """
        Combines and converts target and divergent mafs into a single vcf file
        :param output_filename: the filename of the output vcf
        """
        output = open(output_filename, 'w+')
        output.write(c.VCF_INFO)
        output.write(c.VCF_HEADER_DIV)

        next(self.target_file)  # skip the header
        d_lines = self.div_file.readlines()
        i = 1  # index in d_lines, start at 1 since we want to skip the header
        d = self.process_line(d_lines[i])

        for line in self.target_file:
            t = self.process_line(line)
            if i < len(d_lines):
                d = self.process_line(d_lines[i])

            # current divergent position is less than current target position; insert it
            while d['chromo'] <= t['chromo'] and d['pos'] < t['pos'] and i < len(d_lines):
                d = self.process_line(d_lines[i])
                output.write(d['row'] + "\t0/0\t0/0\t0/1\n")
                i += 1

            if d['chromo'] == t['chromo'] and d['pos'] == t['pos']:
                print('same')
                if float(t['knownEM']) < 0.99:  # then the site is polymorphic
                    output.write(t['row'] + "\t0/0\t0/1\t0/1\n")
                else:  # the site is fixed
                    output.write(t['row'] + "\t1/1\t1/1\t0/1\n")
                i += 1
            else:  # then this locus in not in the divergent file
                if float(t['knownEM']) < 0.99:  # then the site is polymorphic
                    output.write(t['row'] + "\t0/0\t0/1\t0/0\n")
                else:  # the site is fixed
                    output.write(t['row'] + "\t1/1\t1/1\t0/0\n")

        output.close()

    def __init_pq(self):
        """
        Initialize the priority queue with values from the files
        """
        for file in [self.target_file, self.div_file, self.anc_file]:
            if file:
                next(file)

        tar = next(self.target_file, None)
        div = next(self.div_file, None)
        anc = next(self.anc_file, None) if self.anc_file else None

        # use ComparableLine as a wrapper for the the object that process_line() returns so that priority can be
        # assigned based on chromosome position and name
        if tar:
            self.pq.put(ComparableLine(self.process_line(tar, 'target')))
        if div:
            self.pq.put(ComparableLine(self.process_line(div, 'divergent')))
        if anc:
            self.pq.put(ComparableLine(self.process_line(anc, 'ancestral')))

    def get_next_line(self, file, default):
        next_line = next(file, default)
        if next_line:
            cols = next_line.split('\t')
            if cols[0] == 'chromo':
                next_line = next(file, default)
            elif len(cols) < 6:
                next_line = None
        return next_line

    def convert_to_VCF_anc(self, output_filename):
        """
        Convert and combine target, divergent, and ancestral mafs files into a single VCF
        Assumes that the lines in the mafs file are sorted (they usually are)
        :param output_filename: the filename of the output vcf
        """
        output = open(output_filename, 'w+')
        output.write(c.VCF_INFO)
        lines = {
            'target': self.target_file,
            'divergent': self.div_file,
        }
        if self.anc_file:
            lines['ancestral'] = self.anc_file
            output.write(c.VCF_HEADER_ANC)
        else:
            output.write(c.VCF_HEADER_DIV)

        self.__init_pq()  # initialize priority queue

        while not self.pq.empty():

            cur = peek_line = self.pq.get().line
            process = {}  # dict of mafs rows to process into a single vcf row
            while peek_line and cur['chromo'] == peek_line['chromo'] and cur['pos'] == peek_line['pos']:
                process[peek_line['type']] = peek_line  # add the peeked line to the dict to process

                next_line = self.get_next_line(lines[peek_line['type']], None)  # add a new line to the priority queue
                if next_line:
                    self.pq.put(ComparableLine(self.process_line(next_line, peek_line['type'])))

                # get the next line
                peek_line = self.pq.get().line if not self.pq.empty() else None

            # put the peeked line back if it is not in in the proccess dict
            if peek_line and peek_line['pos'] != cur['pos']:
                self.pq.put(ComparableLine(peek_line))

            GT = {  # default genotypes for target, divergent, and ancestral
                'target': '\t0/0\t0/0',
                'divergent': '\t0/0',
                'ancestral': '\t0/0\n'
            }
            if 'target' in process:
                if float(process['target']['knownEM']) < 0.99:  # then the site is polymorphic
                    GT['target'] = '\t0/0\t0/1'
                else:  # the site is fixed
                    GT['target'] = '\t1/1\t1/1'
            if 'divergent' in process:
                if float(process['divergent']['knownEM']) < 0.99:  # then the site is polymorphic
                    GT['divergent'] = '\t0/1'
                else:  # the site is fixed
                    GT['divergent'] = '\t1/1'
            if 'ancestral' in process:
                if float(process['ancestral']['knownEM']) < 0.99:  # then the site is polymorphic
                    GT['ancestral'] = '\t0/1\n'
                else:  # the site is fixed
                    GT['ancestral'] = '\t1/1\n'

            if self.anc_file:
                output.write(cur['row'] + GT['target'] + GT['divergent'] + GT['ancestral'])
            else:
                output.write(cur['row'] + GT['target'] + GT['divergent'] + '\n')

        output.close()


if __name__ == "__main__":
    # M1 = MafsConverter('C:/Users/selua/PycharmProjects/PyMAFS/data/test1.mafs',
    #                    'C:/Users/selua/PycharmProjects/PyMAFS/data/test2.mafs',
    #                    'C:/Users/selua/PycharmProjects/PyMAFS/data/test1.mafs')

    M1 = MafsConverter('C:/Users/selua/PycharmProjects/PyMAFS/data/HMS_MMS_poly_all.mafs',
                       'C:/Users/selua/PycharmProjects/PyMAFS/data/WED_poly_all.mafs',
                       'C:/Users/selua/PycharmProjects/PyMAFS/data/HG_poly_all.mafs')
    M1.convert_to_VCF_anc('output.vcf')
