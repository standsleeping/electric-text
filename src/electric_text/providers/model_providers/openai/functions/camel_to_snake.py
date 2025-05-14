def camel_to_snake(camel_case: str) -> str:
    """Convert a camelCase string to snake_case."""
    snake_case = ""
    for i, char in enumerate(camel_case):
        if char.isupper():
            # Add underscore if not first character and either:
            # 1. Previous character is lowercase (camelCase boundary)
            # 2. Next character is lowercase and previous character is uppercase (HTTPResponse -> http_response)
            if i > 0 and (camel_case[i-1].islower() or
                          (i < len(camel_case)-1 and camel_case[i+1].islower() and camel_case[i-1].isupper())):
                snake_case += "_"
            snake_case += char.lower()
        else:
            snake_case += char
    return snake_case