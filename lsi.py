from collections import defaultdict
from scipy.sparse import csc_matrix
from scipy import array
from scipy.spatial.distance import cosine
import numpy
import sys
import glob
import os
from sparsesvd import sparsesvd


class SparseMatrix(object):
    def __init__(self):
        self._matrix = defaultdict(lambda: defaultdict(int))
        self.max_row = 0
        self.max_col = 0

    def get(self, row, col):
        return self._matrix[row][col]

    def set(self, row, col, value):
        self._matrix[row][col] = value
        self.max_row = max(row, self.max_row)
        self.max_col = max(col, self.max_col)

    def __str__(self):
        ret = ""
        for row in range(self.max_row + 1):
            line = ""
            for col in range(self.max_col + 1):
                line += "%s " % self._matrix[row][col]
            ret += line + "\n"
        return ret

    def as_indexed(self):
        ''' returns the matrix in a form that can be used with scipy.sparse '''
        data = []
        rows = []
        cols = []
        for row in self._matrix:
            for col in self._matrix[row]:
                rows.append(row)
                cols.append(col)
                data.append(self._matrix[row][col])
        return (data, rows, cols)

    def unpacked(self):
        matrix = [[0 for _ in xrange(self.max_col + 1)] for _ in xrange(self.max_row + 1)]
        for row in self._matrix:
            for col in self._matrix[row]:
                matrix[row][col] = self._matrix[row][col]
        return matrix

    def as_csc(self):
        data, rows, cols = self.as_indexed()
        return csc_matrix((array(data), (array(rows), array(cols))))


class TermDoc(object):
    def __init__(self):
        self._words = []
        self._documents = []
        self._matrix = SparseMatrix()

    def add_document(self, document, tokens):
        self._documents.append(document)
        doc_ind = len(self._documents) - 1
        for token in tokens:
            try:
                token_ind = self._words.index(token)
            except ValueError:
                # The word hasn't been seen yet
                self._words.append(token)
                token_ind = len(self._words) - 1
            self._matrix.set(token_ind, doc_ind, self._matrix.get(token_ind, doc_ind) + 1)

    def get_term_vector(self, tokens):
        for token in tokens:
            try:
                token_ind = self._words.index(token)
            except ValueError:
                # The word hasn't been seen yet
                self._words.append(token)
                token_ind = len(self._words) - 1
            self._matrix.set(token_ind, doc_ind, self._matrix.get(token_ind, doc_ind) + 1)

    def __str__(self):
        return str(self._matrix)


class LSI(object):
    def __init__(self, corpus):
        term_doc = TermDoc()
        for document in corpus:
            # Tokenize/stem each document
            tokens = process_document(document)
            # Add it to the sparse term-document matrix
            term_doc.add_document(document, tokens)
        print len(term_doc._words), len(term_doc._documents)
        # Calculate the SVD
        self.T, self.s, self.D = sparsesvd(term_doc._matrix.as_csc(), 300)
        # Recreate the original matrix
        # print numpy.dot(self.T.T, numpy.dot(numpy.diag(self.s), self.D))

    def doc_similarity(self):
        sim_matrix = [[0 for _ in xrange(self.D.shape[1])] for _ in xrange(self.D.shape[1])]
        for row, vec1 in enumerate(self.D):
            for col, vec2 in enumerate(self.D):
                print cosine(vec1, vec2)
                sim_matrix[row][col] = cosine(vec1, vec2)
        return sim_matrix

    def query(self, query_string):
        tokens = process_document(query_string)
        self.term_doc.get_term_vector(tokens)


def process_document(doc):
    with open(doc) as f:
        text = f.read()
    text = text.lower()
    return text.split()


if __name__ == "__main__":
    corpus = glob.glob(os.path.join(sys.argv[1], '*'))
    a = LSI(corpus)
    print a.doc_similarity()
