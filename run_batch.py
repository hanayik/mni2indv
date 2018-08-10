import os
import sys
from glob import glob

# 1) set base paths
imgDir = "/Users/thanayik/mni_2_individual/wissdomFolders_croppedz"
mniimg = "/Users/thanayik/mni_2_individual/mni152.nii"
mnianat = "/Users/thanayik/mni_2_individual/mni152.anat"
# 2) list sub folders
subdirs = glob(os.path.join(imgDir,"NS*/"))

for j, sub in enumerate(subdirs):
    T1 = glob(os.path.join(sub, "T1_*.nii"))
    if not T1:
        continue
    T1 = glob(os.path.join(sub, "T1_*.nii"))[0]
    print(T1)
    # python mni2indv.py -anatfile mni152.anat -refimg T1_NS003_POLARz.nii -inimg mni152.nii
    cmd = "python mni2indv.py -anatfile {} -refimg {} -inimg {}".format(
        mnianat,
        T1,
        mniimg
    )
    print(cmd)
    os.system(cmd)
