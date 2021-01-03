#!/usr/bin/env python3

def crossword_format(word):
    rows = [[], [], []]

    for letter in word:
        top = bot = '───'
        if letter == '*':
            top = bot = '┄┄┄┄┄┄'
            letter = '╌╌╌╌'
        elif letter == '?':
            letter = ' '
        letter = ' ' + letter + ' '
        rows[0].append(top)
        rows[1].append(letter)
        rows[2].append(bot)

    rows[0] = '┌' + '┬'.join(rows[0]) + '┐'
    rows[1] = '│' + '│'.join(rows[1]) + '│'
    rows[2] = '└' + '┴'.join(rows[2]) + '┘'

    return '\n'.join(rows)

def fullsize_input(prompt):
    from shutil import get_terminal_size
    col, row = get_terminal_size((80, 20))

    ESC = "\x1b"
    CSI = ESC + '['
    up = f'{CSI}A'
    forward = f'{CSI}C'
    none = f'{CSI}0m'
    bold = f'{CSI}1m'

    box = '╭' + '─' * (col - 2) + '╮\n│' + ' ' * (col - 2) + '│\n╰' + '─' * (col - 2) + '╯'
    print(box)
    print(up + up + forward + forward + bold + prompt + none, end='')
    res = input("")
    print('')
    return res

if __name__ == '__main__':
    fullsize_input("Test: ")
