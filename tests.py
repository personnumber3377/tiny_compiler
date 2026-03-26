import os
import subprocess
import re
import compiler
import armlet_runner

TEST_SRC_DIR = "test_src"
WORK_DIR = "work"

# Ensure work dir exists
os.makedirs(WORK_DIR, exist_ok=True)


# -----------------------------
# Expected results (hardcoded)
# -----------------------------
EXPECTED = {
    "simple_add.src": {2: 7},
    "loop_increment.src": {0: 10},
    "memory_store_load.src": {2: 42},
    "branch_if.src": {2: 1},
    "nested_while_sum.src": {0: 10},
    "nested_if.src": {2: 42},
    "if_inside_while.src": {2: 5},
    "while_inside_if.src": {2: 10},
    "memory_sum.src": {2: 10},
    "simple_swap.src": {5: 3, 6: 5},
    "if_chain.src": {1: 2},
    # FIX THIS TOO HERE:
    # "spill_test.src": {9: 17,   # 8 + 9
    #     10: 24   # 17 + 7
    # }

    "spill_test.src": {
        2: 17,
        3: 24
    },
    "simple_if_else.src": {
        2: 2
    },
    "nested_if_else.src": {
        2: 42
    },
    "if_else_overwrite.src": {
        2: 2
    },
    "if_else_in_while.src": {
        2: 8
    },
    "break_simple.src": {2: 0},
    "break_if.src": {2: 5},
    "break_nested.src": {3: 3},

}


# -----------------------------
# Compile source → assembly
# -----------------------------
def compile_to_asm(src_path, asm_path):
    with open(src_path) as f:
        program = f.readlines()

    asm = compiler.compile(program)
    asm = compiler.postprocess_labels(asm)

    with open(asm_path, "w") as f:
        # Optional wrapper (you can extend this)
        for line in asm:
            f.write(line + "\n")
        f.write("hlt\n")


# -----------------------------
# Run one test
# -----------------------------
def run_test(src_filename):
    src_path = os.path.join(TEST_SRC_DIR, src_filename)
    asm_path = os.path.join(WORK_DIR, src_filename.replace(".src", ".s"))

    print(f"\n[TEST] {src_filename}")

    # Compile
    compile_to_asm(src_path, asm_path)

    # Run
    output = armlet_runner.run_program(asm_path)
    print("Got this output here: "+str(output))
    regs = armlet_runner.parse_registers(output)

    expected = EXPECTED.get(src_filename, {})

    ok = True
    for reg, exp_val in expected.items():
        actual = regs.get(reg)
        if actual != exp_val:
            print(f"❌ FAIL: x{reg} expected {exp_val}, got {actual}")
            ok = False

    if ok:
        print("✅ PASS")

    return ok


# -----------------------------
# Run all tests
# -----------------------------

import sys # For command line parameter handling...

def run_all_tests():

    files = [f for f in os.listdir(TEST_SRC_DIR) if f.endswith(".src")]

    if len(sys.argv) >= 2: # Check if only one test is supplied...
        for fn in sys.argv[1:]: # Iterate over the given test files...
            if fn not in files:
                print("Invalid test file")
                exit(1)
            if run_test(fn):
                print("Passed!!!")
            else:
                print("Failed!!!")
        exit(0)

    total = len(files)
    passed = 0

    for f in files:
        if run_test(f):
            passed += 1

    print("\n====================")
    print(f"Passed {passed}/{total} tests")
    print("====================")


if __name__ == "__main__":
    run_all_tests()
