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


def svg_to_data(svgfile):
    """ function to read svg file and convert it to data to be stored in python files"""
    with open(svgfile, 'rb') as sf:
        svg_buff = io.BytesIO(sf.read())
    return base64.b64encode(zlib.compress(svg_buff.read()))


def data_to_svg(bitmap_data):
    """ function to read data to be stored in python files and convert it to svg file """
    return zlib.decompress(base64.b64decode(bitmap_data))


# svg_file = "icons/Document-open.svg"
# print(png2str(svg_file))

file = "icons/Document-open.svg"
file_tgt = "icons/Document-open_new.svg"
bitmap = svg_to_data(file)
print(bitmap)

b2 = data_to_svg(bitmap)
with open(file_tgt, 'wb') as nf:
    nf.write(b2)
