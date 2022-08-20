import io
import zlib
import base64
import wx
from wx.svg import SVGimage
from configs import icons

app = wx.App()


def get_icon(name):
    with io.BytesIO(zlib.decompress(base64.b64decode(icons[name]))) as stream:
        icon = wx.Bitmap(wx.Image(stream))
    return icon


def png2str(svg_file):
    img = SVGimage.CreateFromFile(svg_file)
    # bmp = img.ConvertToScaledBitmap(wx.Size(32, 32), window=None)
    # bmp = img.ConvertToBitmap(tx=0.0, ty=0.0, scale=1.0, 
    #                           width=48, height=48, stride=-1)
    bmp = img.ConvertToScaledBitmap(wx.Size(32, 32), None)
    png_file = '.'.join(svg_file.split('.')[:-1]) + '.png'

    bmp.SaveFile(png_file, wx.BITMAP_TYPE_PNG)

    with open(png_file, 'rb') as png_file:
        buff = io.BytesIO(png_file.read())
        res = base64.b64encode(zlib.compress(buff.read()))
    return res


svg_file = "icons\\snip_trash.svg"
print(png2str(svg_file))
