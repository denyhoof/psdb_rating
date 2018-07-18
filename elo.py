import argparse
import os
import json

def LoadJsonFromFile(filename):
    with open(filename, 'r') as f:
        return json.load(f, strict=False)


def DumpJsonToFile(obj, filename):
    with open(filename, 'w') as f:
        json.dump(obj, f, indent=4, sort_keys=True, ensure_ascii=False)


class Contest:
    def __init__(self, contest_info_path):
        self.__contestants = []
        with open(contest_info_path, 'r') as f:
            for line in f:
                self.__contestants.append(line.replace('\n', ''))

    @property
    def contestants(self):
        return self.__contestants


class RatingElo:
    def __init__(self, init_rating=None):
        self.__rating = {} if init_rating is None else init_rating
        self.__log = []

    def __GetEloWinProbability(self, ra, rb):
        return 1.0 / (1.0 + 10.0 ** ((rb - ra) / 400.0))

    def __GetSeed(self, head_contestant, contestants_info):
        if contestants_info[head_contestant]['new']:
            return len(contestants_info) / 2
        else:
            seed = 0
            for contestant in contestants_info:
                if contestant != head_contestant:
                    seed += self.__GetEloWinProbability(
                        contestants_info[head_contestant]['before'],
                        contestants_info[contestant]['before']
                    )
            return seed

    def AddContest(self, contest):
        contestants_info = {}
        contestants_len = len(contest.contestants)
        for place, contestant in enumerate(contest.contestants):
            contestants_info[contestant] = {}
            if contestant in self.__rating:
                contestants_info[contestant]['before'] = self.__rating[contestant]
                contestants_info[contestant]['new'] = False
                contestants_info[contestant]['points'] = contestants_len - place - 1
            else:
                contestants_info[contestant]['before'] = 1500
                contestants_info[contestant]['new'] = True
                contestants_info[contestant]['points'] = contestants_len - place - 1

        for contestant in contest.contestants:
            contestants_info[contestant]['seed'] = self.__GetSeed(contestant, contestants_info)

        expected_rank = list(contestants_info.keys())
        expected_rank.sort(key=lambda x: -contestants_info[x]['before'])

        print('Expected:', expected_rank)
        print('Result:', contest.contestants)
        total_delta = 0
        for contestant in contest.contestants:
            contestants_info[contestant]['after'] = contestants_info[contestant]['before'] + int(35 * 10 * (contestants_info[contestant]['points'] - contestants_info[contestant]['seed']) / contestants_len)
            total_delta += int(30 * 10 * (contestants_info[contestant]['points'] - contestants_info[contestant]['seed']) / contestants_len)
        for contestant in contest.contestants:
            contestants_info[contestant]['after'] -= int(total_delta / len(contest.contestants))
        print('Changes:', [
            (contestant, contestants_info[contestant]['after'] - contestants_info[contestant]['before'])
            for contestant in contestants_info]
        )
        for contestant in contestants_info:
            self.__rating[contestant] = contestants_info[contestant]['after']

        self.__log.append(contestants_info)

    @property
    def rating(self):
        return self.__rating

    @property
    def log(self):
        return self.__log


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        '--result_path',
        type=str,
        help='JSON file containing result rating'
    )
    parser.add_argument(
        '--contests_dir',
        type=str,
    )
    parser.add_argument(
        '--logs',
        type=str,
    )
    args = parser.parse_args()

    rating = RatingElo()
    with open(os.path.join(args.contests_dir, 'info'), 'r') as f:
        for line in f:
            line = line.replace('\n', '')
            contest = Contest(os.path.join(args.contests_dir, line))
            rating.AddContest(contest)
    DumpJsonToFile(rating.rating, args.result_path)
    DumpJsonToFile(rating.log, args.logs)
