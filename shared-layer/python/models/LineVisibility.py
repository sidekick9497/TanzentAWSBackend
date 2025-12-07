class LineVisibility:
    public = "LineVisibility.public"
    private = "LineVisibility.private"
    friends = "LineVisibility.friends"

# Clean names for internal counters and Dynamo placeholders
VISIBILITY_MAP = {
    LineVisibility.public: "public",
    LineVisibility.private: "private",
    LineVisibility.friends: "selective"
}

def get_db_mapped_visibility(visibility: str) -> str:
    return VISIBILITY_MAP.get(visibility, "public")

def isPrivate(visibility):
    return visibility == LineVisibility.private
