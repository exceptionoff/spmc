# coding: utf-8
from cards.card import CardInfo, ApduInterface


card_info = CardInfo(
    name="sle4442",
    size=256,
    protection_field=[0, 31],
    max_size_file=None,
    size_pin=3,
    read_need_pin=False,
    write_need_pin=True,
    sw_success={
        "select_card_type": [0x90, 0x00],
        "read": [0x90, 0x00],
        "write": [0x90, 0x00],
        "change_pin": [0x90, 0x00],
        "verify_pin": [0x90, 0x07],
    },
)


class ApduInterface_sle4442(ApduInterface):
    @classmethod
    def select_card_type(cls):
        select_card_type_command = [0xFF, 0xA4, 0x00, 0x00, 0x01, 0x06]
        return [select_card_type_command]

    @classmethod
    def verify_pin(cls, pin):
        assert len(pin) == card_info.size_pin
        pin_lb = list(pin)
        verify_pin_command = [0xFF, 0x20, 0x00, 0x00, 0x03, *pin_lb]
        return [verify_pin_command]

    @classmethod
    def read(cls, offset, size):
        assert 0 <= offset <= card_info.size - 1
        assert 1 <= size <= card_info.size
        assert 1 <= offset + size <= card_info.size

        read_commands = []
        if size == 256:
            offset_lb = list(int(255).to_bytes(1, "big"))
            size_lb = list(int(1).to_bytes(1, "big"))
            read_commands.append([0xFF, 0xB0, 0x00, *offset_lb, *size_lb])
            size = 255
        offset_lb = list(offset.to_bytes(1, "big"))
        size_lb = list(size.to_bytes(1, "big"))
        read_commands.append([0xFF, 0xB0, 0x00, *offset_lb, *size_lb])
        read_commands.reverse()

        return read_commands

    @classmethod
    def write(cls, offset, data):
        size = len(data)
        assert 0 <= offset <= card_info.size - 1
        assert 1 <= size <= card_info.size
        assert 1 <= offset + size <= card_info.size

        write_commands = []
        if size == 256:
            offset_lb = list(int(255).to_bytes(1, "big"))
            size_lb = list(int(1).to_bytes(1, "big"))
            data_lb = list(data[-1:])
            write_commands.append([0xFF, 0xD0, 0x00, *offset_lb, *size_lb, *data_lb])
            data = data[:-1]
            size = 255
        offset_lb = list(offset.to_bytes(1, "big"))
        size_lb = list(size.to_bytes(1, "big"))
        data_lb = list(data)
        write_commands.append([0xFF, 0xD0, 0x00, *offset_lb, *size_lb, *data_lb])
        write_commands.reverse()
        return write_commands

    @classmethod
    def change_pin(cls, pin):
        assert len(pin) == card_info.size_pin
        pin_lb = list(pin)
        change_pin_command = [0xFF, 0xD2, 0x00, 0x01, 0x03, *pin_lb]
        return [change_pin_command]

    @classmethod
    def read_protection_bits(cls):
        read_protection_bits_command = [0xFF, 0xB2, 0x00, 0x00, 0x04]
        return [read_protection_bits_command]

    @classmethod
    def write_protection(cls, offset, data):
        size = len(data)
        assert (
            card_info.protection_field[0] <= offset <= card_info.protection_field[1] - 1
        )
        assert (
            1 <= size <= card_info.protection_field[1] - card_info.protection_field[0]
        )
        assert (
            1
            <= offset + size
            <= card_info.protection_field[1] - card_info.protection_field[0]
        )

        offset_lb = list(offset.to_bytes(1, "big"))
        size_lb = list(size.to_bytes(1, "big"))
        data_lb = list(data)

        write_protection_command = [0xFF, 0xD1, 0x00, *offset_lb, *size_lb, *data_lb]
        return [write_protection_command]


apdu: ApduInterface = ApduInterface_sle4442
