
"""

"""


# from typing import Any


class CommandRepr:
    """
    this is class for storing command and its args
    and also creating their representation image
    for users remote call
    """

    def __init__(self, name: str, annotation: str = None, input_kwargs: dict = None, output_kwargs: dict = None):
        """

        """
        self.name = name
        self.annotation = annotation
        self.input_args = input_kwargs
        self.output_args = output_kwargs
        self.image = {"name": self.name, "annotation": self.annotation,
                       "input_args": self.input_args, "output_args": self.output_args}.__repr__()

    def __str__(self):
        return self.image

    def __repr__(self):
        return self.image


if __name__ == "__main__":
    c = CommandRepr("ramambar", input_kwargs={"x": "int"}, annotation="stupid method")
    print(type(c))
    print(c)
    print(c.__repr__())
