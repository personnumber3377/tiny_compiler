mov $7, 5
mov $0, $7
mov $7, 0
mov $2, $7
mov $6, $0
cmp $6, 0
bne >else8
mov $7, 1
mov $2, $7
jmp >ifend9
@else8:
mov $7, 2
mov $2, $7
@ifend9:
hlt
