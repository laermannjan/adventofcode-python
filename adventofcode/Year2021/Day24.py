"""
--- Day 24: Arithmetic Logic Unit ---

Magic smoke starts leaking from the submarine's arithmetic logic unit (ALU). Without the ability to perform basic arithmetic and logic functions, the submarine can't produce cool patterns with its Christmas lights!
It also can't navigate. Or run the oxygen system.
Don't worry, though - you probably have enough oxygen left to give you enough time to build a new ALU.
The ALU is a four-dimensional processing unit: it has integer variables w, x, y, and z. These variables all start with the value 0. The ALU also supports six instructions:

    inp a - Read an input value and write it to variable a.
    add a b - Add the value of a to the value of b, then store the result in variable a.
    mul a b - Multiply the value of a by the value of b, then store the result in variable a.
    div a b - Divide the value of a by the value of b, truncate the result to an integer, then store the result in variable a. (Here, "truncate" means to round the value toward zero.)
    mod a b - Divide the value of a by the value of b, then store the remainder in variable a. (This is also called the modulo operation.)
    eql a b - If the value of a and b are equal, then store the value 1 in variable a. Otherwise, store the value 0 in variable a.

In all of these instructions, a and b are placeholders; a will always be the variable where the result of the operation is stored (one of w, x, y, or z), while b can be either a variable or a number. Numbers can be positive or negative, but will always be integers.
The ALU has no jump instructions; in an ALU program, every instruction is run exactly once in order from top to bottom. The program halts after the last instruction has finished executing.
(Program authors should be especially cautious; attempting to execute div with b=0 or attempting to execute mod with a<0 or b<=0 will cause the program to crash and might even damage the ALU. These operations are never intended in any serious ALU program.)
For example, here is an ALU program which takes an input number, negates it, and stores it in x:

inp x
mul x -1

Here is an ALU program which takes two input numbers, then sets z to 1 if the second input number is three times larger than the first input number, or sets z to 0 otherwise:

inp z
inp x
mul z 3
eql z x

Here is an ALU program which takes a non-negative integer as input, converts it into binary, and stores the lowest (1's) bit in z, the second-lowest (2's) bit in y, the third-lowest (4's) bit in x, and the fourth-lowest (8's) bit in w:

inp w
add z w
mod z 2
div w 2
add y w
mod y 2
div w 2
add x w
mod x 2
div w 2
mod w 2

Once you have built a replacement ALU, you can install it in the submarine, which will immediately resume what it was doing when the ALU failed: validating the submarine's model number. To do this, the ALU will run the MOdel Number Automatic Detector program (MONAD, your puzzle input).
Submarine model numbers are always fourteen-digit numbers consisting only of digits 1 through 9. The digit 0 cannot appear in a model number.
When MONAD checks a hypothetical fourteen-digit model number, it uses fourteen separate inp instructions, each expecting a single digit of the model number in order of most to least significant. (So, to check the model number 13579246899999, you would give 1 to the first inp instruction, 3 to the second inp instruction, 5 to the third inp instruction, and so on.) This means that when operating MONAD, each input instruction should only ever be given an integer value of at least 1 and at most 9.
Then, after MONAD has finished running all of its instructions, it will indicate that the model number was valid by leaving a 0 in variable z. However, if the model number was invalid, it will leave some other non-zero value in z.
MONAD imposes additional, mysterious restrictions on model numbers, and legend says the last copy of the MONAD documentation was eaten by a tanuki. You'll need to figure out what MONAD does some other way.
To enable as many submarine features as possible, find the largest valid fourteen-digit model number that contains no 0 digits. What is the largest model number accepted by MONAD?

--- Part Two ---

As the submarine starts booting up things like the Retro Encabulator, you realize that maybe you don't need all these submarine features after all.
What is the smallest model number accepted by MONAD?

"""


class Monad:
    """
    There are 14 inputs w and thus 14 operation sets, each consisting of 18 instructions.
    We observe that these operations only differ at a few places:

    - instruction #4 is either: `div z 1` or `div z 26`  <-- we call this "kind"
    - instruction #5 adds a variable integer N to x: `add x N`
    - instruction #15 adds a variable integer M to y: `add y M`

    We observe further, that operations that share instruction #4 also share all other instructions, except the values `N` and `M`.

    Looking these instructions we find:

    ### kind == 1 ###
    x = ((last_z % 26 + N) == w) == 0  -->  0 if [last_z % 26 == w - N] else 1
    y = 25 * x + 1  -->  1 if [last_z % 26 == w - N] else 26
    z = last_z * y
    y = (w + M) * x  -->  0 if [last_z % 26 == w - N] else (w + M)
    z = z + y

    Combined this means:
    [1] z = last_z if [last_z % 26 == w - N] else (26 * last_z + w + M)

    ### kind == 26 ###
    x = last_z % 26
    z = last_z // 26
    x = ((x + N) == w) == 0 --> 0 if [last_z % 26 == w - N] else 1
    y = 25 * x + 1  -->  1 if [last_z % 26 == w - N] else 26
    z = z * y
    y = (w + M) * x  -->  0 if [last_z % 26 == w - N] else (w + M)
    z = z + y

    Combined:
    [26] z = (last_z // 26) if [last_z % 26 == w - N] else (26 * (last_z // 26) + w + M)


    These modulo operations are always `z % 26`, additionally we only ever multiply z with `z * 26` (except when we multiply with 1)
    This means we probably can represent z as a base26 number (or a letter, as the english alphabet has 26 letters).

    Inspecting operation kind==1, we see that it either doesn't change z, or it "base26-left-shifts" (as in bit-left-shift) it one place to the left and adds w + N [z <<_26 1 + (w + N)]

    Similarly operation kind==26, we see that it either "base26-right-shifts" z one place [z//26 => z >>_26 1] (thereby losing the last base26-letter)
    or it replaces the last letter with w + M --> first base26-right-shift (losing the last letter), then base26-left-shift and adding w + M.


    Observing the relevant (stdout from `from_file()`):
    inst#   kind    N       M
     1:      1       11       1
     2:      1       11      11
     3:      1       14       1
     4:      1       11      11
     5:     26       -8       2
     6:     26       -5       9
     7:      1       11       7
     8:     26      -13      11
     9:      1       12       6
    10:     26       -1      15
    11:      1       14       7
    12:     26       -5       1
    13:     26       -4       8
    14:     26       -8       6

    We find that for all kind==1, N > 9. As 1 <= w <= 9 holds, we know that for [1] only the "else" clause will ever be executed.
    That means that each kind==1 operation appends a base26-letter to z.

    As a valid valid number passed to the MONAD will produce z == 0, there are only two options:
    - The remaining kind==26 instructions remove all base26-letters again and "base26-right-shift" z to 0  (all instructions follow the "if" clause").
    - There are some kind==26 instructions that follow the "else" clause, but replace the value with w+N=0.

    With these observations we start:

    z0 = 0
    z1 = 26 * z0 + w1 + 1  = w1 + 1
    z2 = 26 * z1 + w2 + 11 = 26(w1 + 1) + w2 + 11
    z3 = 26 * z2 + w3 + 1  = 26^2(w1 + 1) + 26(w2 + 11) + w3 + 1
    z4 = 26 * z3 + w4 + 11 = 26^3(w1 + 1) + 26^2(w2 + 11) + 26(w3 + 1) + w4 + 11

    --- z5 ---
    # from [26]
    if z4 % 26 == w5 - N:
        # z4 % 26 gets the last "base26-letter" of z, therefore, z4 % 26 = w4 + 11
        w4 + 11 == w5 + 8
        w4 = w5 - 3
        z5 = z3

    # otherwise must replace letter with 0
    else:
        w5 + M == 0
        w5 + 2 == 0
        w5 = -2 --> impossible, must be in range 1..9

    ---z6 ---
    # from [26]
    if z5 % 26 == w6 - N:
        # since z5 == z3
        w3 + 1 == w6 + 5
        w3 = w6 + 4
        z6 = z2

    # otherwise must replace letter with 0
    else:
        w6 + M == 0
        w6 + 9 == 0
        w6 = -9  --> impossible (w must be in 1..9)

    ### At this point I noticed that for all kind==26 instructions, M is positive.
    ### As w must be in range 1..9, w + M == 0 never holds, as w would have to be negative.
    ### Thus we can skip the else "clause" for all kind==26 parts

    z7 = 26 * z2 + w7 + 7 = 26^2(w1 + 1) + 26(w2 + 11) + w7 + 7

    --- z8 ---
    since z7 % 26 == w8 - N:
        w7 + 7 == w8 + 13
        w7 = w8 + 6
        z8 = z2

    z9 = 26 * z2 + w9 + 6 = 26^2(w1 + 1) + 26(w2 + 11) + w9 + 6

    --- z10 ---
    since z9 % 26 == w10 - N:
        w9 + 6 == w10 + 1
        w9 = w10 - 5
        z10 = z2

    z11 = 26 * z2 + w11 + 7 = 26^2(w1 + 1) + 26(w2 + 11) + w11 + 7

    --- z12 ---
    since z11 % 26 == w12 - N:
        w11 + 7 == w12 + 5
        w11 = w12 - 2
        z12 = z2

    --- z13 ---
    since z12 % 26 == w13 - N:
        w2 + 11 == w13 + 4
        w2 = w13 - 7
        z13 = z1

    --- z14 ---
    since z13 % 26 == w14 - N:
        w1 + 1 == w14 + 8
        w1 = w14 + 7
        z14 = 0


    So in conclusion, we got the following constraints on our model number:
    - w4 = w5 - 3
    - w3 = w6 + 4
    - w7 = w8 + 6
    - w9 = w10 - 5
    - w11 = w12 - 2
    - w2 = w13 - 7
    - w1 = w14 + 7
    """

    def __init__(self, relevant_instructions_params: list[tuple[int, int, int]]):
        self.instructions = relevant_instructions_params

    def _find_model_number_largest(self):
        """
        To find the largest possible model number, we want a number that has the maximally possible w at each position.
        As they are pair-wise constraint, we want w1, w2, ... to be as unconstraint as possible, to set them maximally.
        So with our constraints in order:

        - w1 = w14 + 7
        - w2 = w13 - 7
        - w3 = w6 + 4
        - w4 = w5 - 3
        - w7 = w8 + 6
        - w9 = w10 - 5
        - w11 = w12 - 2

        With the fact, that all w must be in range 1..9, we derive:
        """
        w1, w14 = 9, 2
        w2, w13 = 2, 9
        w3, w6 = 9, 5
        w4, w5 = 6, 9
        w7, w8 = 9, 3
        w9, w10 = 4, 9
        w11, w12 = 7, 9
        return int(f"{w1}{w2}{w3}{w4}{w5}{w6}{w7}{w8}{w9}{w10}{w11}{w12}{w13}{w14}")

    def _find_model_number_smallest(self):
        """
        To find the smallest possible model number, we want a number that has the minimally possible w at each position.
        As they are pair-wise constraint, we want w1, w2, ... to be as unconstraint as possible, to set them minimall.
        So with our constraints in order:

        - w1 = w14 + 7
        - w2 = w13 - 7
        - w3 = w6 + 4
        - w4 = w5 - 3
        - w7 = w8 + 6
        - w9 = w10 - 5
        - w11 = w12 - 2

        With the fact, that all w must be in range 1..9, we derive:
        """

        w1, w14 = 8, 1
        w2, w13 = 1, 8
        w3, w6 = 5, 1
        w4, w5 = 1, 4
        w7, w8 = 7, 1
        w9, w10 = 1, 6
        w11, w12 = 1, 3
        return int(f"{w1}{w2}{w3}{w4}{w5}{w6}{w7}{w8}{w9}{w10}{w11}{w12}{w13}{w14}")

    def find_model_number(self, typ: str) -> int:
        model_number = [0] * len(self.instructions)
        stack = []
        for this_op, (kind, n, m) in enumerate(self.instructions):
            if kind == 1:
                # base26-left-shift and append letter (w + M)
                stack.append((this_op, m))
            else:
                # last as in last of the base26-letters of z
                last_op, last_m = stack.pop()

                # from last_z % 26 == w - N
                # --> last_w + last_m == w - N
                # --> w - last_w = last_m - N
                delta = last_m + n

                # examples (from pen&paper solution):
                # w7 = w8 + 6 -> w8 - w7 = -6
                # w9 = w10 - 5 -> w10 - w9 = 5
                # model_number[op_number] := w
                # model_number[last_op_number] := last_w
                if typ == "largest":
                    model_number[this_op] = 9 if delta > 0 else 9 - abs(delta)
                    model_number[last_op] = 9 - abs(delta) if delta > 0 else 9
                elif typ == "smallest":
                    model_number[this_op] = 1 + abs(delta) if delta > 0 else 1
                    model_number[last_op] = 1 if delta > 0 else 1 + abs(delta)

        model_number = int("".join(map(str, model_number)))
        if typ == "largest":
            pen_paper = self._find_model_number_largest()
        elif typ == "smallest":
            pen_paper = self._find_model_number_smallest()
        else:
            raise ValueError("Can only find smallest and largest model number")
        assert model_number == pen_paper, f"{model_number=} != {pen_paper=}"
        return model_number

    @classmethod
    def from_file(cls, filename: str) -> "Monad":
        with open(filename, "r") as f:
            data = f.read().splitlines()
        instructions = list(map(lambda x: x.split(" ")[-1], data))

        kinds = map(int, instructions[4::18])
        Ns = map(int, instructions[5::18])
        Ms = map(int, instructions[15::18])

        relevant_instructions_params = list(zip(kinds, Ns, Ms))
        print(f"Creating {cls.__name__} from relevant instruction parameters:")
        print("op#\tkind\tN\tM")
        for op, (kind, N, M) in enumerate(relevant_instructions_params):
            print(f"{op+1:2}:\t{kind:2}\t{N:3}\t{M:3}")
        return cls(relevant_instructions_params)


def day24a(filename: str):
    monad = Monad.from_file(filename)
    return monad.find_model_number("largest")


def day24b(filename: str):

    monad = Monad.from_file(filename)
    return monad.find_model_number("smallest")
