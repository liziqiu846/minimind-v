# Phase 4 conditional message v1

The public protocol is `complexity_protocol.json`; this note is explanatory and
is not a decoder input.

One message begins with a byte whose high nibble is the fixed candidate ID and
whose low nibble is paid zero framing. For each block declared by that
candidate, in declared order, it then stores a little-endian IEEE-754 float32
scale, a little-endian uint32 compressed length, and exactly that many bytes of
canonical zlib-9 data. The decompressed bytes are MSB-first packed three-bit
codes for levels -3 through 3. The final 32 bytes are SHA256 over everything
before the digest.

The paid length is four candidate bits, four alignment bits, 32 length bits and
32 scale bits per block, 256 integrity bits, and every compressed payload bit.
No MMS2 structure metadata is part of this message.

The protocol was designed after the frozen M2/M3 training runs. Their converted
messages support post-hoc code-length comparison only and do not replace their
original training certificates. M4 models trained after this protocol freeze
may use the conditional length as training complexity. A future selection over
all fifteen frozen models on a wholly new independent confirmation set is a
separate external candidate-selection guarantee with a four-bit identity cost.

