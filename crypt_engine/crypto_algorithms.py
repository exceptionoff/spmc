# -*- coding: utf-8 -*-
from collections import namedtuple

EncryptAlgHeader = namedtuple(
    "EncryptAlgHeader", "name key_len block_len iv_size program_id"
)


encryptAlgs = {
    "GOST_34_13_128_ECB": EncryptAlgHeader(
        name="GOST_34_13_128_ECB",
        key_len=32,
        block_len=16,
        iv_size=0,
        program_id=bytes([0x00, 0x01]),
    ),
    "GOST_34_13_128_CTR": EncryptAlgHeader(
        name="GOST_34_13_128_CTR",
        key_len=32,
        block_len=16,
        iv_size=8,
        program_id=bytes([0x00, 0x02]),
    ),
    "GOST_34_13_128_OFB": EncryptAlgHeader(
        name="GOST_34_13_128_OFB",
        key_len=32,
        block_len=16,
        iv_size=32,
        program_id=bytes([0x00, 0x03]),
    ),
    "GOST_34_13_128_CBC": EncryptAlgHeader(
        name="GOST_34_13_128_CBC",
        key_len=32,
        block_len=16,
        iv_size=32,
        program_id=bytes([0x00, 0x04]),
    ),
    "GOST_34_13_128_CFB": EncryptAlgHeader(
        name="GOST_34_13_128_CFB",
        key_len=32,
        block_len=16,
        iv_size=32,
        program_id=bytes([0x00, 0x05]),
    ),
    "GOST_34_13_64_ECB": EncryptAlgHeader(
        name="GOST_34_13_64_ECB",
        key_len=32,
        block_len=8,
        iv_size=0,
        program_id=bytes([0x00, 0x81]),
    ),
    "GOST_34_13_64_CTR": EncryptAlgHeader(
        name="GOST_34_13_64_CTR",
        key_len=32,
        block_len=8,
        iv_size=4,
        program_id=bytes([0x00, 0x82]),
    ),
    "GOST_34_13_64_OFB": EncryptAlgHeader(
        name="GOST_34_13_64_OFB",
        key_len=32,
        block_len=8,
        iv_size=16,
        program_id=bytes([0x00, 0x83]),
    ),
    "GOST_34_13_64_CBC": EncryptAlgHeader(
        name="GOST_34_13_64_CBC",
        key_len=32,
        block_len=8,
        iv_size=24,
        program_id=bytes([0x00, 0x84]),
    ),
    "GOST_34_13_64_CFB": EncryptAlgHeader(
        name="GOST_34_13_64_CFB",
        key_len=32,
        block_len=8,
        iv_size=16,
        program_id=bytes([0x00, 0x85]),
    ),
    "3DES_ECB": EncryptAlgHeader(
        name="3DES_ECB",
        key_len=24,
        block_len=8,
        iv_size=0,
        program_id=bytes([0x80, 0x81]),
    ),
    "3DES_CTR": EncryptAlgHeader(
        name="3DES_CTR",
        key_len=24,
        block_len=8,
        iv_size=4,
        program_id=bytes([0x80, 0x82]),
    ),
    "3DES_OFB": EncryptAlgHeader(
        name="3DES_OFB",
        key_len=24,
        block_len=8,
        iv_size=8,
        program_id=bytes([0x80, 0x83]),
    ),
    "3DES_CBC": EncryptAlgHeader(
        name="3DES_CBC",
        key_len=24,
        block_len=8,
        iv_size=8,
        program_id=bytes([0x80, 0x84]),
    ),
    "3DES_CFB": EncryptAlgHeader(
        name="3DES_CFB",
        key_len=24,
        block_len=8,
        iv_size=8,
        program_id=bytes([0x80, 0x85]),
    ),
    "AES-256_ECB": EncryptAlgHeader(
        name="AES-256_ECB",
        key_len=32,
        block_len=16,
        iv_size=0,
        program_id=bytes([0x81, 0x01]),
    ),
    "AES-256_CTR": EncryptAlgHeader(
        name="AES-256_CTR",
        key_len=32,
        block_len=16,
        iv_size=8,
        program_id=bytes([0x81, 0x02]),
    ),
    "AES-256_OFB": EncryptAlgHeader(
        name="AES-256_OFB",
        key_len=32,
        block_len=16,
        iv_size=16,
        program_id=bytes([0x81, 0x03]),
    ),
    "AES-256_CBC": EncryptAlgHeader(
        name="AES-256_CBC",
        key_len=32,
        block_len=16,
        iv_size=16,
        program_id=bytes([0x81, 0x04]),
    ),
    "AES-256_CFB": EncryptAlgHeader(
        name="AES-256_CFB",
        key_len=32,
        block_len=16,
        iv_size=16,
        program_id=bytes([0x81, 0x05]),
    ),
}

EncryptAlgProgramId_to_Name = {
    EncryptAlg.program_id: EncryptAlg.name for EncryptAlg in encryptAlgs.values()
}


def get_encrypt_algorithms():
    return [encrypt_alg.name for encrypt_alg in encryptAlgs.values()]
