# coding: utf-8
# This file containing a class for interacting with card readers
from typing import List, Tuple, Optional, Any
import logging

from smartcard.scard import *
from smartcard.System import readers
from smartcard.util import toHexString


logging.basicConfig(level=logging.WARNING)


class CardReaderManager:
    """A class for interacting with smart cards and card readers. At
    initialization gets a list of all card readers around and does active
    is the first card reader in the list.
    """

    class NoCardReaders(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "No card readers found!"

    class NoSelectCardReader(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "No card reader selected!"

    class ConnectionIsActive(Exception):
        def __init__(self, reader: str):
            super().__init__()
            self.reader = str(reader)
            self.msg = f"The connection is already established on the card reader {self.reader}!"

    class ConnectionIsNotActive(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "The connection is not active!"

    class IncorrectReaderName(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "Incorrect card reader name!"

    class CardBackendError(Exception):
        def __init__(self, msg: str):
            super().__init__()
            self.msg = msg

    _current_reader: Optional[str] = None
    _connection_is_active: bool = False
    __hcontext: Optional[Any] = None
    __hcard: Optional[Any] = None
    __dwActiveProtocol: Optional[Any] = None

    @classmethod
    @property
    def current_reader(cls) -> Optional[str]:
        logging.info(cls._current_reader)
        return cls._current_reader

    @classmethod
    @property
    def connection_is_active(cls) -> bool:
        logging.info(cls._connection_is_active)
        return cls._connection_is_active

    @classmethod
    def readers_list(cls) -> List[str]:
        lst = [reader.name for reader in readers()]
        logging.info(lst)
        return lst

    @classmethod
    def set_current_reader(cls, reader: str) -> None:
        """Set the current card reader from which the card will be read.
        :param reader: card reader from readers_list
        """
        if cls._connection_is_active:
            raise CardReaderManager.ConnectionIsActive(cls._current_reader)

        readers_list = cls.readers_list()
        if not readers_list:
            raise cls.NoCardReaders()
        if not (reader in readers_list):
            raise cls.IncorrectReaderName()
        cls._current_reader = reader
        logging.info(f"Selected card reader: {cls._current_reader}")


    @classmethod
    def connect(cls) -> None:
        """Connect to the card in the selected card reader."""

        if cls._connection_is_active:
            raise cls.ConnectionIsActive(cls._current_reader)

        if cls._current_reader is None:
            raise cls.NoSelectCardReader()

        hresult, cls.__hcontext = SCardEstablishContext(SCARD_SCOPE_USER)

        if hresult != SCARD_S_SUCCESS:
            raise cls.CardBackendError(
                "Ошибка SCardEstablishContext: "
                + SCardGetErrorMessage(hresult)
                .encode("ISO-8859-2")
                .decode("windows-1251")
            )

        hresult, cls.__hcard, cls.__dwActiveProtocol = SCardConnect(
            cls.__hcontext,
            str(cls._current_reader),
            SCARD_SHARE_SHARED,
            SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1,
        )

        if hresult != SCARD_S_SUCCESS:
            raise cls.CardBackendError(
                "Ошибка SCardConnect: "
                + SCardGetErrorMessage(hresult)
                .encode("ISO-8859-2")
                .decode("windows-1251")
            )

        cls._connection_is_active = True
        logging.info("Card connected!")

    @classmethod
    def disconnect(cls) -> None:
        """Disconnect from the card."""
        if cls.connection_is_active:
            hresult = SCardDisconnect(cls.__hcard, SCARD_UNPOWER_CARD)
            if hresult != SCARD_S_SUCCESS:
                raise cls.CardBackendError(
                    "Failed to disconnect: "
                    + SCardGetErrorMessage(hresult)
                    .encode("ISO-8859-2")
                    .decode("windows-1251")
                )
            cls._connection_is_active = False
            logging.info("Card disconnected!")
        else:
            logging.info("Connection is not active!")

    @classmethod
    def get_card_ATR(cls) -> List[int]:
        """Get the ATR of the connected card.
        :return: ATR
        """

        if not cls._connection_is_active:
            raise cls.ConnectionIsNotActive()

        hresult, atr = SCardGetAttrib(cls.__hcard, scard.SCARD_ATTR_ATR_STRING)

        if hresult != SCARD_S_SUCCESS:
            raise cls.CardBackendError(
                "Ошибка SCardGetAtr: "
                + SCardGetErrorMessage(hresult)
                .encode("ISO-8859-2")
                .decode("windows-1251")
            )

        logging.info(f"ATR: {toHexString(atr)}")
        return atr

    @classmethod
    def transmit(cls, apdu) -> Tuple[List[int], List[int]]:
        """Send APDU to the map.
        :param apdu: apdu
        :return: SW, DATA
        """
        if not cls._connection_is_active:
            raise cls.ConnectionIsNotActive()

        hresult, response = SCardTransmit(cls.__hcard, cls.__dwActiveProtocol, apdu)
        if hresult != SCARD_S_SUCCESS:
            raise cls.CardBackendError(
                "Ошибка transmit: "
                + SCardGetErrorMessage(hresult)
                .encode("ISO-8859-2")
                .decode("windows-1251")
            )
        sw_ = response[-2:]
        data_ = response[:-2]
        logging.debug(f"> {toHexString(apdu)}")
        logging.info(f"< {response}")
        return sw_, data_
