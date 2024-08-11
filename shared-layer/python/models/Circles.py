"""
Initializes a new instance of the CircleLines class.

Args:
    circle_id (str): The ID of the circle.
    name (str): The name of the circle.
    quote (str, optional): The quote associated with the circle. Defaults to "Write as I may".
    display_picture (str, optional): The display picture associated with the circle. Defaults to "abcdef123".
"""


class Circle:
    def __init__(self, circle_id, name, quote="Write as I may", display_picture="abcdef123"):
        self.circle_id = circle_id
        self.name = name
        self.quote = quote
        self.display_picture = display_picture
