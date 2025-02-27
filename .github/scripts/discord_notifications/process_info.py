import re


def _tokenize(text: str):
    """Splits the Markdown text into sections based on the specified break tags."""
    return [s.strip() for s in re.split(r'(?=^# )', text, flags=re.MULTILINE) if s.strip()]


def _extract_table(lines):
    """Extracts table data from Markdown format and returns a dictionary or list of dictionaries."""
    headers = [h.strip() for h in lines[0].split('|')[1:-1]]
    rows = [dict(zip(headers, [v.strip() for v in line.split('|')[1:-1]])) for line in lines[2:] if line.strip()]
    return rows[0] if len(rows) == 1 else rows  # Return a single dictionary if only one row exists


def _parse_h1_section(h1_section):
    """Parses an H1 section and extracts relevant data, including H2 sections."""
    lines = h1_section.split('\n')
    section_title = lines[0].replace('# ', '').strip()
    section_data = {}
    current_table, tables = [], []
    current_h2, h2_data = None, {}

    for line in lines[1:]:
        # If an H2 header is found, store the previous H2 section if it exists
        if line.startswith('## '):
            if current_h2:
                section_data[current_h2] = h2_data if h2_data else {}
            current_h2, h2_data = line.replace('## ', '').strip(), {}

        # If the line contains a table row, add it to the current table
        elif '|' in line:
            current_table.append(line)

        # If an empty line is encountered, store the completed table
        elif current_table:
            tables.append((current_h2, current_table) if current_h2 else current_table)
            current_table = []

    # Ensure the last table is added to the tables list
    if current_table:
        tables.append((current_h2, current_table) if current_h2 else current_table)

    # Ensure the last H2 section is stored
    if current_h2:
        section_data[current_h2] = h2_data if h2_data else {}

    # Process the extracted tables and add them to the section data
    for table in tables:
        if isinstance(table, tuple):  # If the table belongs to an H2 section
            h2_title, table_lines = table
            section_data[h2_title] = _extract_table(table_lines)
        else:  # If the table belongs to the main H1 section
            section_data.update(_extract_table(table))

    return section_title, section_data


def _read_md_tables(md_text):
    """Reads Markdown text and extracts structured data organized by H1 and H2 sections."""
    return {
        title: data for title, data in (_parse_h1_section(section)
                                        for section in _tokenize(md_text))
    }


def get_info(dtype: str, path: str):
    """Reads Markdown file and extracts structured data for a specific dtype."""
    with open(path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    return _read_md_tables(md_text).get(dtype, {})
