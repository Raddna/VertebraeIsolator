import numpy as np
import sys

class Masked_volume:

    def __init__(self,img,mask,center):
        """Apply a mask over an image to yield an volumetric image over the masked section

        Keyword arguments:
        img -- The nparray image that is to be masked
        mask -- The nparray image of the mask
        """
        self.img=img
        self.mask=mask
        self.size=img.shape
        self.active=False
        self.masked_image=np.zeros(self.size)
        self.values=list()

        if self.img.shape != self.mask.shape:
            print("ERROR: Mask and image size differs! ")
            sys.exit()

        for y in range(self.size[0]):
            for x in range(center-20, center+20):
                for z in range(self.size[2]):

                    if self.mask[y, x, z] == 0:
                        continue
                    else:
                        self.masked_image[y, x, z] = self.img[y, x, z]
                        self.values.append(self.img[y, x, z])

    def Switch_active_status(self):
        if self.active==False:
            self.active=True
        elif self.active==True:
            self.active=False

    def Get_masked_image(self):
        return self.masked_image

    def Get_active_status(self):
        return self.active

    def Get_list_of_values(self):
        return self.values
            


        
