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
        # Actually this is not even supported by the instruction set architecture :D
        '''
        m2 = re.match(r"(\d+)", expr) # Immediate address???
        if m2:
            return ("store_immediate", m.group(1), m2.group(1))
        '''
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

def compile_if(condition, body_lines):
    cond = condition.strip()
    end = new_label("ifend")
    code = []

    # x OP x
    m = re.match(r"(x\d+)\s*(==|<|>)\s*(x\d+)", cond)
    if m:
        a, op, b = m.groups()

        code.append(f"cmp ${a[1:]}, ${b[1:]}")

        if op == "<":
            code.append(f"bge {end}")
        elif op == ">":
            code.append(f"ble {end}")
        elif op == "==":
            code.append(f"bne {end}")

    else:
        # x OP immediate
        m = re.match(r"(x\d+)\s*(==|<|>)\s*(\d+)", cond)
        if not m:
            raise Exception(f"unsupported if condition: {cond}")

        a, op, imm = m.groups()

        code.append(f"cmp ${a[1:]}, {imm}")

        if op == "<":
            code.append(f"bge {end}")
        elif op == ">":
            code.append(f"ble {end}")
        elif op == "==":
            code.append(f"bne {end}")

    # body
    for line in body_lines:
        code += compile([line])

    code.append(f"{end}:")
    return code

def compile_while(condition, body_lines):
    cond = condition.strip()

    # parse condition like: x0 < x1
    m = re.match(r"(x\d+)\s*<\s*(x\d+)", cond)
    if not m:
        raise Exception("Only supports x < y for now")

    a, b = m.group(1), m.group(2)

    start = new_label("whilestart")
    end = new_label("whileend")

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

        if line.startswith("if"):
            condition = line[len("if"):].strip().rstrip(":")
            i += 1
            body = []
            while i < len(lines) and lines[i].startswith("    "):
                body.append(lines[i].strip())
                i += 1
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
