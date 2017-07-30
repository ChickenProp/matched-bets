#! /usr/bin/env python3

import argparse
from decimal import Decimal
from collections import namedtuple

BetReturn = namedtuple('BetReturn',
                       '''back_stake lay_stake
                          back_odds lay_odds
                          back_comm lay_comm
                          back_win_back_return back_win_lay_return
                          back_win_total_return
                          lay_win_back_return lay_win_lay_return
                          lay_win_total_return
                       '''.split())

br_header = """\
  B odds  L odds   B stk   L stk  L liab  B rtrn  L rtrn     P/L  (B win)
                                                                  (L win)
"""

br_top_row = '''back_odds lay_odds back_stake lay_stake back_win_lay_return
                back_win_back_return back_win_lay_return
                back_win_total_return'''.split()
br_bottom_row = '''lay_win_back_return lay_win_lay_return
                   lay_win_total_return'''.split()

br_top_format = ''.join('{%s:>8.2f}' % (k,) for k in br_top_row)
br_bottom_format = ''.join('{%s:>8.2f}' % (k,) for k in br_bottom_row)
br_format = '%s\n%s%s' % (br_top_format, ' ' * 40, br_bottom_format)

br_row = """\
{back_odds:>8.2f}{lay_odds:>8.2f}
{back_odds:>8.2f}{lay_odds:>8.2f}
{back_odds:>8.2f}{lay_odds:>8.2f}
{back_odds:>8.2f}{lay_odds:>8.2f}

"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lay-commission', '-c', type=Decimal,
                        default=Decimal('0.02'))
    parser.add_argument('stake', type=Decimal)
    parser.add_argument('odds', nargs='+', type=Decimal)

    bet_type = parser.add_mutually_exclusive_group()
    bet_type.add_argument('--free', '-f', action='store_true')
    bet_type.add_argument('--qual', '-q', action='store_true')

    args = parser.parse_args()

    assert len(args.odds) % 2 == 0
    mid = len(args.odds) // 2

    odds_pairs = zip(args.odds[:mid], args.odds[mid:])

    bet_getter = get_free_bet
    if args.qual:
        bet_getter = get_qualifying_bet

    print(br_header)
    for o1, o2 in odds_pairs:
        fb = bet_getter(args.stake, o1, o2, Decimal('0'), args.lay_commission)
        print(br_format.format(**fb._asdict()))

def get_free_bet(back_stake, back_odds, lay_odds, back_comm, lay_comm,
                 round_lay_stake=True):
    bwbr = back_stake * (back_odds - 1) * (1 - back_comm)
    lwbr = 0
    bwlr_ls = 1 - lay_odds
    lwlr_ls = 1 - lay_comm

    lay_stake = optimal_lay_stake(bwbr, bwlr_ls, lwbr, lwlr_ls, round_lay_stake)

    bwlr = lay_stake * bwlr_ls
    lwlr = lay_stake * lwlr_ls

    return BetReturn(
        back_stake=back_stake,
        lay_stake=lay_stake,
        back_odds=back_odds,
        lay_odds=lay_odds,
        back_comm=back_comm,
        lay_comm=lay_comm,

        back_win_back_return = bwbr,
        back_win_lay_return = bwlr,
        back_win_total_return = bwbr + bwlr,

        lay_win_back_return = lwbr,
        lay_win_lay_return = lwlr,
        lay_win_total_return = lwbr + lwlr
    )

def get_qualifying_bet(back_stake, back_odds, lay_odds, back_comm, lay_comm,
                       round_lay_stake=True):
    bwbr = back_stake * (back_odds - 1) * (1 - back_comm)
    lwbr = -back_stake
    bwlr_ls = 1 - lay_odds
    lwlr_ls = 1 - lay_comm

    lay_stake = optimal_lay_stake(bwbr, bwlr_ls, lwbr, lwlr_ls, round_lay_stake)

    bwlr = lay_stake * bwlr_ls
    lwlr = lay_stake * lwlr_ls

    return BetReturn(
        back_stake=back_stake,
        lay_stake=lay_stake,
        back_odds=back_odds,
        lay_odds=lay_odds,
        back_comm=back_comm,
        lay_comm=lay_comm,

        back_win_back_return = bwbr,
        back_win_lay_return = bwlr,
        back_win_total_return = bwbr + bwlr,

        lay_win_back_return = lwbr,
        lay_win_lay_return = lwlr,
        lay_win_total_return = lwbr + lwlr
    )

def optimal_lay_stake(bwbr, bwlr_ls, lwbr, lwlr_ls, round=True):
    """Get the optimal lay stake.

    bwbr: back-win-back-return
    bwlr_ls: back-win-lay-return / lay_stake
    lwbr: lay-win-back-return
    lwlr_ls: lay-win-lay-return / lay_stake"""

    lay_stake =  (lwbr - bwbr) / (bwlr_ls - lwlr_ls)
    if round:
        lay_stake = lay_stake.quantize(Decimal('0.01'))
    return lay_stake

if __name__ == '__main__':
    main()

# arithmetic:

# free bet
# if back wins:
#     on back: back_stake * (back_odds - 1) * (1 - back_comm)
#     on lay: - lay_stake * (lay_odds - 1)
# if lay wins:
#     on back: 0
#     on lay: lay_stake * (1 - lay_comm)

# (bs * bo-1 * 1-bc) - (ls * lo-1) = ls * 1-lc
# (bs * bo-1 * 1-bc) = ls * (lo-1 + 1-lc)
# ls = (bs * bo-1 * 1-bc) / (lo-1 + 1-lc)

# qualifier
# if back wins:
#     on back: back_stake * (back_odds - 1) * (1 - back_comm)
#     on lay: - lay_stake * (lay_odds - 1)
# if lay wins:
#     on back: - back_stake
#     on lay: lay_stake * (1 - lay_comm)

# (bs * bo-1 * 1-bc) - (ls * lo-1) = ls * 1-lc - bs
# (bs * bo-1 * 1-bc + bs) = ls * (lo-1 + 1-lc)
# ls = (bs * bo-1 * 1-bc + bs) / (lo-1 + 1-lc)

# in general
#   bwbr + ls*(bwlr/ls) = lwbr + ls*(lwlr/ls)
#   ls(bwlr/ls - lwlr/ls) = lwbr - bwbr
#   ls = (lwbr - bwbr) / (bwlr/ls - lwlr/ls)
# so if bwlr/ls and lwlr/ls are known, we can get ls
