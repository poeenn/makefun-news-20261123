"""Sum up 23 November 2026's world news in one image.

Entry for make.fun's news-image-20261123 bounty. Python standard library
only, no network. Draws an English newspaper front page for Monday
23 November 2026 onto a 1024x1024 canvas and writes it as a PNG to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png). Fixed data and
integer geometry only, so two runs write exactly the same bytes.
"""
import os
import struct
import zlib

W = H = 1024
PAPER = (244, 239, 226)
CARD = (253, 250, 242)
NAVY = (18, 32, 56)
INK = (24, 24, 28)
RED = (172, 30, 38)
BLUE = (30, 72, 138)
TEAL = (18, 102, 108)
GOLD = (184, 128, 30)
GREY = (92, 92, 88)
LINE = (206, 196, 172)
SEA = (92, 138, 176)
SMOKE = (130, 130, 126)
SUN = (232, 168, 52)

BUF = bytearray(W * H * 3)

GLYPHS = {
"A": ("01110","10001","10001","11111","10001","10001","10001"),
"B": ("11110","10001","10001","11110","10001","10001","11110"),
"C": ("01110","10001","10000","10000","10000","10001","01110"),
"D": ("11100","10010","10001","10001","10001","10010","11100"),
"E": ("11111","10000","10000","11110","10000","10000","11111"),
"F": ("11111","10000","10000","11110","10000","10000","10000"),
"G": ("01110","10001","10000","10111","10001","10001","01111"),
"H": ("10001","10001","10001","11111","10001","10001","10001"),
"I": ("01110","00100","00100","00100","00100","00100","01110"),
"J": ("00111","00010","00010","00010","00010","10010","01100"),
"K": ("10001","10010","10100","11000","10100","10010","10001"),
"L": ("10000","10000","10000","10000","10000","10000","11111"),
"M": ("10001","11011","10101","10101","10001","10001","10001"),
"N": ("10001","11001","10101","10011","10001","10001","10001"),
"O": ("01110","10001","10001","10001","10001","10001","01110"),
"P": ("11110","10001","10001","11110","10000","10000","10000"),
"Q": ("01110","10001","10001","10001","10101","10010","01101"),
"R": ("11110","10001","10001","11110","10100","10010","10001"),
"S": ("01111","10000","10000","01110","00001","00001","11110"),
"T": ("11111","00100","00100","00100","00100","00100","00100"),
"U": ("10001","10001","10001","10001","10001","10001","01110"),
"V": ("10001","10001","10001","10001","10001","01010","00100"),
"W": ("10001","10001","10001","10101","10101","10101","01010"),
"X": ("10001","01010","00100","00100","00100","01010","10001"),
"Y": ("10001","01010","00100","00100","00100","00100","00100"),
"Z": ("11111","00001","00010","00100","01000","10000","11111"),
"0": ("01110","10001","10011","10101","11001","10001","01110"),
"1": ("00100","01100","00100","00100","00100","00100","01110"),
"2": ("01110","10001","00001","00010","00100","01000","11111"),
"3": ("11110","00001","00001","01110","00001","00001","11110"),
"4": ("00010","00110","01010","10010","11111","00010","00010"),
"5": ("11111","10000","11110","00001","00001","10001","01110"),
"6": ("01110","10000","10000","11110","10001","10001","01110"),
"7": ("11111","00001","00010","00100","01000","01000","01000"),
"8": ("01110","10001","10001","01110","10001","10001","01110"),
"9": ("01110","10001","10001","01111","00001","00001","01110"),
" ": ("00000",)*7,
".": ("00000","00000","00000","00000","00000","01100","01100"),
",": ("00000","00000","00000","00000","01100","00100","01000"),
":": ("00000","01100","01100","00000","01100","01100","00000"),
"-": ("00000","00000","00000","01110","00000","00000","00000"),
"'": ("00100","00100","01000","00000","00000","00000","00000"),
"/": ("00001","00010","00010","00100","01000","01000","10000"),
"+": ("00000","00100","00100","01110","00100","00100","00000"),
"%": ("11001","11010","00010","00100","01000","01011","10011"),
"!": ("00100","00100","00100","00100","00100","00000","00100"),
"?": ("01110","10001","00001","00110","00100","00000","00100"),
"(": ("00010","00100","01000","01000","01000","00100","00010"),
")": ("01000","00100","00010","00010","00010","00100","01000"),
}

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i:i+3] = bytes(c)

def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        base = yy * W
        for xx in range(x, x + w):
            if 0 <= xx < W and 0 <= yy < H:
                i = (base + xx) * 3
                BUF[i:i+3] = bytes(c)

def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, c)

def frame(x, y, w, h, c, t=3):
    rect(x, y, w, t, c); rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c); rect(x + w - t, y, t, h, c)

def text_w(s, scale):
    return len(s) * 6 * scale - scale

def draw_text(x, y, s, scale, c):
    for ch in s.upper():
        g = GLYPHS.get(ch, GLYPHS[" "])
        for r, row in enumerate(g):
            for col, bit in enumerate(row):
                if bit == "1":
                    rect(x + col * scale, y + r * scale, scale, scale, c)
        x += 6 * scale
    return x

def centered(y, s, scale, c):
    draw_text((W - text_w(s, scale)) // 2, y, s, scale, c)

def wrap(s, n):
    out, cur = [], ""
    for word in s.split():
        if len(cur) + len(word) + 1 > n:
            out.append(cur); cur = word
        else:
            cur = (cur + " " + word).strip()
    if cur:
        out.append(cur)
    return out

def para(x, y, s, scale, c, n, gap=10):
    for line in wrap(s, n):
        draw_text(x, y, line, scale, c)
        y += 7 * scale + gap
    return y

def headline(x, y, s, scale, c, n):
    return para(x, y, s, scale, c, n, gap=6)

# ---- canvas ----
rect(0, 0, W, H, PAPER)
frame(14, 14, W - 28, H - 28, NAVY, 4)
frame(24, 24, W - 48, H - 48, LINE, 2)

# ---- masthead ----
rect(34, 34, W - 68, 104, NAVY)
centered(52, "THE WORLD IN ONE DAY", 6, (255, 255, 255))
centered(108, "MONDAY 23 NOVEMBER 2026", 2, SUN)

# ---- lead story: COP31 ----
draw_text(44, 154, "CLIMATE - ANTALYA, TURKIYE", 2, RED)
headline(44, 180, "COP31 TALKS COLLAPSE WITH NO FOSSIL-FUEL DEAL", 4, INK, 21)
para(44, 292, "AFTER 49 HOURS OF OVERTIME, THE UN CLIMATE SUMMIT ENDED "
     "WITHOUT ADOPTING THE ANTALYA PACT. AN EU-LED BLOC OF 130+ "
     "COUNTRIES REJECTED A TEXT THAT SAID NOTHING ABOUT PHASING OUT "
     "COAL, OIL AND GAS.", 2, INK, 46)
# illustration: sun behind factory chimneys and smoke
frame(690, 164, 290, 250, LINE, 2)
rect(692, 166, 286, 246, (214, 228, 238))
circle(900, 216, 34, SUN)
for i, (cx, cy, r) in enumerate([(748, 226, 22), (782, 208, 28), (822, 220, 24)]):
    circle(cx, cy, r, SMOKE)
rect(716, 300, 26, 96, INK); rect(762, 282, 30, 114, INK); rect(816, 306, 22, 90, INK)
rect(700, 396, 270, 14, NAVY)
for wx in range(724, 950, 36):
    rect(wx, 356, 14, 14, SUN)

# ---- middle cards ----
rect(34, 446, 468, 252, CARD); frame(34, 446, 468, 252, LINE, 2)
draw_text(52, 462, "LIBYA - BENGHAZI", 2, BLUE)
headline(52, 488, "ZELENSKYY: UKRAINE SANK RUSSIAN WARSHIP", 3, INK, 24)
para(52, 560, "KYIV SAYS ITS FORCES SANK THE RUSSIAN CORVETTE MERKURY OFF "
     "LIBYA IN A BENGHAZI BLAST.", 2, INK, 34)
rect(52, 660, 432, 22, SEA)
rect(210, 648, 110, 14, INK); rect(238, 636, 52, 12, GREY)
circle(350, 654, 8, RED)

rect(522, 446, 468, 252, CARD); frame(522, 446, 468, 252, LINE, 2)
draw_text(540, 462, "WASHINGTON", 2, RED)
headline(540, 488, "DEMOCRATS WIN BIGGEST HOUSE MAJORITY SINCE 1992", 3, INK, 24)
para(540, 578, "FLIPPING A NORTH CAROLINA SEAT GAVE DEMOCRATS THEIR "
     "LARGEST HOUSE MAJORITY SINCE 1992.", 2, INK, 34)
rect(540, 660, 432, 10, RED)
rect(540, 674, 432, 8, BLUE)

# ---- bottom cards ----
cards = [
    ("TECHNOLOGY", TEAL, "NVIDIA BRINGS BACK JENSEN HUANG AS CEO",
     "THE CHIP GIANT REINSTATED ITS FOUNDER AT ONCE, UNDER PRESSURE FROM PRESIDENT TRUMP."),
    ("SOUTH KOREA", GOLD, "EDUCATION MINISTER QUITS OVER AI CHEATING",
     "THE MINISTER RESIGNED OVER AN AI-ASSISTED CHEATING SCANDAL DAYS BEFORE THE SUNEUNG EXAM."),
    ("CONGO - HEALTH", RED, "FIGHTING BLOCKS EBOLA RESPONSE IN EAST",
     "THE WHO WARNS CONFLICT NEAR THE OUTBREAK ZONE IS DISRUPTING THE EMERGENCY RESPONSE."),
]
cx = 34
for kicker, kc, head, body in cards:
    rect(cx, 714, 304, 196, CARD); frame(cx, 714, 304, 196, LINE, 2)
    draw_text(cx + 16, 728, kicker, 2, kc)
    headline(cx + 16, 754, head, 2, INK, 23)
    para(cx + 16, 812, body, 2, GREY, 23, gap=6)
    cx += 322

# ---- footer briefs ----
rect(34, 926, W - 68, 62, NAVY)
draw_text(48, 940, "ALSO: SOUTH SUDAN ATTACK KILLS 24 - DELTA GLITCH DELAYS 1,000+ FLIGHTS", 2, (255, 255, 255))
draw_text(48, 962, "HOUTHIS CLAIM SAUDI REFINERY HIT - M6.1 QUAKE IN NORTHERN JAPAN", 2, SUN)

def png_bytes():
    raw = b""
    stride = W * 3
    for y in range(H):
        raw += b"\x00" + bytes(BUF[y * stride:(y + 1) * stride])
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(png_bytes())

if __name__ == "__main__":
    main()
