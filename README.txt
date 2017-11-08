A command-line tool for calculating matched bets.

Has some features that I haven't found in any online calculators. But it's kind
of awkward to use. I don't currently intend to keep developing this in its
current form.

Back and lay odds are entered in the order "B1 B2 B3 ... L1 L2 L3 ...". That is,
the back odds for several bets, and then the corresponding lay odds for those
bets. That's because I optimised it for a particular use-case: look at some bets
at a bookmaker in one browser tab, type in the back odds, then switch to another
browser tab and enter the corresponding lay odds from an exchange. It's useful
when that's how you're doing things, but inconvenient otherwise.

```
usage: matched-bets.py [-h] [--lay-commission LCOMM] [--free | --qual]
                       stake odds [odds ...]

positional arguments:
  stake                 Stake on the back side
  odds                  Back and lay odds on pairs of bets, in order "B1 B2 B3
                        ... L1 L2 L3 ..."

optional arguments:
  -h, --help            show this help message and exit
  --lay-commission LCOMM, -c LCOMM
                        Commission on the lay side, in %. Default: 2
  --free, -f            Free bet (default)
  --qual, -q            Qualifying bet
```

Example usage:

```
$ ./matched-bets.py -c5 10 7.5 5.2 17 8.2 6.4 21
Free bet (stake not returned; no back liability)
5% lay commission
  B odds  L odds   B stk   L stk  L liab  B rtrn  L rtrn     P/L  (B win)
                                                                  (L win)
    7.50    8.20   10.00    7.98  -57.46   65.00  -57.46    7.54
                                            0.00    7.58    7.58
    5.20    6.40   10.00    6.61  -35.69   42.00  -35.69    6.31
                                            0.00    6.28    6.28
   17.00   21.00   10.00    7.64 -152.80  160.00 -152.80    7.20
                                            0.00    7.26    7.26
--- To beat with no spread ---
    4.74    4.74   10.00    7.98  -29.86   37.42  -29.86    7.56
                                            0.00    7.58    7.58
```
