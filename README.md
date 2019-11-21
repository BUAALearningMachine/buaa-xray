# buaa-xray

机器学习大作业

## 注意事项

+ 训练集和数据集在项目根路径 data_sets 文件夹下
+ 训练好的模型在根目录 weights 文件夹下
+ 测试图片 id 在 img_ids.txt 里

## 模型指标

| mAP    | core_AP | coreless_AP |
| ------ | ------- | ----------- |
| 0.8521 | 0.8581  | 0.8460      |

## References

+  Xinlong Wang, et al. "Repulsion Loss: Detecting Pedestrians in a Crowd." [CVPR2018](https://arxiv.org/abs/1711.07752). 
+  [Pytorch-SSD](https://github.com/amdegroot/ssd.pytorch). 
+  [repulsion_loss_ssd](https://github.com/bailvwangzi/repulsion_loss_ssd)
+  Wei Liu, et al. "SSD: Single Shot MultiBox Detector." [ECCV2016](http://arxiv.org/abs/1512.02325). 