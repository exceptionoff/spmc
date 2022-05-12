# coding: utf-8

from collections import namedtuple

TypeCardsHeader = namedtuple('TypeCards', 'typename program_id')

listTypeCards = [TypeCardsHeader(typename='sle4442', program_id=bytes([0x00, 0x01]))]


TypeCardsProgramId_to_Name = {typeCard.program_id: typeCard.typename for typeCard in listTypeCards}