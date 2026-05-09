"""
确保SPD模块可用的脚本
在导入ultralytics之前，先动态注册SPD类
"""
import sys
import os

def register_spd_module():
    """
    动态注册SPD模块到ultralytics.nn.modules.block和torch反序列化
    """
    import torch
    import torch.nn as nn
    
    # 定义SPD类
    class SPD(nn.Module):
        def __init__(self, dimension=1):
            super().__init__()
            self.d = dimension

        def forward(self, x):
            return torch.cat([x[..., ::2, ::2], x[..., 1::2, ::2], 
                           x[..., ::2, 1::2], x[..., 1::2, 1::2]], 1)
    
    # 注册到ultralytics模块
    try:
        import ultralytics.nn.modules.block as ultralytics_block
        if not hasattr(ultralytics_block, 'SPD'):
            ultralytics_block.SPD = SPD
            print("✓ SPD模块已注册到ultralytics.nn.modules.block")
    except ImportError:
        # 如果导入失败，先添加项目路径后再试
        project_ultralytics = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ultralytics-main'))
        if project_ultralytics not in sys.path:
            sys.path.insert(0, project_ultralytics)
        import ultralytics.nn.modules.block as ultralytics_block
        if not hasattr(ultralytics_block, 'SPD'):
            ultralytics_block.SPD = SPD
            print("✓ SPD模块已注册到ultralytics.nn.modules.block")
    
    # 重写torch的find_class函数以支持SPD
    import torch.serialization
    original_find_class = None
    
    def custom_find_class(mod_name, class_name):
        if mod_name == 'ultralytics.nn.modules.block' and class_name == 'SPD':
            return SPD
        # 对于其他类，调用原来的find_class
        if original_find_class is not None:
            return original_find_class(mod_name, class_name)
        # 如果没有原来的find_class，使用标准方式
        import importlib
        module = importlib.import_module(mod_name)
        return getattr(module, class_name)
    
    # 保存原始的find_class并替换为我们的版本
    if hasattr(torch.serialization, '_find_class'):
        original_find_class = torch.serialization._find_class
        torch.serialization._find_class = custom_find_class
    elif hasattr(torch.serialization, 'default_restore_location'):
        # 不同版本的torch可能有不同的方式
        pass
    
    # 也注册到builtins以确保万无一失
    import builtins
    if 'SPD' not in dir(builtins):
        builtins.SPD = SPD
    
    print("✓ SPD模块注册完成")
    return True

if __name__ == "__main__":
    register_spd_module()