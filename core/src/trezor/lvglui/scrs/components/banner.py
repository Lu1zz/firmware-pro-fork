from .. import font_GeistRegular26, font_GeistSemiBold26, lv, lv_colors
from ..widgets.style import StyleWrapper
from trezor.lvglui.scrs.common import Anim


class LEVEL:
    DEFAULT = 0
    HIGHLIGHT = 1
    WARNING = 2
    DANGER = 3


class Banner(lv.obj):
    def __init__(self, parent, level: int, text: str, title: str = None) -> None:
        super().__init__(parent)
        self.remove_style_all()
        bg_color, text_color, icon_path = get_style(level)
        self.add_style(
            StyleWrapper()
            .width(456)
            .height(lv.SIZE.CONTENT)
            .text_font(font_GeistRegular26)
            .text_color(text_color)
            .text_letter_space(-1)
            .bg_color(bg_color)
            .bg_opa()
            .radius(40)
            .border_width(0)
            .pad_hor(24)
            .pad_ver(16),
            0,
        )
        self.align(lv.ALIGN.BOTTOM_MID, 0, -8)
        self.lead_icon = lv.img(self)
        self.lead_icon.set_src(icon_path)
        self.lead_icon.set_align(lv.ALIGN.TOP_LEFT)
        if title:
            self.banner_title = lv.label(self)
            self.banner_title.set_size(368, lv.SIZE.CONTENT)
            self.banner_title.set_long_mode(lv.label.LONG.WRAP)
            self.banner_title.add_style(
                StyleWrapper().text_font(font_GeistSemiBold26),
                0,
            )
            self.banner_title.align_to(self.lead_icon, lv.ALIGN.OUT_RIGHT_TOP, 8, 3)
            self.banner_title.set_text(title)
        self.banner_desc = lv.label(self)
        self.banner_desc.set_size(368, lv.SIZE.CONTENT)
        self.banner_desc.set_long_mode(lv.label.LONG.WRAP)
        if title:
            self.banner_desc.align_to(self.banner_title, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 8)
        else:
            self.banner_desc.align_to(self.lead_icon, lv.ALIGN.OUT_RIGHT_TOP, 8, 3)
        self.banner_desc.set_text(text)


def get_style(level: int):
    if level == LEVEL.HIGHLIGHT:
        return (
            lv.color_hex(0x00206B),
            lv.color_hex(0x4178FF),
            "A:/res/banner-icon-blue.png",
        )
    elif level == LEVEL.WARNING:
        return (
            lv.color_hex(0x6B5C00),
            lv.color_hex(0xFFD500),
            "A:/res/banner-icon-yellow.png",
        )
    elif level == LEVEL.DANGER:
        return (
            lv.color_hex(0x640E00),
            lv.color_hex(0xFF1100),
            "A:/res/banner-icon-red.png",
        )
    else:
        return (
            lv_colors.ONEKEY_BLACK_3,
            lv_colors.LIGHT_GRAY,
            "A:/res/banner-icon-gray.png",
        )

class TurboBanner(lv.obj):
    def __init__(self, parent, level: int, text: str, title: str = None, 
                 icon_path="A:/res/banner-icon-gray.png", fade_in=False) -> None:
        super().__init__(parent)
        self.remove_style_all()
        bg_color, text_color, icon_path_none = get_style(level)
        self.add_style(
            StyleWrapper()
            .width(456)
            .height(lv.SIZE.CONTENT)
            .text_font(font_GeistRegular26)
            .text_color(text_color)
            .text_letter_space(-1)
            .bg_color(bg_color)
            .bg_opa()
            .radius(40)
            .border_width(0)
            .pad_hor(24)
            .pad_ver(16),
            0,
        )
        # self.align(lv.ALIGN.BOTTOM_MID, 0, -136)
        self.lead_icon = lv.img(self)
        self.lead_icon.set_src(icon_path)
        self.lead_icon.set_align(lv.ALIGN.TOP_LEFT)
        if title:
            self.banner_title = lv.label(self)
            self.banner_title.set_size(368, lv.SIZE.CONTENT)
            self.banner_title.set_long_mode(lv.label.LONG.WRAP)
            self.banner_title.add_style(
                StyleWrapper().text_font(font_GeistSemiBold26),
                0,
            )
            self.banner_title.align_to(self.lead_icon, lv.ALIGN.OUT_RIGHT_TOP, 8, 3)
            self.banner_title.set_text(title)
        self.banner_desc = lv.label(self)
        self.banner_desc.set_size(368, lv.SIZE.CONTENT)
        self.banner_desc.set_long_mode(lv.label.LONG.WRAP)
        if title:
            self.banner_desc.align_to(self.banner_title, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 8)
        else:
            self.banner_desc.align_to(self.lead_icon, lv.ALIGN.OUT_RIGHT_TOP, 8, 3)
        self.banner_desc.set_text(text)
        

        # 设置位置
        self.target_height = -5
        parent_height = parent.get_height()
        self.set_y(44)
        # self.set_y(parent_height if fade_in else self.target_height)
        print("fade_in", fade_in)
        print("Init set y", self.get_y())
        print("target y", self.target_height)
        print("parent y", parent_height)

        # 初始设置所有元素的透明度
        self.max_opacity = 225
        initial_opacity = 0 if fade_in else self.max_opacity
        self.set_style_bg_opa(initial_opacity, 0)
        self.set_style_text_opa(initial_opacity, 0)
        self.lead_icon.set_style_img_opa(initial_opacity, 0)
        
        # if fade_in:
        self._play_enter_anim(fade_in=fade_in)
    
    def _set_opacity(self, opa):
        """设置所有元素的透明度"""
        try:
            opacity = int(opa)
            self.set_style_bg_opa(opacity, 0)  # 背景
            self.set_style_text_opa(opacity, 0)  # 文字
            self.lead_icon.set_style_img_opa(opacity, 0)  # 图标
        except Exception:
            pass
    
    def _play_enter_anim(self, fade_in=False):
        """播放垂直进入动画和透明度动画"""
        # current_y = self.get_y()
        current_y = 50
        print("Enter anim start y", current_y)
        # 位置动画
        pos_anim = Anim(
            current_y,
            self.target_height,
            self._set_y,
            time=1000 if fade_in else 10,
            delay=0,
        )
        pos_anim.start_anim()
        
        # 透明度动画
        opa_anim = Anim(
            0,
            self.max_opacity,
            self._set_opacity,
            time=800 if fade_in else 30,
            delay=0,
        )
        opa_anim.start_anim()
    
    def _set_y(self, y):
        """动画回调函数"""
        try:
            self.set_y(int(y))
        except Exception:
            pass
    
    def delete(self, delay_ms=0, fade_out=False):
        print("Delete anim start y\n", self.get_y())
        if delay_ms > 0:
            self.del_delayed(delay_ms)
        elif not fade_out:
            super().delete()
        else:
            current_y = self.get_y()
            
            # 创建两个动画
            pos_anim = Anim(
                current_y,
                -50,
                # -self.get_height(),
                self._set_y,
                time=500,
                delay=0,
                del_cb=lambda _: self.del_delayed(100)
            )
            
            opa_anim = Anim(
                self.max_opacity,
                0,
                self._set_opacity,
                time=300,
                delay=0,
            )
            
            pos_anim.start_anim()
            opa_anim.start_anim()
