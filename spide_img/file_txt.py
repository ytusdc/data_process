import os


file_path = "./file.txt"
result_lines = ''
with open(file_path, 'r') as f_r:
    lines = f_r.readlines()
    for l in lines:
        line = l.strip()
        if line == "":
            continue
        # print(line)
        result_lines += line + "\n\n"

with open(file_path, 'w') as f_w:
    f_w.write(result_lines)

print(result_lines)


