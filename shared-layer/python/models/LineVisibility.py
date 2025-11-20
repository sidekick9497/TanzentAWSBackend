
class LineVisibility:
    public = "LineVisibility.public"
    private = "LineVisibility.private"
    friends = "LineVisibility.friends"

def isPrivate(visibility):
    return visibility == LineVisibility.private