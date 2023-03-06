from scoutfish import Scoutfish
import chess.pgn
import io
import os
import pickle
import sys

GAMES_THRESHOLD = 100

print('Opening DB...', flush=True)
p = Scoutfish()
p.setoption('threads', 4)
p.open('elite_db_2022-12.pgn')

fen = sys.argv[1]

#if not os.path.exists(f'games.pkl'):

print(f'Searching for {fen}...', flush=True)
result = p.scout({'sub-fen': fen})

print(f'Found {result["match count"]} games.')

print('Gathering games...', flush=True)
games = p.get_games(result['matches'])
with open(f'games.pkl', 'wb') as f:
    pickle.dump(games, f)

#else:
#   with open(f'games.pkl', 'rb') as f:
#       games = pickle.load(f)

print('Compiling results...', flush=True)

players = {}
for g in games:
    headers = chess.pgn.read_headers(io.StringIO(g['pgn']))
    player = headers['Black']
    if player not in players:
        players[player] = {'perfs': list(), 'actual': 0}
    if headers['Result'] == '1-0':
        players[player]['perfs'].append(int(headers['WhiteElo']) - 400)
    elif headers['Result'] == '0-1':
        players[player]['perfs'].append(int(headers['WhiteElo']) + 400)
    else:
        players[player]['perfs'].append(int(headers['WhiteElo']))
    players[player]['actual'] = (players[player]['actual'] * len(players[player]['perfs']) + int(headers['BlackElo'])) / (len(players[player]['perfs']) + 1)

for player in players:
    players[player]['n'] = len(players[player]['perfs'])
    players[player]['perf'] = int(sum(players[player]['perfs']) / len(players[player]['perfs']))
    players[player]['diff'] = int(players[player]["perf"] - players[player]["actual"])

players = {k:v for (k,v) in players.items() if v['n'] > GAMES_THRESHOLD}

print('username' + (' '*17) + 'n    \tperf\tdiff')
print('-'*50)

for player in sorted(players, key = lambda x: players[x]['perf'], reverse=True)[:20]:
    spaced_username = (player + ' ' * 25)[:25]
    print(f'{spaced_username}{players[player]["n"]}\t{players[player]["perf"]}\t{players[player]["diff"]:+0}')


print()
print('username' + (' '*17) + 'n    \tperf\tdiff')
print('-'*50)
for player in sorted(players, key = lambda x: players[x]['diff'], reverse=True)[:20]:
    spaced_username = (player + ' ' * 25)[:25]
    print(f'{spaced_username}{players[player]["n"]}\t{players[player]["perf"]}\t{players[player]["diff"]:+0}')
