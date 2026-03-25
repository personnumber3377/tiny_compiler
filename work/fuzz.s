mov $0, 0
mov $1, 5
mov $2, 2
mov $3, 1
mov $4, 5
mov $5, 3
mov $6, 7
mov $7, 8
cmp $3, $1
bge >ifend19
add $7, $4, 1
@ifend19:
mov $7, 13
cmp $5, $5
bge >ifend20
add $2, $7, 2
@ifend20:
hlt
