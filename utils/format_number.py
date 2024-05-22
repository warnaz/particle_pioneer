import random


def random_value():
    lower_bound = int(0.00001 * 1e12)
    upper_bound = int(0.01 * 1e17
                      )
    amount = int(random.randint(lower_bound, upper_bound))
    hex_number = hex(amount)
    print("Random amount: ", amount, hex_number)

    return hex_number
