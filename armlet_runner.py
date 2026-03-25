import subprocess
import re

def run_program(asm_file):
    cmd = f"sbt 'armlet/runMain armlet.ArmletRunner {asm_file}'"

    print("[TEST] Running "+cmd)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        shell=True,
        timeout=20   # 🔥 KEY LINE
    )

    if result.returncode != 0:
        raise Exception("Execution failed")

    return result.stdout

def parse_registers(output):
    regs = {}

    in_section = False
    for line in output.splitlines():
        line = line.strip()

        if line == "===REGISTERS===":
            in_section = True
            continue
        if line == "===END===":
            break

        if in_section:
            m = re.match(r"\$(\d+)=(\d+)", line)
            if m:
                reg = int(m.group(1))
                val = int(m.group(2))
                regs[reg] = val

    return regs


def test_case(name, asm_file, expected_regs):
    print(f"[TEST] {name}")

    output = run_program(asm_file)
    regs = parse_registers(output)

    for reg, expected in expected_regs.items():
        actual = regs.get(reg)
        if actual != expected:
            print("❌ FAIL")
            print(f"Register x{reg}: expected {expected}, got {actual}")
            return False

    print("✅ PASS")
    return True


if __name__ == "__main__":
    # Example test
    test_case(
        "most frequent",
        "program.s",
        {
            2: 33345  # x2 should contain result
        }
    )
