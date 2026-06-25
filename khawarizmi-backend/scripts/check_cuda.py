import torch

print(f'torch: {torch.__version__}')
print(f'CUDA avail: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'Device: {torch.cuda.get_device_name(0)}')
    print(f'Mem: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
    print(f'CUDA ver: {torch.version.cuda}')
