# -*- coding: utf-8 -*-
# This file contains tests on the encryption algorithms
# used in the application.
from collections import namedtuple
import pytest

from crypt_engine.engine import Cipher


test_set = namedtuple("test_set", "alg_name key iv plain_text cipher_text")

key_GOST_34_13_128 = (
    0x8899AABBCCDDEEFF0011223344556677FEDCBA98765432100123456789ABCDEF.to_bytes(
        32, "big"
    )
)
key_GOST_34_13_64 = (
    0xFFEEDDCCBBAA99887766554433221100F0F1F2F3F4F5F6F7F8F9FAFBFCFDFEFF.to_bytes(
        32, "big"
    )
)
plain_text_GOST_34_13_128 = 0x1122334455667700FFEEDDCCBBAA998800112233445566778899AABBCCEEFF0A112233445566778899AABBCCEEFF0A002233445566778899AABBCCEEFF0A0011.to_bytes(
    64, "big"
)
plain_text_GOST_34_13_64 = (
    0x92DEF06B3C130A59DB54C704F8189D204A98FB2E67A8024C8912409B17B57E41.to_bytes(
        32, "big"
    )
)

test_sets = [
    test_set(
        "GOST_34_13_128_ECB",
        key_GOST_34_13_128,
        None,
        plain_text_GOST_34_13_128,
        0x7F679D90BEBC24305A468D42B9D4EDCDB429912C6E0032F9285452D76718D08BF0CA33549D247CEEF3F5A5313BD4B157D0B09CCDE830B9EB3A02C4C5AA8ADA98.to_bytes(
            64, "big"
        ),
    ),
    test_set(
        "GOST_34_13_128_CTR",
        key_GOST_34_13_128,
        0x1234567890ABCEF0.to_bytes(8, "big"),
        plain_text_GOST_34_13_128,
        0xF195D8BEC10ED1DBD57B5FA240BDA1B885EEE733F6A13E5DF33CE4B33C45DEE4A5EAE88BE6356ED3D5E877F13564A3A5CB91FAB1F20CBAB6D1C6D15820BDBA73.to_bytes(
            64, "big"
        ),
    ),
    test_set(
        "GOST_34_13_128_OFB",
        key_GOST_34_13_128,
        0x1234567890ABCEF0A1B2C3D4E5F0011223344556677889901213141516171819.to_bytes(
            32, "big"
        ),
        plain_text_GOST_34_13_128,
        0x81800A59B1842B24FF1F795E897ABD95ED5B47A7048CFAB48FB521369D9326BF66A257AC3CA0B8B1C80FE7FC10288A13203EBBC066138660A0292243F6903150.to_bytes(
            64, "big"
        ),
    ),
    test_set(
        "GOST_34_13_128_CBC",
        key_GOST_34_13_128,
        0x1234567890ABCEF0A1B2C3D4E5F0011223344556677889901213141516171819.to_bytes(
            32, "big"
        ),
        plain_text_GOST_34_13_128,
        0x689972D4A085FA4D90E52E3D6D7DCC272826E661B478ECA6AF1E8E448D5EA5ACFE7BABF1E91999E85640E8B0F49D90D0167688065A895C631A2D9A1560B63970.to_bytes(
            64, "big"
        ),
    ),
    test_set(
        "GOST_34_13_128_CFB",
        key_GOST_34_13_128,
        0x1234567890ABCEF0A1B2C3D4E5F0011223344556677889901213141516171819.to_bytes(
            32, "big"
        ),
        plain_text_GOST_34_13_128,
        0x81800A59B1842B24FF1F795E897ABD95ED5B47A7048CFAB48FB521369D9326BF79F2A8EB5CC68D38842D264E97A238B54FFEBECD4E922DE6C75BD9DD44FBF4D1.to_bytes(
            64, "big"
        ),
    ),
    test_set(
        "GOST_34_13_64_ECB",
        key_GOST_34_13_64,
        None,
        plain_text_GOST_34_13_64,
        0x2B073F0494F372A0DE70E715D3556E4811D8D9E9EACFBC1E7C68260996C67EFB.to_bytes(
            32, "big"
        ),
    ),
    test_set(
        "GOST_34_13_64_CTR",
        key_GOST_34_13_64,
        0x12345678.to_bytes(4, "big"),
        plain_text_GOST_34_13_64,
        0x4E98110C97B7B93C3E250D93D6E85D69136D868807B2DBEF568EB680AB52A12D.to_bytes(
            32, "big"
        ),
    ),
    test_set(
        "GOST_34_13_64_OFB",
        key_GOST_34_13_64,
        0x1234567890ABCDEF234567890ABCDEF1.to_bytes(16, "big"),
        plain_text_GOST_34_13_64,
        0xDB37E0E266903C830D46644C1F9A089CA0F83062430E327EC824EFB8BD4FDB05.to_bytes(
            32, "big"
        ),
    ),
    test_set(
        "GOST_34_13_64_CBC",
        key_GOST_34_13_64,
        0x1234567890ABCDEF234567890ABCDEF134567890ABCDEF12.to_bytes(24, "big"),
        plain_text_GOST_34_13_64,
        0x96D1B05EEA683919AFF76129ABB937B95058B4A1C4BC001920B78B1A7CD7E667.to_bytes(
            32, "big"
        ),
    ),
    test_set(
        "GOST_34_13_64_CFB",
        key_GOST_34_13_64,
        0x1234567890ABCDEF234567890ABCDEF1.to_bytes(16, "big"),
        plain_text_GOST_34_13_64,
        0xDB37E0E266903C830D46644C1F9A089C24BDD2035315D38BBCC0321421075505.to_bytes(
            32, "big"
        ),
    ),
]


@pytest.mark.parametrize("ts", test_sets)
def test_encrypt_algorithms(ts: test_set):
    cipher = Cipher(ts.alg_name, ts.key, ts.iv)
    assert cipher.encrypt(ts.plain_text) == ts.cipher_text
    assert cipher.decrypt(ts.cipher_text) == ts.plain_text
