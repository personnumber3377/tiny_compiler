mov $7, 5
mov $0, $7
mov $7, 5
mov $1, $7
mov $6, $0
mov $5, $1
cmp $6, $5
bne >else24
mov $6, $0
cmp $6, 0
bbe >else26
mov $7, 42
mov $2, $7
jmp >ifend27
@else26:
mov $7, 1
mov $2, $7
@ifend27:
jmp >ifend25
@else24:
mov $7, 0
mov $2, $7
@ifend25:
hlt
