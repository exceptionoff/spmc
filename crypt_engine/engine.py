# -*- coding: utf-8 -*-
# This file contains the cryptographic primitives
# necessary for the program to encrypt.
import typing
from hashlib import sha512

from Crypto.Random import get_random_bytes
from pygost.gost3413 import pad1

from crypt_engine.crypto_algorithms import EncryptAlgHeader, encryptAlgs


class Cipher:
    """This class representing encryption/decryption capabilities on selected algorithms."""

    def __init__(
        self, enc_alg_name: str, key: bytes, iv: typing.Optional[bytes] = None
    ):
        enc_alg = encryptAlgs[enc_alg_name]
        if len(key) != enc_alg.key_len:
            raise Cipher.WrongKeyLength(len(key), enc_alg.key_len)
        if iv:
            if len(iv) != enc_alg.iv_size:
                raise Cipher.WrongIVLength(len(iv), enc_alg.iv_size)
        self.enc_alg = enc_alg
        self._key = key
        self._iv = iv
        self.encrypter = None
        self.decrypter = None
        if not self._iv:
            if enc_alg.iv_size != 0:
                self._iv = get_random_bytes(enc_alg.iv_size)
        self._init_encrypter_decrypter()

    @property
    def iv(self):
        """

        :return: iv
        """
        return self._iv

    def encrypt(self, data: bytes) -> bytes:
        """Performs encryption, if necessary, complements the encrypted message
        to a multiple of the block size, adding zero bytes to its end.

        :return: encrypted data
        """
        if "ECB" in self.enc_alg.name or "CBC" in self.enc_alg.name:
            if len(data) % self.enc_alg.block_len != 0:
                data = self._pad(data)
        return self.encrypter(data)

    def decrypt(self, data: bytes, data_len: typing.Optional[int] = None) -> bytes:
        """Performs data decryption by cutting off extra bytes from the
        specified size data_len. If the size is not specified, nothing is cut off.

        :return: decrypted data
        """
        if not data_len:
            data_len = len(data)
        return self._unpad(self.decrypter(data), data_len)

    def _pad(self, data: bytes) -> bytes:
        """Padding data up to a multiple of the block size with zero bytes."""
        return pad1(data, self.enc_alg.block_len)

    def _unpad(self, data: bytes, data_len: int) -> bytes:
        """Cuts off extra bytes from the data up to length data_len."""
        return data[:data_len]

    def _init_encrypter_decrypter(self):
        """The method initializes the encoder and decoder of the selected algorithm."""

        if (
            "GOST_34_13_64" in self.enc_alg.name
            or "GOST_34_13_128" in self.enc_alg.name
        ):
            if "GOST_34_13_64" in self.enc_alg.name:
                from pygost.gost3412 import GOST3412Magma as EncAlgorithm
            elif "GOST_34_13_128" in self.enc_alg.name:
                from pygost.gost3412 import GOST3412Kuznechik as EncAlgorithm

            if "ECB" in self.enc_alg.name:
                from pygost.gost3413 import ecb_encrypt, ecb_decrypt

                self.encrypter = lambda data: ecb_encrypt(
                    EncAlgorithm(self._key).encrypt, self.enc_alg.block_len, data
                )
                self.decrypter = lambda data: ecb_decrypt(
                    EncAlgorithm(self._key).decrypt, self.enc_alg.block_len, data
                )
            if "CTR" in self.enc_alg.name:
                from pygost.gost3413 import ctr

                self.encrypter = lambda data: ctr(
                    EncAlgorithm(self._key).encrypt,
                    self.enc_alg.block_len,
                    data,
                    self._iv,
                )
                self.decrypter = self.encrypter

            if "OFB" in self.enc_alg.name:
                from pygost.gost3413 import ofb

                self.encrypter = lambda data: ofb(
                    EncAlgorithm(self._key).encrypt,
                    self.enc_alg.block_len,
                    data,
                    self._iv,
                )
                self.decrypter = self.encrypter

            if "CBC" in self.enc_alg.name:
                from pygost.gost3413 import cbc_encrypt, cbc_decrypt

                self.encrypter = lambda data: cbc_encrypt(
                    EncAlgorithm(self._key).encrypt,
                    self.enc_alg.block_len,
                    data,
                    self._iv,
                )
                self.decrypter = lambda data: cbc_decrypt(
                    EncAlgorithm(self._key).decrypt,
                    self.enc_alg.block_len,
                    data,
                    self._iv,
                )

            if "CFB" in self.enc_alg.name:
                from pygost.gost3413 import cfb_encrypt, cfb_decrypt

                self.encrypter = lambda data: cfb_encrypt(
                    EncAlgorithm(self._key).encrypt,
                    self.enc_alg.block_len,
                    data,
                    self._iv,
                )
                self.decrypter = lambda data: cfb_decrypt(
                    EncAlgorithm(self._key).encrypt,
                    self.enc_alg.block_len,
                    data,
                    self._iv,
                )

        if "3DES" in self.enc_alg.name or "AES-256" in self.enc_alg.name:
            if "3DES" in self.enc_alg.name:
                from Crypto.Cipher import DES3 as EncAlgorithm
            elif "AES-256" in self.enc_alg.name:
                from Crypto.Cipher import AES as EncAlgorithm

            if "ECB" in self.enc_alg.name:
                self.encrypter = lambda data: EncAlgorithm.new(
                    self._key, EncAlgorithm.MODE_ECB
                ).encrypt(data)
                self.decrypter = lambda data: EncAlgorithm.new(
                    self._key, EncAlgorithm.MODE_ECB
                ).decrypt(data)
            if "CTR" in self.enc_alg.name:
                self.encrypter = lambda data: EncAlgorithm.new(
                    self._key, EncAlgorithm.MODE_CTR, nonce=self._iv
                ).encrypt(data)
                self.decrypter = lambda data: EncAlgorithm.new(
                    self._key, EncAlgorithm.MODE_CTR, nonce=self._iv
                ).decrypt(data)
            if "OFB" in self.enc_alg.name:
                self.encrypter = lambda data: EncAlgorithm.new(
                    self._key, EncAlgorithm.MODE_OFB, iv=self._iv
                ).encrypt(data)
                self.decrypter = lambda data: EncAlgorithm.new(
                    self._key, EncAlgorithm.MODE_OFB, iv=self._iv
                ).decrypt(data)
            if "CBC" in self.enc_alg.name:
                self.encrypter = lambda data: EncAlgorithm.new(
                    self._key, EncAlgorithm.MODE_CBC, iv=self._iv
                ).encrypt(data)
                self.decrypter = lambda data: EncAlgorithm.new(
                    self._key, EncAlgorithm.MODE_CBC, iv=self._iv
                ).decrypt(data)
            if "CFB" in self.enc_alg.name:
                self.encrypter = lambda data: EncAlgorithm.new(
                    self._key, EncAlgorithm.MODE_CFB, iv=self._iv
                ).encrypt(data)
                self.decrypter = lambda data: EncAlgorithm.new(
                    self._key, EncAlgorithm.MODE_CFB, iv=self._iv
                ).decrypt(data)

    class WrongKeyLength(Exception):
        def __init__(self, actual_value: int, excepted_value: int):
            super().__init__()
            self.msg = (
                f"The key length must be {excepted_value} bytes (actual {actual_value})"
            )

    class WrongIVLength(Exception):
        def __init__(self, actual_value: int, excepted_value: int):
            super().__init__()
            self.msg = f"The initialization vector length must be {excepted_value} bytes (actual {actual_value})"


def calculate_key(password: str, enc_alg_name) -> bytes:
    key = password.encode("utf8")
    key_len = encryptAlgs[enc_alg_name].key_len
    for i in range(2**20):
        key = sha512(key).digest()
    return key[:key_len]
