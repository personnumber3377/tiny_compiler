mov $7, 0
mov $0, $7
mov $7, 10
mov $1, $7
@whilestart8:
mov $6, $0
mov $5, $1
cmp $6, $5
bae >whileend9
jmp >whileend9
jmp >whilestart8
@whileend9:
mov $7, $0
mov $2, $7
hlt
