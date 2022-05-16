# coding: utf-8
# File containing card markup
import typing
from hashlib import sha256
import bip39
from crypt_engine.crypto_algorithms import encryptAlgs, EncryptAlgProgramId_to_Name, EncryptAlgHeader
from cards.cards_types_list import listTypeCards, TypeCardsProgramId_to_Name


VERSION_SOFTWARE = 1


class CardMarkup:
    version_software = VERSION_SOFTWARE

    class FieldStructure:
        max_size = 100
        header_size = 32

        def __init__(self):
            self.card_type: typing.Optional[str] = None
            self.card_name: typing.Optional[str] = None
            self.version_software: typing.Optional[str] = None
            self.enc_alg: typing.Optional[str] = None
            self.count_words_seed: typing.Optional[int] = None
            self.encrypted_seed: typing.Optional[bytes] = None
            self.iv: typing.Optional[bytes] = None


    @classmethod
    def info_pack_bytes(cls, info: FieldStructure()) -> bytes:
        data = listTypeCards[info.card_type].program_id +\
               cls._card_name_to_bytes(info.card_name) +\
               cls.version_software.to_bytes(2, 'big') +\
               b'\x00' * 5
        data += sha256(data).digest()[:4]
        data += encryptAlgs[info.enc_alg].program_id
        data += info.count_words_seed.to
        data += info.encrypted_seed
        data += info.to_bytes(1, 'big')
        data += sha256(data).digest()[:4]
        return data

    @classmethod
    def info_bytes_unpack(cls, bytes_: bytes) -> FieldStructure:
        if cls.FieldStructure.max_size > len(bytes_):
            raise cls.NotEnoughInformation()
        if sha256(bytes_[:25]).digest()[:4] != bytes_[25:29]:
            raise cls.CardIsNotMarkup()
        if b"\x00" * 5 != bytes_[20:25]:
            raise cls.CardIsNotMarkup()
        data = cls.FieldStructure()
        data.card_type = TypeCardsProgramId_to_Name[bytes_[:2]]
        data.card_name = cls._bytes_to_card_name(bytes_[2:18])
        data.version_software = '.'.join(list(bytes_[18:20]))

        try:
            enc_alg_name = EncryptAlgProgramId_to_Name[bytes_[29:31]]
            count_words_seed = bytes_[31]
            size_enc_seed = cls._size_encrypted_seed(encryptAlgs[enc_alg_name], bip39.get_entropy_bits(count_words_seed) // 8)
            size_iv = encryptAlgs[enc_alg_name].iv_size

            size_without_checksum = cls.FieldStructure.header_size + size_enc_seed + size_iv
            if sha256(bytes_[:size_without_checksum]).digest()[:4] != bytes_[size_without_checksum:size_without_checksum+4]:
                raise cls.DataIsCorrupted(data)
            data.enc_alg = enc_alg_name
            data.count_words_seed = count_words_seed
            data.encrypted_seed = bytes_[32:32+size_enc_seed]
            if not size_iv:
                data.iv = None
            else:
                data.iv = bytes_[32+size_enc_seed:32+size_enc_seed+size_iv]

        except:
            raise cls.DataIsCorrupted(data)

    @classmethod
    def print_info(cls, info: FieldStructure):
        data = {a: info.__dict__[a] for a in dir(info) if not a.startswith('__') and
                not callable(getattr(info, a)) and
                info.__dict__[a] is not None}
        print(data)

    @classmethod
    def _card_name_to_bytes(cls, card_name: str):
        card_name_b = card_name.encode('utf8')
        assert 0 < len(card_name_b) <= 15
        return b'\x80'.join([card_name.encode('utf8'), b'\x00' * (15 - len(card_name_b))])

    @classmethod
    def _bytes_to_card_name(cls, bytes_: bytes):
        return b'\x80'.join(bytes_.split(b'\x80')[:-1]).decode('utf8')

    @classmethod
    def _size_iv(cls, enc_alg_name: str):
        return encryptAlgs[enc_alg_name].iv_size

    @classmethod
    def _size_encrypted_seed(cls, enc_alg: EncryptAlgHeader, seed_size: int):
        if ('ECB' in enc_alg.name or 'CBC' in enc_alg.name) and (seed_size % enc_alg.block_len != 0):
            return seed_size + enc_alg.block_len - seed_size % enc_alg.block_len
        return seed_size

    class CardIsNotMarkup(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "The card is not marked up!"

    class DataIsCorrupted(Exception):
        def __init__(self, data):
            super().__init__()
            self.msg = "The data is corrupted!"
            self.data = data

    class NotEnoughInformation(Exception):
        def __init__(self):
            super().__init__()
            self.msg = "Not enough information!"
