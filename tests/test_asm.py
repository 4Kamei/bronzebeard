from ctypes import c_int32
import struct

import pytest

from asm import *


@pytest.mark.parametrize(
    'value,      bits, expected', [
    # full-size extension simply applies two's complement
    (0b00000000, 8,    0),
    (0b01111111, 8,    127),
    (0b11111111, 8,    -1),
    (0b10000000, 8,    -128),
    (0b00000110, 8,    6),
    (0b00000110, 4,    6),
    (0b00000110, 3,    -2),
    (0x00000000, 32,   0),
    (0xffffffff, 32,   -1),
    (0x00000fff, 12,   -1),
])
def test_sign_extend(value, bits, expected):
    assert sign_extend(value, bits) == expected


@pytest.mark.parametrize(
    'value,      expected', [
    (0x00000000, 0),
    (0x00001000, 1),
    (0x7ffff000, 0x7ffff),
    (0xfffff000, -1),
    (0x80000000, -0x80000),
    # MSB of lower portion being 1 should affect result
    (0x00000800, 1),
    (0x00001800, 2),
    (0x7ffff800, -0x80000),
    (0xfffff800, 0),
    (0x80000800, -0x7ffff),
])
def test_relocate_hi(value, expected):
    assert relocate_hi(value) == expected


@pytest.mark.parametrize(
    'value,      expected', [
    (0x00000000, 0),
    (0x00000001, 1),
    (0x000007ff, 2047),
    (0x00000fff, -1),
    (0x00000800, -2048),
    # upper 20 bits should have no affect
    (0xfffff000, 0),
    (0xfffff001, 1),
    (0xfffff7ff, 2047),
    (0xffffffff, -1),
    (0xfffff800, -2048),
])
def test_relocate_lo(value, expected):
    assert relocate_lo(value) == expected


@pytest.mark.parametrize(
    'value', [
    (0x00000000),
    (0x00000001),
    (0x000007ff),
    (0x00000fff),
    (0x00000800),
    (0xfffff000),
    (0xfffff7ff),
    (0xfffff800),
    (0xffffffff),
    (0x7fffffff),
    (0x02000000),
    (0x02000004),
    (0xdeadbeef),
    (0x12345678),
    (0xcafec0fe),
])
def test_relocate_hi_lo_sum(value):
    hi = relocate_hi(value)
    lo = relocate_lo(value)
    expected = sign_extend(value, 32)

    sum_raw = (hi << 12) + lo
    sum_wrapped = c_int32(sum_raw).value
    assert sum_wrapped == expected


@pytest.mark.parametrize(
    'rd, imm,      code', [
    (0,  0,        0b00000000000000000000000000110111),
    (31, 0,        0b00000000000000000000111110110111),
    (0,  1,        0b00000000000000000001000000110111),
    (0,  0x7ffff,  0b01111111111111111111000000110111),
    (0,  -1,       0b11111111111111111111000000110111),
    (0,  -0x80000, 0b10000000000000000000000000110111),
])
def test_lui(rd, imm, code):
    assert LUI(rd, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, imm,      code', [
    (0,  0,        0b00000000000000000000000000010111),
    (31, 0,        0b00000000000000000000111110010111),
    (0,  1,        0b00000000000000000001000000010111),
    (0,  0x7ffff,  0b01111111111111111111000000010111),
    (0,  -1,       0b11111111111111111111000000010111),
    (0,  -0x80000, 0b10000000000000000000000000010111),
])
def test_auipc(rd, imm, code):
    assert AUIPC(rd, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, imm,       code', [
    (0,  0,         0b00000000000000000000000001101111),
    (31, 0,         0b00000000000000000000111111101111),
    (0,  2,         0b00000000001000000000000001101111),
    (0,  2046,      0b01111111111000000000000001101111),
    (0,  2048,      0b00000000000100000000000001101111),
    (0,  0x0ff000,  0b00000000000011111111000001101111),
    (0,  0x0ffffe,  0b01111111111111111111000001101111),
    (0,  -2,        0b11111111111111111111000001101111),
    (0,  -0x1000,   0b10000000000011111111000001101111),
    (0,  -0xff800,  0b10000000000100000000000001101111),
    (0,  -0xff802,  0b11111111111000000000000001101111),
    (0,  -0x100000, 0b10000000000000000000000001101111),
])
def test_jal(rd, imm, code):
    assert JAL(rd, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000000000001100111),
    (31, 0,   0,      0b00000000000000000000111111100111),
    (0,  31,  0,      0b00000000000011111000000001100111),
    (31, 31,  0,      0b00000000000011111000111111100111),
    (0,  0,   1,      0b00000000000100000000000001100111),
    (0,  0,   0x7ff,  0b01111111111100000000000001100111),
    (0,  0,   -1,     0b11111111111100000000000001100111),
    (0,  0,   -0x800, 0b10000000000000000000000001100111),
])
def test_jalr(rd, rs1, imm, code):
    assert JALR(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rs1, rs2, imm,     code', [
    (0,   0,   0,       0b00000000000000000000000001100011),
    (31,  0,   0,       0b00000000000011111000000001100011),
    (0,   31,  0,       0b00000001111100000000000001100011),
    (31,  31,  0,       0b00000001111111111000000001100011),
    (0,   0,   2,       0b00000000000000000000000101100011),
    (0,   0,   0xffe,   0b01111110000000000000111111100011),
    (0,   0,   -2,      0b11111110000000000000111111100011),
    (0,   0,   -0x1000, 0b10000000000000000000000001100011),
])
def test_beq(rs1, rs2, imm, code):
    assert BEQ(rs1, rs2, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rs1, rs2, imm,     code', [
    (0,   0,   0,       0b00000000000000000001000001100011),
    (31,  0,   0,       0b00000000000011111001000001100011),
    (0,   31,  0,       0b00000001111100000001000001100011),
    (31,  31,  0,       0b00000001111111111001000001100011),
    (0,   0,   2,       0b00000000000000000001000101100011),
    (0,   0,   0xffe,   0b01111110000000000001111111100011),
    (0,   0,   -2,      0b11111110000000000001111111100011),
    (0,   0,   -0x1000, 0b10000000000000000001000001100011),
])
def test_bne(rs1, rs2, imm, code):
    assert BNE(rs1, rs2, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rs1, rs2, imm,     code', [
    (0,   0,   0,       0b00000000000000000100000001100011),
    (31,  0,   0,       0b00000000000011111100000001100011),
    (0,   31,  0,       0b00000001111100000100000001100011),
    (31,  31,  0,       0b00000001111111111100000001100011),
    (0,   0,   2,       0b00000000000000000100000101100011),
    (0,   0,   0xffe,   0b01111110000000000100111111100011),
    (0,   0,   -2,      0b11111110000000000100111111100011),
    (0,   0,   -0x1000, 0b10000000000000000100000001100011),
])
def test_blt(rs1, rs2, imm, code):
    assert BLT(rs1, rs2, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rs1, rs2, imm,     code', [
    (0,   0,   0,       0b00000000000000000101000001100011),
    (31,  0,   0,       0b00000000000011111101000001100011),
    (0,   31,  0,       0b00000001111100000101000001100011),
    (31,  31,  0,       0b00000001111111111101000001100011),
    (0,   0,   2,       0b00000000000000000101000101100011),
    (0,   0,   0xffe,   0b01111110000000000101111111100011),
    (0,   0,   -2,      0b11111110000000000101111111100011),
    (0,   0,   -0x1000, 0b10000000000000000101000001100011),
])
def test_bge(rs1, rs2, imm, code):
    assert BGE(rs1, rs2, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rs1, rs2, imm,     code', [
    (0,   0,   0,       0b00000000000000000110000001100011),
    (31,  0,   0,       0b00000000000011111110000001100011),
    (0,   31,  0,       0b00000001111100000110000001100011),
    (31,  31,  0,       0b00000001111111111110000001100011),
    (0,   0,   2,       0b00000000000000000110000101100011),
    (0,   0,   0xffe,   0b01111110000000000110111111100011),
    (0,   0,   -2,      0b11111110000000000110111111100011),
    (0,   0,   -0x1000, 0b10000000000000000110000001100011),
])
def test_bltu(rs1, rs2, imm, code):
    assert BLTU(rs1, rs2, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rs1, rs2, imm,     code', [
    (0,   0,   0,       0b00000000000000000111000001100011),
    (31,  0,   0,       0b00000000000011111111000001100011),
    (0,   31,  0,       0b00000001111100000111000001100011),
    (31,  31,  0,       0b00000001111111111111000001100011),
    (0,   0,   2,       0b00000000000000000111000101100011),
    (0,   0,   0xffe,   0b01111110000000000111111111100011),
    (0,   0,   -2,      0b11111110000000000111111111100011),
    (0,   0,   -0x1000, 0b10000000000000000111000001100011),
])
def test_bgeu(rs1, rs2, imm, code):
    assert BGEU(rs1, rs2, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000000000000000011),
    (31, 0,   0,      0b00000000000000000000111110000011),
    (0,  31,  0,      0b00000000000011111000000000000011),
    (31, 31,  0,      0b00000000000011111000111110000011),
    (0,  0,   1,      0b00000000000100000000000000000011),
    (0,  0,   0x7ff,  0b01111111111100000000000000000011),
    (0,  0,   -1,     0b11111111111100000000000000000011),
    (0,  0,   -0x800, 0b10000000000000000000000000000011),
])
def test_lb(rd, rs1, imm, code):
    assert LB(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000001000000000011),
    (31, 0,   0,      0b00000000000000000001111110000011),
    (0,  31,  0,      0b00000000000011111001000000000011),
    (31, 31,  0,      0b00000000000011111001111110000011),
    (0,  0,   1,      0b00000000000100000001000000000011),
    (0,  0,   0x7ff,  0b01111111111100000001000000000011),
    (0,  0,   -1,     0b11111111111100000001000000000011),
    (0,  0,   -0x800, 0b10000000000000000001000000000011),
])
def test_lh(rd, rs1, imm, code):
    assert LH(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000010000000000011),
    (31, 0,   0,      0b00000000000000000010111110000011),
    (0,  31,  0,      0b00000000000011111010000000000011),
    (31, 31,  0,      0b00000000000011111010111110000011),
    (0,  0,   1,      0b00000000000100000010000000000011),
    (0,  0,   0x7ff,  0b01111111111100000010000000000011),
    (0,  0,   -1,     0b11111111111100000010000000000011),
    (0,  0,   -0x800, 0b10000000000000000010000000000011),
])
def test_lw(rd, rs1, imm, code):
    assert LW(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000100000000000011),
    (31, 0,   0,      0b00000000000000000100111110000011),
    (0,  31,  0,      0b00000000000011111100000000000011),
    (31, 31,  0,      0b00000000000011111100111110000011),
    (0,  0,   1,      0b00000000000100000100000000000011),
    (0,  0,   0x7ff,  0b01111111111100000100000000000011),
    (0,  0,   -1,     0b11111111111100000100000000000011),
    (0,  0,   -0x800, 0b10000000000000000100000000000011),
])
def test_lbu(rd, rs1, imm, code):
    assert LBU(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000101000000000011),
    (31, 0,   0,      0b00000000000000000101111110000011),
    (0,  31,  0,      0b00000000000011111101000000000011),
    (31, 31,  0,      0b00000000000011111101111110000011),
    (0,  0,   1,      0b00000000000100000101000000000011),
    (0,  0,   0x7ff,  0b01111111111100000101000000000011),
    (0,  0,   -1,     0b11111111111100000101000000000011),
    (0,  0,   -0x800, 0b10000000000000000101000000000011),
])
def test_lhu(rd, rs1, imm, code):
    assert LHU(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rs1, rs2, imm,   code', [
    (0,   0,   0,     0b00000000000000000000000000100011),
    (31,  0,   0,     0b00000000000011111000000000100011),
    (0,   31,  0,     0b00000001111100000000000000100011),
    (31,  31,  0,     0b00000001111111111000000000100011),
    (0,   0,   1,     0b00000000000000000000000010100011),
    (0,   0,   2047,  0b01111110000000000000111110100011),
    (0,   0,   -1,    0b11111110000000000000111110100011),
    (0,   0,   -2048, 0b10000000000000000000000000100011),
])
def test_sb(rs1, rs2, imm, code):
    assert SB(rs1, rs2, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rs1, rs2, imm,   code', [
    (0,   0,   0,     0b00000000000000000001000000100011),
    (31,  0,   0,     0b00000000000011111001000000100011),
    (0,   31,  0,     0b00000001111100000001000000100011),
    (31,  31,  0,     0b00000001111111111001000000100011),
    (0,   0,   1,     0b00000000000000000001000010100011),
    (0,   0,   2047,  0b01111110000000000001111110100011),
    (0,   0,   -1,    0b11111110000000000001111110100011),
    (0,   0,   -2048, 0b10000000000000000001000000100011),
])
def test_sh(rs1, rs2, imm, code):
    assert SH(rs1, rs2, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rs1, rs2, imm,   code', [
    (0,   0,   0,     0b00000000000000000010000000100011),
    (31,  0,   0,     0b00000000000011111010000000100011),
    (0,   31,  0,     0b00000001111100000010000000100011),
    (31,  31,  0,     0b00000001111111111010000000100011),
    (0,   0,   1,     0b00000000000000000010000010100011),
    (0,   0,   2047,  0b01111110000000000010111110100011),
    (0,   0,   -1,    0b11111110000000000010111110100011),
    (0,   0,   -2048, 0b10000000000000000010000000100011),
])
def test_sw(rs1, rs2, imm, code):
    assert SW(rs1, rs2, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000000000000010011),
    (31, 0,   0,      0b00000000000000000000111110010011),
    (0,  31,  0,      0b00000000000011111000000000010011),
    (31, 31,  0,      0b00000000000011111000111110010011),
    (0,  0,   1,      0b00000000000100000000000000010011),
    (0,  0,   0x7ff,  0b01111111111100000000000000010011),
    (0,  0,   -1,     0b11111111111100000000000000010011),
    (0,  0,   -0x800, 0b10000000000000000000000000010011),
])
def test_addi(rd, rs1, imm, code):
    assert ADDI(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000010000000010011),
    (31, 0,   0,      0b00000000000000000010111110010011),
    (0,  31,  0,      0b00000000000011111010000000010011),
    (31, 31,  0,      0b00000000000011111010111110010011),
    (0,  0,   1,      0b00000000000100000010000000010011),
    (0,  0,   0x7ff,  0b01111111111100000010000000010011),
    (0,  0,   -1,     0b11111111111100000010000000010011),
    (0,  0,   -0x800, 0b10000000000000000010000000010011),
])
def test_slti(rd, rs1, imm, code):
    assert SLTI(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000011000000010011),
    (31, 0,   0,      0b00000000000000000011111110010011),
    (0,  31,  0,      0b00000000000011111011000000010011),
    (31, 31,  0,      0b00000000000011111011111110010011),
    (0,  0,   1,      0b00000000000100000011000000010011),
    (0,  0,   0x7ff,  0b01111111111100000011000000010011),
    (0,  0,   -1,     0b11111111111100000011000000010011),
    (0,  0,   -0x800, 0b10000000000000000011000000010011),
])
def test_sltiu(rd, rs1, imm, code):
    assert SLTIU(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000100000000010011),
    (31, 0,   0,      0b00000000000000000100111110010011),
    (0,  31,  0,      0b00000000000011111100000000010011),
    (31, 31,  0,      0b00000000000011111100111110010011),
    (0,  0,   1,      0b00000000000100000100000000010011),
    (0,  0,   0x7ff,  0b01111111111100000100000000010011),
    (0,  0,   -1,     0b11111111111100000100000000010011),
    (0,  0,   -0x800, 0b10000000000000000100000000010011),
])
def test_xori(rd, rs1, imm, code):
    assert XORI(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000110000000010011),
    (31, 0,   0,      0b00000000000000000110111110010011),
    (0,  31,  0,      0b00000000000011111110000000010011),
    (31, 31,  0,      0b00000000000011111110111110010011),
    (0,  0,   1,      0b00000000000100000110000000010011),
    (0,  0,   0x7ff,  0b01111111111100000110000000010011),
    (0,  0,   -1,     0b11111111111100000110000000010011),
    (0,  0,   -0x800, 0b10000000000000000110000000010011),
])
def test_ori(rd, rs1, imm, code):
    assert ORI(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, imm,    code', [
    (0,  0,   0,      0b00000000000000000111000000010011),
    (31, 0,   0,      0b00000000000000000111111110010011),
    (0,  31,  0,      0b00000000000011111111000000010011),
    (31, 31,  0,      0b00000000000011111111111110010011),
    (0,  0,   1,      0b00000000000100000111000000010011),
    (0,  0,   0x7ff,  0b01111111111100000111000000010011),
    (0,  0,   -1,     0b11111111111100000111000000010011),
    (0,  0,   -0x800, 0b10000000000000000111000000010011),
])
def test_andi(rd, rs1, imm, code):
    assert ANDI(rd, rs1, imm) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b00000000000000000001000000010011),
    (31, 0,   0,   0b00000000000000000001111110010011),
    (0,  31,  0,   0b00000000000011111001000000010011),
    (31, 31,  0,   0b00000000000011111001111110010011),
    (0,  0,   31,  0b00000001111100000001000000010011),
    (31, 0,   31,  0b00000001111100000001111110010011),
    (0,  31,  31,  0b00000001111111111001000000010011),
    (31, 31,  31,  0b00000001111111111001111110010011),
])
def test_slli(rd, rs1, rs2, code):
    assert SLLI(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b00000000000000000101000000010011),
    (31, 0,   0,   0b00000000000000000101111110010011),
    (0,  31,  0,   0b00000000000011111101000000010011),
    (31, 31,  0,   0b00000000000011111101111110010011),
    (0,  0,   31,  0b00000001111100000101000000010011),
    (31, 0,   31,  0b00000001111100000101111110010011),
    (0,  31,  31,  0b00000001111111111101000000010011),
    (31, 31,  31,  0b00000001111111111101111110010011),
])
def test_srli(rd, rs1, rs2, code):
    assert SRLI(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b01000000000000000101000000010011),
    (31, 0,   0,   0b01000000000000000101111110010011),
    (0,  31,  0,   0b01000000000011111101000000010011),
    (31, 31,  0,   0b01000000000011111101111110010011),
    (0,  0,   31,  0b01000001111100000101000000010011),
    (31, 0,   31,  0b01000001111100000101111110010011),
    (0,  31,  31,  0b01000001111111111101000000010011),
    (31, 31,  31,  0b01000001111111111101111110010011),
])
def test_srai(rd, rs1, rs2, code):
    assert SRAI(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b00000000000000000000000000110011),
    (31, 0,   0,   0b00000000000000000000111110110011),
    (0,  31,  0,   0b00000000000011111000000000110011),
    (31, 31,  0,   0b00000000000011111000111110110011),
    (0,  0,   31,  0b00000001111100000000000000110011),
    (31, 0,   31,  0b00000001111100000000111110110011),
    (0,  31,  31,  0b00000001111111111000000000110011),
    (31, 31,  31,  0b00000001111111111000111110110011),
])
def test_add(rd, rs1, rs2, code):
    assert ADD(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b01000000000000000000000000110011),
    (31, 0,   0,   0b01000000000000000000111110110011),
    (0,  31,  0,   0b01000000000011111000000000110011),
    (31, 31,  0,   0b01000000000011111000111110110011),
    (0,  0,   31,  0b01000001111100000000000000110011),
    (31, 0,   31,  0b01000001111100000000111110110011),
    (0,  31,  31,  0b01000001111111111000000000110011),
    (31, 31,  31,  0b01000001111111111000111110110011),
])
def test_sub(rd, rs1, rs2, code):
    assert SUB(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b00000000000000000001000000110011),
    (31, 0,   0,   0b00000000000000000001111110110011),
    (0,  31,  0,   0b00000000000011111001000000110011),
    (31, 31,  0,   0b00000000000011111001111110110011),
    (0,  0,   31,  0b00000001111100000001000000110011),
    (31, 0,   31,  0b00000001111100000001111110110011),
    (0,  31,  31,  0b00000001111111111001000000110011),
    (31, 31,  31,  0b00000001111111111001111110110011),
])
def test_sll(rd, rs1, rs2, code):
    assert SLL(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b00000000000000000010000000110011),
    (31, 0,   0,   0b00000000000000000010111110110011),
    (0,  31,  0,   0b00000000000011111010000000110011),
    (31, 31,  0,   0b00000000000011111010111110110011),
    (0,  0,   31,  0b00000001111100000010000000110011),
    (31, 0,   31,  0b00000001111100000010111110110011),
    (0,  31,  31,  0b00000001111111111010000000110011),
    (31, 31,  31,  0b00000001111111111010111110110011),
])
def test_slt(rd, rs1, rs2, code):
    assert SLT(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b00000000000000000011000000110011),
    (31, 0,   0,   0b00000000000000000011111110110011),
    (0,  31,  0,   0b00000000000011111011000000110011),
    (31, 31,  0,   0b00000000000011111011111110110011),
    (0,  0,   31,  0b00000001111100000011000000110011),
    (31, 0,   31,  0b00000001111100000011111110110011),
    (0,  31,  31,  0b00000001111111111011000000110011),
    (31, 31,  31,  0b00000001111111111011111110110011),
])
def test_sltu(rd, rs1, rs2, code):
    assert SLTU(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b00000000000000000100000000110011),
    (31, 0,   0,   0b00000000000000000100111110110011),
    (0,  31,  0,   0b00000000000011111100000000110011),
    (31, 31,  0,   0b00000000000011111100111110110011),
    (0,  0,   31,  0b00000001111100000100000000110011),
    (31, 0,   31,  0b00000001111100000100111110110011),
    (0,  31,  31,  0b00000001111111111100000000110011),
    (31, 31,  31,  0b00000001111111111100111110110011),
])
def test_xor(rd, rs1, rs2, code):
    assert XOR(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b00000000000000000101000000110011),
    (31, 0,   0,   0b00000000000000000101111110110011),
    (0,  31,  0,   0b00000000000011111101000000110011),
    (31, 31,  0,   0b00000000000011111101111110110011),
    (0,  0,   31,  0b00000001111100000101000000110011),
    (31, 0,   31,  0b00000001111100000101111110110011),
    (0,  31,  31,  0b00000001111111111101000000110011),
    (31, 31,  31,  0b00000001111111111101111110110011),
])
def test_srl(rd, rs1, rs2, code):
    assert SRL(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b01000000000000000101000000110011),
    (31, 0,   0,   0b01000000000000000101111110110011),
    (0,  31,  0,   0b01000000000011111101000000110011),
    (31, 31,  0,   0b01000000000011111101111110110011),
    (0,  0,   31,  0b01000001111100000101000000110011),
    (31, 0,   31,  0b01000001111100000101111110110011),
    (0,  31,  31,  0b01000001111111111101000000110011),
    (31, 31,  31,  0b01000001111111111101111110110011),
])
def test_sra(rd, rs1, rs2, code):
    assert SRA(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b00000000000000000110000000110011),
    (31, 0,   0,   0b00000000000000000110111110110011),
    (0,  31,  0,   0b00000000000011111110000000110011),
    (31, 31,  0,   0b00000000000011111110111110110011),
    (0,  0,   31,  0b00000001111100000110000000110011),
    (31, 0,   31,  0b00000001111100000110111110110011),
    (0,  31,  31,  0b00000001111111111110000000110011),
    (31, 31,  31,  0b00000001111111111110111110110011),
])
def test_or(rd, rs1, rs2, code):
    assert OR(rd, rs1, rs2) == struct.pack('<I', code)


@pytest.mark.parametrize(
    'rd, rs1, rs2, code', [
    (0,  0,   0,   0b00000000000000000111000000110011),
    (31, 0,   0,   0b00000000000000000111111110110011),
    (0,  31,  0,   0b00000000000011111111000000110011),
    (31, 31,  0,   0b00000000000011111111111110110011),
    (0,  0,   31,  0b00000001111100000111000000110011),
    (31, 0,   31,  0b00000001111100000111111110110011),
    (0,  31,  31,  0b00000001111111111111000000110011),
    (31, 31,  31,  0b00000001111111111111111110110011),
])
def test_and(rd, rs1, rs2, code):
    assert AND(rd, rs1, rs2) == struct.pack('<I', code)
