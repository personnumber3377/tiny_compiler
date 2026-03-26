mov $7, 7
mov $0, $7
mov $7, 0
mov $1, $7
mov $6, $0
cmp $6, 5
bae >else4
mov $7, 1
mov $1, $7
jmp >ifend5
@else4:
@ifend5:
mov $6, $0
cmp $6, 5
bbe >else6
mov $7, 2
mov $1, $7
jmp >ifend7
@else6:
@ifend7:
hlt
