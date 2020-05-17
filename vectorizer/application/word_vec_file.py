import os
import base64
import numpy as np

from application.utils.helpers import tokenize


class WordVecFile:
    def __init__(self, path):
        self.path = path
        self.fp = open(path, "rt", encoding='utf-8', newline='\n',
                       errors='ignore')

        self._word_indices = self._get_word_indices()
        self.n, self.dim = self._get_word_count_and_dim()

    def get_word_vector(self, word):
        word = base64.b64encode(word.encode("utf-8", errors="ignore")).decode(
            "utf-8", errors="ignore")
        #         print(f'word: {word}')

        word_index = self._word_indices.get(word, None)
        #         print(f'word_index: {word_index}')

        if not word_index:
            return np.zeros(300)

        self.fp.seek(0)

        self.fp.seek(5302 * word_index + 61)

        line = self.fp.read(5302)
        #         print(f'line: {line}')

        tokens = line.split()
        #         print(f'tokens: {tokens}')

        word_b64, vector_b64 = tokens[0], tokens[1]
        #         print(f'word_b64: {word_b64}')
        #         print(f'vector_b64: {vector_b64}')

        vector_str = base64.b64decode(vector_b64.encode("utf-8")).decode(
            "utf-8")
        #         print(f'vector_str: {vector_str}')

        vector = np.array(list(map(float, vector_str.split())))

        self.fp.seek(0)
        return vector

    def get_sentence_vector(self, sentence):
        words = tokenize(sentence)
        word_vectors = [self.get_word_vector(w) for w in words]
        return np.mean(word_vectors, axis=0)

    def _get_word_count_and_dim(self):
        self.fp.readline()
        res = tuple(map(int, self.fp.readline().split()))
        self.fp.seek(0)
        return res

    def _get_word_indices(self):
        self.fp.seek(0)
        self.fp.seek(61)

        data = {}

        for index, line in enumerate(self.fp):
            tokens = line.strip().split(" ")
            data[tokens[0]] = index

        self.fp.seek(0)

        return data

    @staticmethod
    def check_is_file_formatted(path):
        with open(path, "rt", encoding='utf-8', newline='\n',
                  errors='ignore') as fp:
            first_line = fp.read(10)

        return first_line == "FORMATTED\n"

    @staticmethod
    def convert_file_format(path):
        print(f'path: {path}')

        fp = open(path, "rt", encoding='utf-8', newline='\n', errors='ignore')

        splitted = path.split(os.path.sep)
        splitted[-1] = "formatted_" + splitted[-1]
        new_path = f'{os.path.sep}'.join(splitted)
        print(f'new_path: {new_path}')

        new_fp = open(new_path, "wt+", encoding='utf-8', newline='\n',
                      errors='ignore')

        new_fp.write("FORMATTED\n")

        first_line = fp.readline()

        n, d = first_line.split()
        print(f'n: {n}, d: {d}')

        line_str = n + " " * (25 - len(n))
        line_str += d + " " * (25 - len(d)) + "\n"

        new_fp.write(line_str)

        for index, line in enumerate(fp):
            try:
                tokens = line.strip().split(" ")
                word = str(tokens[0])
                word = base64.b64encode(
                    word.encode("utf-8", errors="ignore")
                ).decode("utf-8", errors="ignore")

                word = word + " " * (200 - len(word))

                vector = " ".join(tokens[1:])
                vector = base64.b64encode(
                    vector.encode("utf-8", errors="ignore")
                ).decode("utf-8", errors="ignore")
                len_vector = len(vector.encode("utf-8"))

                if len_vector < 17 * 300:
                    vector = " " * (17 * 300 - len_vector) + vector

                line = word + " " + vector + "\n"

                new_fp.write(line)
            except Exception as e:
                print(f'{index}: {str(e)}')

        fp.close()
        new_fp.close()
        return new_path

    def __del__(self):
        self.fp.close()
