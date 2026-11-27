import psutil 

vm = psutil.virtual_memory()
swap = psutil.swap_memory()

vm_total = vm.total / (1024 ** 2)
vm_used = vm.used / (1024 ** 2)
vm_free = vm.free / (1024 ** 2)
vm_percent = vm.percent

swap_total = swap.total / (1024 ** 2)
swap_used = swap.used / (1024 ** 2)
swap_free = swap.free / (1024 ** 2)
swap_percent = swap.percent

print(f"vm_total={vm_total:.1f} MiB | vm_used={vm_used:.1f} MiB | vm_free={vm_free:.1f} MiB | vm_percent={vm_percent:.1f} % | swap_total={swap_total:.1f} MiB | swap_used={swap_used:.1f} MiB | swap_free={swap_free:.1f} MiB | swap_percent={swap_percent:.1f} %")