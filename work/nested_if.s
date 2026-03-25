mov $0, 5
mov $1, 10
mov $2, 0
cmp $0, $1
bae >ifend14
cmp $0, 3
beq >ifend15
mov $2, 42
@ifend15:
@ifend14:
hlt
