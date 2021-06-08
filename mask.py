import numpy as np

class Mask:

    def __init__(self, img):
        """Create a mask

        Keyword arguments:
        img -- The nparray image that is to be masked
        """
        self.size=img.shape
        self.checked=np.zeros(img.shape)
        self.img=img

    def reset_checked(self):
        self.checked=np.zeros(self.img.shape)

    def segment(self, x, downmargin, upmargin):
        """Basic threshold segmentation

        Keyword arguments:
        x -- The center position
        downmargin -- Number of pixels in the negative axial direction from the center to be included
        upmargin -- Number of pixels in the positive axial direction from the center to be included
        """
        y=self.size[0]
        z=self.size[2]

        seg=np.zeros(self.img.shape)

        for i in range(y):
            for ii in range(x-upmargin,x+downmargin):
                for iii in range(z):
                    
                    if self.img[i,ii,iii]==0:
                        continue
                    
                    if self.img[i,ii,iii]>=0 and self.checked[i,ii,iii]==0:
                        seg[i,ii,iii]=self.img[i,ii,iii]
                        self.checked[i,ii,iii]=1

        return seg




