# image downloader
from PIL import Image
import requests
import pandas as pd
from io import BytesIO
from glob import glob
import pdb


def imgage_from_row(row: pd.Series, objids: list):
    "obtain image from row"
    objid = row["objid"]
    imurl = row["Image"]
    # pdb.set_trace()
    if isinstance(imurl, str):
        if "https" in imurl:
            if objid not in objids:
                resp = requests.get(imurl, stream=True, verify=False)
                img = Image.open(BytesIO(resp.content))
                img.save("images/" + objid + ".png")


if __name__ == "__main__":
    df = pd.read_csv("./EgyptBritishMuseum-2021-03-05CSVUnique.csv")
    imgs = glob("images/*.png")
    imgs = [im[7 : (len(im) - 4)] for im in imgs]
    for i, row in df.iterrows():
        imgage_from_row(row, objids=imgs)
        pass
