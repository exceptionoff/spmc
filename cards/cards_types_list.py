# coding: utf-8
# File containing a list of card types supported by the program

import os
from collections import namedtuple

TypeCardsHeader = namedtuple("TypeCards", "typename program_id")

listTypeCards = {
    "sle4442": TypeCardsHeader(typename="sle4442", program_id=bytes([0x00, 0x01]))
}

TypeCardsProgramId_to_Name = {
    typeCard.program_id: typeCard.typename for typeCard in listTypeCards.values()
}


class NoCardTypes(Exception):
    def __init__(self):
        super().__init__()
        self.msg = "The application does not have supported card types!"


def get_card_types():
    return [typeCards.typename for typeCards in listTypeCards.values()]
