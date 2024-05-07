#!/bin/python3

import json
from pathlib import Path
import sys
from typing import Any, Generator, Iterable, TypeAlias, Sized

LD: TypeAlias = dict[str, "LD"]


def list_and_select_dict() -> Path:
    dict_dir_path = Path("/usr/share/dict")

    available_files = list(dict_dir_path.iterdir())
    print("Select a file from the following list:")
    for c, file in enumerate(available_files):
        print(f"\t{c+1}. {file.name}")

    while True:
        u_in = input()
        try:
            return available_files[int(u_in) - 1]
        except ValueError:
            print("Input must be an int")
        except IndexError:
            print(f"Number must be between {1} and {len(available_files)}")


def load_dict(dict_path: Path) -> set[str]:
    with open(dict_path, "r") as file:
        return set(map(str.strip, file.readlines()))


def get_letters() -> tuple[str, ...]:
    return tuple(i for i in input("Enter character permutations: "))


def get_max_perms(letters: Sized) -> int:
    num_letters = len(letters)
    return num_letters ** (num_letters - 1)


def generate_dict_lookup(words: Iterable[str]) -> LD:
    word_lookup_dict: LD = {}
    for word in words:
        current_wld_entry = word_lookup_dict
        for char in word:
            current_wld_entry = current_wld_entry.setdefault(char, {})
    return word_lookup_dict


def get_others(
    input_iter: Iterable[str],
) -> Generator[tuple[str, tuple[str, ...]], None, None]:
    for index, elem in enumerate(input_iter):
        yield elem, tuple(i for c, i in enumerate(input_iter) if c != index)


def narrow_perms(
    letters: tuple[str, ...], word_lookup_dict: LD, words_set: set[str], pre: str = ""
) -> set[str]:
    available_words: set[str] = set()

    for letter, others in get_others(letters):
        if letter in word_lookup_dict:
            cur_word = pre + letter
            available_words.add(cur_word) if cur_word in words_set else None
            available_words.update(
                narrow_perms(others, word_lookup_dict[letter], words_set, cur_word)
            )
    return available_words


def print_output(max_perms: int, all_perms: set[str], letters: tuple[str, ...]) -> None:
    print(f"found {len(all_perms):,} of {max_perms:,} for ({','.join(letters)})")

    sorted_perms = sorted(all_perms, key=len, reverse=True)
    max_len = len(sorted_perms)
    index = 0

    while index < max_len:
        try:
            count_sol = min(
                int(input("How many solutions would you like to see? (0 to exit) ")),
                1_000,
                max_len - index - 1,
            )

        except ValueError:
            continue

        if count_sol <= 0:
            break

        print("{ ", end="")
        for _ in range(count_sol):
            print(sorted_perms[index], end=" : ")

            index += 1

        print(f"{sorted_perms[index]}", "}")

        index += 1


def main(*args: str, **kwargs: Any) -> int:
    TESTING = "-t" in args
    if TESTING:
        word_list_path = (
            Path(__file__).parent.joinpath("word_list_testing.txt").resolve()
        )
    else:
        word_list_path = list_and_select_dict()

    words_set = load_dict(word_list_path)
    word_lookup_dict = generate_dict_lookup(words_set)

    if TESTING:
        print(json.dumps(word_lookup_dict, indent=4))

    letters = get_letters()
    max_perms = get_max_perms(letters)
    all_perms = narrow_perms(letters, word_lookup_dict, words_set)

    print_output(max_perms, all_perms, letters)

    return 0


if __name__ == "__main__":
    main(*sys.argv)
