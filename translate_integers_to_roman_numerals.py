import random
from rom import rom_generate
import sys
import getopt
from typing import Final, Optional

map_value_to_roman: Final[dict[int, str]] = {
    1 : "I",
    5: "V",
    10: "X",
    50: "L",
    100: "C",
    500: "D",
    1000: "M",
}

def breakupNumber(number_: int) -> dict[int, int]:
    """We create the same building blocks from the number that the roman version uses to express cardinality"""
    
    remnant_1000 = number_ % 1000
    remnant_500 = remnant_1000 % 500
    remnant_100 = remnant_500 % 100
    remnant_50 = remnant_100 % 50
    remnant_10 = remnant_50 % 10
    
    return {
        1: number_ % 5,
        5: remnant_10 // 5,
        10: remnant_50 // 10,
        50: remnant_100 // 50,
        100: remnant_500 // 100,
        500: remnant_1000 // 500,
        1000: number_ // 1000,
    }

def representCountOfValue(value_: int, count_: int) -> str:
    """
    If the count of this value in the input number is 4 or 9, return the letter corresponding to this value
    followed by the letter that belongs to the amount that is
    5 times this value if this value's first digit is 1 and 2 times otherwise (when it is 5).
    In the standard case, return the value as many times as the value of $count_
    """
    
    if count_ == 4:
        return f"{map_value_to_roman[value_]}" \
               f"{map_value_to_roman[value_ * (5 if str(value_)[0] == '1' else 2)]}"
    
    else:
        return map_value_to_roman[value_] * count_

def translateCountsToRoman(counts_: dict[int, int]) -> str:
    return ''.join(representCountOfValue(key_, counts_[key_]) for key_ in list(counts_)[::-1])

# Compare every third possible value to its library-generated translation equivalent
tests: list[dict[str, str]] = [
    {
        "generated": translateCountsToRoman(breakupNumber(number_)),
        "via library": rom_generate(number_),
    } for number_ in range(0, 3999, 3)
]

# Only launch the program if it works correctly
for test_ in tests:
    assert test_, f"Failed asserting that {test_['generated']} equals {test_['via library']}"
print("tests passed")

user_input = getopt.getopt(sys.argv[1:], "")
number: Optional[int] = None

try:
    number = int(user_input[1][0])
    assert 0 <= number < 4000, "Input can only be in range of 0, 3999 (inclusive)"
except (TypeError, IndexError):
    print("Did not specify number, generating random")

number = number or random.randint(0, 3999)
print(f"Roman equivalent of {number} is {translateCountsToRoman(breakupNumber(number))}")