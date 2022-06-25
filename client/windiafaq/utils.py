__all__ = ["make_columns"]


def make_columns(string_list: list[str], *, amount_columns: int = 3) -> str:
    longest_command = len(max(string_list, key=len))
    
    chunked_strings: list[list[str]] = []

    for i in range(0, len(string_list), amount_columns):
        chunked_strings.append(string_list[i:i+amount_columns])

    columns = ''
    for chunked_string in chunked_strings:
        line = ''
        for string in chunked_string:
            line += string + " " * (longest_command - len(string)) + "  "
        
        columns += line.strip() + "\n"

    return columns