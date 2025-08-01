def deduplicate_markdown_lines(markdown_list: list) -> list:
    deduped_list = []
    for md in markdown_list:
        lines_seen = set()
        unique_lines = []
        for line in md.splitlines():
            if line.strip() and line not in lines_seen:
                lines_seen.add(line)
                unique_lines.append(line)
        deduped_list.append("\n".join(unique_lines))
    return deduped_list