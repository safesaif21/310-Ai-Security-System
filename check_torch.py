import torch
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("CUDA version PyTorch was built with:", torch.version.cuda)
print("GPU device name:", torch.cuda.get_device_name(0))

import torchvision
print("TorchVision version:", torchvision.__version__)