from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

from kivy.graphics.texture import Texture

def Img_To_Texture(img):
    texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr', bufferfmt='ubyte') # BGRモードで用意,ubyteはデフォルト引数なので指定なくてもよい
    texture.blit_buffer(img.tostring(),colorfmt='bgr', bufferfmt='ubyte')  # ★ここもここもBGRで指定しないとRGBになって色の表示がおかしくなる
    texture.flip_vertical()    # 画像を上下反転する
    return texture
