# -*- coding: utf-8 -*-
# The file containing the program

import sys
from typing import Optional, List, Dict, Tuple
import bip39
from smartcard.util import toBytes
from cards.card_manager import CardManager
from cards.card_markup import CardMarkup
from crypt_engine.crypto_algorithms import get_encrypt_algorithms
from crypt_engine.engine import Cipher, calculate_key


class Program:
    class Critical(Exception):
        def __init__(self, msg):
            self.msg = msg
            super().__init__(msg)

        def __repr__(self):
            return f"Critical error: {self.msg}"

        def __str__(self):
            return f"Critical error: {self.msg}"

    class Error(Exception):
        def __init__(self, msg):
            self.msg = msg
            super().__init__(msg)

        def __repr__(self):
            return f"Error: {self.msg}"

        def __str__(self):
            return f"Error: {self.msg}"

    class Warning(Exception):
        def __init__(self, msg):
            self.msg = msg
            super().__init__(msg)

        def __repr__(self):
            return f"Warning: {self.msg}"

        def __str__(self):
            return f"Warning: {self.msg}"

    class Dialog(Exception):
        def __init__(self, msg: str, choices: Dict[str, str]):
            self.msg = msg
            self.choices = choices
            super().__init__(msg)

        def __repr__(self):
            return f'{self.msg} ({"/".join(self.choices)})'

        def __str__(self):
            return f'{self.msg} ({"/".join(self.choices)})'

        def get_answer(self):
            print(self)
            answer = input()
            try:
                exec(self.choices[answer])
            except KeyError:
                print("Command failed, invalid response!")

    class Input(Exception):
        def __init__(self, name: str, action: str, help: str = "", example: str = ""):
            self.name = name
            self.action = action
            self.help = help
            self.example = example
            super().__init__(name)

        def __repr__(self):
            info = ""
            if self.help:
                info = "(" + self.help
                if self.example:
                    info += f' (example: "{self.example}")'
                info += ")"
            return f"Enter {self.name} {info}: "

        def __str__(self):
            info = ""
            if self.help:
                info = "(" + self.help
                if self.example:
                    info += f' (example: "{self.example}")'
                info += ")"
            return f"Enter {self.name} {info}: "

        def get_value(self, value: Optional[str] = None):
            print(self, end="")
            if value is None:
                value = input()
            exec(self.action.format(value))

    Pin_request = Input(
        name="Pin-code card",
        action="from smartcard.util import toBytes\n"
        'CardManager.verify_pin(bytes(toBytes("{}")))',
        help="Consecutive hex numbers",
        example="FFFFFF",
    )

    @staticmethod
    def exit(code: Optional[int] = None) -> None:
        if code is None:
            sys.exit(0)
        raise Program.Dialog(
            "Are you sure you want to exit the program?",
            {"yes": f"sys.exit({code})", "no": "pass"},
        )

    @staticmethod
    def card_readers() -> List[str]:
        card_readers = CardManager.readers_list()
        if not card_readers:
            raise Program.Warning(
                "No card readers found!\n"
                "(Please connect a card reader to your device)"
            )
        for card_reader in card_readers:
            print(f'"{card_reader}"')
        return card_readers

    @staticmethod
    def card_types() -> List[str]:
        card_types = CardManager.card_types_list()
        if not card_types:
            raise Program.Critical(
                r"The application does not have supported card types!\n"
                r'(Please look in the "cards\constants.py" file and compare '
                r'it with the contents of the "cards" directory)'
            )
        for card_type in card_types:
            print(f'"{card_type}"')
        return card_types

    @staticmethod
    def supported_algorithms() -> List[str]:
        supported_algorithms = get_encrypt_algorithms()
        if not supported_algorithms:
            raise Program.Critical(
                "The application does not have supported encrypt algorithms!"
            )
        for supported_algorithm in supported_algorithms:
            print(f'"{supported_algorithm}"')
        return supported_algorithms

    @staticmethod
    def select_card_reader(reader: Optional[str]) -> None:
        try:
            CardManager.set_current_reader(reader)
            print(f"Selected card reader: {CardManager.current_reader}!")
        except (
            CardManager.ConnectionIsActive,
            CardManager.NoCardReaders,
            CardManager.IncorrectReaderName,
        ) as err:
            raise Program.Error(err.msg)

    @staticmethod
    def select_card_type(typename: Optional[str]) -> None:
        try:
            CardManager.set_card_type(typename)
            print(f"Selected card type: {CardManager.card_info.name}")
        except (CardManager.NoSuchCardTypes, CardManager.FailureCommand) as err:
            raise Program.Error(err.msg)

    @staticmethod
    def connect_to_card() -> None:
        try:
            CardManager.connect()
            CardManager.select_card_type()
            print("Card connected!")
        except (CardManager.NoSelectCardReader, CardManager.CardBackendError) as err:
            raise Program.Error(err.msg)

    @staticmethod
    def disconnect_from_card() -> None:
        try:
            CardManager.disconnect()
            print("Card disconnected!")
        except CardManager.CardBackendError as err:
            raise Program.Error(err.msg)

    @staticmethod
    def verify_pin(pin: Optional[str] = None) -> None:
        if not pin:
            raise Program.Pin_request
        try:
            CardManager.verify_pin(bytes(toBytes(pin)))
            print("Pin is verify!")
        except CardManager.WrongPin as err:
            raise Program.Error(err.msg)

    @staticmethod
    def read_seed_phrase(
        password: Optional[str] = None,
    ) -> CardMarkup.FieldStructure | str:
        try:
            data = CardManager.read_bytes(0, CardMarkup.FieldStructure.max_size)
        except CardManager.PinIsNotVerify:
            raise Program.Pin_request
        except CardManager.ReadError as err:
            raise Program.Error(err.msg)

        try:
            info = CardMarkup.info_bytes_unpack(data)
            if not (password is None):
                seed_phrase = bip39.encode_bytes(
                    Cipher(
                        info.enc_alg, calculate_key(password, info.enc_alg), info.iv
                    ).decrypt(
                        info.encrypted_seed,
                        bip39.get_entropy_bits(info.count_words_seed) // 8,
                    )
                )
                print("Seed phrase:", seed_phrase)
                return seed_phrase
            print(
                "Please pass the decryption password.\n"
                "Data available without a password:"
            )
            CardMarkup.print_metadata(info)
            return info

        except CardMarkup.CardIsNotMarkup as err:
            raise Program.Error(err.msg)
        except CardMarkup.DataIsCorrupted as err:
            CardMarkup.print_metadata(err.data)
            raise Program.Error(err.msg)

    @staticmethod
    def write_seed_phrase(
        seed_phrase: str, enc_alg: str, password: str, contact_data: str = ""
    ) -> None:
        Program.check_seed_phrase(seed_phrase)
        data = CardMarkup.FieldStructure()
        cipher = Cipher(enc_alg, calculate_key(password, enc_alg))

        data.card_type = CardManager.card_info.name
        data.contact_data = contact_data
        data.version_markup = CardMarkup.version_markup
        data.enc_alg = enc_alg
        data.count_words_seed = len(seed_phrase.split(" "))
        data.encrypted_seed = cipher.encrypt(bip39.decode_phrase(seed_phrase))
        data.iv = cipher.iv

        data_b = CardMarkup.info_pack_bytes(data)
        try:
            CardManager.write_bytes(0, data_b)
        except CardManager.PinIsNotVerify:
            raise Program.Pin_request

    @staticmethod
    def check_card_readers():
        if not CardManager.readers_list():
            raise Program.Warning(
                "No card readers found!\n"
                "(Please connect a card reader to your device)"
            )

    @staticmethod
    def check_card_types():
        if not CardManager.card_types_list():
            raise Program.Critical("No supported card types!")

    @staticmethod
    def check_supported_algorithms():
        if not get_encrypt_algorithms():
            raise Program.Critical("No supported encrypt algorithms!")

    @staticmethod
    def check_seed_phrase(phrase: str) -> None:
        if bip39.check_phrase(phrase):
            print("Phrase is valid")
        else:
            raise Program.Error("Phrase is not valid!")

    @staticmethod
    def main_loop():
        try:
            Program.check_supported_algorithms()
            Program.check_card_types()
            Program.check_card_readers()
        except Program.Warning as err:
            print(err)
        except Program.Critical as err:
            print(err)
            sys.exit(1)

        while True:
            try:
                Program._input_command()

            except Program.Dialog as dialog:
                dialog.get_answer()

            except Program.Input as _input:
                _input.get_value()

            except (Program.Warning, Program.Error) as err:
                print(err)

            except Program.Critical as err:
                print(err)
                sys.exit(1)

    @staticmethod
    def _input_command():
        try:
            u_input = input(">>> ")
            command = "Program." + Program._input_to_command(u_input)
            exec(command)
        except TypeError:
            raise Program.Warning("Invalid command arguments!")
        except AttributeError:
            raise Program.Warning("No such command!")
        except (NameError, SyntaxError) as err:
            raise Program.Warning(f"({err.args[0]})")

    @staticmethod
    def _parse_input(input_: str) -> Tuple[str, List[str]]:
        start_end = {'"': '"', "'": "'", "(": ")", "[": "]", "{": "}"}

        command = input_.split(" ")[0]
        params = []

        param = ""
        for i in input_.split(" ")[1:]:
            if i[0] in start_end.keys():
                if i[-1] == start_end[i[0]]:
                    params.append(i)
                else:
                    end = start_end[i[0]]
                    param += i
            elif param:
                param += " " + i
                if i[-1] == end:
                    params.append(param)
                    param = ""
            else:
                params.append(i)

        return command, params

    @staticmethod
    def _input_to_command(input_: str) -> str:
        command, params = Program._parse_input(input_)
        return f'{command}({",".join(params)})'


if __name__ == "__main__":
    Program.main_loop()

