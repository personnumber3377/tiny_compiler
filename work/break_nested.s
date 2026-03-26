mov $7, 0
mov $0, $7
mov $7, 3
mov $1, $7
@whilestart4:
mov $6, $0
mov $5, $1
cmp $6, $5
bae >whileend5
mov $7, 0
mov $2, $7
@whilestart6:
mov $6, $2
cmp $6, 10
bae >whileend7
jmp >whileend7
jmp >whilestart6
@whileend7:
mov $6, $0
add $7, $6, 1
mov $0, $7
jmp >whilestart4
@whileend5:
mov $7, $0
mov $3, $7
hlt
