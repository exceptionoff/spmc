# coding: utf-8
# This file contains the tests of the program

import random
import pytest

from spmc import Program
from crypt_engine.crypto_algorithms import get_encrypt_algorithms

test_seed_phrases = [
    "endless similar ahead slogan aerobic iron track priority fame kiss clever furnace",
    "retreat reunion turn risk mutual coffee vapor swap library opinion police couple reunion staff dignity",
    "siege parade soup congress fiscal boat tree vicious oval sick bike traffic gossip faculty increase provide blast economy",
    "ice wasp that rude history sadness rich increase dragon flip scare lyrics own shadow parent cheese enact trumpet good wasp best",
    "potato mobile lake oak umbrella deputy long venture jump sort one shift kiwi ill bone away old enhance number rich orphan math motor net",
]
test_passwords = ["test_password", "12345678qwerty", "ns$dkn..12nsaAA@"]
test_contact_data = ["", "89679092399", "Georgy.Valiev"]

test_card_reader_name = "ACS ACR39U ICC Reader 0"
test_card_type_name = "sle4442"
test_card_pin = "FFFFFF"


@pytest.mark.parametrize("seed_phrase", test_seed_phrases)
def test_spmc(seed_phrase):
    program = Program()
    program.set_current_reader(test_card_reader_name)
    program.set_card_type(test_card_type_name)
    program.verify_pin("FFFFFF")

    enc_alg = random.choice(get_encrypt_algorithms())
    password = random.choice(test_passwords)
    contact_data = random.choice(test_contact_data)

    program.write_seed_phrase_to_card(seed_phrase, enc_alg, password, contact_data)
    program.disconnect_from_card()

    program = Program()
    program.set_current_reader(test_card_reader_name)
    program.set_card_type(test_card_type_name)
    program.verify_pin(test_card_pin)

    data = program.read_card_data()
    assert data.card_type == test_card_type_name
    assert data.contact_data == contact_data
    assert data.enc_alg == enc_alg
    assert program.read_card_data(password) == seed_phrase

    program.disconnect_from_card()

