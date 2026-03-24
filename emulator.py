import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


# ---------- AST nodes ----------

@dataclass
class Assign:
    left: str
    right: str


@dataclass
class IfStmt:
    condition: str
    body: list


@dataclass
class WhileStmt:
    condition: str
    body: list


Statement = Union[Assign, IfStmt, WhileStmt]


# ---------- Parser ----------

def strip_comment(line: str) -> str:
    if "#" in line:
        return line.split("#", 1)[0]
    return line


def get_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_program(lines: List[str], base_indent: int = 0, start: int = 0) -> Tuple[List[Statement], int]:
    stmts = []
    i = start

    while i < len(lines):
        raw = strip_comment(lines[i]).rstrip("\n")
        if raw.strip() == "":
            i += 1
            continue

        indent = get_indent(raw)
        line = raw.strip()

        if indent < base_indent:
            break
        if indent > base_indent:
            raise SyntaxError(f"Unexpected indent at line {i+1}: {lines[i]!r}")

        if line.startswith("if ") and line.endswith(":"):
            cond = line[3:-1].strip()
            body, i = parse_program(lines, base_indent + 4, i + 1)
            stmts.append(IfStmt(cond, body))
            continue

        if line.startswith("while ") and line.endswith(":"):
            cond = line[6:-1].strip()
            body, i = parse_program(lines, base_indent + 4, i + 1)
            stmts.append(WhileStmt(cond, body))
            continue

        if "=" in line:
            left, right = map(str.strip, line.split("=", 1))
            stmts.append(Assign(left, right))
            i += 1
            continue

        raise SyntaxError(f"Unsupported syntax at line {i+1}: {line}")

    return stmts, i


# ---------- Emulator ----------

class Emulator:
    def __init__(self, memory_size: int = 65536, debug: bool = False):
        self.regs = {f"x{i}": 0 for i in range(8)}
        self.mem = [0] * memory_size
        self.debug = debug
        self.step_counter = 0
        self.max_steps = 1_000_000

    def log(self, msg: str):
        if self.debug:
            print(msg)

    def check_reg(self, name: str):
        if name not in self.regs:
            raise RuntimeError(f"Invalid register {name}; only x0..x7 exist")

    def eval_atom(self, expr: str) -> int:
        expr = expr.strip()

        m = re.fullmatch(r"mem\[(.+)\]", expr)
        if m:
            addr = self.eval_expr(m.group(1))
            if addr < 0 or addr >= len(self.mem):
                raise RuntimeError(f"Memory read out of bounds: {addr}")
            return self.mem[addr]

        if re.fullmatch(r"x[0-7]", expr):
            self.check_reg(expr)
            return self.regs[expr]

        if re.fullmatch(r"\d+", expr):
            return int(expr)

        raise RuntimeError(f"Unsupported atom: {expr}")

    def eval_expr(self, expr: str) -> int:
        expr = expr.strip()

        # mem[...] or plain atom
        if expr.startswith("mem["):
            return self.eval_atom(expr)

        # x + y or x + 5 or more general atom + atom
        m = re.fullmatch(r"(.+?)\s*\+\s*(.+)", expr)
        if m:
            return self.eval_expr(m.group(1)) + self.eval_expr(m.group(2))

        # x - y or x - 5 or more general atom - atom
        m = re.fullmatch(r"(.+?)\s*-\s*(.+)", expr)
        if m:
            return self.eval_expr(m.group(1)) - self.eval_expr(m.group(2))

        return self.eval_atom(expr)

    def eval_condition(self, cond: str) -> bool:
        cond = cond.strip()

        for op in ["==", "!=", "<", ">"]:
            parts = cond.split(op)
            if len(parts) == 2:
                a = self.eval_expr(parts[0].strip())
                b = self.eval_expr(parts[1].strip())

                if op == "==":
                    return a == b
                if op == "!=":
                    return a != b
                if op == "<":
                    return a < b
                if op == ">":
                    return a > b

        raise RuntimeError(f"Unsupported condition: {cond}")

    def assign(self, left: str, right: str):
        value = self.eval_expr(right)

        m = re.fullmatch(r"mem\[(.+)\]", left)
        if m:
            addr = self.eval_expr(m.group(1))
            if addr < 0 or addr >= len(self.mem):
                raise RuntimeError(f"Memory write out of bounds: {addr}")
            self.mem[addr] = value
            self.log(f"mem[{addr}] = {value}")
            return

        if re.fullmatch(r"x[0-7]", left):
            self.check_reg(left)
            self.regs[left] = value
            self.log(f"{left} = {value}")
            return

        raise RuntimeError(f"Unsupported assignment target: {left}")

    def exec_stmt(self, stmt: Statement):
        self.step_counter += 1
        if self.step_counter > self.max_steps:
            raise RuntimeError("Step limit exceeded")

        if isinstance(stmt, Assign):
            self.assign(stmt.left, stmt.right)
            return

        if isinstance(stmt, IfStmt):
            if self.eval_condition(stmt.condition):
                self.exec_block(stmt.body)
            return

        if isinstance(stmt, WhileStmt):
            while self.eval_condition(stmt.condition):
                self.exec_block(stmt.body)
            return

        raise RuntimeError(f"Unknown statement type: {stmt}")

    def exec_block(self, stmts: List[Statement]):
        for stmt in stmts:
            self.exec_stmt(stmt)

    def run(self, source: str):
        lines = source.splitlines()
        program, idx = parse_program(lines)
        if idx != len(lines):
            raise RuntimeError("Parser did not consume entire input")
        self.exec_block(program)

    def dump_registers(self):
        return {k: self.regs[k] for k in sorted(self.regs.keys())}

    def dump_memory(self, start: int = 0, count: int = 16):
        return self.mem[start:start + count]


# ---------- Example usage ----------

if __name__ == "__main__":
    source = r"""
x3 = 0
while x3 < x1 - 1:
    x4 = 0

    x2 = x1 - x3
    x2 = x2 - 1

    while x4 < x2:
        x5 = x0 + x4
        x6 = mem[x5]

        x7 = x5 + 1
        x7 = mem[x7]

        if x6 > x7:
            mem[x5] = x7

            x7 = x0 + x4
            x7 = x7 + 1
            mem[x7] = x6

        x4 = x4 + 1

    x3 = x3 + 1

x4 = mem[x0]
x5 = 1
x2 = x4
x6 = 1
x3 = 1

while x3 < x1:
    x7 = x0 + x3
    x7 = mem[x7]

    if x7 == x4:
        x5 = x5 + 1

    if x7 != x4:
        if x5 > x6:
            x6 = x5
            x2 = x4

        x4 = x7
        x5 = 1

    x3 = x3 + 1

if x5 > x6:
    x6 = x5
    x2 = x4
"""

    emu = Emulator(debug=False)

    # Set up the same test data
    data = [
        28923, 23130, 4809, 44797, 33345, 26862, 11608, 11608, 30127,
        23130, 50720, 33345, 28923, 44797, 4809, 44797, 3977, 50720,
        19570, 11608, 19570, 33345, 41386, 33345, 50720
    ]

    emu.regs["x0"] = 0
    emu.regs["x1"] = len(data)

    for i, v in enumerate(data):
        emu.mem[i] = v

    emu.run(source)

    print("Registers:")
    for k, v in emu.dump_registers().items():
        print(f"  {k} = {v}")

    print("\nSorted memory:")
    print(emu.dump_memory(0, len(data)))

    print("\nMost frequent value candidate in x2:")
    print(emu.regs["x2"])