mov $7, 7
mov $0, $7
mov $7, 0
mov $1, $7
cmp $0, 5
bae >ifend3
mov $7, 1
mov $1, $7
@ifend3:
cmp $0, 5
bbe >ifend4
mov $7, 2
mov $1, $7
@ifend4:
hlt
