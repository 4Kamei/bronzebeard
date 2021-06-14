import pytest

from bronzebeard import asm


@pytest.mark.parametrize(
    'rd, imm,     code', [
    (8,  4,      0b0000000001000000),
    (8,  1020,   0b0001111111100000),
    (15, 0x01*4, 0b0000000001011100),
    (15, 0xff*4, 0b0001111111111100),
    (8,  8,      0b0000000000100000),
    (8,  12,     0b0000000001100000),
])
def test_c_addi4spn(rd, imm, code):
    assert asm.C_ADDI4SPN(rd, imm) == code


@pytest.mark.parametrize(
    'rd, rs1, imm, code', [
    (8,  8,   0,   0b0100000000000000),
    (8,  8,   124, 0b0101110001100000),
    (8,  15,  0,   0b0100001110000000),
    (15, 8,   0,   0b0100000000011100),
    (15, 15,  124, 0b0101111111111100),
])
def test_c_lw(rd, rs1, imm, code):
    assert asm.C_LW(rd, rs1, imm) == code


@pytest.mark.parametrize(
    'rs1, rs2, imm, code', [
    (8,   8,   0,   0b1100000000000000),
    (8,   8,   124, 0b1101110001100000),
    (8,   15,  0,   0b1100000000011100),
    (15,  8,   0,   0b1100001110000000),
    (15,  15,  124, 0b1101111111111100),
])
def test_c_sw(rs1, rs2, imm, code):
    assert asm.C_SW(rs1, rs2, imm) == code


@pytest.mark.parametrize(
    'code', [
    0b0000000000000001,
])
def test_c_nop(code):
    assert asm.C_NOP() == code


@pytest.mark.parametrize(
    'rd_rs1, imm, code', [
    (1,      1,   0b0000000010000101),
    (1 ,     31,  0b0000000011111101),
    (1,      -1,  0b0001000011111101),
    (1,      -32, 0b0001000010000001),
    (31,     1,   0b0000111110000101),
    (31,     31,  0b0000111111111101),
    (31,     -1,  0b0001111111111101),
    (31,     -32, 0b0001111110000001),
])
def test_c_addi(rd_rs1, imm, code):
    assert asm.C_ADDI(rd_rs1, imm) == code


@pytest.mark.parametrize(
    'rd_rs1, imm, code', [
    (1,      1,   0b0100000010000101),
    (1 ,     31,  0b0100000011111101),
    (1,      -1,  0b0101000011111101),
    (1,      -32, 0b0101000010000001),
    (31,     1 ,  0b0100111110000101),
    (31,     31,  0b0100111111111101),
    (31,     -1,  0b0101111111111101),
    (31,     -32, 0b0101111110000001),
])
def test_c_li(rd_rs1, imm, code):
    assert asm.C_LI(rd_rs1, imm) == code


@pytest.mark.parametrize(
    'rd_rs1, imm,  code', [
    (2,      16,   0b0110000100000101),
    (2,      496,  0b0110000101111101),
    (2,      -16,  0b0111000101111101),
    (2,      -512, 0b0111000100000001),
])
def test_c_addi16sp(rd_rs1, imm, code):
    assert asm.C_ADDI16SP(rd_rs1, imm) == code


@pytest.mark.parametrize(
    'rd_rs1, imm, code', [
    (1,      1,   0b0110000010000101),
    (1 ,     31,  0b0110000011111101),
    (1,      -1,  0b0111000011111101),
    (1,      -32, 0b0111000010000001),
    (31,     1 ,  0b0110111110000101),
    (31,     31,  0b0110111111111101),
    (31,     -1,  0b0111111111111101),
    (31,     -32, 0b0111111110000001),
])
def test_c_lui(rd_rs1, imm, code):
    assert asm.C_LUI(rd_rs1, imm) == code


@pytest.mark.parametrize(
    'rd_rs1, imm, code', [
    (8,      1,   0b1000010000000101),
    (8 ,     31,  0b1000010001111101),
    (15,     1 ,  0b1000011110000101),
    (15,     31,  0b1000011111111101),
])
def test_c_srai(rd_rs1, imm, code):
    assert asm.C_SRAI(rd_rs1, imm) == code


@pytest.mark.parametrize(
    'rd_rs1, imm, code', [
    (8,      1,   0b1000100000000101),
    (8 ,     31,  0b1000100001111101),
    (15,     1 ,  0b1000101110000101),
    (15,     31,  0b1000101111111101),
])
def test_c_andi(rd_rs1, imm, code):
    assert asm.C_ANDI(rd_rs1, imm) == code


@pytest.mark.parametrize(
    'rd_rs1, imm, code', [
    (8,      1,   0b1000000000000101),
    (8 ,     31,  0b1000000001111101),
    (15,     1 ,  0b1000001110000101),
    (15,     31,  0b1000001111111101),
])
def test_c_srli(rd_rs1, imm, code):
    assert asm.C_SRLI(rd_rs1, imm) == code


@pytest.mark.parametrize(
    'rd_rs1, rs2, code', [
    (8,      8,   0b1000110000000001),
    (8 ,     15,  0b1000110000011101),
    (15,     8 ,  0b1000111110000001),
    (15,     15,  0b1000111110011101),
])
def test_c_sub(rd_rs1, rs2, code):
    assert asm.C_SUB(rd_rs1, rs2) == code


@pytest.mark.parametrize(
    'rd_rs1, rs2, code', [
    (8,      8,   0b1000110000100001),
    (8 ,     15,  0b1000110000111101),
    (15,     8 ,  0b1000111110100001),
    (15,     15,  0b1000111110111101),
])
def test_c_xor(rd_rs1, rs2, code):
    assert asm.C_XOR(rd_rs1, rs2) == code


@pytest.mark.parametrize(
    'rd_rs1, rs2, code', [
    (8,      8,   0b1000110001000001),
    (8 ,     15,  0b1000110001011101),
    (15,     8 ,  0b1000111111000001),
    (15,     15,  0b1000111111011101),
])
def test_c_or(rd_rs1, rs2, code):
    assert asm.C_OR(rd_rs1, rs2) == code


@pytest.mark.parametrize(
    'rd_rs1, rs2, code', [
    (8,      8,   0b1000110001100001),
    (8 ,     15,  0b1000110001111101),
    (15,     8 ,  0b1000111111100001),
    (15,     15,  0b1000111111111101),
])
def test_c_and(rd_rs1, rs2, code):
    assert asm.C_AND(rd_rs1, rs2) == code


@pytest.mark.parametrize(
    'imm,   code', [
    (0,     0b1010000000000001),
    (2,     0b1010000000001001),
    (4,     0b1010000000010001),
    (8,     0b1010000000100001),
    (16,    0b1010100000000001),
    (32,    0b1010000000000101),
    (64,    0b1010000010000001),
    (128,   0b1010000001000001),
    (256,   0b1010001000000001),
    (512,   0b1010010000000001),
    (1024,  0b1010000100000001),
    (2046,  0b1010111111111101),
    (-2,    0b1011111111111101),
    (-2048, 0b1011000000000001),
])
def test_c_j(imm, code):
    assert asm.C_J(imm) == code


@pytest.mark.parametrize(
    'rs1, imm,  code', [
    (8,   0,    0b1100000000000001),
    (8,   2,    0b1100000000001001),
    (8,   4,    0b1100000000010001),
    (8,   8,    0b1100010000000001),
    (8,   16,   0b1100100000000001),
    (8,   32,   0b1100000000000101),
    (8,   64,   0b1100000000100001),
    (8,   128,  0b1100000001000001),
    (8,   254,  0b1100110001111101),
    (15,  -2,   0b1101111111111101),
    (15,  -256, 0b1101001110000001),
])
def test_c_beqz(rs1, imm, code):
    assert asm.C_BEQZ(rs1, imm) == code


@pytest.mark.parametrize(
    'rs1, imm,  code', [
    (8,   0,    0b1110000000000001),
    (8,   2,    0b1110000000001001),
    (8,   4,    0b1110000000010001),
    (8,   8,    0b1110010000000001),
    (8,   16,   0b1110100000000001),
    (8,   32,   0b1110000000000101),
    (8,   64,   0b1110000000100001),
    (8,   128,  0b1110000001000001),
    (8,   254,  0b1110110001111101),
    (15,  -2,   0b1111111111111101),
    (15,  -256, 0b1111001110000001),
])
def test_c_bnez(rs1, imm, code):
    assert asm.C_BNEZ(rs1, imm) == code


@pytest.mark.parametrize(
    'rd_rs1, imm, code', [
    (1,      1,   0b0000000010000110),
    (1 ,     31,  0b0000000011111110),
    (31,     1 ,  0b0000111110000110),
    (31,     31,  0b0000111111111110),
])
def test_c_slli(rd_rs1, imm, code):
    assert asm.C_SLLI(rd_rs1, imm) == code


@pytest.mark.parametrize(
    'rd, imm, code', [
    (1,  0,   0b0100000010000010),
    (1 , 252, 0b0101000011111110),
    (31, 0 ,  0b0100111110000010),
    (31, 252, 0b0101111111111110),
])
def test_c_lwsp(rd, imm, code):
    assert asm.C_LWSP(rd, imm) == code


@pytest.mark.parametrize(
    'rd_rs1, rs2, code', [
    (1,      0,   0b1000000010000010),
    (1 ,     0,   0b1000000010000010),
    (31,     0 ,  0b1000111110000010),
    (31,     0,   0b1000111110000010),
])
def test_c_jr(rd_rs1, rs2, code):
    assert asm.C_JR(rd_rs1, rs2) == code


@pytest.mark.parametrize(
    'rd_rs1, rs2, code', [
    (1,      1,   0b1000000010000110),
    (1 ,     31,  0b1000000011111110),
    (31,     1,   0b1000111110000110),
    (31,     31,  0b1000111111111110),
])
def test_c_mv(rd_rs1, rs2, code):
    assert asm.C_MV(rd_rs1, rs2) == code


@pytest.mark.parametrize(
    'rd_rs1, rs2, code', [
    (1,      1,   0b1001000010000110),
    (1,      31,  0b1001000011111110),
    (31,     1,   0b1001111110000110),
    (31,     31,  0b1001111111111110),
])
def test_c_add(rd_rs1, rs2, code):
    assert asm.C_ADD(rd_rs1, rs2) == code


@pytest.mark.parametrize(
    'rs2, imm, code', [
    (0,   0,   0b1100000000000010),
    (0,   4,   0b1100001000000010),
    (0,   8,   0b1100010000000010),
    (0,   16,  0b1100100000000010),
    (0,   32,  0b1101000000000010),
    (0,   64,  0b1100000010000010),
    (0,   128, 0b1100000100000010),
    (0,   252, 0b1101111110000010),
    (31,  0,   0b1100000001111110),
])
def test_c_swsp(rs2, imm, code):
    assert asm.C_SWSP(rs2, imm) == code