import random

def gen_debug_code():
    # This is shamelessly stonlen from Ignacio Vazquez-Abrams' SO answer here:
    # http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    return ''.join(random.SystemRandom().choice(str.ascii_uppercase + str.digits) for _ in range(10))