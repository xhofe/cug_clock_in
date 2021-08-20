from PIL import Image,ImageSequence
import io
import pytesseract
import requests

def gif_to_png(gif):
  png = Image.new('RGB',gif.size,(255,255,255))
  for frame in ImageSequence.Iterator(gif):
    px = frame.load()
    for x in range(gif.size[0]):
      for y in range(gif.size[1]):
        if (px[x,y] < 250):
          png.putpixel((x,y),px[x,y])
  return png

def file_gif_to_png(file_path):
  gif = Image.open(file_path)
  gif_to_png(gif).save(file_path.replace('.gif','.png'))


def add_margin(pil_img, top, right, bottom, left, color):
        width, height = pil_img.size
        new_width = width + right + left
        new_height = height + top + bottom
        result = Image.new('RGBA', (new_width, new_height), color)
        result.paste(pil_img, (left, top))
        return result

def ocr(content):
  """
  OCR Engine modes:
  　　　　0 Legacy engine only.
  　　　　1 Neural nets LSTM engine only.
  　　　　2 Legacy + LSTM engines.
  　　　　3 Default, based on what is available.

  Page segmentation modes:
  　　　　0 Orientation and script detection (OSD) only.
  　　　　1 Automatic page segmentation with OSD.
  　　　　2 Automatic page segmentation, but no OSD, or OCR.
  　　　　3 Fully automatic page segmentation, but no OSD. (Default)
  　　　　4 Assume a single column of text of variable sizes.
  　　　　5 Assume a single uniform block of vertically aligned text.
  　　　　6 Assume a single uniform block of text.
  　　　　7 Treat the image as a single text line.
  　　　　8 Treat the image as a single word.
  　　　　9 Treat the image as a single word in a circle.
  　　　　10 Treat the image as a single character.
  　　　　11 Sparse text. Find as much text as possible in no particular order.
  　　　　12 Sparse text with OSD.
  　　　　13 Raw line. Treat the image as a single text line,
  　　　　 bypassing hacks that are Tesseract-specific.
  """

  im = Image.open(io.BytesIO(content))
  threshold = 230
  # gif 验证码，第一张具有所有信息
  im.seek(im.tell() + 1)
  # 二值化并且增加 padding 使识别更准确
  bi_im = im.convert("L").point(lambda p: p > threshold and 255)
  bi_im = add_margin(bi_im, 0, 0, 0, int(bi_im.size[0] * 0.1), (255, 255, 255))
  bi_im.save("temp.png")
  result = pytesseract.image_to_string(bi_im,config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
  return result

def notic(key,msg):
  if key:
    requests.get('https://qmsg.zendee.cn/send/{}?msg={}'.format(key,msg))

def get_sjd():
  import datetime
  d_time0 = datetime.datetime.strptime(str(datetime.datetime.now().date())+'05:00', '%Y-%m-%d%H:%M')
  d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date())+'11:30', '%Y-%m-%d%H:%M')
  d_time2 = datetime.datetime.strptime(str(datetime.datetime.now().date())+'17:30', '%Y-%m-%d%H:%M')
  d_time3 = datetime.datetime.strptime(str(datetime.datetime.now().date())+'23:30', '%Y-%m-%d%H:%M')
  now = datetime.datetime.now()
  if now < d_time0:
    return '0'
  elif now <= d_time1:
    return '1'
  elif now <= d_time2:
    return '2'
  elif now <= d_time3:
    return '3'
  else:
    return '0'

if __name__ == '__main__':
  print(get_sjd())