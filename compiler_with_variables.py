import re
import sys # For command line handling

label_counter = 0

DEBUG = True
SIGNED_COMPARISONS = False

SPILL_BASE = 1000

def is_spilled(x):
    return int(x[1:]) >= 7

def phys_reg(x):
    return int(x[1:])

def load_var(x, target):
    idx = phys_reg(x)

    # ❌ If source == target, this is ONLY safe if it's a real register
    if idx < 7:
        if idx < 7:
            # ⚠️ ALWAYS move, never trust register state
            return [f"mov ${target}, ${idx}"]

    else:
        addr = SPILL_BASE + (idx - 7)

        # ⚠️ if target == 7, still fine
        return [
            f"mov $7, {addr}",
            f"loa ${target}, $7"
        ]

def store_var(x, source):
    idx = phys_reg(x)

    if idx < 7:
        if idx == source:
            return []
        return [f"mov ${idx}, ${source}"]
    else:
        addr = SPILL_BASE + (idx - 7)

        # ⚠️ if source == 7, we must preserve it
        if source == 7:
            return [
                "mov $6, $7",            # save value
                f"mov $7, {addr}",       # load address
                "sto $7, $6"             # store value
            ]
        else:
            return [
                f"mov $7, {addr}",
                f"sto $7, ${source}"
            ]

def dprint(msg: str): # Debug printing
    if DEBUG:
        print("[DEBUG] "+str(msg))

def new_label(prefix="L"):
    global label_counter
    label = f"{prefix}{label_counter}"
    label_counter += 1
    return label

def get_indent(line):
    return len(line) - len(line.lstrip(" "))

def parse_expr(left, expr):
    expr = expr.strip()

    dprint(expr)

    # First check if we are storing into memory, since it is special and has square brackets on the left hand side...

    # mem[x] = rN or mem[x] = 
    m = re.match(r"mem\[(x\d+)\]", left)
    if m:
        # Now check if the right hand side is a register or if it is just a number...
        m2 = re.match(r"(x\d+)", expr)
        if m2: # Register value, so therefore it is storing the register value...
            return ("store_register", m.group(1), m2.group(1))
        # ???
        raise Exception(f"Unknown expr: {expr}")
    
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

    # x - 5
    m = re.match(r"(x\d+)\s*\-\s*(\d+)", expr)
    if m:
        return ("sub_imm", m.group(1), int(m.group(2)))

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
        expr = parse_expr(left, right)
        dprint("expr: "+str(expr))
        # if len(expr) == 3: # Memory storage instruction?
        #     assert expr[0] == "store_register" # The only instruction which has length 3 as expr length

        if expr[0] == "store_register":
            return [f"sto ${expr[1][1]}, ${expr[2][1]}"]
            # Actually in reality the store instruction is the other way around...
            # return [f"sto ${expr[2][1]}, ${expr[1][1]}"]

        if expr[0] == "mov":
            src = expr[1]
            dst = left

            code = []
            code += load_var(src, 7)        # load into scratch
            code += store_var(dst, 7)       # store from scratch
            return code

        if expr[0] == "imm":
            dst = left
            val = expr[1]

            code = [f"mov $7, {val}"]
            code += store_var(dst, 7)
            return code


        if expr[0] == "add":
            a, b = expr[1], expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code += load_var(b, 5)
            code.append("add $7, $6, $5")
            code += store_var(dst, 7)
            return code


        if expr[0] == "add_imm":
            a = expr[1]
            imm = expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code.append(f"add $7, $6, {imm}")
            code += store_var(dst, 7)
            return code


        if expr[0] == "sub":
            a, b = expr[1], expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code += load_var(b, 5)
            code.append("sub $7, $6, $5")
            code += store_var(dst, 7)
            return code


        if expr[0] == "sub_imm":
            a = expr[1]
            imm = expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code.append(f"sub $7, $6, {imm}")
            code += store_var(dst, 7)
            return code


        if expr[0] == "lsl":
            a = expr[1]
            shift = expr[2]
            dst = left

            code = []
            code += load_var(a, 6)
            code.append(f"lsl $7, $6, {shift}")
            code += store_var(dst, 7)
            return code


        if expr[0] == "load":
            src = expr[1]
            dst = left

            code = []
            code += load_var(src, 6)     # address
            code.append("loa $7, $6")    # load value
            code += store_var(dst, 7)
            return code

    return []

def compile_if(condition, body_lines):
    dprint("condition: "+str(condition))
    cond = condition.strip()
    end = new_label("ifend")
    code = []

    # x OP x
    m = re.match(r"(x\d+)\s*(==|<|>|!=)\s*(x\d+)", cond)
    if m:
        a, op, b = m.groups()

        code.append(f"cmp ${a[1:]}, ${b[1:]}")

        if op == "<":
            if SIGNED_COMPARISONS:
                code.append(f"bge {end}")
            else:
                code.append(f"bae {end}")
        elif op == ">":
            if SIGNED_COMPARISONS:
                code.append(f"ble {end}")
            else:
                code.append(f"bbe {end}")
        elif op == "==":
            code.append(f"bne {end}")
        elif op == "!=":
            code.append(f"beq {end}")

    else:
        # x OP immediate
        m = re.match(r"(x\d+)\s*(==|<|>|!=)\s*(\d+)", cond)
        if not m:
            raise Exception(f"unsupported if condition: {cond}")

        a, op, imm = m.groups()

        code.append(f"cmp ${a[1:]}, {imm}")

        if op == "<":
            if SIGNED_COMPARISONS:
                code.append(f"bge {end}")
            else:
                code.append(f"bae {end}")
        elif op == ">":
            if SIGNED_COMPARISONS:
                code.append(f"ble {end}")
            else:
                code.append(f"bbe {end}")
        elif op == "==":
            code.append(f"bne {end}")
        elif op == "!=":
            code.append(f"beq {end}")

    # body
    # for line in body_lines:
    #     code += compile([line])
    # This is needed for multiline and nested if and while cases to not break
    code += compile(body_lines)

    code.append(f"{end}:")
    return code

def compile_while(condition, body_lines):
    cond = condition.strip()

    start = new_label("whilestart")
    end = new_label("whileend")

    code = []
    code.append(f"{start}:")

    # -------------------------
    # Case 1: x < x
    # -------------------------
    m = re.match(r"(x\d+)\s*<\s*(x\d+)", cond)
    if m:
        a, b = m.groups()
        code.append(f"cmp ${a[1]}, ${b[1]}")
        # bge
        # bae
        if SIGNED_COMPARISONS:
            code.append(f"bge {end}")
        else:
            code.append(f"bae {end}")
    else:
        # -------------------------
        # Case 2: x < immediate
        # -------------------------
        m = re.match(r"(x\d+)\s*<\s*(\d+)", cond)
        if m:
            a, imm = m.groups()
            code.append(f"cmp ${a[1]}, {imm}")
            if SIGNED_COMPARISONS:
                code.append(f"bge {end}")
            else:
                code.append(f"bae {end}")
        else:
            raise Exception(f"Unsupported while condition: {cond}")

    # body
    code += compile(body_lines)

    code.append(f"jmp {start}")
    code.append(f"{end}:")

    return code

def is_blank(line):
    return line.strip() == ""

def postprocess_labels(lines):
    # First collect all label names
    labels = set()

    for line in lines:
        # line = line.strip()
        if line.endswith(":"):
            label = line[:-1]
            labels.add(label)

    out = []

    for line in lines:
        stripped = line.strip()

        # -----------------------------
        # Case 1: label definition
        # -----------------------------
        if stripped.endswith(":"):
            label = stripped[:-1]
            out.append(f"@{label}:")
            continue

        # -----------------------------
        # Case 2: instruction with label
        # -----------------------------
        # Replace only standalone label tokens
        for label in labels:
            # match whole word only (avoid partial replacements)
            pattern = rf"\b{label}\b"
            replacement = f">{label}"
            stripped = re.sub(pattern, replacement, stripped)

        out.append(stripped)

    return out

def strip_comments(original: str) -> str:
    # Check if "#" exists...
    # Inefficient, but I don't care...
    # while "#" in original:
    #     original = original[:-1]

    if "#" in original:
        original = original[:original.index("#")]
    return original

def compile(lines, base_indent=0):
    i = 0
    out = []

    while i < len(lines):
        raw = lines[i]
        raw = strip_comments(raw)
        indent = get_indent(raw)
        line = raw.strip()

        if line == "": # Ignore blank lines
            i += 1
            continue

        if indent < base_indent:
            break  # end of this block

        if line.startswith("while"):
            condition = line[len("while"):].strip().rstrip(":")
            i += 1

            body = []
            while i < len(lines):
                if is_blank(lines[i]):
                    body.append(lines[i])
                    i += 1
                    continue

                if get_indent(lines[i]) > indent:
                    body.append(lines[i])
                    i += 1
                    continue

                break

            # out += compile_while(condition, compile(body))
            dprint("Compiling while with this body here: '''"+str(body)+"'''")
            out += compile_while(condition, body)
            continue

        if line.startswith("if"):
            condition = line[len("if"):].strip().rstrip(":")
            i += 1

            body = []
            # while i < len(lines) and get_indent(lines[i]) > indent:
            #     body.append(lines[i])
            #     i += 1
            
            while i < len(lines):
                if is_blank(lines[i]):
                    body.append(lines[i])
                    i += 1
                    continue

                if get_indent(lines[i]) > indent:
                    body.append(lines[i])
                    i += 1
                    continue

                break

            dprint("Compiling if with this body here: '''"+str(body)+"'''")
            # out += compile_if(condition, compile(body))
            out += compile_if(condition, body)
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

    asm = compile(program)

    asm = postprocess_labels(asm) # Postprocessing to fix syntax...

    for line in asm:
        print(line)
    exit(0)
