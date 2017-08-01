#! /usr/bin/env python3

import argparse
from decimal import Decimal
from collections import namedtuple

class Bet(object):
    description = 'Qualifying bet (no unusual features)'

    def bwbr(self):
        return self.back_stake * (self.back_odds - 1) * (1 - self.back_comm)
    def lwbr(self):
        return -self.back_stake
    def bwlr_ls(self):
        return 1 - self.lay_odds
    def lwlr_ls(self):
        return 1 - self.lay_comm

    def bwlr(self):
        return self.lay_stake * self.bwlr_ls()
    def lwlr(self):
        return self.lay_stake * self.lwlr_ls()

    def optimal_lay_stake(self, round=True):
        """Get the optimal lay stake."""

        lay_stake = ((self.lwbr() - self.bwbr())
                     / (self.bwlr_ls() - self.lwlr_ls()))
        if round:
            lay_stake = lay_stake.quantize(Decimal('0.01'))
        return lay_stake

    @classmethod
    def get_with_optimal_lay_stake(cls, back_stake, back_odds, lay_odds,
                                   back_comm, lay_comm):
        b = cls()
        b.back_stake = back_stake
        b.back_odds = back_odds
        b.lay_odds = lay_odds
        b.back_comm = back_comm
        b.lay_comm = lay_comm

        b.lay_stake = b.optimal_lay_stake()
        return b

    def _asdict(self):
        return dict(
            back_stake=self.back_stake,
            lay_stake=self.lay_stake,
            back_odds=self.back_odds,
            lay_odds=self.lay_odds,
            back_comm=self.back_comm,
            lay_comm=self.lay_comm,

            back_win_back_return = self.bwbr(),
            back_win_lay_return = self.bwlr(),
            back_win_total_return = self.bwbr() + self.bwlr(),

            lay_win_back_return = self.lwbr(),
            lay_win_lay_return = self.lwlr(),
            lay_win_total_return = self.lwbr() + self.lwlr()
        )

    # Tuple (top row, bottom row). Each field is (header name, dict key); None
    # gives a blank space.
    format_fields = (
        [ ('B odds', 'back_odds'),
          ('L odds', 'lay_odds'),
          ('B stk', 'back_stake'),
          ('L stk', 'lay_stake'),
          ('L liab', 'back_win_lay_return'),
          ('B rtrn', 'back_win_back_return'),
          ('L rtrn', 'back_win_lay_return'),
          ('P/L', 'back_win_total_return'),
          ('  (B win)', None) ], # Leading spaces to overflow %8s, looks nicer.
        [ (None, None),
          (None, None),
          (None, None),
          (None, None),
          (None, None),
          (None, 'lay_win_back_return'),
          (None, 'lay_win_lay_return'),
          (None, 'lay_win_total_return'),
          ('  (L win)', None) ]
    )

    @classmethod
    def format_header(cls):
        def format_field(f):
            return '%8s' % (f[0] or '',)
        def format_row(r):
            return ''.join(format_field(f) for f in r)
        return '\n'.join(format_row(r) for r in cls.format_fields)

    def format_row(self):
        d = self._asdict()
        def format_field(f):
            return '%8.2f' % (d[f[1]],) if f[1] else ' ' * 8
        def format_row(r):
            return ''.join(format_field(f) for f in r)
        return '\n'.join(format_row(r) for r in self.format_fields)

class FreeBet(Bet):
    description = 'Free bet (stake not returned; no back liability)'

    def lwbr(self):
        return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lay-commission', '-c', type=Decimal,
                        default=Decimal('2'))
    parser.add_argument('stake', type=Decimal)
    parser.add_argument('odds', nargs='+', type=Decimal)

    bet_type = parser.add_mutually_exclusive_group()
    bet_type.add_argument('--free', '-f', action='store_true')
    bet_type.add_argument('--qual', '-q', action='store_true')

    args = parser.parse_args()

    assert len(args.odds) % 2 == 0
    mid = len(args.odds) // 2

    odds_pairs = zip(args.odds[:mid], args.odds[mid:])

    bet_getter = FreeBet
    if args.qual:
        bet_getter = Bet

    lay_commission = args.lay_commission / 100

    print(bet_getter.description)
    print('%s%% lay commission' % (args.lay_commission,))

    print(bet_getter.format_header())

    for o1, o2 in odds_pairs:
        bet = bet_getter.get_with_optimal_lay_stake(args.stake, o1, o2,
                                                    Decimal('0'),
                                                    lay_commission)
        print(bet.format_row())

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
