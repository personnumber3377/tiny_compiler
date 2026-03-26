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

loop_stack = [] # This is needed for break and control flow...

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

    # Here are some commonly used logical operators

    # AND
    m = re.match(r"(x\d+)\s*&\s*(x\d+)", expr)
    if m:
        return ("and", m.group(1), m.group(2))

    m = re.match(r"(x\d+)\s*&\s*(\d+)", expr)
    if m:
        return ("and_imm", m.group(1), int(m.group(2)))

    # OR
    m = re.match(r"(x\d+)\s*\|\s*(x\d+)", expr)
    if m:
        return ("or", m.group(1), m.group(2))

    m = re.match(r"(x\d+)\s*\|\s*(\d+)", expr)
    if m:
        return ("or_imm", m.group(1), int(m.group(2)))

    # XOR
    m = re.match(r"(x\d+)\s*\^\s*(x\d+)", expr)
    if m:
        return ("xor", m.group(1), m.group(2))

    m = re.match(r"(x\d+)\s*\^\s*(\d+)", expr)
    if m:
        return ("xor_imm", m.group(1), int(m.group(2)))

    # SHIFT RIGHT
    m = re.match(r"(x\d+)\s*>>\s*(\d+)", expr)
    if m:
        return ("lsr", m.group(1), int(m.group(2)))

    # if re.match(r"x\d+", expr): # This was too permissive as it incorrectly parsed "x1 = x2 & 2" as a simple mov instruction
    if re.fullmatch(r"x\d+", expr):
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

        # Logical operators:

        if expr[0] == "and":
            a, b = expr[1], expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code += load_var(b, 5)
            code.append("and $7, $6, $5")
            code += store_var(dst, 7)
            return code

        if expr[0] == "and_imm":
            a = expr[1]
            imm = expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code.append(f"and $7, $6, {imm}")
            code += store_var(dst, 7)
            return code

        if expr[0] == "or":
            a, b = expr[1], expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code += load_var(b, 5)
            code.append("ior $7, $6, $5")
            code += store_var(dst, 7)
            return code

        if expr[0] == "or_imm":
            a = expr[1]
            imm = expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code.append(f"ior $7, $6, {imm}")
            code += store_var(dst, 7)
            return code


        if expr[0] == "xor":
            a, b = expr[1], expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code += load_var(b, 5)
            code.append("eor $7, $6, $5")
            code += store_var(dst, 7)
            return code

        if expr[0] == "xor_imm":
            a = expr[1]
            imm = expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code.append(f"eor $7, $6, {imm}")
            code += store_var(dst, 7)
            return code

        if expr[0] == "lsr":
            a = expr[1]
            shift = expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code.append(f"lsr $7, $6, {shift}")
            code += store_var(dst, 7)
            return code

    return []


# -----------------------------
# Control flow (unchanged)
# -----------------------------
def compile_if(condition, body_lines):
    end = new_label("ifend")

    code = []
    code += compile_condition(condition.strip(), end)
    code += compile(body_lines)
    code.append(f"{end}:")

    return code

def compile_while(condition, body_lines):
    cond = condition.strip()

    start = new_label("whilestart")
    end = new_label("whileend")

    code = [f"{start}:"]

    # 🔥 PUSH loop end label
    loop_stack.append(end)

    code += compile_condition(cond, end)
    code += compile(body_lines)

    code.append(f"jmp {start}")
    code.append(f"{end}:")

    # 🔥 POP after loop
    loop_stack.pop()

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

def compile_if_else(condition, if_body, else_body):
    else_label = new_label("else")
    end_label = new_label("ifend")

    code = []

    # If condition false then jump to else
    code += compile_condition(condition.strip(), else_label)

    # IF body
    # code += compile(if_body)
    # Jump over else
    # code.append(f"jmp {end_label}")

    # IF body
    if_code = compile(if_body)
    code += if_code

    # Only add jump if IF body does NOT already end in jump
    if not if_code or not if_code[-1].startswith("jmp"):
        code.append(f"jmp {end_label}")

    # ELSE label
    code.append(f"{else_label}:")

    # ELSE body
    code += compile(else_body)

    # END label
    code.append(f"{end_label}:")

    return code

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

            body_if, i = collect_block(lines, i, indent)

            # Check for "else" too. This basically supports "else" clauses
            body_else = []
            if i < len(lines):
                next_line = lines[i]
                next_line_clean = next_line.strip()

                if next_line_clean.startswith("else"):
                    i += 1
                    body_else, i = collect_block(lines, i, indent)

            out += compile_if_else(condition, body_if, body_else)
            continue

        # 🔥 HANDLE BREAK FIRST
        if line == "break":
            if not loop_stack:
                raise Exception("break used outside of loop")

            end_label = loop_stack[-1]
            out.append(f"jmp {end_label}")
            i += 1
            continue

        # normal line
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