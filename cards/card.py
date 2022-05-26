# -*- coding: utf-8 -*-
# A file containing structures with the technical data of cards, having
# described them for each card, you can start working with it. To do this,
# create a file in this directory with the name of the card and the
# extension *.py, creating in it:
# card_info = CardInfo()
# apdu = APDU()

from dataclasses import dataclass
import typing
from abc import ABC, abstractmethod

Apdu_command = typing.List[int]


class ApduInterface(ABC):
    """An abstract class containing methods for interacting with maps."""

    @classmethod
    @abstractmethod
    def select_card_type(cls) -> typing.List[Apdu_command]:
        """
        :return: a list of APDU commands to select the type of card for the
        card reader.
        """
        pass

    @classmethod
    @abstractmethod
    def verify_pin(cls, pin: bytes) -> typing.List[Apdu_command]:
        """
        :param pin: card pin
        :return: a list of APDU commands for presenting a pin code to a card.
        """
        pass

    @classmethod
    @abstractmethod
    def read(cls, offset: int, size: int) -> typing.List[Apdu_command]:
        """
        :param offset: in bytes
        :param size: in bytes
        :return: list of APDU commands, commands for reading data from the card.
        """
        pass

    @classmethod
    @abstractmethod
    def write(cls, offset: int, data: bytes) -> typing.List[Apdu_command]:
        """
        :param offset: in bytes
        :param data: the data we write
        :return: list of APDU commands, commands for writing data to the card.
        """
        pass

    @classmethod
    @abstractmethod
    def change_pin(cls, pin: bytes) -> typing.List[Apdu_command]:
        """
        :param pin: card pin
        :return: list of APDU commands, commands for changing the pin-code of the card.
        """
        pass

    @classmethod
    @abstractmethod
    def read_protection_bits(cls) -> typing.List[Apdu_command]:
        """
        :return: list of APDU commands, commands for reading the list of
        protected card data from overwriting.
        """
        pass

    @classmethod
    @abstractmethod
    def write_protection(cls, offset: int, data: bytes) -> typing.List[Apdu_command]:
        """
        :param offset: in bytes
        :param size: in bytes
        :return: list of APDU commands, irreversible data write commands.
        """
        pass


@dataclass
class CardInfo:
    name: str
    size: int
    protection_field: typing.Optional[typing.List[int]]
    max_size_file: typing.Optional[int]
    size_pin: int
    read_need_pin: bool
    write_need_pin: bool
    sw_success: dict
