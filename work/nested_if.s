mov $7, 5
mov $0, $7
mov $7, 10
mov $1, $7
mov $7, 0
mov $2, $7
mov $6, $0
mov $5, $1
cmp $6, $5
bae >ifend14
mov $6, $0
cmp $6, 3
beq >ifend15
mov $7, 42
mov $2, $7
@ifend15:
@ifend14:
hlt
