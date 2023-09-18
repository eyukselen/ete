import io
import zlib
import base64
import wx
from wx.svg import SVGimage


app = wx.App()


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
    """ function to read svg file and convert it
    to data to be stored in python files"""
    with open(svgfile, 'rb') as sf:
        svg_buff = io.BytesIO(sf.read())
    return base64.b64encode(zlib.compress(svg_buff.read()))


def data_to_svg(bitmap_data):
    """ function to read data to be stored in
    python files and convert it to svg file """
    return zlib.decompress(base64.b64decode(bitmap_data))


def get_svg_icon(svg_bytes, icon_size):
    with io.BytesIO(zlib.decompress(base64.b64decode(svg_bytes))) as stream:
        bmp = SVGimage.CreateFromBytes(
            stream.read()).ConvertToScaledBitmap(icon_size)
    return bmp
