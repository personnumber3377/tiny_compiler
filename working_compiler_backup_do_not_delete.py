import re
import sys

label_counter = 0

DEBUG = True
SIGNED_COMPARISONS = False

SPILL_BASE = 1000

# -----------------------------
# Register model:
# x0–x4 = real registers
# x5+   = spilled
# $5,$6,$7 = temporaries ONLY
# -----------------------------

NUM_REAL_REGS = 5  # x0–x4

def phys_reg(x):
    return int(x[1:])

def compile_condition(cond, end_label):
    code = []

    # x ? x
    m = re.match(r"(x\d+)\s*(==|!=|<|>)\s*(x\d+)", cond)
    if m:
        a, op, b = m.groups()

        code += load_var(a, 6)
        code += load_var(b, 5)
        code.append("cmp $6, $5")

        if op == "<":
            code.append(f"bae {end_label}")  # exit if >=
        elif op == ">":
            code.append(f"bbe {end_label}")  # exit if <=
        elif op == "==":
            code.append(f"bne {end_label}")
        elif op == "!=":
            code.append(f"beq {end_label}")

        return code

    # x ? IMM
    m = re.match(r"(x\d+)\s*(==|!=|<|>)\s*(\d+)", cond)
    if m:
        a, op, imm = m.groups()

        code += load_var(a, 6)
        code.append(f"cmp $6, {imm}")

        if op == "<":
            code.append(f"bae {end_label}")
        elif op == ">":
            code.append(f"bbe {end_label}")
        elif op == "==":
            code.append(f"bne {end_label}")
        elif op == "!=":
            code.append(f"beq {end_label}")

        return code

    raise Exception(f"Unsupported condition: {cond}")

# -----------------------------
# LOAD VARIABLE → target reg
# -----------------------------
def load_var(x, target):
    idx = phys_reg(x)

    if idx < NUM_REAL_REGS:
        # ALWAYS move (never trust register state)
        return [f"mov ${target}, ${idx}"]
    else:
        addr = SPILL_BASE + (idx - NUM_REAL_REGS)
        return [
            f"mov $7, {addr}",
            f"loa ${target}, $7"
        ]


# -----------------------------
# STORE VARIABLE ← source reg
# -----------------------------
def store_var(x, source):
    idx = phys_reg(x)

    if idx < NUM_REAL_REGS:
        return [f"mov ${idx}, ${source}"]
    else:
        addr = SPILL_BASE + (idx - NUM_REAL_REGS)

        if source == 7:
            return [
                "mov $6, $7",          # save value
                f"mov $7, {addr}",     # load address
                "sto $7, $6"
            ]
        else:
            return [
                f"mov $7, {addr}",
                f"sto $7, ${source}"
            ]


# -----------------------------
# Debug
# -----------------------------
def dprint(msg):
    if DEBUG:
        print("[DEBUG]", msg)


def new_label(prefix="L"):
    global label_counter
    label = f"{prefix}{label_counter}"
    label_counter += 1
    return label


def get_indent(line):
    return len(line) - len(line.lstrip(" "))


# -----------------------------
# Expression parsing
# -----------------------------
def parse_expr(left, expr):
    expr = expr.strip()

    dprint(expr)

    m = re.match(r"mem\[(x\d+)\]", left)
    if m:
        m2 = re.match(r"(x\d+)", expr)
        if m2:
            return ("store_register", m.group(1), m2.group(1))
        raise Exception(f"Unknown expr: {expr}")

    m = re.match(r"mem\[(x\d+)\]", expr)
    if m:
        return ("load", m.group(1))

    m = re.match(r"(x\d+)\s*<<\s*(\d+)", expr)
    if m:
        return ("lsl", m.group(1), int(m.group(2)))

    m = re.match(r"(x\d+)\s*\+\s*(x\d+)", expr)
    if m:
        return ("add", m.group(1), m.group(2))

    m = re.match(r"(x\d+)\s*\+\s*(\d+)", expr)
    if m:
        return ("add_imm", m.group(1), int(m.group(2)))

    m = re.match(r"(x\d+)\s*-\s*(x\d+)", expr)
    if m:
        return ("sub", m.group(1), m.group(2))

    m = re.match(r"(x\d+)\s*\-\s*(\d+)", expr)
    if m:
        return ("sub_imm", m.group(1), int(m.group(2)))

    if re.match(r"x\d+", expr):
        return ("mov", expr)

    if expr.isdigit():
        return ("imm", int(expr))

    raise Exception(f"Unknown expr: {expr}")


# -----------------------------
# Compile line
# -----------------------------
def compile_line(line):
    line = line.strip()

    if "=" in line and not line.startswith("while"):
        dprint("line: " + line)

        left, right = map(str.strip, line.split("="))
        expr = parse_expr(left, right)

        dprint("expr: " + str(expr))

        # -------------------------
        if expr[0] == "store_register":
            # return [f"sto ${expr[1][1]}, ${expr[2][1]}"]
            # if expr[0] == "store_register":
            addr = expr[1]
            value = expr[2]

            code = []
            '''
            code += load_var(addr, 6)   # address → $6
            code += load_var(value, 5)  # value   → $5
            code.append("sto $6, $5")
            '''

            code += load_var(addr, 6)
            code += load_var(value, 7)
            code.append("sto $6, $7")

            return code

        # -------------------------
        if expr[0] == "mov":
            src = expr[1]
            dst = left

            code = []
            code += load_var(src, 7)
            code += store_var(dst, 7)
            return code

        # -------------------------
        if expr[0] == "imm":
            dst = left
            val = expr[1]

            code = [f"mov $7, {val}"]
            code += store_var(dst, 7)
            return code

        # -------------------------
        if expr[0] == "add":
            a, b = expr[1], expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code += load_var(b, 5)
            code.append("add $7, $6, $5")
            code += store_var(dst, 7)
            return code

        # -------------------------
        if expr[0] == "add_imm":
            a = expr[1]
            imm = expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code.append(f"add $7, $6, {imm}")
            code += store_var(dst, 7)
            return code

        # -------------------------
        if expr[0] == "sub":
            a, b = expr[1], expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code += load_var(b, 5)
            code.append("sub $7, $6, $5")
            code += store_var(dst, 7)
            return code

        # -------------------------
        if expr[0] == "sub_imm":
            a = expr[1]
            imm = expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code.append(f"sub $7, $6, {imm}")
            code += store_var(dst, 7)
            return code

        # -------------------------
        if expr[0] == "lsl":
            a = expr[1]
            shift = expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code.append(f"lsl $7, $6, {shift}")
            code += store_var(dst, 7)
            return code

        # -------------------------
        if expr[0] == "load":
            src = expr[1]
            dst = left

            code = []
            code += load_var(src, 6)     # address → $6
            # code.append("loa $5, $6")    # value → $5  (NOT $7)
            # code += store_var(dst, 5)    # store safely
            
            code.append("loa $7, $6")
            code += store_var(dst, 7)

            return code

    return []


# -----------------------------
# Control flow (unchanged)
# -----------------------------
def compile_if(condition, body_lines):
    cond = condition.strip()
    end = new_label("ifend")

    code = []

    m = re.match(r"(x\d+)\s*(==|<|>|!=)\s*(x\d+)", cond)
    if m:
        a, op, b = m.groups()

        code += load_var(a, 6)
        code += load_var(b, 5)
        code.append("cmp $6, $5")

        if op == "<":
            code.append(f"bae {end}")   # skip if a >= b
        elif op == ">":
            '''
            code.append(f"bae {end}")
            code[-1] = f"bbe {end}"
            '''

            # code[-1] = f"bbe {end}"

            code.append(f"bbe {end}")

        elif op == "==":
            code.append(f"bne {end}")
        elif op == "!=":
            code.append(f"beq {end}")

    else:
        m = re.match(r"(x\d+)\s*(==|<|>|!=)\s*(\d+)", cond)
        a, op, imm = m.groups()

        code += load_var(a, 6)
        code.append(f"cmp $6, {imm}")

        if op == "<":
            code.append(f"bae {end}")
        elif op == ">":
            code.append(f"bbe {end}")   # skip if <=
        elif op == "==":
            code.append(f"bne {end}")
        elif op == "!=":
            code.append(f"beq {end}")

    code += compile(body_lines)
    code.append(f"{end}:")

    return code

def compile_while(condition, body_lines):
    cond = condition.strip()

    start = new_label("whilestart")
    end = new_label("whileend")

    code = [f"{start}:"]

    m = re.match(r"(x\d+)\s*<\s*(x\d+)", cond)
    if m:
        a, b = m.groups()

        code += load_var(a, 6)
        code += load_var(b, 5)
        code.append("cmp $6, $5")
        code.append(f"bae {end}")   # exit if a >= b

    else:
        print("cond: "+str(cond))
        m = re.match(r"(x\d+)\s*<\s*(\d+)", cond)
        a, imm = m.groups()

        code += load_var(a, 6)
        code.append(f"cmp $6, {imm}")
        code.append(f"bae {end}")

    code += compile(body_lines)
    code.append(f"jmp {start}")
    code.append(f"{end}:")

    return code


def is_blank(line):
    return line.strip() == ""

def collect_block(lines, i, base_indent):
    body = []

    while i < len(lines):
        line = lines[i]

        if is_blank(line):
            body.append(line)
            i += 1
            continue

        indent = get_indent(line)

        if indent <= base_indent:
            break

        body.append(line)
        i += 1

    return body, i

def compile(lines, base_indent=0):
    i = 0
    out = []

    while i < len(lines):
        raw = lines[i]
        raw = raw.split("#")[0]

        indent = get_indent(raw)
        line = raw.strip()

        if line == "":
            i += 1
            continue

        if indent < base_indent:
            break

        if line.startswith("while"):
            condition = line[len("while"):].strip().rstrip(":")
            i += 1

            body, i = collect_block(lines, i, indent)

            out += compile_while(condition, body)
            continue

        if line.startswith("if"):
            condition = line[len("if"):].strip().rstrip(":")
            i += 1

            body, i = collect_block(lines, i, indent)

            out += compile_if(condition, body)
            continue

        out += compile_line(line)
        i += 1

    return out


def postprocess_labels(lines):
    labels = set()

    for line in lines:
        if line.endswith(":"):
            labels.add(line[:-1])

    out = []

    for line in lines:
        if line.endswith(":"):
            out.append(f"@{line[:-1]}:")
            continue

        for label in labels:
            line = re.sub(rf"\b{label}\b", f">{label}", line)

        out.append(line)

    return out


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "SOURCE")
        exit(1)

    with open(sys.argv[1]) as f:
        program = f.readlines()

    asm = compile(program)
    asm = postprocess_labels(asm)

    for line in asm:
        print(line)