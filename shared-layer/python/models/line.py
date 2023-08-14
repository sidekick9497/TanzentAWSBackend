# Model class representing one tanzent line


class PrivateLines:
    """
    contains the info about the text which is private, -1 denotes it is not shared with anyone
    """

    def __init__(self, from_offset, length):
        self.userIds = [-1]
        self.from_offset = from_offset
        self.length = length

    def add_user(self, user_id):
        if user_id in self.userIds:
            return
        self.userIds.append(user_id)

    def remove_user(self, user_id):
        if user_id not in self.userIds:
            return
        self.userIds.remove(user_id)


class LineProperty:
    """
        Contains the properties of one line
    """

    def __init__(self, line_id, private_lines: PrivateLines, content, hide_on_read):
        self.line_id = line_id
        self.private_lines: PrivateLines = private_lines
        self.content = content
        self.hide_on_read = hide_on_read
        # Not implemented, setting the property defaults
        self.read_by = []
        self.delete_on_read = False


class Line:
    """
     Model class representing line entity, contains all the info including the property
    """

    def __init__(self, title, user_id, line_id, created_at, visibility, short_text):
        self._properties = None
        self.user_id = user_id
        self.title = title
        self.line_id = line_id
        self.created_at = created_at
        self.visibility = visibility
        self.short_text = short_text
        self.properties = None

    def set_properties(self, properties: LineProperty):
        self._properties = properties

    def get_properties(self) -> LineProperty:
        return self.properties