import uuid
from DWords import utils

def test_del_word():
    word, paraphrase = str(uuid.uuid1()), str(uuid.uuid1())
    utils.add_words((word, paraphrase))
    utils.delete_words(word)

def test_dictionary():
    assert utils.consult('apple') != ''
