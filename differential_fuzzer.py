import os
import random
import compiler
import armlet_runner
from emulator import run_python_emulator

WORK_DIR = "work"
os.makedirs(WORK_DIR, exist_ok=True)


# -------------------------
# Random program generator
# -------------------------

REGS = [f"x{i}" for i in range(8)]

def rand_reg():
    return random.choice(REGS)

def rand_val():
    return str(random.randint(0, 20))

def rand_expr():
    if random.random() < 0.5:
        return rand_val()
    return f"{rand_reg()} + {random.randint(0,5)}"

def rand_assign():
    return f"{rand_reg()} = {rand_expr()}"

def rand_if():
    a = rand_reg()
    b = rand_reg()
    return [
        f"if {a} < {b}:",
        f"    {rand_assign()}"
    ]

def rand_while():
    a = rand_reg()
    b = rand_reg()
    return [
        f"while {a} < {b}:",
        f"    {rand_assign()}",
        f"    {a} = {a} + 1"
    ]

def generate_program():
    lines = []

    # initialize registers
    for r in REGS:
        lines.append(f"{r} = {random.randint(0,10)}")

    for _ in range(random.randint(5, 15)):
        t = random.random()
        if t < 0.5:
            lines.append(rand_assign())
        elif t < 0.75:
            lines += rand_if()
        else:
            lines += rand_while()

    return "\n".join(lines)


# -------------------------
# Compile helper
# -------------------------

def compile_to_asm(src_code, asm_path):
    program = src_code.splitlines()
    asm = compiler.compile(program)
    asm = compiler.postprocess_labels(asm)

    with open(asm_path, "w") as f:
        for line in asm:
            f.write(line + "\n")
        f.write("hlt\n")


# -------------------------
# Compare results
# -------------------------

def compare(py, scala):
    for i in range(8):
        if py["regs"][f"x{i}"] != scala.get(i):
            return False, i
    return True, None


# -------------------------
# Main fuzz loop
# -------------------------

def fuzz(iterations=1000):
    for i in range(iterations):
        print(f"\n[FUZZ] iteration {i}")

        prog = generate_program()
        asm_path = os.path.join(WORK_DIR, "fuzz.s")

        try:
            # Python run
            py = run_python_emulator(prog)

            # Compile + Scala run
            compile_to_asm(prog, asm_path)
            scala_regs = run_scala(asm_path)

            ok, reg = compare(py, scala_regs)

            if not ok:
                print("\n💥 DIFFERENCE FOUND!")
                print("\nProgram:\n")
                print(prog)

                print("\nPython:")
                print(py["regs"])

                print("\nScala:")
                print(scala_regs)

                print(f"\nMismatch at x{reg}")
                return

        except Exception as e:
            print("Error:", e)
            continue

    print("\n✅ No differences found")


if __name__ == "__main__":
    fuzz(10000)
