import re
import sys # For command line handling

label_counter = 0

DEBUG = True

def dprint(msg: str): # Debug printing
    if DEBUG:
        print("[DEBUG] "+str(msg))

def new_label(prefix="L"):
    global label_counter
    label = f"{prefix}{label_counter}"
    label_counter += 1
    return label

def parse_expr(expr):
    expr = expr.strip()

    dprint(expr)

    # x = mem[y]
    m = re.match(r"mem\[(x\d+)\]", expr)
    if m:
        return ("load", m.group(1))

    # x << 3
    m = re.match(r"(x\d+)\s*<<\s*(\d+)", expr)
    if m:
        return ("lsl", m.group(1), int(m.group(2)))

    # x + y
    m = re.match(r"(x\d+)\s*\+\s*(x\d+)", expr)
    if m:
        return ("add", m.group(1), m.group(2))

    # x + 5
    m = re.match(r"(x\d+)\s*\+\s*(\d+)", expr)
    if m:
        return ("add_imm", m.group(1), int(m.group(2)))

    # x - y
    m = re.match(r"(x\d+)\s*-\s*(x\d+)", expr)
    if m:
        return ("sub", m.group(1), m.group(2))

    # x
    if re.match(r"x\d+", expr):
        return ("mov", expr)

    # immediate
    if expr.isdigit():
        return ("imm", int(expr))

    raise Exception(f"Unknown expr: {expr}")


def compile_line(line):
    line = line.strip()

    # assignment
    if "=" in line and not line.startswith("while"):
        dprint("line: "+str(line))
        left, right = map(str.strip, line.split("="))
        expr = parse_expr(right)

        if expr[0] == "mov":
            return [f"mov ${left[1]}, ${expr[1][1]}"]

        if expr[0] == "imm":
            return [f"mov ${left[1]}, {expr[1]}"]

        if expr[0] == "add":
            return [f"add ${left[1]}, ${expr[1][1]}, ${expr[2][1]}"]

        if expr[0] == "add_imm":
            return [f"add ${left[1]}, ${expr[1][1]}, {expr[2]}"]

        if expr[0] == "sub":
            return [f"sub ${left[1]}, ${expr[1][1]}, ${expr[2][1]}"]

        if expr[0] == "lsl":
            return [f"lsl ${left[1]}, ${expr[1][1]}, {expr[2]}"]

        if expr[0] == "load":
            return [f"loa ${left[1]}, ${expr[1][1]}"]

    return []


def compile_while(condition, body_lines):
    cond = condition.strip()

    # parse condition like: x0 < x1
    m = re.match(r"(x\d+)\s*<\s*(x\d+)", cond)
    if not m:
        raise Exception("Only supports x < y for now")

    a, b = m.group(1), m.group(2)

    start = new_label("while_start")
    end = new_label("while_end")

    code = []
    code.append(f"{start}:")

    code.append(f"cmp ${a[1]}, ${b[1]}")
    code.append(f"bge {end}")  # exit if not <

    for line in body_lines:
        code += compile([line])

    code.append(f"jmp {start}")
    code.append(f"{end}:")

    return code


def compile(lines):
    i = 0
    out = []

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("while"):
            condition = line[len("while"):].strip().rstrip(":")
            i += 1

            body = []
            while i < len(lines) and lines[i].startswith("    "):
                body.append(lines[i].strip())
                i += 1

            out += compile_while(condition, body)
            continue

        out += compile_line(line)
        i += 1

    return out


# -----------------------------
# Example usage
# -----------------------------



if __name__=="__main__":
    
    if len(sys.argv) < 2:
        print("Usage: "+str(sys.argv[0])+" SOURCE_FILENAME")
        exit(1)

    fh = open(sys.argv[1])
    program = fh.readlines()
    fh.close()

    '''
    program = [
        "x0 = 0",
        "x1 = 10",
        "while x0 < x1:",
        "    x0 = x0 + 1",
    ]
    '''

    asm = compile(program)

    for line in asm:
        print(line)
    exit(0)
