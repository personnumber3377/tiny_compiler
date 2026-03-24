mov $0, 7
mov $1, 6
mov $2, 7
mov $3, 10
mov $4, 5
mov $5, 0
mov $6, 2
mov $7, 4
cmp $5, $3
bge >ifend0
add $1, $4, 5
@ifend0:
mov $4, 20
mov $2, 0
@whilestart1:
cmp $2, 2
bge >whileend2
mov $7, 18
add $2, $2, 1
jmp >whilestart1
@whileend2:
mov $2, 0
@whilestart3:
cmp $2, 4
bge >whileend4
add $7, $6, 0
add $2, $2, 1
jmp >whilestart3
@whileend4:
hlt
