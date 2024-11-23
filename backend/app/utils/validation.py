def validate_instructions(instructions):
    if not instructions or len(instructions) < 5:
        raise ValueError("Instructions must be at least 5 characters long.")
