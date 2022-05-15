# coding: utf-8
# File containing a list of card types supported by the program

import os
from collections import namedtuple

TypeCardsHeader = namedtuple('TypeCards', 'typename program_id')

listTypeCards = [TypeCardsHeader(typename='sle4442', program_id=bytes([0x00, 0x01]))]

TypeCardsProgramId_to_Name = {typeCard.program_id: typeCard.typename for typeCard in listTypeCards}


class NoCardTypes(Exception):
    def __init__(self):
        super().__init__()
        self.msg = "'The application does not have supported card types!"


def get_card_types():
    card_t_in_file = set([typeCards.typename for typeCards in listTypeCards])
    card_t_in_dir = set(map(lambda x: x.removesuffix('.py'),
                            list(set(os.listdir('cards')) - {'card.py',
                                                             'card_manager.py',
                                                             'card_markup.py',
                                                             'cardreader_manager.py',
                                                             'cards_types_list.py',
                                                             '__pycache__'})))

    return list(set.intersection(card_t_in_file, card_t_in_dir))

