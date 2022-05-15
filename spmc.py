# coding: utf-8
# The file containing the program

import os
import sys
import argparse
import typing
import bip39
from cards.card_manager import CardManager
from cards.cards_types_list import listTypeCards
from cards.card_markup import CardMarkup


class Program:

    class Critical(Exception):
        def __init__(self, msg):
            self.msg = msg
            super().__init__(msg)

        def __repr__(self):
            return f'Critical error: {self.msg}'

        def __str__(self):
            return f'Critical error: {self.msg}'

    class Error(Exception):
        def __init__(self, msg):
            self.msg = msg
            super().__init__(msg)

        def __repr__(self):
            return f'Error: {self.msg}'

        def __str__(self):
            return f'Error: {self.msg}'

    class Warning(Exception):
        def __init__(self, msg):
            self.msg = msg
            super().__init__(msg)

        def __repr__(self):
            return f'Warning: {self.msg}'

        def __str__(self):
            return f'Warning: {self.msg}'

    class Dialog(Exception):
        def __init__(self, msg: str, choices: typing.Dict[str, str]):
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
                print('Command failed, invalid response!')

    class Input(Exception):
        def __init__(self,
                     name: str,
                     action: str,
                     help: str = '',
                     example: str = ''):
            self.name = name
            self.action = action
            self.help = help
            self.example = example
            super().__init__(name)

        def __repr__(self):
            info = ''
            if self.help:
                info = '(' + self.help
                if self.example:
                    info += f' (example: "{self.example}")'
                info += ')'
            return f'Enter {self.name} {info}: '

        def __str__(self):
            info = ''
            if self.help:
                info = '(' + self.help
                if self.example:
                    info += f' (example: "{self.example}")'
                info += ')'
            return f'Enter {self.name} {info}: '

        def get_value(self):
            print(self, end='')
            value = input()
            exec(self.action.format(value))

    Pin_request = Input(name='Pin-code card',
                        action='from smartcard.util import toBytes\n'
                               'CardManager.verify_pin(bytes(toBytes("{}")))',
                        help='Consecutive hex numbers',
                        example='FFFFFF')


    def exit(self, code: typing.Optional[int] = None) -> None:
        if not code:
            sys.exit(0)
        raise Program.Dialog('Are you sure you want to exit the program?',
                             {'yes': f'sys.exit({code})',
                              'no': 'pass'})

    def check_phrase(self, phrase: str) -> None:
        if bip39.check_phrase(phrase):
            print('Phrase is valid')
        else:
            raise Program.Error('Phrase is not valid!')

    def cardreaders_list(self) -> typing.List[str]:
        card_readers = CardManager.readers_list()
        if not card_readers:
            raise Program.Warning('No card readers found!\n'
                                  '(Please connect a card reader to your device)')
        print(card_readers)
        return card_readers

    def set_current_reader(self, reader: str):
        try:
            CardManager.set_current_reader(reader)
            print(f'Selected card reader: {CardManager.current_reader}')
        except (CardManager.ConnectionIsActive,
                CardManager.NoCardReaders,
                CardManager.IncorrectReaderName) as err:
            raise Program.Error(err.msg)

    def connect_to_card(self):
        try:
            CardManager.connect()
            print("Card connected!")
        except (CardManager.NoSelectCardReader, CardManager.CardBackendError) as err:
            raise Program.Error(err.msg)

    def disconnect_from_card(self):
        try:
            CardManager.disconnect()
            print("Card disconnected!")
        except CardManager.CardBackendError as err:
            raise Program.Error(err.msg)

    def card_type_list(self) -> list:
        card_type_list = CardManager.card_type_list()
        if not card_type_list:
            raise Program.Critical('The application does not have supported card types!\n'
                                   '(Please look in the "cards\constants.py" file and compare '
                                   'it with the contents of the "cards" directory)')
        print(card_type_list)
        return card_type_list

    def set_card_type(self, typename: str):
        try:
            CardManager.set_card_type(typename)
            print(f'Selected card type: {CardManager._card_info.name}')
            CardManager.select_card_type()
        except (CardManager.NoSuchCardTypes, CardManager.FailureCommand) as err:
            raise Program.Error(err.msg)

    def verify_pin(self, pin: str):
        raise Program.Pin_request

    def read_card_data(self) -> CardMarkup.FieldStructure:
        try:
            data = CardManager.read_bytes(0, CardMarkup.FieldStructure.max_size)
            print(list(data)) #
        except CardManager.PinIsNotVerify:
            raise Program.Pin_request

        try:
            info = CardMarkup.info_bytes_unpack(data)
            CardMarkup.print_info(info)
            return info

        except (CardMarkup.CardIsNotMarkup, CardMarkup.DataIsCorrupted) as err:
            raise err

    def write_card_data(self, card_name: str):
        pass

    # def write_card_data(self, offset: int, *args):
    #     try:
    #         CardManager.write_bytes(offset, bytes(list(args)))
    #     except CardManager.PinIsNotVerify:
    #         raise Program.Pin_request

        # data = CardMarkup.FieldStructure()
        # CardManager.read_bytes(0, )
        # pass

    def check_card_type(self):
        pass

    def __init__(self):
        self.program_warnings = []
        self.debug_mode = False

        self.__parse_args()
        self._load_card_types()
        self.__check_cardreaders()
        for warning_msg in self.program_warnings:
            print('Warning:', warning_msg)

    def _parse_user_input(self, command: str):
        command_name = command.split(' ')[0]

        command_params = []
        params = command.removeprefix(command_name)
        index = 0

        while index < len(params):
            if params[index] == ' ':
                pass
            elif params[index] in ['"', "'"]:
                sep = params[index]
                index += 1
                param = ''
                while index < len(params):
                    if params[index] == sep:
                        index += 1
                        if index >= len(params):
                            break
                        elif params[index] != ' ':
                            raise SyntaxError('Arguments must be separated by spaces!')
                        break
                    elif index == len(params) - 1:
                        raise SyntaxError('The bracket is not closed!')
                    param += params[index]
                    index += 1
                command_params.append('"' + param + '"')
            else:
                param = ''
                while index < len(params):
                    if params[index] == ' ':
                        break
                    elif params[index] in ['"', "'"]:
                        raise SyntaxError('Incorrect identifier name!')
                    param += params[index]
                    index += 1
                command_params.append(param)

            index += 1
        return command_name, command_params

    def main_loop(self):
        while True:
            try:
                u_input = input('>>> ')
                u_command, u_param = self._parse_user_input(u_input)
                if u_command[:2] == '__' or (u_command[:1] == '_' and not self.debug_mode) or u_command == 'main_loop':
                    raise AttributeError(f"'Program' object has no attribute '{u_command}'")

                command = f'self.{u_command}' + f'({",".join(u_param)})'
                exec(command)

            except self.Error as err:
                print("Error:", err.msg)

            except self.Dialog as dialog:
                dialog.get_answer()

            except self.Input as _input:
                _input.get_value()

            except TypeError as err:
                warning_msg = 'Invalid command arguments!'
                if self.debug_mode:
                    warning_msg += f'\n({err.args[0]})'

                print(Program.Warning(warning_msg).msg)

            except AttributeError as err:
                warning_msg = 'No such command!'
                if self.debug_mode:
                    warning_msg += f'\n({err.args[0]})'
                print(Program.Warning(warning_msg).msg)

            except (NameError, SyntaxError) as err:
                print(Program.Warning(f'({err.args[0]})').msg)

            except CardMarkup.DataIsCorrupted as err:
                print(err.msg)
                CardMarkup.print_info(err.data)

            except CardMarkup.CardIsNotMarkup as err:
                print(Program.Error(err.msg))

    def __parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug_mode', type=int, choices=[0, 1])
        args = parser.parse_args()
        self.debug_mode = bool(args.debug_mode)

    def __check_cardreaders(self):
        if not CardManager.readers_list():
            warning_msg = 'No card readers found!\n' \
                          '(Please connect a card reader to your device)'
            self.program_warnings.append(warning_msg)

    def _load_card_types(self):
        assert False







if __name__ == '__main__':
    try:
        program = Program()
        program.main_loop()
    except Program.Critical as err:
        Program._printCritical(err.msg)
        sys.exit(1)