def open_func(file, read_header=False, header_start="#", skip_rows=0, to_list=False, sep="\t"):
    '''for row count: headers or lines with empty spaces are counted'''
    gzipped = is_gzipped(file)
    file_open = gzip.open if gzipped else open
    row_count = 0
    with file_open(file) as infile:
        for xline in infile:
            row_count += 1
            line = xline.decode("utf-8").replace("\n", "") if gzipped else xline.replace("\n", "")
            if line == "" or (line.startswith(header_start) and read_header is False) or row_count <= skip_rows:
                continue
            yield line if not to_list else line.split(sep)