from byubit import Bit


@Bit.worlds("boxes")
def stack_boxes(bit):
    while bit.front_clear():
        bit.paint('red')
        bit.move()
    bit.paint('red')

    bit.left()

    while bit.front_clear():
        bit.move()

    bit.left()

    while bit.front_clear():
        bit.move()

    bit.left()
    bit.left()


if __name__ == '__main__':
    stack_boxes(Bit.new_bit)