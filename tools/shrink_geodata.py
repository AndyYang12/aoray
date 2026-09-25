#!/usr/bin/env python3
"""Subset bundled geodata (geoip.dat / geosite.dat) to the codes the built-in
routing templates actually use. Unknown/unparsable tails are kept verbatim."""
import os
import sys


def rv(b, i):
    shift = val = 0
    while True:
        c = b[i]
        i += 1
        val |= (c & 0x7F) << shift
        if not c & 0x80:
            return val, i
        shift += 7


def wv(v):
    out = bytearray()
    while True:
        c = v & 0x7F
        v >>= 7
        out.append(c | 0x80 if v else c)
        if not v:
            return bytes(out)


def items(buf):
    """yield (code, raw_item_bytes, raw_span) for top-level field-1 records"""
    i = 3 if buf[:3] == b"\n\x00\x12" else 0   # some files start with an empty field-3
    n = len(buf)
    while i < n:
        start = i
        try:
            key, i = rv(buf, i)
        except IndexError:
            yield None, None, buf[start:]
            return
        fno, wt = key >> 3, key & 7
        if wt != 2:
            yield None, None, buf[start:]
            return
        try:
            ln, i = rv(buf, i)
            end = i + ln
            if end > n:
                yield None, None, buf[start:]
                return
            raw = buf[i:end]
        except IndexError:
            yield None, None, buf[start:]
            return
        code = None
        j = 0
        while j < len(raw):                       # find item's field-1 string
            try:
                k2, j = rv(raw, j)
            except IndexError:
                break
            w2 = k2 & 7
            if (k2 >> 3) == 1 and w2 == 2:
                l2, j = rv(raw, j)
                cand = raw[j:j + l2]
                try:
                    code = cand.decode("ascii")
                    if not code.isprintable():
                        code = None
                except UnicodeDecodeError:
                    code = None
                break
            elif w2 == 2:
                l2, j = rv(raw, j)
                j += l2
            elif w2 == 0:
                _, j = rv(raw, j)
            else:
                break
        i = end
        yield code, raw, buf[start:end]


def subset(path, keep, out_path):
    buf = open(path, "rb").read()
    out = bytearray()
    kept = dropped = 0
    tail = b""
    for code, raw, span in items(buf):
        if raw is None:                     # unparsable remainder
            tail = span
            break
        if code is None or code.lower() in keep:
            out += span
            kept += 1
        else:
            dropped += 1
    out += tail
    open(out_path, "wb").write(out)
    print("%-13s %7.2f MB -> %6.2f MB  kept %d codes, dropped %d (+%d B trailer)"
          % (os.path.basename(path), len(buf) / 1048576.0, len(out) / 1048576.0,
             kept, dropped, len(tail)))
    return len(buf) - len(out)


if __name__ == "__main__":
    d = sys.argv[1]
    saved = 0
    saved += subset(os.path.join(d, "geoip.dat"), {"cn", "private"}, os.path.join(d, "geoip.dat.n"))
    saved += subset(os.path.join(d, "geosite.dat"),
                    {"cn", "private", "category-ads", "category-ads-all"},
                    os.path.join(d, "geosite.dat.n"))
    os.replace(os.path.join(d, "geoip.dat.n"), os.path.join(d, "geoip.dat"))
    os.replace(os.path.join(d, "geosite.dat.n"), os.path.join(d, "geosite.dat"))
    print("raw saved: %.2f MB" % (saved / 1048576.0))
