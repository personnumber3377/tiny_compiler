mov $7, 5
mov $0, $7
mov $7, 10
mov $1, $7
mov $7, 0
mov $2, $7
mov $6, $0
mov $5, $1
cmp $6, $5
bae >else28
mov $6, $0
cmp $6, 3
beq >else30
mov $7, 42
mov $2, $7
jmp >ifend31
@else30:
@ifend31:
jmp >ifend29
@else28:
@ifend29:
hlt
