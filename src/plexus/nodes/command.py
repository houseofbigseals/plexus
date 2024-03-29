"""

"""
from typing import Any


class Command:
    """
    this is class for storing command and its args
    and also creating their representation image
    for users remote call
    """

    def __init__(self,
                 name: str,
                 annotation: str = None,
                 input_kwargs: dict = None,
                 output_kwargs: dict = None,
                 action: Any = None
                 ):
        """

        """
        self.name = name
        self.action = action
        self.annotation = annotation
        self.input_args = input_kwargs
        self.output_args = output_kwargs  # only for info method
        self.image = {"name": self.name,
                      "annotation": self.annotation,
                      "input_kwargs": self.input_args,
                      "output_kwargs": self.output_args}

    def __str__(self):
        return self.image.__repr__()

    def __repr__(self):
        return self.image.__repr__()

    def __call__(self, **kwargs):
        return self.action(**kwargs)

    def get_image(self):
        return self.image


if __name__ == "__main__":
    c = Command("ramambar", input_kwargs={"x": "int"}, annotation="stupid method")
    print(type(c))
    print(c)
    print(c.__repr__())
