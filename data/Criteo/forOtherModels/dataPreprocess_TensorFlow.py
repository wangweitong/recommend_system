import numpy as np

from data.Criteo.util import *

"""
Data Process for FM, PNN, and DeepFM.

[1] PaddlePaddle implementation of DeepFM for CTR prediction
    https://github.com/PaddlePaddle/models/blob/develop/PaddleRec/ctr/deepfm/data/preprocess.py
"""


def get_train_test_file(file_path, feat_dict_, split_ratio=0.9):
    train_label_fout = open('train_label', 'w')
    train_value_fout = open('train_value', 'w')
    train_idx_fout = open('train_idx', 'w')
    test_label_fout = open('test_label', 'w')
    test_value_fout = open('test_value', 'w')
    test_idx_fout = open('test_idx', 'w')

    categorical_range_  = range(1, 11)
    continuous_range_ = range(11, 19)

    cont_min_ = [1.00000000e+00, 0.00000000e+00, -1.00000000e+00, 1.38888889e-03,
                 -8.70709083e+03, -9.62673000e+05, -1, -4.00000000e+00]
    cont_max_ = [3.02320000e+04, 4.04000000e+02, 9.00000000e+00, 9.85688611e+03,
                 8.72573694e+03, 2.19570650e+06, 9.00000000e+00, 4.00000000e+00]
    cont_diff_ = [cont_max_[i] - cont_min_[i] for i in range(len(cont_min_))]

    # 分割并获取索引以及特征值这些
    def process_line_(line):
        # 用,分割获取每行元素
        features = line.rstrip('\n').split(',')
        feat_idx, feat_value, label = [], [], []

        # MinMax Normalization 对于连续特征 最大最小标准化
        for idx in continuous_range_:
            # 如果特征的值为空则索引为0
            if features[idx] == '':
                # print(idx,features[idx],"0000000000000000000000")
                feat_idx.append(0)
                feat_value.append(0.0)
            else:
                # 否则用索引值代替
                feat_idx.append(feat_dict_[idx])
                # 原来的值
                feat_value.append(features[idx])

        # 处理分类型数据
        for idx in categorical_range_:
            if features[idx] == '' or features[idx] not in feat_dict_:
                feat_idx.append(0)
                feat_value.append(0.0)
            else:
                feat_idx.append(feat_dict_[features[idx]])
                feat_value.append(1.0)
        return feat_idx, feat_value, [int(features[0])]

    # 打开训练文件train.txt
    with open(file_path, 'r') as fin:
        # 遍历行号和每行的值
        for line_idx, line in enumerate(fin):
            # print(line_idx,"----------",line)
            if line_idx % 1000000 == 0:
                print(line_idx)
            # 数据超过某个界限就停止
            if line_idx >= EACH_FILE_DATA_NUM * 10:
                break
            # 给每一行赋值
            feat_idx, feat_value, label = process_line_(line)

            feat_value = ','.join([str(v) for v in feat_value]) + '\n'
            feat_idx = ','.join([str(idx) for idx in feat_idx]) + '\n'
            label = ','.join([str(idx) for idx in label]) + '\n'
            # print("feat_value",feat_value, "feat_idx", feat_idx, "label", label)

            if np.random.random() <= split_ratio:
                train_label_fout.write(label)
                train_idx_fout.write(feat_idx)
                train_value_fout.write(feat_value)
            else:
                test_label_fout.write(label)
                test_idx_fout.write(feat_idx)
                test_value_fout.write(feat_value)

        fin.close()

    train_label_fout.close()
    train_idx_fout.close()
    train_value_fout.close()
    test_label_fout.close()
    test_idx_fout.close()
    test_value_fout.close()


def get_feat_dict():
    freq_ = 10
    dir_feat_dict_ = 'feat_dict_' + str(freq_) + '.pkl2'
    # 确定连续和分类特征的列
    categorical_range_ = range(1, 11)
    continuous_range_ = range(11, 19)

    if os.path.exists(dir_feat_dict_):
        feat_dict = pickle.load(open(dir_feat_dict_, 'rb'))
    else:
        # 设置全局的特征索引，用counter来整
        # print('generate a feature dict')
        # Count the number of occurrences of discrete features
        feat_cnt = Counter()
        with open('../train.txt', 'r') as fin:
            for line_idx, line in enumerate(fin):
                # for test
                # print("line_idx---", line_idx, "line---", line)
                if line_idx >= EACH_FILE_DATA_NUM * 10:
                    break

                if line_idx % EACH_FILE_DATA_NUM == 0:
                    print('generating feature dict', line_idx / 45000000)
                features = line.rstrip('\n').split(',')
                for idx in categorical_range_:
                    if features[idx] == '': continue
                    # print(features[idx], "----categorical_range_333", idx)
                    feat_cnt.update([features[idx]])

        # Only retain discrete features with high frequency
        # 仅保留高频离散特征
        dis_feat_set = set()
        for feat, ot in feat_cnt.items():
            if ot >= freq_:
                dis_feat_set.add(feat)

        # Create a dictionary for continuous and discrete features
        # 创建连续和离散特征的字典
        feat_dict = {}
        tc = 1
        # Continuous features
        # 1 到14 就赋值为原来的列号
        for idx in continuous_range_:
            feat_dict[idx] = tc
            tc += 1
        # Discrete features
        cnt_feat_set = set()
        with open('../train.txt', 'r') as fin:
            for line_idx, line in enumerate(fin):
                # get mini-sample for test
                if line_idx >= EACH_FILE_DATA_NUM * 10:
                    break

                features = line.rstrip('\n').split(',')
                for idx in categorical_range_:
                    if features[idx] == '' or features[idx] not in dis_feat_set:
                        continue
                    if features[idx] not in cnt_feat_set:
                        cnt_feat_set.add(features[idx])
                        feat_dict[features[idx]] = tc
                        tc += 1

        # Save dictionary
        with open(dir_feat_dict_, 'wb') as fout:
            pickle.dump(feat_dict, fout)
        print('args.num_feat ', len(feat_dict) + 1)

    return feat_dict


if __name__ == '__main__':
    feat_dict = get_feat_dict()
    get_train_test_file('../train.txt', feat_dict)
    print('Done!')
