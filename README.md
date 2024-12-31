# id3manager

The ID3 tags manager that you have been missing.

```console
$ pipx install id3manager
```

## Usage

```console
$ id3manager get шопокоду-E01.mp3 > metadata.txt    # get audio metadata
$ nvim metadata.txt                                 # update the metadata
$ id3manager set шопокоду-E01.mp3 < metadata.txt    # set audio metadata
$ id3manager edit шопокоду-E01.mp3                  # to edit metadata interactively using $EDITOR
```

The `metadata.txt` could look like this:

```text
TIT2 = Обробка помилок
TDRC = 2022-11-27
TPE1 = Ігор, Роман
TRCK = 14/14
TALB = Шо по коду?
TCOP = Шо по коду?
TPUB = Шо по коду?
TENC = Шо по коду?
TCON = Podcast
TLAN = ukr
WORS = https://xn--d1allabd6a7a.xn--j1amh
APIC = https://github.com/shopokodu/community/blob/main/assets/logo-square-day.svg

00:00:00 Початок
00:02:00 Помилка на мільярд доларів
00:05:27 Як Meta бореться із NullPointerException в Java
00:09:10 Виключення як спосіб сигналізації помилок
00:14:00 Null-safety в Kotlin
00:18:40 Складність використання виключень в C++. Чому Joel Spolsky і Google їх не люблять
00:28:20 Коди помилок як альтернатива виключенням
00:37:30 Функціональний підхід
00:50:30 Особливості використання Result у Rust
01:00:45 Висновок
```

Alternative metadata formats can be selected by passing `--format` (or `-f`), e.g.:

```console
$ id3manager --format toml get шопокоду-E01.mp3 > metadata.toml    # get audio metadata as TOML
```

Which produces an output like:

```toml
[[TIT2]]
text = "Обробка помилок"

[[TPE1]]
text = "Ігор, Роман"

[[TRCK]]
text = "14/14"

[[TALB]]
text = "Шо по коду?"

[[TDRC]]
text = "2022-11-27"

[[TCON]]
text = "Podcast"

[[TSSE]]
text = "Lavf59.27.100"

[[CHAP]]
text = "Початок"
timestamp = "00:00:00"
```

## Frames

Most commonly used ID3 frames are supported. The complete list of
supported/unsupported frames could be found below.

- [X] APIC
- [x] CHAP
- [x] CTOC
- [x] TBPM
- [x] TBP
- [x] TCMP
- [x] TCP
- [x] TDLY
- [x] TDY
- [x] TLEN
- [x] TLE
- [x] TORY
- [x] TOR
- [x] TSIZ
- [x] TSI
- [x] TYER
- [x] TYE
- [x] MVIN
- [x] MVI
- [x] TPOS
- [x] TPA
- [x] TRCK
- [x] TRK
- [x] TDEN
- [x] TDOR
- [x] TDRC
- [x] TDRL
- [x] TDTG
- [x] TALB
- [x] TAL
- [x] TCOM
- [x] TCM
- [x] TCON
- [x] TCO
- [x] TCOP
- [x] TCR
- [x] TDAT
- [x] TDA
- [x] TDES
- [x] TKWD
- [x] TCAT
- [x] MVNM
- [x] MVN
- [x] GRP1
- [x] GP1
- [x] TENC
- [x] TEN
- [x] TEXT
- [x] TXT
- [x] TFLT
- [x] TFT
- [x] TGID
- [x] TIME
- [x] TIM
- [x] TIT1
- [x] TT1
- [x] TIT2
- [x] TT2
- [x] TIT3
- [x] TT3
- [x] TKEY
- [x] TKE
- [x] TLAN
- [x] TLA
- [x] TMED
- [x] TMT
- [x] TMOO
- [x] TOAL
- [x] TOT
- [x] TOFN
- [x] TOF
- [x] TOLY
- [x] TOL
- [x] TOPE
- [x] TOA
- [x] TOWN
- [x] TPE1
- [x] TP1
- [x] TPE2
- [x] TP2
- [x] TPE3
- [x] TP3
- [x] TPE4
- [x] TP4
- [x] TPRO
- [x] TPUB
- [x] TPB
- [x] TRDA
- [x] TRD
- [x] TRSN
- [x] TRSO
- [x] TSO2
- [x] TS2
- [x] TSOA
- [x] TSA
- [x] TSOC
- [x] TSC
- [x] TSOP
- [x] TSP
- [x] TSOT
- [x] TST
- [x] TSRC
- [x] TRC
- [x] TSSE
- [x] TSS
- [x] TSST
- [x] TXXX
- [x] TXX
- [x] COMM
- [x] COM
- [x] WCOM
- [x] WCM
- [x] WOAR
- [x] WAR
- [x] WCOP
- [x] WCP
- [x] WFED
- [x] WOAF
- [x] WAF
- [x] WOAS
- [x] WAS
- [x] WORS
- [x] WPAY
- [x] WPUB
- [x] WPB
- [x] WXXX
- [x] WXX
- [ ] TIPL
- [ ] IPLS
- [ ] IPL
- [ ] TMCL
- [ ] MCDI
- [ ] MCI
- [ ] ETCO
- [ ] ETC
- [ ] MLLT
- [ ] MLL
- [ ] SYTC
- [ ] STC
- [ ] USLT
- [ ] ULT
- [ ] SYLT
- [ ] SLT
- [ ] RVA2
- [ ] EQU2
- [ ] RVAD
- [ ] RVA
- [ ] RVRB
- [ ] REV
- [ ] PIC
- [ ] PCNT
- [ ] CNT
- [ ] PCST
- [ ] POPM
- [ ] POP
- [ ] GEOB
- [ ] GEO
- [ ] RBUF
- [ ] BUF
- [ ] AENC
- [ ] CRA
- [ ] LINK
- [ ] LNK
- [ ] POSS
- [ ] UFID
- [ ] UFI
- [ ] USER
- [ ] OWNE
- [ ] COMR
- [ ] ENCR
- [ ] GRID
- [ ] PRIV
- [ ] SIGN
- [ ] SEEK
- [ ] ASPI
- [ ] CRM
