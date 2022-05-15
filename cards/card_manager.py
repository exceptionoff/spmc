# coding: utf-8
# This file containing a class for interacting with cards using card readers

import importlib
import typing
from cards.cardreader_manager import CardReaderManager
from cards.cards_types_list import get_card_types
from cards.card import Apdu_command, ApduInterface, CardInfo


class CardManager(CardReaderManager):
    """A class for working with different types of maps, providing a single interface.
    """
    _card_apdu_interface: typing.Optional[ApduInterface] = None
    _card_info: typing.Optional[CardInfo] = None
    _pin_is_verify: typing.Optional[bool] = None

    @classmethod
    @property
    def card_apdu_interface(cls) -> typing.Optional[ApduInterface]:
        if not CardManager._card_apdu_interface:
            raise CardManager.NoSelectCardType()
        return CardManager._card_apdu_interface

    @classmethod
    @property
    def card_info(cls) -> typing.Optional[CardInfo]:
        if not CardManager._card_info:
            raise CardManager.NoSelectCardType()
        return CardManager._card_info

    @classmethod
    @property
    def pin_is_verify(cls) -> bool:
        if not CardManager.connection_is_active:
            raise CardManager.ConnectionIsNotActive()
        if CardManager._pin_is_verify is None:
            raise CardManager.NoSelectCardType()
        return CardManager._pin_is_verify

    @classmethod
    def card_type_list(cls) -> typing.List[str]:
        lst = get_card_types()
        if not lst:
            raise CardManager.NoCardTypes()
        return lst

    @classmethod
    def set_card_type(cls, typename: str) -> None:
        if not (typename in cls.card_type_list()):
            raise CardManager.NoSuchCardTypes()
        try:
            module = importlib.import_module('cards.' + typename)
            cls._card_apdu_interface = module.apdu
            cls._card_info = module.card_info
        except ModuleNotFoundError:
            raise CardManager.NoSuchCardTypes()

    @classmethod
    def connect(cls) -> None:
        super().connect()
        cls._pin_is_verify = not bool(cls._card_info.size_pin)

    @classmethod
    def disconnect(cls) -> None:
        super().disconnect()
        cls._pin_is_verify = None

    @classmethod
    def execute_commands(cls, commands: typing.List[Apdu_command]) -> typing.Tuple[Apdu_command, Apdu_command]:
        if not CardManager.connection_is_active:
            CardManager.connect()
        sw_list = []
        data_list = []
        for command in commands:
            sw, data = CardManager.transmit(command)
            sw_list.append(sw)
            data_list.append(data)
        return sw_list, data_list

    @classmethod
    def select_card_type(cls) -> None:
        sw_list, data_list = cls.execute_commands(cls._card_apdu_interface.select_card_type())
        for sw in sw_list:
            if sw != cls._card_info.sw_success['select_card_type']:
                raise cls.FailureCommand()

    @classmethod
    def verify_pin(cls, pin: bytes) -> None:
        sw_list, data_list = cls.execute_commands(cls._card_apdu_interface.verify_pin(pin))
        for sw in sw_list:
            if sw != cls._card_info.sw_success['verify_pin']:
                raise cls.FailureCommand()
        cls._pin_is_verify = True

    @classmethod
    def change_pin(cls, pin: bytes) -> None:
        if not CardManager.pin_is_verify:
            raise CardManager.PinIsNotVerify()
        sw_list, data_list = cls.execute_commands(cls._card_apdu_interface.change_pin(pin))
        for sw in sw_list:
            if sw != cls._card_info.sw_success['change_pin']:
                raise cls.FailureCommand()

    @classmethod
    def read_bytes(cls, offset_b: int, size_b: int) -> bytes:
        if not CardManager.pin_is_verify and CardManager._card_info.read_need_pin:
            raise CardManager.PinIsNotVerify()
        sw_list, data_list = cls.execute_commands(cls._card_apdu_interface.read(offset_b, size_b))
        for sw in sw_list:
            if sw != cls._card_info.sw_success['read']:
                raise cls.FailureCommand()
        data = []
        for data_ in data_list:
            data += data_
        return bytes(data)

    @classmethod
    def write_bytes(cls, offset_b: int, data: bytes) -> None:
        if not CardManager.pin_is_verify and CardManager._card_info.write_need_pin:
            raise CardManager.PinIsNotVerify()
        sw_list, data_list = cls.execute_commands(cls._card_apdu_interface.write(offset_b, data))
        for sw in sw_list:
            if sw != cls._card_info.sw_success['write']:
                raise cls.FailureCommand()

        if cls.read_bytes(offset_b, len(data)) != data:
            raise cls.FailureCommand()

    class NoSuchCardTypes(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "No such card type!"

    class NoCardTypes(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "No card types!"

    class NoSelectCardType(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "No card type selected!"

    class FailureCommand(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "Command failed!"

    class PinIsNotVerify(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "PIN code not presented!"
