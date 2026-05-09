import pickle
import numpy as np


if __name__=='__main__':
    with open('IEMOCAP_features.pkl','rb') as f:
        data = pickle.load(f)
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    print("原始数据形状:",data.shape)
# 4.对指定行范围进行乘法
    start_row=29734
    end_row=44681
# 确保行号在有效范围内
    start_row = max(0,start_row)
    end_row = min(data.shape[0],end_row)
# 对指定行乘以0.5
    data[start_row:end_row+1] *= 0.5
#5.保存处理后的数据
    with open('IEMOCAP_features_new.pkl', 'wb') as f:
        pickle.dump(data,f)