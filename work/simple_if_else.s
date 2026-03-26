mov $7, 5
mov $0, $7
mov $7, 10
mov $1, $7
mov $6, $0
mov $5, $1
cmp $6, $5
bbe >else34
mov $7, 1
mov $2, $7
jmp >ifend35
@else34:
mov $7, 2
mov $2, $7
@ifend35:
hlt
