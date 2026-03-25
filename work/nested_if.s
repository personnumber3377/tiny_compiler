mov $7, 5
mov $0, $7
mov $7, 10
mov $1, $7
mov $7, 0
mov $2, $7
cmp $0, $1
bae >ifend14
cmp $0, 3
beq >ifend15
mov $7, 42
mov $2, $7
@ifend15:
@ifend14:
hlt
