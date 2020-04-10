import os
import base64
import numpy as np

from word_embedder.utils import tokenize


class WordVecFile:
    def __init__(self, fpath, not_formatted_file=False):
        self.fpath = fpath
        self.fp = open(fpath, "rt", encoding='utf-8', newline='\n',
                       errors='ignore')

        if not_formatted_file is True:
            self._convert_file_format()

        self.n, self.dim = self._get_word_count_and_dim()
        self._word_indices = self._get_word_indices()

        self.line_len = self._set_line_len()

    def get_word_vector(self, word):
        word = base64.b64encode(word.encode("utf-8", errors="ignore"))\
            .decode("utf-8", errors="ignore")
        word_index = self._word_indices.get(word, None)

        if not word_index:
            return np.zeros(300)

        self.fp.seek(0)

        self.fp.seek(51 + (word_index * 2601))
        word_line = self.fp.read(2601)

        print(word_line)

        tokens = word_line.split()

        vector = np.array(list(map(float, tokens[1:])))
        self.fp.seek(0)
        return vector

    def get_sentence_vector(self, sentence):
        words = tokenize(sentence)
        word_vectors = [self.get_word_vector(w) for w in words]
        return np.mean(word_vectors, axis=0)

    def _get_word_count_and_dim(self):
        res = tuple(map(int, self.fp.readline().split()))
        self.fp.seek(0)
        return res

    def _get_word_indices(self):
        self.fp.seek(51)
        data = {}

        index = 0
        for line in self.fp:
            tokens = line.rstrip().split(" ")
            data[tokens[0]] = index
            index += 1

        self.fp.seek(0)

        return data

    def _set_line_len(self):
        self.fp.seek(0)
        self.fp.readline()
        len_line = len(self.fp.readline())
        self.fp.seek(0)
        return len_line

    def _generate_file_name(self):
        splitted = self.fpath.split(os.path.sep)
        splitted[-1] = "formatted_" + splitted[-1]
        new_fpath = f'{os.path.sep}'.join(splitted)
        return new_fpath

    def _convert_file_format(self):
        new_fpath = self._generate_file_name()
        new_file_fp = open(new_fpath, "wt+", encoding='utf-8', newline='\n',
                           errors='ignore')

        self.fp.seek(0)

        first_line = self.fp.readline()
        n, d = first_line.split()
        line_str = n + " " * (25 - len(n))
        line_str += d + " " * (25 - len(d)) + "\n"
        new_file_fp.write(line_str)

        for line in self.fp:
            try:
                line_str = ""

                tokens = line.rstrip().split(' ')
                token = str(tokens[0])
                token = base64.b64encode(
                    token.encode("utf-8", errors="ignore")
                ).decode("utf-8", errors="ignore")
                line_str += token
                line_str += " " * (200 - len(token))

                vector = tokens[1:]
                for v in vector:
                    len_v = len(v)
                    spaces = " " * (8 - len_v)

                    v = spaces + v

                    line_str += v

                line_str += "\n"

                new_file_fp.write(line_str)
            except Exception as e:
                print(e)
                print(line)

        self.fpath = new_fpath
        self.fp = new_file_fp
        self.fp.seek(0)

    def __del__(self):
        self.fp.close()
