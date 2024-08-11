# Model class representing one tanzent line


class PrivateLines:
    """
    contains the info about the text which is private, -1 denotes it is not shared with anyone
    """

    def __init__(self, from_offset: int, length:int):
        self.userIds = []
        self.from_offset = from_offset
        self.length = length

    def add_user(self, user_id: str):
        if user_id in self.userIds:
            return
        self.userIds.append(user_id)

    def remove_user(self, user_id: str):
        if user_id not in self.userIds:
            return
        self.userIds.remove(user_id)


class LineProperty:
    """
        Contains the properties of one line
    """

    def __init__(self, line_id, content, hide_on_read, delete_on_read=False, read_by=[],
                 contains_private_lines=False):
        self.line_id = line_id
        self.content = content
        self.hide_on_read = hide_on_read
        # Not implemented, setting the property defaults
        self.read_by = []
        self.delete_on_read = delete_on_read
        self.contains_private_lines: bool = contains_private_lines


class Line:
    """
     Model class representing line entity, contains all the info including the property
    """

    def __init__(self, title, user_id, line_id, created_at, visibility, short_text, shared_to: list = []):
        self.user_id = user_id
        self.title = title
        self.line_id = line_id
        self.created_at = created_at
        self.visibility = visibility
        self.short_text = short_text
        self.shared_to = shared_to
        self.properties = None

    def set_properties(self, properties: LineProperty):
        self.properties = properties

    def get_properties(self) -> LineProperty:
        return self.properties
