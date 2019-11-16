from data import *
from matplotlib import pyplot as plt
import cv2
from data.SIXray import SIXrayDetection, XRAY_ROOT
from train import args
from utils import SSDAugmentation

test_set = SIXrayDetection(XRAY_ROOT, image_sets=args.imagesetfile, transform=SSDAugmentation(voc['min_dim'],MEANS))
img_id = '00000009'
image = test_set.pull_image(img_id)
annos = test_set.pull_annotation(img_id)

for anno in annos:
    cv2.rectangle(image, anno[1], anno[2], (0, 0, 255), 2)
    cv2.putText(image, 'P_Battery_Core', (int(631), int(700) - 5), 0,
                0.6, (0, 0, 255), 2)

plt.figure(figsize=(10, 10))
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
plt.imshow(rgb_image)
plt.show()
