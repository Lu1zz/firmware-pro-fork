import utime
import math

from trezor import utils
from trezor.enums import InputScriptType
from trezor.lvglui.scrs.components.button import NormalButton
from trezor.lvglui.scrs.components.pageable import PageAbleMessage

from ..i18n import gettext as _, keys as i18n_keys
from ..lv_colors import lv_colors
from ..lv_symbols import LV_SYMBOLS
from . import (
    font_GeistMono28,
    font_GeistRegular20,
    font_GeistRegular30,
    font_GeistSemiBold26,
    font_GeistRegular26,
    font_GeistSemiBold38,
    font_GeistSemiBold48,
)
from .common import FullSizeWindow, lv
from .components.banner import LEVEL, Banner
from .components.button import ListItemBtn
from .components.container import ContainerFlexCol
from .components.button import ListItemBtn
from .components.listitem import CardHeader, CardItem, DisplayItem
from .components.qrcode import QRCode
from .widgets.style import StyleWrapper

from trezor.enums import InputScriptType

class Address(FullSizeWindow):
    class SHOW_TYPE:
        ADDRESS = 0
        QRCODE = 1

    def __init__(
        self,
        title,
        path,
        address,
        primary_color,
        icon_path: str,
        xpubs=None,
        address_qr=None,
        multisig_index: int | None = 0,
        addr_type=None,
        evm_chain_id: int | None = None,
        qr_first: bool = False,
    ):
        super().__init__(
            title,
            None,
            confirm_text=_(i18n_keys.BUTTON__DONE),
            cancel_text=_(i18n_keys.BUTTON__QRCODE)
            if not qr_first
            else _(i18n_keys.BUTTON__ADDRESS),
            anim_dir=0,
            primary_color=primary_color,
        )
        self.path = path
        self.xpubs = xpubs
        self.multisig_index = multisig_index
        self.address = address
        self.address_qr = address_qr
        self.icon = icon_path
        self.addr_type = addr_type
        self.evm_chain_id = evm_chain_id
        if primary_color:
            self.title.add_style(StyleWrapper().text_color(primary_color), 0)
        self.qr_first = qr_first
        if qr_first:
            self.show_qr_code(self.qr_first)
        else:
            self.show_address(evm_chain_id=evm_chain_id)

    def show_address(self, evm_chain_id: int | None = None):
        self.current = self.SHOW_TYPE.ADDRESS
        if hasattr(self, "qr"):
            self.qr.delete()
            del self.qr
        if hasattr(self, "subtitle"):
            self.subtitle.delete()
            del self.subtitle
        self.btn_no.label.set_text(_(i18n_keys.BUTTON__QRCODE))

        self.item_addr = DisplayItem(self.content_area, None, self.address, radius=40)
        self.item_addr.add_style(StyleWrapper().pad_ver(24), 0)
        self.item_addr.label.add_style(
            StyleWrapper()
            .text_font(font_GeistSemiBold48)
            .text_line_space(-2)
            .text_color(lv_colors.LIGHT_GRAY),
            0,
        )

        self.item_addr.align_to(self.title, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 40)

        self.container = ContainerFlexCol(
            self.content_area, self.item_addr, pos=(0, 8), padding_row=0
        )
        self.container.add_dummy()
        if self.addr_type:
            self.item_type = DisplayItem(
                self.container, _(i18n_keys.LIST_KEY__TYPE__COLON), self.addr_type
            )
        if evm_chain_id:
            self.item_chin_id = DisplayItem(
                self.container,
                _(i18n_keys.LIST_KEY__CHAIN_ID__COLON),
                str(evm_chain_id),
            )
        self.item_path = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__PATH__COLON), self.path
        )
        self.container.add_dummy()
        self.xpub_group = ContainerFlexCol(
            self.content_area,
            self.container,
            pos=(0, 8),
            clip_corner=False,
        )
        for i, xpub in enumerate(self.xpubs or []):
            self.item3 = CardItem(
                self.xpub_group,
                _(i18n_keys.LIST_KEY__XPUB_STR_MINE__COLON).format(i + 1)
                if i == self.multisig_index
                else _(i18n_keys.LIST_KEY__XPUB_STR_COSIGNER__COLON).format(i + 1),
                xpub,
                "A:/res/group-icon-more.png",
            )

    def show_qr_code(self, has_tips: bool = False):
        self.current = self.SHOW_TYPE.QRCODE
        if hasattr(self, "container"):
            self.container.delete()
            del self.container
        if hasattr(self, "xpub_group"):
            self.xpub_group.delete()
            del self.xpub_group
        if hasattr(self, "item_addr"):
            self.item_addr.delete()
            del self.item_addr
        self.btn_no.label.set_text(_(i18n_keys.BUTTON__ADDRESS))
        if has_tips:
            from .components.label import SubTitle

            self.subtitle = SubTitle(
                self.content_area,
                self.title,
                (0, 16),
                _(
                    i18n_keys.CONTENT__RETUNRN_TO_THE_APP_AND_SCAN_THE_SIGNED_TX_QR_CODE_BELOW
                ),
            )
        self.qr = QRCode(
            self.content_area,
            self.address if self.address_qr is None else self.address_qr,
            self.icon,
        )
        self.qr.align_to(
            self.title if not has_tips else self.subtitle,
            lv.ALIGN.OUT_BOTTOM_LEFT,
            0,
            30,
        )

    def eventhandler(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            utils.lcd_resume()
            if target == self.btn_no:
                if self.current == self.SHOW_TYPE.ADDRESS:
                    self.show_qr_code(self.qr_first)
                else:
                    self.show_address(self.evm_chain_id)
            elif target == self.btn_yes:
                self.show_unload_anim()
                self.channel.publish(1)


class BTCDeriveSelectionScreen(FullSizeWindow):
    def __init__(self, prev_scr=None, addr_type=None, net_scr=None, has_taproot=True):
        super().__init__(
            _(i18n_keys.TITLE__SELECT_DERIVATION_PATH),
            None,
            confirm_text="",
            cancel_text="",
            anim_dir=2,
        )
        self.prev_scr = prev_scr
        self.net_scr = net_scr

        self.add_nav_back()

        # Create derivation option buttons
        if has_taproot:
            self.derive_options = [
                ("Nested Segwit", InputScriptType.SPENDP2SHWITNESS),
                ("Taproot", InputScriptType.SPENDTAPROOT),
                ("Native Segwit", InputScriptType.SPENDWITNESS),
                ("Legacy", InputScriptType.SPENDADDRESS),
            ]
        else:
            self.derive_options = [
                ("Nested Segwit", InputScriptType.SPENDP2SHWITNESS),
                ("Native Segwit", InputScriptType.SPENDWITNESS),
                ("Legacy", InputScriptType.SPENDADDRESS),
            ]

        self.container = ContainerFlexCol(self.content_area, self.title, padding_row=2)

        # Create buttons and set checked state
        self.option_btns = []
        for text, type_value in self.derive_options:
            btn = ListItemBtn(
                self.container,
                text,
                has_next=False,
                use_transition=False,
            )
            btn.add_check_img()
            if text == addr_type:
                btn.set_checked()
                self.selected_type = type_value
                self.origin_type = type_value
            self.option_btns.append(btn)

        self.add_event_cb(self.on_nav_back, lv.EVENT.GESTURE, None)

    def on_nav_back(self, event_obj):
        code = event_obj.code
        if code == lv.EVENT.GESTURE:
            _dir = lv.indev_get_act().get_gesture_dir()
            if _dir == lv.DIR.RIGHT:
                lv.event_send(self.nav_back.nav_btn, lv.EVENT.CLICKED, None)

    def eventhandler(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()

        if code == lv.EVENT.CLICKED:
            if utils.lcd_resume():
                return

            if isinstance(target, lv.imgbtn):
                if target == self.nav_back.nav_btn:
                    if self.prev_scr is not None:
                        self.prev_scr.btc_derive_changed(self.selected_type)
                        self.destroy(50)

            else:
                for i, btn in enumerate(self.option_btns):
                    if target == btn:
                        for other_btn in self.option_btns:
                            other_btn.set_uncheck()

                        btn.set_checked()
                        self.selected_type = self.derive_options[i][1]


class ETHDeriveSelectionScreen(FullSizeWindow):
    def __init__(self, prev_scr=None, addr_type=None):
        super().__init__(
            _(i18n_keys.TITLE__SELECT_DERIVATION_PATH),
            None,
            confirm_text="",
            cancel_text="",
            anim_dir=2,
        )
        self.prev_scr = prev_scr

        self.add_nav_back()

        # Create derivation option buttons
        self.derive_options = [
            ("BIP44 Standard", False),
            ("Ledger Live", True),
        ]

        self.container = ContainerFlexCol(self.content_area, self.title, padding_row=2)

        # Create buttons and set checked state
        self.option_btns = []
        for text, type_value in self.derive_options:
            btn = ListItemBtn(
                self.container,
                text,
                has_next=False,
                use_transition=False,
            )
            btn.add_check_img()
            if text == addr_type:
                btn.set_checked()
                self.selected_type = type_value
            self.option_btns.append(btn)

        self.add_event_cb(self.on_nav_back, lv.EVENT.GESTURE, None)

    def on_nav_back(self, event_obj):
        code = event_obj.code
        if code == lv.EVENT.GESTURE:
            _dir = lv.indev_get_act().get_gesture_dir()
            if _dir == lv.DIR.RIGHT:
                lv.event_send(self.nav_back.nav_btn, lv.EVENT.CLICKED, None)

    def eventhandler(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()

        if code == lv.EVENT.CLICKED:
            if utils.lcd_resume():
                return

            if isinstance(target, lv.imgbtn):
                if target == self.nav_back.nav_btn:
                    if self.prev_scr is not None:
                        self.prev_scr.eth_derive_changed(self.selected_type)
                        self.destroy(50)

            else:
                for i, btn in enumerate(self.option_btns):
                    if target == btn:
                        for other_btn in self.option_btns:
                            other_btn.set_uncheck()

                        btn.set_checked()
                        self.selected_type = self.derive_options[i][1]


class ADDRESS_OFFLINE_RETURN_TYPE:
    DONE = 0
    ETH_LEDGER_PATH = 1
    BTC_DERIVE_SCRIPTS = 2


class AddressOffline(FullSizeWindow):
    class SHOW_TYPE:
        ADDRESS = 0
        QRCODE = 1

    def __init__(
        self,
        title,
        address,
        primary_color,
        icon_path: str,
        xpubs=None,
        address_qr=None,
        multisig_index: int | None = 0,
        addr_type=None,
        evm_chain_id: int | None = None,
        qr_first: bool = False,
        network: str = "",
        prev_scr=None,
        account_name: str = "",
    ):
        super().__init__(
            title,
            None,
            confirm_text=_(i18n_keys.BUTTON__DONE),
            cancel_text=_(i18n_keys.BUTTON__QRCODE)
            if not qr_first
            else _(i18n_keys.BUTTON__ADDRESS),
            anim_dir=0,
            primary_color=primary_color,
        )
        self.xpubs = xpubs
        self.multisig_index = multisig_index
        self.address = address
        self.address_qr = address_qr
        self.icon = icon_path
        self.addr_type = addr_type
        self.evm_chain_id = evm_chain_id
        self.network = network
        self.prev_scr = prev_scr
        self.account_name = account_name
        if primary_color:
            self.title.add_style(StyleWrapper().text_color(primary_color), 0)
        self.qr_first = qr_first
        if qr_first:
            self.show_qr_code(self.qr_first)
        else:
            self.show_address(evm_chain_id=evm_chain_id)

    def show_address(self, evm_chain_id: int | None = None):
        self.current = self.SHOW_TYPE.ADDRESS
        if hasattr(self, "qr"):
            self.qr.delete()
            del self.qr
        if hasattr(self, "subtitle"):
            self.subtitle.delete()
            del self.subtitle
        self.btn_no.label.set_text(_(i18n_keys.BUTTON__QRCODE))

        # derive btn
        if self.network in ("Bitcoin", "Ethereum", "Solana", "Litecoin"):
            self.derive_btn = ListItemBtn(
                self.content_area,
                self.addr_type,
                left_img_src="A:/res/branches.png",
                has_next=True,
            )

            self.derive_btn.align_to(self.title, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 40)
            self.derive_btn.set_style_radius(40, 0)
            self.derive_btn.add_style(
                StyleWrapper().bg_color(lv_colors.ONEKEY_GRAY_3),
                0,
            )

            # address
            self.group_address = ContainerFlexCol(
                self.content_area, self.derive_btn, pos=(0, 8), padding_row=0
            )
        else:
            self.group_address = ContainerFlexCol(
                self.content_area,
                self.title,
                lv.ALIGN.OUT_BOTTOM_LEFT,
                pos=(0, 40),
                padding_row=0,
            )
        self.item_group_header = CardHeader(
            self.group_address,
            self.account_name,
            "A:/res/group-icon-wallet.png",
        )
        self.item_group_body = DisplayItem(
            self.group_address,
            None,
            content=self.address,
            font=font_GeistSemiBold48,
        )
        self.group_address.add_dummy()

        if self.network == "Ethereum":
            self.erc20_tips = Banner(
                self.content_area,
                LEVEL.DEFAULT,
                _(i18n_keys.CONTENT__NETWORK_ADDRESS_ETHEREUM),
            )
            self.erc20_tips.align_to(self.group_address, lv.ALIGN.OUT_BOTTOM_MID, 0, 8)
            self.erc20_tips.add_style(
                StyleWrapper().bg_color(lv_colors.ONEKEY_GRAY_3),
                0,
            )

    def show_qr_code(self, has_tips: bool = False):
        self.current = self.SHOW_TYPE.QRCODE
        if hasattr(self, "group_address"):
            self.group_address.delete()
            del self.group_address
        if hasattr(self, "derive_btn"):
            self.derive_btn.delete()
            del self.derive_btn
        if hasattr(self, "erc20_tips"):
            self.erc20_tips.delete()
            del self.erc20_tips
        self.btn_no.label.set_text(_(i18n_keys.BUTTON__ADDRESS))
        if has_tips:
            from .components.label import SubTitle

            self.subtitle = SubTitle(
                self.content_area,
                self.title,
                (0, 16),
                _(
                    i18n_keys.CONTENT__RETUNRN_TO_THE_APP_AND_SCAN_THE_SIGNED_TX_QR_CODE_BELOW
                ),
            )
        self.qr = QRCode(
            self.content_area,
            self.address if self.address_qr is None else self.address_qr,
            self.icon,
        )
        self.qr.align_to(
            self.title if not has_tips else self.subtitle,
            lv.ALIGN.OUT_BOTTOM_LEFT,
            0,
            30,
        )

    def btc_derive_changed(self, new_type):
        self.channel.publish((ADDRESS_OFFLINE_RETURN_TYPE.BTC_DERIVE_SCRIPTS, new_type))
        self.destroy(50)

    def eth_derive_changed(self, new_type):
        self.channel.publish((ADDRESS_OFFLINE_RETURN_TYPE.ETH_LEDGER_PATH, new_type))
        self.destroy(50)

    def eventhandler(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            utils.lcd_resume()
            if target == self.btn_no:
                if self.current == self.SHOW_TYPE.ADDRESS:
                    self.show_qr_code(self.qr_first)
                else:
                    self.show_address(self.evm_chain_id)
            elif target == self.btn_yes:
                self.destroy(50)
                self.channel.publish(ADDRESS_OFFLINE_RETURN_TYPE.DONE)
            elif hasattr(self, "derive_btn") and target == self.derive_btn:
                if self.network == "Bitcoin":
                    BTCDeriveSelectionScreen(
                        self, self.addr_type, self.prev_scr, has_taproot=True
                    )
                elif self.network == "Litecoin":
                    BTCDeriveSelectionScreen(
                        self, self.addr_type, self.prev_scr, has_taproot=False
                    )
                elif self.network in ("Ethereum", "Solana"):
                    ETHDeriveSelectionScreen(self, self.addr_type)
                else:
                    pass


class XpubOrPub(FullSizeWindow):
    def __init__(
        self, title, path, primary_color, icon_path: str, xpub=None, pubkey=None
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__EXPORT),
            _(i18n_keys.BUTTON__CANCEL),
            anim_dir=2,
            icon_path=icon_path,
            primary_color=primary_color,
        )
        self.title.add_style(StyleWrapper().text_color(primary_color), 0)
        self.item_xpub_or_pub = CardItem(
            self.content_area,
            _(i18n_keys.LIST_KEY__XPUB__COLON)
            if xpub
            else _(i18n_keys.LIST_KEY__PUBLIC_KEY__COLON),
            xpub or pubkey,
            "A:/res/group-icon-more.png",
        )
        self.item_xpub_or_pub.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)
        self.container = ContainerFlexCol(
            self.content_area, self.item_xpub_or_pub, pos=(0, 16), padding_row=0
        )
        self.container.add_dummy()
        self.item_path = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__PATH__COLON), path
        )
        self.container.add_dummy()


class Message(FullSizeWindow):
    def __init__(
        self,
        title,
        address,
        message,
        primary_color,
        icon_path,
        verify: bool = False,
        item_other: int | str | None = None,
        item_addr_title: str | None = None,
        item_other_title: str | None = None,
        is_standard: bool = True,
        warning_banner_text: str | None = None,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__VERIFY) if verify else _(i18n_keys.BUTTON__SIGN),
            _(i18n_keys.BUTTON__CANCEL),
            anim_dir=2,
            primary_color=primary_color,
            icon_path=icon_path,
        )
        self.primary_color = primary_color
        self.long_message = False
        self.full_message = message
        if len(message) > 150:
            self.message = message[:147] + "..."
            self.long_message = True
        else:
            self.message = message
        if not is_standard:
            self.warning_banner = Banner(
                self.content_area,
                2,
                warning_banner_text
                or _(i18n_keys.CONTENT__NON_STANDARD_MESSAGE_SIGNATURE),
            )
            self.warning_banner.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)
        self.item_message = CardItem(
            self.content_area,
            _(i18n_keys.LIST_KEY__MESSAGE__COLON),
            self.message,
            "A:/res/group-icon-data.png",
        )
        self.item_message.align_to(
            self.title if is_standard else self.warning_banner,
            lv.ALIGN.OUT_BOTTOM_LEFT,
            0,
            40 if is_standard else 8,
        )
        if self.long_message:
            self.show_full_message = NormalButton(
                self.item_message.content, _(i18n_keys.BUTTON__VIEW_DATA)
            )
            self.show_full_message.set_size(lv.SIZE.CONTENT, 77)
            self.show_full_message.add_style(
                StyleWrapper().text_font(font_GeistSemiBold26), 0
            )
            self.show_full_message.align(lv.ALIGN.CENTER, 0, 0)
            self.show_full_message.remove_style(None, lv.PART.MAIN | lv.STATE.PRESSED)
            self.show_full_message.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)
        self.container = ContainerFlexCol(
            self.content_area, self.item_message, pos=(0, 8), padding_row=0
        )
        self.container.add_dummy()
        if item_other:
            self.item_other = DisplayItem(
                self.container,
                item_other_title or _(i18n_keys.LIST_KEY__CHAIN_ID__COLON),
                str(item_other),
            )
        self.item_addr = DisplayItem(
            self.container,
            _(i18n_keys.LIST_KEY__ADDRESS__COLON)
            if not item_addr_title
            else item_addr_title,
            address,
        )
        self.container.add_dummy()

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.show_full_message:
                PageAbleMessage(
                    _(i18n_keys.TITLE__MESSAGE),
                    self.full_message,
                    None,
                    primary_color=self.primary_color,
                    font=font_GeistMono28,
                    confirm_text=None,
                    cancel_text=None,
                )


class TransactionOverview(FullSizeWindow):
    def __init__(self, title, address, primary_color, icon_path, has_details=None):
        if __debug__:
            self.layout_address = address

        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            anim_dir=2,
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path or "A:/res/evm-eth.png",
        )
        self.group_directions = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            address,
        )
        self.group_directions.add_dummy()

        if has_details:
            self.view_btn = NormalButton(
                self.content_area,
                f"{LV_SYMBOLS.LV_SYMBOL_ANGLE_DOUBLE_DOWN}  {_(i18n_keys.BUTTON__DETAILS)}",
            )
            self.view_btn.set_size(456, 82)
            self.view_btn.add_style(StyleWrapper().text_font(font_GeistSemiBold26), 0)
            self.view_btn.enable()
            self.view_btn.align_to(self.group_directions, lv.ALIGN.OUT_BOTTOM_MID, 0, 8)
            self.view_btn.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.view_btn:
                self.destroy(400)
                self.channel.publish(2)

    if __debug__:

        def read_content(self) -> list[str]:
            return (
                [self.layout_title or ""]
                + [self.layout_subtitle or ""]
                + [self.layout_address or ""]
            )


from trezor.lvglui.scrs.components.banner import TurboBanner
from trezor import loop


class ShowMeter(FullSizeWindow):
    def __init__(
        self,
        title="Turbo Mode",
        primary_color=lv_colors.ONEKEY_GREEN,
        icon_path="A:/res/icon-send.png",
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path=icon_path,
        )
        
        # Create meter widget
        self.meter = lv.meter(self.content_area)
        self.meter.center()
        self.meter.set_size(250, 250)
        self.meter.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)

        # Remove the circle from the middle
        self.meter.remove_style(None, lv.PART.INDICATOR)

        # Add scale
        scale = self.meter.add_scale()
        # self.meter.set_scale_ticks(scale, 11, 2, 10, lv_colors.LIGHT_GRAY)
        # self.meter.set_scale_major_ticks(scale, 1, 2, 30, lv_colors.WHITE, 10)
        self.meter.set_scale_range(scale, 0, 100, 270, 90)

        # Add three arc indicators
        self.indic1 = self.meter.add_arc(scale, 15, lv_colors.RED, 20)
        self.indic2 = self.meter.add_arc(scale, 15, lv_colors.GREEN, 35)
        self.indic3 = self.meter.add_arc(scale, 15, lv_colors.BLUE, 50)
        # Create animations
        self._create_animation(self.indic1, 2000, 500)
        self._create_animation(self.indic2, 1000, 1000)
        self._create_animation(self.indic3, 1000, 2000)

    def _create_animation(self, indic, time_ms, playback_time_ms):
        anim = lv.anim_t()
        anim.init()
        anim.set_values(0, 100)
        anim.set_time(time_ms)
        anim.set_repeat_delay(100)
        anim.set_playback_delay(100)
        anim.set_playback_time(playback_time_ms)
        anim.set_var(indic)
        anim.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
        anim.set_custom_exec_cb(lambda a, val: self.meter.set_indicator_end_value(indic, val))
        lv.anim_t.start(anim)

class ShowCircle(FullSizeWindow):
    def __init__(
        self,
        title="Loading",
        primary_color=lv_colors.ONEKEY_GREEN,
        icon_path="A:/res/icon-send.png",
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path=icon_path,
        )
        
        # 创建中心圆
        self.center_circle = lv.obj(self.content_area)
        self.center_circle.set_size(60, 60)
        self.center_circle.center()
        self.center_circle.add_style(
            StyleWrapper()
            .radius(30)
            .bg_color(primary_color)
            .bg_opa(lv.OPA._40),
            0
        )
        self.center_circle.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 80)
        
        # 创建多个弧形
        self.arcs = []
        arc_count = 4  # 弧形数量
        for i in range(arc_count):
            arc = lv.arc(self.content_area)
            arc.set_size(40, 40)
            arc.set_bg_angles(0, 0)  # 移除背景弧
            arc.set_range(0, 180)    # 设置为半圆
            arc.set_value(180)       # 显示整个半圆
            arc.set_rotation(0)      # 初始旋转角度
            
            # 设置弧形样式
            arc.remove_style(None, lv.PART.KNOB)  # 移除旋钮
            arc.add_style(StyleWrapper().bg_color(lv_colors.RED), lv.PART.INDICATOR)
            
            self.arcs.append(arc)
            
            # 创建环绕动画
            self._create_orbit_animation(arc, i * (360 // arc_count))
            
    def _create_orbit_animation(self, arc, start_angle):
        """创建环绕动画
        
        Args:
            arc: 弧形对象
            start_angle: 初始角度
        """
        # 创建轨道动画
        anim = lv.anim_t()
        anim.init()
        anim.set_var(arc)
        anim.set_values(start_angle, start_angle + 360)  # 完整的圆周运动
        anim.set_time(2000)  # 2秒一圈
        anim.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
        anim.set_repeat_delay(0)
        
        # 自定义动画回调函数
        def anim_cb(arc, value):
            # 计算轨道位置
            radius = 60  # 轨道半径
            angle = math.radians(value)
            center_x = self.center_circle.get_x() + self.center_circle.get_width() // 2
            center_y = self.center_circle.get_y() + self.center_circle.get_height() // 2
            
            x = int(center_x + radius * math.cos(angle) - 20)  # 20是arc宽度的一半
            y = int(center_y + radius * math.sin(angle) - 20)
            
            # 更新位置和旋转
            arc.set_pos(x, y)
            arc.set_angle(value + 90)  # 保持弧形朝向中心
            
        # 使用 set_exec_cb 而不是 set_custom_exec_cb
        anim.set_exec_cb(lambda a, val: anim_cb(arc, val))
        lv.anim_t.start(anim)


class ArcLoader:
    """圆形进度条加载器类"""
    def __init__(
        self,
        parent,
        size=(200, 200),
        pos=(0, 0),
        align=lv.ALIGN.CENTER,
        align_to=None,
        primary_color=lv_colors.ONEKEY_GREEN,
        arc_width=15,
        start_angle=270,
        angle_step=5,
        arc_length=60,  # 新增：弧形长度
    ):
        """初始化加载器
        
        Args:
            parent: 父容器
            size: (width, height) 元组，默认 (200, 200)
            pos: (x, y) 元组，相对于对齐点的偏移，默认 (0, 0)
            align: 对齐方式，默认居中
            align_to: 对齐参考对象，默认None
            primary_color: 主弧形颜色
            arc_width: 弧形宽度，默认15
            start_angle: 起始角度，默认270（12点钟位置）
            timer_period: 定时器周期（毫秒），默认20
            angle_step: 每次更新增加的角度，默认5
            arc_length: 弧形跨越的角度，默认60
        """
        # 创建弧形进度条
        self.arc = lv.arc(parent)
        self.arc.set_size(size[0], size[1])
        if align_to:
            self.arc.align_to(align_to, align, pos[0], pos[1])
        else:
            self.arc.align(align, pos[0], pos[1])
        
        # 设置角度
        self.arc.set_bg_angles(0, 360)
        self.arc.set_angles(start_angle, start_angle + arc_length)
        
        # 移除旋钮
        self.arc.remove_style(None, lv.PART.KNOB)
        
        # 设置主弧形样式
        style_arc = lv.style_t()
        style_arc.init()
        style_arc.set_arc_color(primary_color)
        style_arc.set_arc_width(arc_width)
        self.arc.add_style(style_arc, lv.PART.INDICATOR)
        
        # 设置背景弧形样式（透明）
        style_bg = lv.style_t()
        style_bg.init()
        style_bg.set_arc_opa(lv.OPA.TRANSP)  # 设置为透明
        self.arc.add_style(style_bg, lv.PART.MAIN)
        
        # 初始化状态
        self.current_angle = start_angle
        self.start_angle = start_angle
        self.angle_step = angle_step
        self.arc_length = arc_length
        
        # 创建定时器
        self.timer = lv.timer_create(self.arc_loader_cb, timer_period, None)
        
    def arc_loader_cb(self, timer):
        """弧形加载器回调函数"""
        self.current_angle += self.angle_step
        
        # 同时更新开始和结束角度
        start_angle = self.current_angle
        end_angle = self.current_angle + self.arc_length
        
        self.arc.set_angles(start_angle, end_angle)
        
        # 检查是否完成一圈
        if self.current_angle >= self.start_angle + 360:
            self.current_angle = self.start_angle
            
    def delete(self):
        """删除加载器及其资源"""
        if hasattr(self, 'timer'):
            self.timer._del()
        if hasattr(self, 'arc'):
            self.arc.delete()

# class ShowLoader(FullSizeWindow):
#     def __init__(
#         self,
#         title="Loading",
#         primary_color=lv_colors.ONEKEY_GREEN,
#         icon_path="A:/res/icon-send.png",
#     ):
#         super().__init__(
#             title,
#             None,
#             _(i18n_keys.BUTTON__CONTINUE),
#             _(i18n_keys.BUTTON__REJECT),
#             primary_color=primary_color,
#             icon_path=icon_path,
#         )
        
#         # 创建一个容器来放置所有加载器
#         loader_container = lv.obj(self.content_area)
#         loader_container.set_size(240, 240)  # 使用最大加载器的尺寸
#         loader_container.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 80)
#         loader_container.set_style_bg_opa(0, 0)  # 设置容器背景透明
#         loader_container.set_style_border_width(0, 0)  # 移除边框
#         loader_container.set_style_pad_all(0, 0)  # 移除内边距
        
#         # 创建三个不同大小的加载器，都在容器中居中
#         arc_1 = ArcLoader(
#             parent=loader_container,
#             size=(160, 160),
#             align=lv.ALIGN.CENTER,  # 在容器中居中
#             primary_color=primary_color,
#             arc_width=8,
#             start_angle=270,
#             angle_step=-3,  # 顺时针旋转
#             arc_length=90
#         )
        
#         arc_2 = ArcLoader(
#             parent=loader_container,
#             size=(160, 160),
#             align=lv.ALIGN.CENTER,  # 在容器中居中
#             primary_color=primary_color,
#             arc_width=8,
#             start_angle=90,
#             angle_step=-3,  # 顺时针旋转
#             arc_length=90
#         )
        
#         arc_3 = ArcLoader(
#             parent=loader_container,
#             size=(200, 200),
#             align=lv.ALIGN.CENTER,  # 在容器中居中
#             primary_color=primary_color,
#             arc_width=8,
#             angle_step=3,  # 顺时针旋转
#             arc_length=270
#         )

#         arc_4 = ArcLoader(
#             parent=loader_container,
#             size=(240, 240),
#             align=lv.ALIGN.CENTER,  # 在容器中居中
#             primary_color=primary_color,
#             arc_width=8,
#             start_angle=270,
#             angle_step=4,
#             arc_length=90
#         )
        
#         # 保存加载器引用以便后续清理
#         self.loaders = [arc_1, arc_2, arc_3, arc_4]
        
#     def destroy(self, delay=0):
#         """销毁窗口时清理所有加载器"""
#         if hasattr(self, 'loaders'):
#             for loader in self.loaders:
#                 loader.delete()
#         super().destroy(delay)

class ShowSpeed(FullSizeWindow):
    def __init__(
        self,
        title = "I Show Speed",
        address_from = "0xabcdef",
        address_to = "0x123456789",
        amount = "1111",
        fee_max = "8888",
        is_eip1559=False,
        gas_price=None,
        max_priority_fee_per_gas=None,
        max_fee_per_gas=None,
        total_amount=None,
        primary_color=lv_colors.ONEKEY_GREEN,
        contract_addr=None,
        token_id=None,
        evm_chain_id=None,
        raw_data=None,
        sub_icon_path=None,
        striped=False,
    ):
        super().__init__(
            title="Turbo Mode",
            subtitle=None,
            # _(i18n_keys.BUTTON__CONTINUE),
            # cancel_text=_(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        
        # self.title.align_to(self, lv.ALIGN.TOP_MID, 0, 44)

        # 添加背景图片
        self.content_area.set_size(lv.pct(100), lv.pct(100))
        self.content_area.set_style_max_height(800, 0)
        self.content_area.align(lv.ALIGN.TOP_MID, 0, 0)  # 将y轴偏移改为0
        self.bg_img = lv.img(self.content_area)
        self.bg_img.set_src("A:/assets/wallpaper-0.jpg")
        # self.bg_img.set_src("A:/assets/linebg.jpg")
        self.bg_img.align(lv.ALIGN.CENTER, 0, 0)
        self.bg_img.add_flag(lv.obj.FLAG.FLOATING)  # 让背景浮动，不影响其他元素布局
        # self.bg_img.move_background()
        
        self.title.move_foreground()

        self.primary_color = primary_color
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        
        # Create fixed container for banner
        self.banner_container = lv.obj(self.container)
        self.banner_container.set_size(456, 200)
        self.banner_container.set_style_bg_opa(0, 0)
        self.banner_container.set_style_border_width(0, 0)
        self.banner_container.set_style_pad_all(0, 0)
        self.banner_container.align(lv.ALIGN.TOP_MID, 0, 100)
        
        # Store all parameters to display with their levels
        self.params = [
            ("Send", f"Send {amount} To\n{address_to}", "A:/res/group-icon-directions.png"),
            ("From", address_from, "A:/res/group-icon-wallet.png"),
            ("Maximum Fee", fee_max, "A:/res/group-icon-fees.png"),
            # ("Gas price", gas_price, "A:/res/group-icon-fees.png"),
            ("Priority Fee Per Gas", max_priority_fee_per_gas, "A:/res/group-icon-fees.png"),
            ("Maximum Fee Per Gas", max_fee_per_gas, "A:/res/group-icon-fees.png"),
            ("Total amount", total_amount, "A:/res/group-icon-fees.png"),
            ("Data", "0x07bc1c4f3268fc74b60587e9bb7e01e38a7d8a9a3f51202bf25332aa2c75c64487e9bb7…", "A:/res/group-icon-more.png"),
        ]
        
        # Create initial banner inside the container
        self.info_banner = TurboBanner(
            parent=self.banner_container,
            level=LEVEL.DEFAULT,
            text=self.params[0][1],
            icon_path=self.params[0][2],
            fade_in=True
        )
        self.info_banner.align(lv.ALIGN.TOP_MID, 0, 50)
        
        self.current_param_index = 0
        
        # Add boost button
        self.hold_btn = NormalButton(self.container, "B O O S T")
        self.hold_btn.set_size(250, 250)
        self.hold_btn.align(lv.ALIGN.TOP_MID, 0, 370)
        self.hold_btn.add_style(
            StyleWrapper()
            .bg_color(lv_colors.ONEKEY_TMP)
            .radius(200)
            .text_font(font_GeistSemiBold38),
            # .bg_opa(lv.OPA._90),
            0
            )
        
        
        self.cancel_btn = NormalButton(self.content_area, "Stop")
        self.cancel_btn.set_size(150, 60)
        # self.cancel_btn.align_to(self.hold_btn, lv.ALIGN.OUT_BOTTOM_MID, 0, 200)
        self.cancel_btn.align(lv.ALIGN.TOP_MID, 0, 650)

        self.cancel_btn.add_style(
            StyleWrapper()
            .bg_color(lv_colors.GRAY_1)
            .radius(20)
            .bg_opa(lv.OPA._90)
            .text_font(font_GeistRegular26),
            0
        )
        self.cancel_btn.move_foreground()

        self.cancel_btn.add_event_cb(self.on_cancel_btn_event, lv.EVENT.CLICKED, None)
        # Initialize timer related variables
        self.hold_timer = None
        self.is_holding = False

        # Add long press events
        self.hold_btn.add_event_cb(self.on_hold_btn_event, lv.EVENT.CLICKED, None)
        self.hold_btn.add_event_cb(self.on_hold_btn_event, lv.EVENT.LONG_PRESSED, None)
        self.hold_btn.add_event_cb(self.on_hold_btn_event, lv.EVENT.LONG_PRESSED_REPEAT, None)
        self.hold_btn.add_event_cb(self.on_hold_btn_event, lv.EVENT.RELEASED, None)

        # self.bg_img.move_background()

    def update_info_display(self, fade_in=False, fade_out=False):
        """Update displayed parameter"""
        # print("fade_in 1", fade_in)

        title, value, path = self.params[self.current_param_index]
        
        # Delete old banner
        if hasattr(self, 'info_banner'):
            self.info_banner.delete(fade_out=fade_out)
            
        # Create new banner in the fixed container
        self.info_banner = TurboBanner(
            parent=self.banner_container,
            level=LEVEL.DEFAULT,
            text=f"{title}: {value}" if title!="Send" else value,
            icon_path=path,
            fade_in=fade_in
        )
        self.info_banner.align(lv.ALIGN.TOP_MID, 0, 50)

    def show_next_param(self, fade_in=False, fade_out=False):
        """Show next parameter"""
        # print("fade_in 0", fade_in)
        self.current_param_index += 1
        
        # if self.current_param_index >= len(self.params):
        #     if hasattr(self, "btn_yes"):
        #         lv.event_send(self.btn_yes, lv.EVENT.CLICKED, None)
        #     return
        if self.current_param_index >= len(self.params):
            self.show_unload_anim()
            self.channel.publish(1)
            return
            
        self.update_info_display(fade_in=fade_in, fade_out=fade_out)

    def on_cancel_btn_event(self, event):
        code = event.code
        if code == lv.EVENT.CLICKED:
            self.show_unload_anim()
            self.channel.publish(1)
            return

    def on_hold_btn_event(self, event):
        code = event.code
        current_time = utime.ticks_ms()
        print("\n")
        if code == lv.EVENT.CLICKED:
            print("clicked")
            self.show_next_param(fade_in=True, fade_out=True)
        elif code == lv.EVENT.LONG_PRESSED:
            print("long pressed")
            self.is_holding = True
            self.show_next_param(fade_in=False, fade_out=False)
            self.last_update_time = current_time
        elif code == lv.EVENT.LONG_PRESSED_REPEAT:
            print("long pressed repeat")
            # 检查是否达到最小时间间隔
            if utime.ticks_diff(current_time, self.last_update_time) >= 300:
                self.show_next_param(fade_in=False, fade_out=False)
                self.last_update_time = current_time
        elif code == lv.EVENT.RELEASED:
            self.is_holding = False

class TransactionDetailsETH(FullSizeWindow):
    def __init__(
        self,
        title,
        address_from,
        address_to,
        amount,
        fee_max,
        is_eip1559=False,
        gas_price=None,
        max_priority_fee_per_gas=None,
        max_fee_per_gas=None,
        total_amount=None,
        primary_color=lv_colors.ONEKEY_GREEN,
        contract_addr=None,
        token_id=None,
        evm_chain_id=None,
        raw_data=None,
        sub_icon_path=None,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=sub_icon_path,
        )
        self.primary_color = primary_color
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            address_to,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            address_from,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee_max = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),

            fee_max,
        )
        if not is_eip1559:
            if gas_price:
                self.item_group_body_gas_price = DisplayItem(
                    self.group_fees,
                    _(i18n_keys.LIST_KEY__GAS_PRICE__COLON),
                    gas_price,
                )
        else:  

            self.item_group_body_priority_fee_per_gas = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__PRIORITY_FEE_PER_GAS__COLON),
                max_priority_fee_per_gas,
            )
            self.item_group_body_max_fee_per_gas = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__MAXIMUM_FEE_PER_GAS__COLON),
                max_fee_per_gas,
            )
        if total_amount is None:
            if not contract_addr:  # token transfer
                total_amount = f"{amount}\n{fee_max}"
            else:  # nft transfer
                total_amount = f"{fee_max}"
        self.item_group_body_total_amount = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__TOTAL_AMOUNT__COLON),
            total_amount,
        )
        self.group_fees.add_dummy()

        if contract_addr or evm_chain_id:
            self.group_more = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
            )
            if evm_chain_id:
                self.item_group_body_chain_id = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__CHAIN_ID__COLON),
                    str(evm_chain_id),
                )
            if contract_addr:
                self.item_group_body_contract_addr = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__CONTRACT_ADDRESS__COLON),
                    contract_addr,
                )
                self.item_group_body_token_id = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__TOKEN_ID__COLON),
                    token_id,
                )
            self.group_more.add_dummy()

        if raw_data:
            from trezor import strings

            self.data_str = strings.format_customer_data(raw_data)
            if not self.data_str:
                return
            self.long_data = False
            if len(self.data_str) > 225:
                self.long_data = True
                self.data = self.data_str[:222] + "..."
            else:
                self.data = self.data_str
            self.item_data = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__DATA__COLON),
                self.data,
                "A:/res/group-icon-data.png",
            )
            if self.long_data:
                self.show_full_data = NormalButton(
                    self.item_data.content, _(i18n_keys.BUTTON__VIEW_DATA)
                )
                self.show_full_data.set_size(lv.SIZE.CONTENT, 77)
                self.show_full_data.add_style(
                    StyleWrapper().text_font(font_GeistSemiBold26).pad_hor(24), 0
                )
                self.show_full_data.align(lv.ALIGN.CENTER, 0, 0)
                self.show_full_data.remove_style(None, lv.PART.MAIN | lv.STATE.PRESSED)
                self.show_full_data.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.show_full_data:
                PageAbleMessage(
                    _(i18n_keys.TITLE__VIEW_DATA),
                    self.data_str,
                    None,
                    primary_color=self.primary_color,
                    font=font_GeistMono28,
                    confirm_text=None,
                    cancel_text=None,
                )


class TransactionDetailsBenFen(FullSizeWindow):
    def __init__(
        self,
        title,
        address_from,
        address_to,
        amount,
        fee_max,
        is_eip1559=False,
        gas_price=None,
        max_priority_fee_per_gas=None,
        max_fee_per_gas=None,
        total_amount=None,
        primary_color=lv_colors.ONEKEY_GREEN,
        contract_addr=None,
        token_id=None,
        evm_chain_id=None,
        raw_data=None,
        sub_icon_path=None,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=sub_icon_path,
        )
        self.primary_color = primary_color
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            address_to,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            address_from,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee_max = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),
            fee_max,
        )
        if not is_eip1559:
            if gas_price:
                self.item_group_body_gas_price = DisplayItem(
                    self.group_fees,
                    _(i18n_keys.LIST_KEY__GAS_PRICE__COLON),
                    gas_price,
                )
        else:
            self.item_group_body_priority_fee_per_gas = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__PRIORITY_FEE_PER_GAS__COLON),
                max_priority_fee_per_gas,
            )
            self.item_group_body_max_fee_per_gas = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__MAXIMUM_FEE_PER_GAS__COLON),
                max_fee_per_gas,
            )
        if amount != "All":
            if total_amount is None:
                if not contract_addr:
                    total_amount = f"{amount}\n{fee_max}"
                else:
                    total_amount = f"{fee_max}"
            self.item_group_body_total_amount = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__TOTAL_AMOUNT__COLON),
                total_amount,
            )

        self.group_fees.add_dummy()

        if contract_addr or evm_chain_id:
            self.group_more = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
            )
            if evm_chain_id:
                self.item_group_body_chain_id = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__CHAIN_ID__COLON),
                    str(evm_chain_id),
                )
            if contract_addr:
                self.item_group_body_contract_addr = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__CONTRACT_ADDRESS__COLON),
                    contract_addr,
                )
                self.item_group_body_token_id = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__TOKEN_ID__COLON),
                    token_id,
                )
            self.group_more.add_dummy()

        if raw_data:
            from trezor import strings

            self.data_str = strings.format_customer_data(raw_data)
            if not self.data_str:
                return
            self.long_data = False
            if len(self.data_str) > 225:
                self.long_data = True
                self.data = self.data_str[:222] + "..."
            else:
                self.data = self.data_str
            self.item_data = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__DATA__COLON),
                self.data,
                "A:/res/group-icon-data.png",
            )
            if self.long_data:
                self.show_full_data = NormalButton(
                    self.item_data.content, _(i18n_keys.BUTTON__VIEW_DATA)
                )
                self.show_full_data.set_size(lv.SIZE.CONTENT, 77)
                self.show_full_data.add_style(
                    StyleWrapper().text_font(font_GeistSemiBold26).pad_hor(24), 0
                )
                self.show_full_data.align(lv.ALIGN.CENTER, 0, 0)
                self.show_full_data.remove_style(None, lv.PART.MAIN | lv.STATE.PRESSED)
                self.show_full_data.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.show_full_data:
                PageAbleMessage(
                    _(i18n_keys.TITLE__VIEW_DATA),
                    self.data_str,
                    None,
                    primary_color=self.primary_color,
                    font=font_GeistMono28,
                    confirm_text=None,
                    cancel_text=None,
                )


class TransactionDetailsAlepHium(FullSizeWindow):
    def __init__(
        self,
        title,
        address_from,
        address_to,
        subtitle=None,
        amount=None,
        gas_amount=None,
        primary_color=lv_colors.ONEKEY_GREEN,
        token_id=None,
        raw_data=None,
        icon_path=None,
        sub_icon_path=None,
        token_amount=None,
    ):
        super().__init__(
            title,
            subtitle,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path=icon_path,
            sub_icon_path=sub_icon_path,
        )
        self.primary_color = primary_color
        if raw_data:
            self.container = ContainerFlexCol(
                self.content_area, self.subtitle, pos=(0, 40)
            )
        else:
            self.container = ContainerFlexCol(
                self.content_area, self.title, pos=(0, 40)
            )
        if amount:
            self.group_directions = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_directions,
                _(i18n_keys.FORM__DIRECTIONS),
                "A:/res/group-icon-directions.png",
            )
            self.item_group_body_to_addr = DisplayItem(
                self.group_directions,
                _(i18n_keys.LIST_KEY__TO__COLON),
                address_to,
            )
            self.item_group_body_from_addr = DisplayItem(
                self.group_directions,
                _(i18n_keys.LIST_KEY__FROM__COLON),
                address_from,
            )
            self.group_directions.add_dummy()

        if token_amount:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.SUBTITLE__ADA_TX_CONTAINS_TOKEN),
                "A:/res/notice.png",
            )
            self.group_amounts.add_dummy()
            self.group_directions = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_directions,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-directions.png",
            )
            self.item_group_body_to_addr = DisplayItem(
                self.group_directions,
                _(i18n_keys.LIST_KEY__TOKEN_ID__COLON),
                token_id,
            )
            self.item_group_body_from_addr = DisplayItem(
                self.group_directions,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                str(token_amount),
            )
            self.group_directions.add_dummy()

            self.group_directions = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_directions,
                _(i18n_keys.FORM__DIRECTIONS),
                "A:/res/group-icon-directions.png",
            )
            self.item_group_body_to_addr = DisplayItem(
                self.group_directions,
                _(i18n_keys.LIST_KEY__TO__COLON),
                address_to,
            )
            self.item_group_body_from_addr = DisplayItem(
                self.group_directions,
                _(i18n_keys.LIST_KEY__FROM__COLON),
                address_from,
            )
            self.group_directions.add_dummy()

        if gas_amount:
            self.group_fees = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
            )
            self.item_group_body_gas_price = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__TRANSACTION_FEE__COLON),
                gas_amount,
            )

        if raw_data:
            from trezor import strings

            self.data_str = strings.format_customer_data(raw_data)
            if not self.data_str:
                return
            self.long_data = False
            if len(self.data_str) > 225:
                self.long_data = True
                self.data = self.data_str[:222] + "..."
            else:
                self.data = self.data_str

            self.item_data = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__DATA__COLON),
                self.data,
                "A:/res/group-icon-data.png",
            )

            if self.long_data:
                self.show_full_data = NormalButton(
                    self.item_data.content, _(i18n_keys.BUTTON__VIEW_DATA)
                )
                self.show_full_data.set_size(lv.SIZE.CONTENT, 77)
                self.show_full_data.add_style(
                    StyleWrapper().text_font(font_GeistSemiBold26).pad_hor(24), 0
                )
                self.show_full_data.align(lv.ALIGN.CENTER, 0, 0)
                self.show_full_data.remove_style(None, lv.PART.MAIN | lv.STATE.PRESSED)
                self.show_full_data.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.show_full_data:
                PageAbleMessage(
                    _(i18n_keys.TITLE__VIEW_DATA),
                    self.data_str,
                    None,
                    primary_color=self.primary_color,
                    font=font_GeistMono28,
                    confirm_text=None,
                    cancel_text=None,
                )


class ContractDataOverview(FullSizeWindow):
    def __init__(self, title, description, data, primary_color):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            anim_dir=0,
        )
        self.primary_color = primary_color
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item_size = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__SIZE__COLON), description
        )
        self.container.add_dummy()

        self.data_str = data
        self.long_data = False
        if len(self.data_str) > 225:
            self.long_data = True
            self.data = self.data_str[:222] + "..."
        else:
            self.data = self.data_str
        self.item_data = CardItem(
            self.content_area,
            _(i18n_keys.LIST_KEY__DATA__COLON),
            self.data,
            "A:/res/group-icon-data.png",
        )
        self.item_data.align_to(self.container, lv.ALIGN.OUT_BOTTOM_MID, 0, 8)
        if self.long_data:
            self.show_full_data = NormalButton(
                self.item_data.content, _(i18n_keys.BUTTON__VIEW_DATA)
            )
            self.show_full_data.set_size(lv.SIZE.CONTENT, 77)
            self.show_full_data.add_style(
                StyleWrapper().text_font(font_GeistSemiBold26).pad_hor(24), 0
            )
            self.show_full_data.align(lv.ALIGN.CENTER, 0, 0)
            self.show_full_data.remove_style(None, lv.PART.MAIN | lv.STATE.PRESSED)
            self.show_full_data.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.show_full_data:
                PageAbleMessage(
                    _(i18n_keys.TITLE__VIEW_DATA),
                    self.data_str,
                    None,
                    primary_color=self.primary_color,
                    font=font_GeistMono28,
                    confirm_text=None,
                    cancel_text=None,
                )


class BlobDisPlay(FullSizeWindow):
    def __init__(
        self,
        title,
        description: str,
        content: str,
        icon_path: str = "A:/res/warning.png",
        anim_dir: int = 1,
        primary_color=lv_colors.ONEKEY_GREEN,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__CANCEL),
            icon_path=icon_path,
            anim_dir=anim_dir,
            primary_color=primary_color or lv_colors.ONEKEY_GREEN,
        )
        self.primary_color = primary_color
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item_data = DisplayItem(self.container, description, content)
        self.container.add_dummy()
        self.long_message = False
        if len(content) > 240:
            self.long_message = True
            self.btn_yes.label.set_text(_(i18n_keys.BUTTON__VIEW))
            self.data = content

    def eventhandler(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.btn_yes:
                if self.long_message:
                    PageAbleMessage(
                        _(i18n_keys.TITLE__MESSAGE),
                        self.data,
                        self.channel,
                        primary_color=self.primary_color,
                    )
                    self.destroy()
                else:
                    self.show_unload_anim()
                    self.channel.publish(1)
            elif target == self.btn_no:
                self.show_dismiss_anim()
                self.channel.publish(0)


class ConfirmMetaData(FullSizeWindow):
    def __init__(self, title, subtitle, description, data, primary_color, icon_path):
        if __debug__:
            self.layout_data = data

        super().__init__(
            title,
            subtitle,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path=icon_path,
        )

        if description:
            self.container = ContainerFlexCol(
                self.content_area, self.subtitle, pos=(0, 40), padding_row=0
            )
            self.container.add_dummy()
            self.item1 = DisplayItem(self.container, description, data)
            self.container.add_dummy()

    if __debug__:

        def read_content(self) -> list[str]:
            return (
                [self.layout_title or ""]
                + [self.layout_subtitle or ""]
                + [self.layout_data or ""]
            )


class TransactionDetailsBTC(FullSizeWindow):
    def __init__(
        self,
        title: str,
        amount: str,
        fee: str,
        total: str,
        primary_color,
        icon_path: str,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
            anim_dir=0,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=8
        )
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()
        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__FEE__COLON),
            fee,
        )
        self.item_group_body_total_amount = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__TOTAL_AMOUNT__COLON),
            total,
        )
        self.group_fees.add_dummy()


class JointTransactionDetailsBTC(FullSizeWindow):
    def __init__(self, title: str, amount: str, total: str, primary_color):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item_spend = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__AMOUNT_YOU_SPEND__COLON), amount
        )
        self.item_total = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__TOTAL_AMOUNT__COLON), total
        )
        self.container.add_dummy()


class ModifyFee(FullSizeWindow):
    def __init__(self, description: str, fee_change: str, fee_new: str, primary_color):
        super().__init__(
            _(i18n_keys.TITLE__MODIFY_FEE),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item_fee_change = DisplayItem(self.container, description, fee_change)
        self.item_fee_new = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__NEW_FEE__COLON), fee_new
        )
        self.container.add_dummy()


class ModifyOutput(FullSizeWindow):
    def __init__(
        self,
        address: str,
        description: str,
        amount_change: str,
        amount_new: str,
        primary_Color,
    ):
        super().__init__(
            _(i18n_keys.TITLE__MODIFY_AMOUNT),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_Color,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item_addr = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__ADDRESS__COLON), address
        )
        self.item_amount_change = DisplayItem(
            self.container, description, amount_change
        )
        self.item_amount_new = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__NEW_AMOUNT__COLON), amount_new
        )
        self.container.add_dummy()


class ConfirmReplacement(FullSizeWindow):
    def __init__(self, title: str, txids: list[str], primary_color):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        for txid in txids:
            self.item_body_tx_id = DisplayItem(
                self.group_directions,
                _(i18n_keys.LIST_KEY__TRANSACTION_ID__COLON),
                txid,
            )
        self.group_directions.add_dummy()


class ConfirmPaymentRequest(FullSizeWindow):
    def __init__(self, title: str, subtitle, amount: str, to_addr: str, primary_color):
        super().__init__(
            title,
            subtitle,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item_to_addr = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__TO__COLON), to_addr
        )
        self.item_amount = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__AMOUNT__COLON), amount
        )
        self.container.add_dummy()


class ConfirmDecredSstxSubmission(FullSizeWindow):
    def __init__(
        self, title: str, subtitle: str, amount: str, to_addr: str, primary_color
    ):
        super().__init__(
            title,
            subtitle,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item_amount = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__AMOUNT__COLON), amount
        )
        self.item_to_addr = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__TO__COLON), to_addr
        )
        self.container.add_dummy()


class ConfirmCoinJoin(FullSizeWindow):
    def __init__(
        self,
        title: str,
        coin_name: str,
        max_rounds: str,
        max_fee_per_vbyte: str,
        primary_color,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item_coin_name = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__COIN_NAME__COLON), coin_name
        )
        self.item_mrc = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__MAXIMUM_ROUNDS__COLON), max_rounds
        )
        self.item_fee_rate = DisplayItem(
            self.container,
            _(i18n_keys.LIST_KEY__MAXIMUM_MINING_FEE__COLON),
            max_fee_per_vbyte,
        )
        self.container.add_dummy()


class ConfirmSignIdentity(FullSizeWindow):
    def __init__(self, title: str, identity: str, subtitle: str | None, primary_color):
        super().__init__(
            title,
            subtitle,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        align_base = self.title if subtitle is None else self.subtitle
        self.container = ContainerFlexCol(
            self.content_area, align_base, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item_id = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__IDENTITY__COLON), identity
        )
        self.container.add_dummy()


class ConfirmProperties(FullSizeWindow):
    def __init__(self, title: str, properties: list[tuple[str, str]], primary_color):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__CANCEL),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        for key, value in properties:
            self.item = DisplayItem(self.container, f"{key.upper()}", value)
        self.container.add_dummy()


class ConfirmTransferBinance(FullSizeWindow):
    def __init__(self, items: list[tuple[str, str, str]], primary_color, icon_path):
        super().__init__(
            _(i18n_keys.TITLE__CONFIRM_TRANSFER),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path=icon_path,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        for key, value, address in items:
            self.item_key = DisplayItem(self.container, key, "")
            self.item_amount = DisplayItem(
                self.container, _(i18n_keys.LIST_KEY__AMOUNT__COLON), value
            )
            self.item_to_addr = DisplayItem(
                self.container, _(i18n_keys.LIST_KEY__TO__COLON), address
            )
        self.container.add_dummy()


class ShouldShowMore(FullSizeWindow):
    def __init__(
        self, title: str, key: str, value: str, button_text: str, primary_color
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__CANCEL),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item = DisplayItem(self.container, f"{key}:", value)
        self.container.add_dummy()
        self.show_more = NormalButton(self.content_area, button_text)
        self.show_more.align_to(self.container, lv.ALIGN.OUT_BOTTOM_MID, 0, 32)
        self.show_more.add_event_cb(self.on_show_more, lv.EVENT.CLICKED, None)

    def on_show_more(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.show_more:
                # 2 means show more
                self.channel.publish(2)
                self.destroy()


class EIP712DOMAIN(FullSizeWindow):
    def __init__(self, title: str, primary_color, icon_path, **kwargs):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__CANCEL),
            anim_dir=2,
            primary_color=primary_color,
            icon_path=icon_path,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        if kwargs.get("name"):
            self.item_name = DisplayItem(
                self.container, "name (string):", kwargs.get("name")
            )
        if kwargs.get("version"):
            self.item_version = DisplayItem(
                self.container, "version (string):", kwargs.get("version")
            )
        if kwargs.get("chainId"):
            self.item_chain_id = DisplayItem(
                self.container, "chainId (uint256):", kwargs.get("chainId")
            )
        if kwargs.get("verifyingContract"):
            self.item_vfc = DisplayItem(
                self.container,
                "verifyingContract (address):",
                kwargs.get("verifyingContract"),
            )
        if kwargs.get("salt"):
            self.item_salt = DisplayItem(
                self.container, "salt (bytes32):", kwargs.get("salt")
            )
        self.container.add_dummy()


class EIP712Warning(FullSizeWindow):
    def __init__(
        self, title: str, warning_level, text, primary_type, primary_color, icon_path
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            anim_dir=2,
            primary_color=primary_color,
            icon_path=icon_path,
        )
        self.warning_banner = Banner(self.content_area, warning_level, text)
        self.warning_banner.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)
        self.container = ContainerFlexCol(
            self.content_area, self.warning_banner, pos=(0, 24), padding_row=0
        )
        self.container.add_dummy(bg_color=lv_colors.ONEKEY_BLACK_3)
        self.primary_type = DisplayItem(
            self.container,
            "PrimaryType:",
            primary_type,
            bg_color=lv_colors.ONEKEY_BLACK_3,
        )
        self.container.add_dummy(bg_color=lv_colors.ONEKEY_BLACK_3)


class TonTransfer(FullSizeWindow):
    def __init__(
        self,
        address_from,
        address_to,
        amount,
        memo,
        primary_color=None,
    ):
        super().__init__(
            _(i18n_keys.TITLE__SIGN_STR_TRANSACTION).format("TON"),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        self.item1 = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__AMOUNT__COLON), amount
        )
        self.item2 = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__TO__COLON), address_to
        )
        self.item3 = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__FROM__COLON), address_from
        )
        if memo:
            self.item4 = DisplayItem(
                self.container, _(i18n_keys.LIST_KEY__MEMO__COLON), memo
            )


class TonTransaction(FullSizeWindow):
    def __init__(
        self,
        title,
        address_from,
        address_to,
        amount,
        fee_max,
        is_eip1559=False,
        gas_price=None,
        max_priority_fee_per_gas=None,
        max_fee_per_gas=None,
        total_amount=None,
        primary_color=lv_colors.ONEKEY_GREEN,
        contract_addr=None,
        token_id=None,
        evm_chain_id=None,
        raw_data=None,
        sub_icon_path=None,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=sub_icon_path,
        )
        self.primary_color = primary_color
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            address_to,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            address_from,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee_max = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),
            fee_max,
        )
        if not is_eip1559:
            if gas_price:
                self.item_group_body_gas_price = DisplayItem(
                    self.group_fees,
                    _(i18n_keys.LIST_KEY__GAS_PRICE__COLON),
                    gas_price,
                )
        else:
            self.item_group_body_priority_fee_per_gas = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__PRIORITY_FEE_PER_GAS__COLON),
                max_priority_fee_per_gas,
            )
            self.item_group_body_max_fee_per_gas = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__MAXIMUM_FEE_PER_GAS__COLON),
                max_fee_per_gas,
            )
        if total_amount is None:
            if not contract_addr:  # token transfer
                total_amount = f"{amount}\n{fee_max}"
            else:  # nft transfer
                total_amount = f"{fee_max}"
        self.item_group_body_total_amount = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__TOTAL_AMOUNT__COLON),
            total_amount,
        )
        self.group_fees.add_dummy()

        if contract_addr or evm_chain_id:
            self.group_more = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
            )
            if evm_chain_id:
                self.item_group_body_chain_id = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__CHAIN_ID__COLON),
                    str(evm_chain_id),
                )
            if contract_addr:
                self.item_group_body_contract_addr = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__CONTRACT_ADDRESS__COLON),
                    contract_addr,
                )
                self.item_group_body_token_id = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__TOKEN_ID__COLON),
                    token_id,
                )
            self.group_more.add_dummy()

        if raw_data:
            from trezor import strings

            self.data_str = strings.format_customer_data(raw_data)
            if not self.data_str:
                return
            self.long_data = False
            if len(self.data_str) > 225:
                self.long_data = True
                self.data = self.data_str[:222] + "..."
            else:
                self.data = self.data_str
            self.item_data = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__DATA__COLON),
                self.data,
                "A:/res/group-icon-data.png",
            )
            if self.long_data:
                self.show_full_data = NormalButton(
                    self.item_data.content, _(i18n_keys.BUTTON__VIEW_DATA)
                )
                self.show_full_data.set_size(lv.SIZE.CONTENT, 77)
                self.show_full_data.add_style(
                    StyleWrapper().text_font(font_GeistSemiBold26).pad_hor(24), 0
                )
                self.show_full_data.align(lv.ALIGN.CENTER, 0, 0)
                self.show_full_data.remove_style(None, lv.PART.MAIN | lv.STATE.PRESSED)
                self.show_full_data.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.show_full_data:
                PageAbleMessage(
                    _(i18n_keys.TITLE__VIEW_DATA),
                    self.data_str,
                    None,
                    primary_color=self.primary_color,
                    font=font_GeistMono28,
                    confirm_text=None,
                    cancel_text=None,
                )


class TonConnect(FullSizeWindow):
    def __init__(
        self,
        doamin,
        address,
        payload,
        primary_color=None,
    ):
        super().__init__(
            _(i18n_keys.TITLE__SIGN_STR_MESSAGE).format("TON"),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        self.item1 = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__DOMAIN__COLON), doamin
        )
        self.item2 = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__ADDRESS__COLON), address
        )
        # self.item3 = DisplayItem(
        #     self.container, _(i18n_keys.LIST_KEY__FROM__COLON), address_from
        # )
        if payload:
            self.item3 = DisplayItem(
                self.container, _(i18n_keys.LIST_KEY__MEMO__COLON), payload
            )


class TonMessage(FullSizeWindow):
    def __init__(
        self,
        title,
        address,
        message,
        domain,
        primary_color,
        icon_path,
        verify: bool = False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__VERIFY) if verify else _(i18n_keys.BUTTON__SIGN),
            _(i18n_keys.BUTTON__CANCEL),
            anim_dir=2,
            primary_color=primary_color,
            icon_path=icon_path,
        )
        self.primary_color = primary_color
        self.long_message = False
        self.full_message = message
        if len(message) > 150:
            self.message = message[:147] + "..."
            self.long_message = True
        else:
            self.message = message
        self.item_message = CardItem(
            self.content_area,
            _(i18n_keys.LIST_KEY__MESSAGE__COLON),
            self.message,
            "A:/res/group-icon-data.png",
        )
        self.item_message.align_to(self.title, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 40)
        if self.long_message:
            self.show_full_message = NormalButton(
                self.item_message.content, _(i18n_keys.BUTTON__VIEW_DATA)
            )
            self.show_full_message.set_size(185, 77)
            self.show_full_message.add_style(
                StyleWrapper().text_font(font_GeistSemiBold26), 0
            )
            self.show_full_message.align(lv.ALIGN.CENTER, 0, 0)
            self.show_full_message.remove_style(None, lv.PART.MAIN | lv.STATE.PRESSED)
            self.show_full_message.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)
        self.container = ContainerFlexCol(
            self.content_area, self.item_message, pos=(0, 8), padding_row=0
        )
        self.container.add_dummy()

        self.item_addr = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__ADDRESS__COLON), address
        )
        self.item_domain = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__DOMAIN__COLON), domain
        )

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.show_full_message:
                PageAbleMessage(
                    _(i18n_keys.TITLE__MESSAGE),
                    self.full_message,
                    None,
                    primary_color=self.primary_color,
                    font=font_GeistMono28,
                    confirm_text=None,
                    cancel_text=None,
                )


class TransactionDetailsTON(FullSizeWindow):
    def __init__(
        self,
        title,
        address_from,
        address_to,
        amount,
        fee_max,
        is_eip1559=False,
        gas_price=None,
        max_priority_fee_per_gas=None,
        max_fee_per_gas=None,
        total_amount=None,
        primary_color=lv_colors.ONEKEY_GREEN,
        contract_addr=None,
        token_id=None,
        evm_chain_id=None,
        raw_data=None,
        is_raw_data=False,
        sub_icon_path=None,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=sub_icon_path,
        )
        self.primary_color = primary_color
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            address_to,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            address_from,
        )
        self.group_directions.add_dummy()

        if contract_addr or evm_chain_id:
            self.group_more = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
            )
            if evm_chain_id:
                self.item_group_body_chain_id = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__CHAIN_ID__COLON),
                    str(evm_chain_id),
                )
            if contract_addr:
                self.item_group_body_contract_addr = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__CONTRACT_ADDRESS__COLON),
                    contract_addr,
                )
                self.item_group_body_token_id = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__TOKEN_ID__COLON),
                    token_id,
                )
            self.group_more.add_dummy()

        if raw_data:
            from trezor import strings

            self.data_str = strings.format_customer_data(raw_data)
            if not self.data_str:
                return
            self.long_data = False
            if len(self.data_str) > 225:
                self.long_data = True
                self.data = self.data_str[:222] + "..."
            else:
                self.data = self.data_str
            self.item_data = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__DATA__COLON)
                if self.data.startswith("b5ee9c72")
                else _(i18n_keys.LIST_KEY__MEMO__COLON),
                self.data,
                "A:/res/group-icon-data.png"
                if self.data.startswith("b5ee9c72")
                else "A:/res/group-icon-more.png",
            )

            if self.long_data:
                self.show_full_data = NormalButton(
                    self.item_data.content, _(i18n_keys.BUTTON__VIEW_DATA)
                )
                self.show_full_data.set_size(lv.SIZE.CONTENT, 77)
                self.show_full_data.add_style(
                    StyleWrapper().text_font(font_GeistSemiBold26).pad_hor(24), 0
                )
                self.show_full_data.align(lv.ALIGN.CENTER, 0, 0)
                self.show_full_data.remove_style(None, lv.PART.MAIN | lv.STATE.PRESSED)
                self.show_full_data.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.show_full_data:
                PageAbleMessage(
                    _(i18n_keys.TITLE__VIEW_DATA),
                    self.data_str,
                    None,
                    primary_color=self.primary_color,
                    font=font_GeistMono28,
                    confirm_text=None,
                    cancel_text=None,
                )


class TransactionDetailsTRON(FullSizeWindow):
    def __init__(
        self,
        title,
        address_from,
        address_to,
        amount,
        fee_max,
        primary_color,
        icon_path,
        total_amount=None,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))

        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()
        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            address_to,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            address_from,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee_max = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),
            fee_max,
        )
        if total_amount is None:
            total_amount = f"{amount}\n{fee_max}"
        self.item_group_body_total = DisplayItem(
            self.group_fees, _(i18n_keys.LIST_KEY__TOTAL_AMOUNT__COLON), total_amount
        )
        self.group_fees.add_dummy()


class TransactionDetailsNear(FullSizeWindow):
    def __init__(
        self,
        title,
        address_from,
        address_to,
        amount,
        primary_color,
        icon_path,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))

        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()
        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            address_to,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            address_from,
        )
        self.group_directions.add_dummy()


class SecurityCheck(FullSizeWindow):
    def __init__(self):
        super().__init__(
            title=_(i18n_keys.TITLE__SECURITY_CHECK),
            subtitle=_(i18n_keys.SUBTITLE__SECURITY_CHECK),
            confirm_text=_(i18n_keys.BUTTON__CONFIRM),
            cancel_text=_(i18n_keys.BUTTON__CANCEL),
            icon_path="A:/res/security-check.png",
            anim_dir=2,
        )


class PassphraseDisplayConfirm(FullSizeWindow):
    def __init__(self, passphrase: str):
        super().__init__(
            title=_(i18n_keys.TITLE__USE_THIS_PASSPHRASE),
            subtitle=_(i18n_keys.SUBTITLE__USE_THIS_PASSPHRASE),
            confirm_text=_(i18n_keys.BUTTON__CONFIRM),
            cancel_text=_(i18n_keys.BUTTON__CANCEL),
            anim_dir=0,
        )

        self.panel = lv.obj(self.content_area)
        self.panel.remove_style_all()
        self.panel.set_size(456, 272)
        self.panel.align_to(self.subtitle, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)

        self.panel.add_style(
            StyleWrapper()
            .bg_color(lv_colors.ONEKEY_BLACK_3)
            .bg_opa()
            .border_width(0)
            .text_font(font_GeistSemiBold38)
            .text_color(lv_colors.LIGHT_GRAY)
            .text_align_left()
            .pad_ver(16)
            .pad_hor(24)
            .radius(40),
            0,
        )
        self.content = lv.label(self.panel)
        self.content.set_size(lv.pct(100), lv.pct(100))
        self.content.set_text(passphrase)
        self.content.set_long_mode(lv.label.LONG.WRAP)
        self.input_count_tips = lv.label(self.content_area)
        self.input_count_tips.align_to(self.panel, lv.ALIGN.OUT_BOTTOM_MID, 0, 8)
        self.input_count_tips.add_style(
            StyleWrapper()
            .text_font(font_GeistRegular20)
            .text_letter_space(-1)
            .text_align_left()
            .text_color(lv_colors.LIGHT_GRAY),
            0,
        )
        self.input_count_tips.set_text(f"{len(passphrase)}/50")

    def show_unload_anim(self):
        self.clean()
        self.destroy(10)


class SolBlindingSign(FullSizeWindow):
    def __init__(self, fee_payer: str, message_hex: str, primary_color, icon_path):
        super().__init__(
            _(i18n_keys.TITLE__VIEW_TRANSACTION),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path=icon_path,
        )
        self.warning_banner = Banner(
            self.content_area, 2, _(i18n_keys.TITLE__UNKNOWN_TRANSACTION)
        )
        self.warning_banner.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)
        self.container = ContainerFlexCol(self.content_area, self.title)
        self.container.align_to(self.warning_banner, lv.ALIGN.OUT_BOTTOM_MID, 0, 8)

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_fee_payer = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FEE_PAYER__COLON),
            fee_payer,
        )
        self.group_directions.add_dummy()

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        self.item_group_body_format = DisplayItem(
            self.group_more,
            _(i18n_keys.LIST_KEY__FORMAT__COLON),
            _(i18n_keys.LIST_VALUE__UNKNOWN__COLON),
        )
        self.item_group_body_message_hex = DisplayItem(
            self.group_more,
            _(i18n_keys.LIST_KEY__MESSAGE_HASH__COLON),
            message_hex,
        )
        self.group_more.add_dummy()


class SolTransfer(FullSizeWindow):
    def __init__(
        self,
        title,
        from_addr: str,
        fee_payer: str,
        to_addr: str,
        amount: str,
        primary_color,
        icon_path,
        striped: bool = False,
    ):
        super().__init__(
            title=title,
            subtitle=None,
            confirm_text=_(i18n_keys.BUTTON__CONTINUE),
            cancel_text=_(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            to_addr,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions, _(i18n_keys.LIST_KEY__FROM__COLON), from_addr
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee_payer = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__FEE_PAYER__COLON),
            fee_payer,
        )
        self.group_fees.add_dummy()


class SolCreateAssociatedTokenAccount(FullSizeWindow):
    def __init__(
        self,
        fee_payer: str,
        funding_account: str,
        associated_token_account: str,
        wallet_address: str,
        token_mint: str,
        primary_color,
    ):
        super().__init__(
            title=_(i18n_keys.TITLE__CREATE_TOKEN_ACCOUNT),
            subtitle=None,
            confirm_text=_(i18n_keys.BUTTON__CONTINUE),
            cancel_text=_(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_body_ata = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__NEW_TOKEN_ACCOUNT),
            associated_token_account,
        )
        self.item_body_owner = DisplayItem(
            self.group_directions, _(i18n_keys.LIST_KEY__OWNER), wallet_address
        )
        self.item_body_mint_addr = DisplayItem(
            self.group_directions, _(i18n_keys.LIST_KEY__MINT_ADDRESS), token_mint
        )
        self.item_body_founder = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FUNDED_BY__COLON),
            funding_account,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee_payer = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__FEE_PAYER__COLON),
            fee_payer,
        )
        self.group_fees.add_dummy()


class SolTokenTransfer(FullSizeWindow):
    def __init__(
        self,
        title,
        from_addr: str,
        to: str,
        amount: str,
        source_owner: str,
        fee_payer: str,
        primary_color,
        icon_path,
        token_mint: str | None = None,
        striped: bool = False,
    ):
        super().__init__(
            title,
            subtitle=None,
            confirm_text=_(i18n_keys.BUTTON__CONTINUE),
            cancel_text=_(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_ata_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO_TOKEN_ACCOUNT__COLON),
            to,
        )
        self.item_group_body_from_ata_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM_TOKEN_ACCOUNT__COLON),
            from_addr,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee_payer = DisplayItem(
            self.group_fees, _(i18n_keys.LIST_KEY__FEE_PAYER__COLON), fee_payer
        )
        self.group_fees.add_dummy()

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        self.item_group_body_signer = DisplayItem(
            self.group_more, _(i18n_keys.LIST_KEY__SIGNER__COLON), source_owner
        )
        if token_mint:
            self.item_group_body_mint_addr = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__MINT_ADDRESS), token_mint
            )
        self.group_more.add_dummy()


class BlindingSignCommon(FullSizeWindow):
    def __init__(self, signer: str, primary_color, icon_path):
        super().__init__(
            _(i18n_keys.TITLE__VIEW_TRANSACTION),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path=icon_path,
        )
        self.warning_banner = Banner(
            self.content_area, 2, _(i18n_keys.TITLE__UNKNOWN_TRANSACTION)
        )
        self.warning_banner.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)
        self.container = ContainerFlexCol(self.content_area, self.title, padding_row=0)
        self.container.align_to(self.warning_banner, lv.ALIGN.OUT_BOTTOM_MID, 0, 24)
        self.container.add_dummy()
        self.item_format = DisplayItem(
            self.container,
            _(i18n_keys.LIST_KEY__FORMAT__COLON),
            _(i18n_keys.LIST_VALUE__UNKNOWN__COLON),
        )
        self.item_signer = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__SIGNER__COLON), signer
        )
        self.container.add_dummy()


class Modal(FullSizeWindow):
    def __init__(
        self,
        title: str | None,
        subtitle: str | None,
        confirm_text: str = "",
        cancel_text: str = "",
        icon_path: str | None = None,
        anim_dir: int = 1,
    ):
        super().__init__(
            title, subtitle, confirm_text, cancel_text, icon_path, anim_dir=anim_dir
        )

    def show_unload_anim(self):
        self.destroy(200)


class AlgoCommon(FullSizeWindow):
    def __init__(self, type: str, primary_color, icon_path):
        super().__init__(
            _(i18n_keys.TITLE__VIEW_TRANSACTION),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path=icon_path,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item_type = DisplayItem(
            self.container,
            _(i18n_keys.LIST_KEY__TYPE__COLON),
            type,
        )
        self.container.add_dummy()


class AlgoPayment(FullSizeWindow):
    def __init__(
        self,
        title,
        sender,
        receiver,
        close_to,
        rekey_to,
        genesis_id,
        note,
        fee,
        amount,
        primary_color,
        icon_path,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.item_group_body_amount = DisplayItem(self.group_amounts, None, amount)
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            receiver,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            sender,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),
            fee,
        )
        self.group_fees.add_dummy()

        if note:
            self.item_note = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__NOTE__COLON),
                note,
                "A:/res/group-icon-data.png",
            )

        if any([close_to, rekey_to, genesis_id]):
            self.group_more = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
            )
            if close_to is not None:
                self.item_close_reminder_to = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__CLOSE_REMAINDER_TO__COLON),
                    close_to,
                )
            if rekey_to is not None:
                self.item_rekey_to = DisplayItem(
                    self.group_more, _(i18n_keys.LIST_KEY__REKEY_TO__COLON), rekey_to
                )
            if genesis_id is not None:
                self.item_genesis_id = DisplayItem(
                    self.group_more, "GENESIS ID:", genesis_id
                )
            self.group_more.add_dummy()


class AlgoAssetFreeze(FullSizeWindow):
    def __init__(
        self,
        sender,
        rekey_to,
        fee,
        index,
        target,
        new_freeze_state,
        genesis_id,
        note,
        primary_color,
    ):
        super().__init__(
            _(i18n_keys.TITLE__SIGN_STR_TRANSACTION).format("ALGO"),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            sender,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),
            fee,
        )
        self.group_fees.add_dummy()

        if note:
            self.item_note = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__NOTE__COLON),
                note,
                "A:/res/group-icon-data.png",
            )

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        self.item_group_body_asset_freeze_state = DisplayItem(
            self.group_more,
            _(i18n_keys.LIST_KEY__FREEZE_ASSET_ID__COLON),
            _(i18n_keys.LIST_VALUE__TRUE)
            if new_freeze_state is True
            else _(i18n_keys.LIST_VALUE__FALSE),
        )
        self.item_group_freeze_account = DisplayItem(
            self.group_more, _(i18n_keys.LIST_KEY__FREEZE_ACCOUNT__COLON), target
        )
        self.item_group_body_asset_id = DisplayItem(
            self.group_more, _(i18n_keys.LIST_KEY__ASSET_ID__COLON), index
        )
        if rekey_to is not None:
            self.item_rekey_to = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__REKEY_TO__COLON), rekey_to
            )
        if genesis_id is not None:
            self.item_genesis_id = DisplayItem(
                self.group_more, "GENESIS ID:", genesis_id
            )
        self.group_more.add_dummy()


class AlgoAssetXfer(FullSizeWindow):
    def __init__(
        self,
        title,
        sender,
        receiver,
        index,
        fee,
        amount,
        close_assets_to,
        revocation_target,
        rekey_to,
        genesis_id,
        note,
        primary_color,
        icon_path,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.item_group_body_amount = DisplayItem(self.group_amounts, None, amount)
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            receiver,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            sender,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),
            fee,
        )
        self.group_fees.add_dummy()

        if note:
            self.item_note = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__NOTE__COLON),
                note,
                "A:/res/group-icon-data.png",
            )

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        if revocation_target is not None:
            self.item_group_body_revocation_addr = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__REVOCATION_ADDRESS__COLON),
                revocation_target,
            )
        self.item_group_body_asset_id = DisplayItem(
            self.group_more, _(i18n_keys.LIST_KEY__ASSET_ID__COLON), index
        )
        if rekey_to is not None:
            self.item_rekey_to = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__REKEY_TO__COLON), rekey_to
            )
        if close_assets_to is not None:
            self.item_close_assets_to = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__CLOSE_ASSET_TO__COLON),
                close_assets_to,
            )
        if genesis_id is not None:
            self.item_genesis_id = DisplayItem(
                self.group_more, "GENESIS ID:", genesis_id
            )
        self.group_more.add_dummy()


class AlgoAssetCfg(FullSizeWindow):
    def __init__(
        self,
        fee,
        sender,
        index,
        total,
        default_frozen,
        unit_name,
        asset_name,
        decimals,
        manager,
        reserve,
        freeze,
        clawback,
        url,
        metadata_hash,
        rekey_to,
        genesis_id,
        note,
        primary_color,
    ):
        super().__init__(
            _(i18n_keys.TITLE__SIGN_STR_TRANSACTION).format("ALGO"),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if url is not None:
            self.banner = Banner(
                self.content_area, 0, _(i18n_keys.LIST_KEY__INTERACT_WITH).format(url)
            )
            self.banner.align(self.lv.ALIGN.TOP_MID, 0, 40)
            self.container.align_to(self.banner, lv.ALIGN.OUT_BOTTOM_MID, 0, 8)

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            sender,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),
            fee,
        )
        self.group_fees.add_dummy()

        if note:
            self.item_note = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__NOTE__COLON),
                note,
                "A:/res/group-icon-data.png",
            )

        if any(
            [
                asset_name,
                index,
                manager,
                reserve,
                freeze,
                clawback,
                default_frozen,
                freeze,
                total,
                decimals,
                unit_name,
                metadata_hash,
                rekey_to,
                genesis_id,
            ]
        ):
            self.group_more = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
            )
            if asset_name is not None:
                self.item_group_body_asset_name = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__ASSET_NAME__COLON),
                    asset_name,
                )
            if unit_name is not None:
                self.item_group_body_unit_name = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__UNIT_NAME__COLON),
                    unit_name,
                )
            if index is not None and index != "0":
                self.item_group_body_asset_id = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__ASSET_ID__COLON),
                    index,
                )
            if clawback is not None:
                self.item_group_body_clawback_addr = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__CLAW_BACK_ADDRESS__COLON),
                    clawback,
                )
            if manager is not None:
                self.item_group_body_manager_addr = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__MANAGER_ADDRESS__COLON),
                    manager,
                )
            if reserve is not None:
                self.item_group_body_reserve_addr = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__RESERVE_ADDRESS__COLON),
                    reserve,
                )
            if default_frozen is not None:
                self.item_group_body_default_frozen = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__FREEZE_ADDRESS__QUESTION),
                    _(i18n_keys.LIST_VALUE__TRUE)
                    if default_frozen is True
                    else _(i18n_keys.LIST_VALUE__FALSE),
                )
            if freeze is not None:
                self.item_group_body_freeze_addr = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__FREEZE_ADDRESS__COLON),
                    freeze,
                )
            if decimals is not None and decimals != "0":
                self.item_group_body_decimals = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__DECIMALS__COLON),
                    decimals,
                )
            if total is not None:
                self.item_group_body_total = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__TOTAL__COLON),
                    total,
                )
            if metadata_hash is not None:
                self.item_group_body_metadata_hash = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__METADATA_HASH__COLON),
                    metadata_hash,
                )
            if rekey_to is not None:
                self.item_rekey_to = DisplayItem(
                    self.group_more, _(i18n_keys.LIST_KEY__REKEY_TO__COLON), rekey_to
                )
            if genesis_id is not None:
                self.item_genesis_id = DisplayItem(
                    self.group_more, "GENESIS ID:", genesis_id
                )
            self.group_more.add_dummy()


class AlgoKeyregOnline(FullSizeWindow):
    def __init__(
        self,
        sender,
        fee,
        votekey,
        selkey,
        sprfkey,
        rekey_to,
        genesis_id,
        note,
        primary_color,
    ):
        super().__init__(
            _(i18n_keys.TITLE__SIGN_STR_TRANSACTION).format("ALGO"),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            sender,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),
            fee,
        )
        self.group_fees.add_dummy()

        if note:
            self.item_note = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__NOTE__COLON),
                note,
                "A:/res/group-icon-data.png",
            )

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        self.item_group_body_vrf_public_key = DisplayItem(
            self.group_more,
            _(i18n_keys.LIST_KEY__VRF_PUBLIC_KEY__COLON),
            selkey,
        )
        self.item_group_body_vote_public_key = DisplayItem(
            self.group_more,
            _(i18n_keys.LIST_KEY__VOTE_PUBLIC_KEY__COLON),
            votekey,
        )
        if sprfkey is not None:
            self.item_group_body_sprf_public_key = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__STATE_PROOF_PUBLIC_KEY__COLON),
                sprfkey,
            )
        if rekey_to is not None:
            self.item_rekey_to = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__REKEY_TO__COLON), rekey_to
            )
        if genesis_id is not None:
            self.item_genesis_id = DisplayItem(
                self.group_more, "GENESIS ID:", genesis_id
            )
        self.group_more.add_dummy()


class AlgoKeyregNonp(FullSizeWindow):
    def __init__(self, sender, fee, nonpart, rekey_to, genesis_id, note, primary_color):
        super().__init__(
            _(i18n_keys.TITLE__SIGN_STR_TRANSACTION).format("ALGO"),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            sender,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),
            fee,
        )
        self.group_fees.add_dummy()

        if note:
            self.item_note = CardItem(
                self.container,
                _(i18n_keys.LIST_KEY__NOTE__COLON),
                note,
                "A:/res/group-icon-data.png",
            )

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        self.item_group_body_nonpart = DisplayItem(
            self.group_more,
            _(i18n_keys.LIST_KEY__NONPARTICIPATION__COLON),
            _(i18n_keys.LIST_VALUE__FALSE)
            if nonpart is True
            else _(i18n_keys.LIST_VALUE__TRUE),
        )
        if rekey_to is not None:
            self.item_rekey_to = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__REKEY_TO__COLON), rekey_to
            )
        self.group_more.add_dummy()


class AlgoApplication(FullSizeWindow):
    def __init__(self, signer: str, primary_color, icon_path):
        super().__init__(
            _(i18n_keys.TITLE__VIEW_TRANSACTION),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path=icon_path,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        self.item1 = DisplayItem(
            self.container,
            _(i18n_keys.LIST_KEY__FORMAT__COLON),
            "Application",
        )
        self.item2 = DisplayItem(
            self.container, _(i18n_keys.LIST_KEY__SIGNER__COLON), signer
        )
        self.container.add_dummy()


class RipplePayment(FullSizeWindow):
    def __init__(
        self,
        title,
        address_from,
        address_to,
        amount,
        fee_max,
        total_amount=None,
        tag=None,
        primary_color=None,
        icon_path=None,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.item_group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            address_to,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            address_from,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_fee = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__MAXIMUM_FEE__COLON),
            fee_max,
        )
        if total_amount is None:
            total_amount = f"{amount}\n{fee_max}"
        self.item_group_body_total_amount = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__TOTAL_AMOUNT__COLON),
            total_amount,
        )
        self.group_fees.add_dummy()

        if tag:
            self.group_more = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
            )
            self.item_group_body_tag = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__DESTINATION_TAG__COLON),
                tag,
            )
            self.group_more.add_dummy()


class NftRemoveConfirm(FullSizeWindow):
    def __init__(self, icon_path):
        super().__init__(
            title=_(i18n_keys.TITLE__REMOVE_NFT),
            subtitle=_(i18n_keys.SUBTITLE__REMOVE_NFT),
            confirm_text=_(i18n_keys.BUTTON__REMOVE),
            cancel_text=_(i18n_keys.BUTTON__CANCEL),
            icon_path=icon_path,
            anim_dir=0,
        )
        self.btn_yes.enable(bg_color=lv_colors.ONEKEY_RED_1, text_color=lv_colors.BLACK)

    def destroy(self, _delay_ms=400):
        self.del_delayed(200)


class FilecoinPayment(FullSizeWindow):
    def __init__(
        self,
        title,
        address_from,
        address_to,
        amount,
        gaslimit,
        gasfeecap=None,
        gaspremium=None,
        total_amount=None,
        primary_color=None,
        icon_path=None,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.item_group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            address_to,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            address_from,
        )
        self.group_directions.add_dummy()

        self.group_fees = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
        )
        self.item_group_body_gas_limit = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__GAS_LIMIT__COLON),
            gaslimit,
        )
        self.item_group_body_gas_cap = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__GAS_FEE_CAP__COLON),
            gasfeecap,
        )
        self.item_group_body_gas_premium = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__GAS_PREMIUM__COLON),
            gaspremium,
        )
        self.item_group_body_total_amount = DisplayItem(
            self.group_fees,
            _(i18n_keys.LIST_KEY__TOTAL_AMOUNT__COLON),
            total_amount,
        )
        self.group_fees.add_dummy()


class CosmosTransactionOverview(FullSizeWindow):
    def __init__(
        self,
        title,
        types,
        value,
        amount,
        address,
        primary_color,
        icon_path,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            anim_dir=2,
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png" if types is None else icon_path,
            sub_icon_path=icon_path if types is None else None,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))

        if types is None:
            if striped:
                self.group_amounts = ContainerFlexCol(
                    self.container, None, padding_row=0, no_align=True
                )
                self.item_group_header = CardHeader(
                    self.group_amounts,
                    _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                    "A:/res/group-icon-amount.png",
                )
                self.item_group_body_amount = DisplayItem(
                    self.group_amounts,
                    None,
                    amount,
                )
                self.group_amounts.add_dummy()

            self.group_directions = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_directions,
                _(i18n_keys.FORM__DIRECTIONS),
                "A:/res/group-icon-directions.png",
            )
            self.item_group_body_to_addr = DisplayItem(
                self.group_directions,
                _(i18n_keys.LIST_KEY__TO__COLON),
                address,
            )
            self.group_directions.add_dummy()
        else:
            self.container.add_style(StyleWrapper().pad_row(0), 0)
            self.container.add_dummy()
            self.item_type = DisplayItem(
                self.container,
                _(i18n_keys.LIST_KEY__TYPE__COLON),
                value,
            )
            self.container.add_dummy()

        self.view_btn = NormalButton(
            self.content_area,
            f"{LV_SYMBOLS.LV_SYMBOL_ANGLE_DOUBLE_DOWN}  {_(i18n_keys.BUTTON__DETAILS)}",
        )
        self.view_btn.set_size(456, 82)
        self.view_btn.add_style(StyleWrapper().text_font(font_GeistSemiBold26), 0)
        self.view_btn.enable()
        self.view_btn.align_to(self.container, lv.ALIGN.OUT_BOTTOM_MID, 0, 16)
        self.view_btn.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.view_btn:
                self.destroy(400)
                self.channel.publish(2)


class CosmosSend(FullSizeWindow):
    def __init__(
        self,
        title,
        chain_id,
        chain_name,
        address_from,
        address_to,
        amount,
        fee,
        memo,
        primary_color=None,
        icon_path=None,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.item_group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                amount,
            )
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            address_to,
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            address_from,
        )
        self.group_directions.add_dummy()

        if fee:
            self.group_fees = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
            )
            self.item_group_body_fee = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__FEE__COLON),
                fee,
            )
            self.group_fees.add_dummy()

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        if chain_name:
            self.item_group_body_chain_name = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__CHAIN_NAME__COLON),
                chain_name,
            )
        else:
            self.item_group_body_chain_id = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__CHAIN_ID__COLON), chain_id
            )
        if memo:
            self.item_group_body_memo = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__MEMO__COLON),
                memo,
            )
        self.group_more.add_dummy()

class CosmosDelegate(FullSizeWindow):
    def __init__(
        self,
        title,
        chain_id,
        chain_name,
        delegator,
        validator,
        amount,
        fee,
        memo,
        primary_color=None,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        self.group_amounts = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_amounts,
            _(i18n_keys.LIST_KEY__AMOUNT__COLON),
            "A:/res/group-icon-amount.png",
        )
        self.item_group_body_amount = DisplayItem(
            self.group_amounts,
            None,
            amount,
        )
        self.group_amounts.add_dummy()

        if fee:
            self.group_fees = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
            )
            self.item_group_body_fee = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__FEE__COLON),
                fee,
            )
            self.group_fees.add_dummy()

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        self.item_group_body_delegator = DisplayItem(
            self.group_more,
            _(i18n_keys.LIST_KEY__DELEGATOR__COLON),
            delegator,
        )
        self.item_group_body_validator = DisplayItem(
            self.group_more,
            _(i18n_keys.LIST_KEY__VALIDATOR__COLON),
            validator,
        )

        if chain_name:
            self.item_group_body_chain_name = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__CHAIN_NAME__COLON),
                chain_name,
            )
        else:
            self.item_group_body_chain_id = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__CHAIN_ID__COLON), chain_id
            )
        if memo:
            self.item_group_body_memo = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__MEMO__COLON),
                memo,
            )
        self.group_more.add_dummy()


class CosmosSignCommon(FullSizeWindow):
    def __init__(
        self,
        chain_id: str,
        chain_name: str,
        signer: str,
        fee: str,
        title: str,
        value: str,
        memo,
        primary_color,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__CANCEL),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if signer:
            self.group_directions = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_directions,
                _(i18n_keys.FORM__DIRECTIONS),
                "A:/res/group-icon-directions.png",
            )
            self.item_group_body_signer = DisplayItem(
                self.group_directions,
                _(i18n_keys.LIST_KEY__SIGNER__COLON),
                signer,
            )
            self.group_directions.add_dummy()

        if fee:
            self.group_fees = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
            )
            self.item_group_body_fee = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__FEE__COLON),
                fee,
            )
            self.group_fees.add_dummy()

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        if chain_name:
            self.item_group_body_chain_name = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__CHAIN_NAME__COLON),
                chain_name,
            )
        else:
            self.item_group_body_chain_id = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__CHAIN_ID__COLON), chain_id
            )
        self.item_group_body_type = DisplayItem(
            self.group_more,
            _(i18n_keys.LIST_KEY__TYPE__COLON),
            value,
        )
        if memo:
            self.item_group_body_memo = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__MEMO__COLON),
                memo,
            )
        self.group_more.add_dummy()


class CosmosSignContent(FullSizeWindow):
    def __init__(
        self,
        msgs_item: dict,
        primary_color,
    ):
        super().__init__(
            _(i18n_keys.TITLE__CONTENT),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__CANCEL),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(
            self.content_area, self.title, pos=(0, 40), padding_row=0
        )
        self.container.add_dummy()
        for key, value in msgs_item.items():
            if len(value) <= 80:
                self.item = DisplayItem(self.container, key, value)
        self.container.add_dummy()


class CosmosLongValue(FullSizeWindow):
    def __init__(
        self,
        title,
        content: str,
        primary_color,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__CANCEL),
            primary_color=primary_color or lv_colors.ONEKEY_GREEN,
        )
        self.primary_color = primary_color
        PageAbleMessage(
            title,
            content,
            self.channel,
            primary_color=self.primary_color,
        )
        self.destroy()


class CosmosSignCombined(FullSizeWindow):
    def __init__(self, chain_id: str, signer: str, fee: str, data: str, primary_color):
        super().__init__(
            _(i18n_keys.TITLE__VIEW_TRANSACTION),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__CANCEL),
            primary_color=primary_color,
        )
        self.primary_color = primary_color
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))
        if signer:
            self.group_directions = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_directions,
                _(i18n_keys.FORM__DIRECTIONS),
                "A:/res/group-icon-directions.png",
            )
            self.item_group_body_signer = DisplayItem(
                self.group_directions,
                _(i18n_keys.LIST_KEY__SIGNER__COLON),
                signer,
            )
            self.group_directions.add_dummy()

        if fee:
            self.group_fees = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
            )
            self.item_group_body_fee = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__FEE__COLON),
                fee,
            )
            self.group_fees.add_dummy()

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        self.item_group_body_chain_id = DisplayItem(
            self.group_more, _(i18n_keys.LIST_KEY__CHAIN_ID__COLON), chain_id
        )
        self.group_more.add_dummy()

        self.long_data = False
        self.data_str = data
        if len(data) > 225:
            self.long_data = True
            self.data = data[:222] + "..."
        else:
            self.data = data
        self.item_data = CardItem(
            self.container,
            _(i18n_keys.LIST_KEY__DATA__COLON),
            self.data,
            "A:/res/group-icon-data.png",
        )
        if self.long_data:
            self.show_full_data = NormalButton(
                self.item_data.content, _(i18n_keys.BUTTON__VIEW_DATA)
            )
            self.show_full_data.set_size(lv.SIZE.CONTENT, 82)
            self.show_full_data.add_style(
                StyleWrapper().text_font(font_GeistSemiBold26).pad_hor(24), 0
            )
            self.show_full_data.align(lv.ALIGN.CENTER, 0, 0)
            self.show_full_data.remove_style(None, lv.PART.MAIN | lv.STATE.PRESSED)
            self.show_full_data.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.show_full_data:
                PageAbleMessage(
                    _(i18n_keys.TITLE__VIEW_DATA),
                    self.data_str,
                    None,
                    primary_color=self.primary_color,
                    font=font_GeistMono28,
                    confirm_text=None,
                    cancel_text=None,
                )


class ConfirmTypedHash(FullSizeWindow):
    def __init__(self, title, icon, domain_hash, message_hash, primary_color):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            icon,
            primary_color=primary_color,
            anim_dir=0,
        )
        self.banner = Banner(
            self.content_area, 2, _(i18n_keys.MSG__SIGNING_MSG_MAY_HAVE_RISK)
        )
        self.banner.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)
        self.container = ContainerFlexCol(self.content_area, self.title, padding_row=0)
        self.container.align_to(self.banner, lv.ALIGN.OUT_BOTTOM_MID, 0, 24)
        self.container.add_dummy()
        self.item_separator_hash = DisplayItem(
            self.container,
            _(i18n_keys.LIST_KEY__DOMAIN_SEPARATOR_HASH__COLON),
            domain_hash,
        )
        self.item_message_hash = DisplayItem(
            self.container,
            _(i18n_keys.LIST_KEY__MESSAGE_HASH__COLON),
            message_hash,
        )
        self.container.add_dummy()


class PolkadotBalances(FullSizeWindow):
    def __init__(
        self,
        title,
        chain_name,
        module,
        method,
        sender,
        dest,
        source,
        balance,
        tip,
        keep_alive,
        primary_color,
        icon_path,
        striped=False,
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__CANCEL),
            primary_color=primary_color,
            icon_path="A:/res/icon-send.png",
            sub_icon_path=icon_path,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 48))
        if striped:
            self.group_amounts = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_amounts,
                _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                "A:/res/group-icon-amount.png",
            )
            self.item_group_body_amount = DisplayItem(
                self.group_amounts,
                None,
                balance,
            )
            self.group_amounts.add_dummy()

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_to_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__TO__COLON),
            dest,
        )

        self.item_group_body_signer = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__SIGNER__COLON),
            sender,
        )
        self.group_directions.add_dummy()

        if tip:
            self.group_fees = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group_fees, _(i18n_keys.FORM__FEES), "A:/res/group-icon-fees.png"
            )
            self.item_group_body_fee = DisplayItem(
                self.group_fees,
                _(i18n_keys.LIST_KEY__TIP__COLON),
                tip,
            )
            self.group_fees.add_dummy()

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        self.item_group_body_chain_name = DisplayItem(
            self.group_more,
            _(i18n_keys.LIST_KEY__CHAIN_NAME__COLON),
            chain_name,
        )
        if source:
            self.item_group_body_source = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__SOURCE_COLON),
                source,
            )
        # if module:
        #     self.item_group_body_module = DisplayItem(
        #         self.group_more,
        #         _(i18n_keys.LIST_KEY__MODULE_COLON),
        #         module,
        #     )
        # if method:
        #     self.item_group_body_method = DisplayItem(
        #         self.group_more,
        #         _(i18n_keys.LIST_KEY__METHOD_COLON),
        #         method,
        #     )
        if keep_alive is not None:
            self.item_group_body_keep_alive = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__KEEP_ALIVE_COLON),
                keep_alive,
            )
        self.group_more.add_dummy()


class TronAssetFreeze(FullSizeWindow):
    def __init__(
        self,
        is_freeze,
        sender,
        resource,
        balance,
        duration,
        receiver,
        lock,
        primary_color,
    ):
        super().__init__(
            _(i18n_keys.TITLE__SIGN_STR_TRANSACTION).format("Tron"),
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
        self.container = ContainerFlexCol(self.content_area, self.title, pos=(0, 40))

        self.group_directions = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_directions,
            _(i18n_keys.FORM__DIRECTIONS),
            "A:/res/group-icon-directions.png",
        )
        self.item_group_body_from_addr = DisplayItem(
            self.group_directions,
            _(i18n_keys.LIST_KEY__FROM__COLON),
            sender,
        )
        self.group_directions.add_dummy()

        self.group_more = ContainerFlexCol(
            self.container, None, padding_row=0, no_align=True
        )
        self.item_group_header = CardHeader(
            self.group_more, _(i18n_keys.FORM__MORE), "A:/res/group-icon-more.png"
        )
        if resource is not None:
            self.item_body_resource = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__RESOURCE_COLON), resource
            )
        if balance:
            if is_freeze:
                self.item_body_freeze_balance = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__FROZEN_BALANCE_COLON),
                    balance,
                )
            else:
                self.item_body_balance = DisplayItem(
                    self.group_more,
                    _(i18n_keys.LIST_KEY__AMOUNT__COLON),
                    balance,
                )
        if duration:
            self.item_body_duration = DisplayItem(
                self.group_more,
                _(i18n_keys.LIST_KEY__FROZEN_DURATION_COLON),
                duration,
            )
        if receiver is not None:
            self.item_body_receiver = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__RECEIVER_ADDRESS_COLON), receiver
            )
        if lock is not None:
            self.item_body_lock = DisplayItem(
                self.group_more, _(i18n_keys.LIST_KEY__LOCK_COLON), lock
            )
        self.group_more.add_dummy()


class UrResponse(FullSizeWindow):
    def __init__(
        self,
        title,
        subtitle,
        qr_code,
        encoder=None,
    ):
        super().__init__(
            title,
            subtitle,
            confirm_text=_(i18n_keys.BUTTON__DONE),
            anim_dir=0,
        )
        self.btn_yes.enable(lv_colors.ONEKEY_GRAY_3, text_color=lv_colors.WHITE)
        import gc

        gc.collect()
        gc.threshold(int(18248 * 1.5))  # type: ignore["threshold" is not a known member of module]
        self.qr_code = qr_code
        self.encoder = encoder
        self.qr = QRCode(
            self.content_area,
            self.qr_code if self.qr_code else encoder.next_part(),  # type: ignore["next_part" is not a known member of "None"]
        )
        self.qr.align_to(self.subtitle, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 30)
        self.content_area.clear_flag(lv.obj.FLAG.SCROLL_ELASTIC)
        self.content_area.clear_flag(lv.obj.FLAG.SCROLL_MOMENTUM)
        self.content_area.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        if encoder is not None:
            from trezor import workflow

            workflow.spawn(self.update_qr())

    def destroy(self, delay_ms=400):
        return self.delete()

    async def update_qr(self):
        from trezor import loop

        while True:
            stop_single = self.request()
            racer = loop.race(stop_single, loop.sleep(100))
            await racer
            if stop_single in racer.finished:
                self.destroy()
                return
            # if self.scrolling:
            #     await loop.sleep(5000)
            #     continue
            qr_data = self.encoder.next_part()  # type: ignore["next_part" is not a known member of "None"]
            self.qr.update(qr_data, len(qr_data))


class ErrorFeedback(FullSizeWindow):
    def __init__(self, title, subtitle, btn_text: str = ""):
        super().__init__(
            title,
            subtitle,
            cancel_text=_(i18n_keys.BUTTON__BACK) if not btn_text else btn_text,
            icon_path="A:/res/danger.png",
        )

    def destroy(self):
        return super().destroy(0)


##################
# misc functions #
##################
class AirgapMode(FullSizeWindow):
    def __init__(self):
        super().__init__(
            _(i18n_keys.TITLE__AIR_GAP_MODE),
            _(i18n_keys.CONTENT__WHAT_DOES_AIR_GAP_MEANS),
            _(i18n_keys.BUTTON__SKIP),
            _(i18n_keys.BUTTON__GO_SETTING),
        )
        self.btn_yes.enable()
        self.btn_no.enable(bg_color=lv_colors.ONEKEY_GREEN, text_color=lv_colors.BLACK)


class AirGapToggleTips(FullSizeWindow):
    def __init__(self, enable, callback_obj=None):
        super().__init__(
            title=_(i18n_keys.TITLE__ENABLE_AIR_GAP)
            if enable
            else _(i18n_keys.TITLE__DISABLE_AIR_GAP),
            subtitle=_(i18n_keys.CONTENT__ARE_YOU_SURE_TO_ENABLE_AIRGAP_MODE)
            if enable
            else _(i18n_keys.CONTENT__ARE_YOU_SURE_TO_DISABLE_AIRGAP_MODE),
            confirm_text=_(i18n_keys.BUTTON__ENABLE)
            if enable
            else _(i18n_keys.BUTTON__DISABLE),
            cancel_text=_(i18n_keys.BUTTON__CANCEL),
            anim_dir=0,
        )
        self.last_click_time = 0
        self.click_interval = 1000
        self.callback_obj = callback_obj

    def eventhandler(self, event_obj):
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, self.last_click_time) < self.click_interval:
            return
        self.last_click_time = current_time
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if utils.lcd_resume():
                return
            elif target == self.btn_no:
                if self.callback_obj:
                    lv.event_send(self.callback_obj, lv.EVENT.CANCEL, None)
                else:
                    self.channel.publish(0)
            elif target == self.btn_yes:
                if self.callback_obj:
                    lv.event_send(self.callback_obj, lv.EVENT.READY, None)
                else:
                    self.channel.publish(1)
            else:
                return
            self.show_dismiss_anim()

    def destroy(self, delay_ms=100):
        return self.del_delayed(100)


class ConnectWalletTutorial(FullSizeWindow):
    def __init__(
        self,
        title: str,
        sub_title,
        steps: list[tuple[str, str]],
        website_url,
        logo_path,
    ):
        super().__init__(
            title,
            sub_title,
            confirm_text=_(i18n_keys.BUTTON__DONE),
            cancel_text=_(i18n_keys.ACTION__LEARN_MORE),
            anim_dir=0,
        )
        self.website_url = website_url
        self.logo_path = logo_path
        self.container = ContainerFlexCol(self.content_area, self.subtitle, pos=(0, 40))
        for i, step in enumerate(steps):
            self.group = ContainerFlexCol(
                self.container, None, padding_row=0, no_align=True
            )
            self.item_group_header = CardHeader(
                self.group,
                step[0],
                f"A:/res/group-icon-num-{i+1}.png",
            )
            self.item_group_body = DisplayItem(
                self.group,
                None,
                step[1],
            )
            self.item_group_body.add_style(
                StyleWrapper().text_color(lv_colors.ONEKEY_GRAY_4), 0
            )
            self.group.add_dummy()

    def eventhandler(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        if code == lv.EVENT.CLICKED:
            if utils.lcd_resume():
                return
            if target == self.btn_yes:
                self.destroy(10)
            elif target == self.btn_no:
                ConnectWalletTutorial.ShowOnlineWebsiteQR(
                    self.website_url, self.logo_path
                )

    class ShowOnlineWebsiteQR(FullSizeWindow):
        def __init__(self, qr_content: str, logo_path):
            super().__init__(
                None,
                None,
                anim_dir=0,
                cancel_text=_(i18n_keys.BUTTON__CLOSE),
            )
            import gc

            gc.collect()
            gc.threshold(int(18248 * 1.5))  # type: ignore["threshold" is not a known member of module]
            self.qr = QRCode(self.content_area, qr_content, logo_path)
            self.qr.align_to(self.content_area, lv.ALIGN.TOP_MID, 0, 16)

            self.desc = lv.label(self.content_area)
            self.desc.set_size(456, lv.SIZE.CONTENT)
            self.desc.set_long_mode(lv.label.LONG.WRAP)
            self.desc.add_style(
                StyleWrapper()
                .text_font(font_GeistRegular30)
                .text_color(lv_colors.LIGHT_GRAY)
                .pad_hor(12)
                .pad_ver(16),
                0,
            )
            self.desc.set_text(
                _(i18n_keys.CONTENT__SCAN_THE_QR_CODE_TO_VIEW_THE_DETAILED_TUTORIAL)
            )
            self.desc.align_to(self.qr, lv.ALIGN.OUT_BOTTOM_MID, 0, 8)

        def eventhandler(self, event_obj):
            code = event_obj.code
            target = event_obj.get_target()
            if code == lv.EVENT.CLICKED:
                if utils.lcd_resume():
                    return
                if target == self.btn_no:
                    self.destroy(10)

import gc
class LoaderManager:
    """加载器管理类，用于管理多个加载器共享一个计时器"""
    def __init__(self, timer_period=30):
        self.loaders = []
        self.timer = lv.timer_create(self.update_all_loaders, timer_period, None)
        
    def add_loader(self, loader):
        """添加一个加载器到管理器"""
        self.loaders.append(loader)
        
    def update_all_loaders(self, timer):
        """更新所有加载器的状态"""
        # if gc.mem_free() < 200000:
        #     print("gc.collect()")
        #     gc.collect()
        
        for loader in self.loaders:
            loader.update()
            
    def delete(self):
        """清理所有资源"""
        if hasattr(self, 'timer'):
            self.timer._del()
        for loader in self.loaders:
            loader.delete()
        self.loaders = []


# class ArcLoader:
#     """圆形进度条加载器类"""
#     def __init__(
#         self,
#         parent,
#         size=(200, 200),
#         pos=(0, 0),
#         align=lv.ALIGN.CENTER,
#         align_to=None,
#         primary_color=lv_colors.ONEKEY_GREEN,
#         arc_width=15,
#         start_angle=270,
#         angle_step=5,
#         arc_length=60,
#     ):
#         # 创建弧形进度条
#         self.arc = lv.arc(parent)
#         self.arc.set_size(size[0], size[1])
#         if align_to:
#             self.arc.align_to(align_to, align, pos[0], pos[1])
#         else:
#             self.arc.align(align, pos[0], pos[1])
        
#         # 设置角度
#         self.arc.set_bg_angles(0, 360)
#         self.arc.set_angles(start_angle, start_angle + arc_length)
        
#         # 移除旋钮
#         self.arc.remove_style(None, lv.PART.KNOB)
        
#         # 设置主弧形样式
#         style_arc = lv.style_t()
#         style_arc.init()
#         style_arc.set_arc_color(primary_color)
#         style_arc.set_arc_width(arc_width)
#         self.arc.add_style(style_arc, lv.PART.INDICATOR)
        
#         # 设置背景弧形样式（透明）
#         style_bg = lv.style_t()
#         style_bg.init()
#         style_bg.set_arc_opa(lv.OPA.TRANSP)
#         self.arc.add_style(style_bg, lv.PART.MAIN)
        
#         # 初始化状态
#         self.current_angle = start_angle
#         self.start_angle = start_angle
#         self.angle_step = angle_step
#         self.arc_length = arc_length
        
#     def update(self):
#         """更新加载器状态"""
#         self.current_angle += self.angle_step
        
#         # 同时更新开始和结束角度
#         # start_angle = self.current_angle
#         # end_angle = self.current_angle + self.arc_length
        
#         # self.arc.set_angles(start_angle, end_angle)
#         self.arc.set_rotation(self.current_angle)
        
#         # 检查是否完成一圈
#         if self.current_angle >= 360:
#             self.current_angle -= 360
            
#     def delete(self):
#         """删除加载器资源"""
#         if hasattr(self, 'arc'):
#             self.arc.delete()


class ArcLoader:
    """圆形进度条加载器类"""
    def __init__(
        self,
        parent,
        size=(200, 200),
        pos=(0, 0),
        align=lv.ALIGN.CENTER,
        align_to=None,
        primary_color=lv_colors.ONEKEY_GREEN,
        arc_width=15,
        arc_length=60,
        arc_rotation=270,
        rotation_step=5,
    ):
        # 创建弧形进度条
        self.arc = lv.arc(parent)
        self.arc.set_size(size[0], size[1])
        if align_to:
            self.arc.align_to(align_to, align, pos[0], pos[1])
        else:
            self.arc.align(align, pos[0], pos[1])
        
        # 设置角度
        self.arc.set_bg_angles(0, 360)
        self.arc.set_range(0, 360)
        self.arc.set_value(arc_length)
        
        # 移除旋钮
        self.arc.remove_style(None, lv.PART.KNOB)
        
        # 设置主弧形样式
        style_arc = lv.style_t()
        style_arc.init()
        style_arc.set_arc_color(primary_color)
        style_arc.set_arc_width(arc_width)
        self.arc.add_style(style_arc, lv.PART.INDICATOR)
        
        # 设置背景弧形样式（透明）
        style_bg = lv.style_t()
        style_bg.init()
        style_bg.set_arc_opa(lv.OPA.TRANSP)
        self.arc.add_style(style_bg, lv.PART.MAIN)
        
        # 初始化状态
        self.current_rotation = arc_rotation
        self.rotation_step = rotation_step
        # self.arc_length = arc_length
        
    def update(self):
        """更新加载器状态"""
        self.current_rotation += self.rotation_step

        self.arc.set_rotation(self.current_rotation)
        
        # 检查是否完成一圈
        if self.current_rotation >= abs(360):
            self.current_rotation = 0
            
    def delete(self):
        """删除加载器资源"""
        if hasattr(self, 'arc'):
            self.arc.delete()

class ShowLoader(FullSizeWindow):
    def __init__(
        self,
        title="Loading",
        primary_color=lv_colors.ONEKEY_GREEN,
        icon_path="A:/res/icon-send.png",
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
            icon_path=icon_path,
        )

        # 创建容器
        self.loader_container = lv.obj(self.content_area)
        self.loader_container.set_size(250, 250)
        self.loader_container.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 60)
        self.loader_container.set_style_bg_opa(0, 0)
        self.loader_container.set_style_border_width(0, 0)
        self.loader_container.set_style_pad_all(0, 0)
        self.loader_container.clear_flag(lv.obj.FLAG.CLICKABLE)

        # 创建加载器管理器
        self.loader_manager = LoaderManager(timer_period=20)
        
        # 创建三个不同大小的加载器
        arc_1 = ArcLoader(
            parent=self.loader_container,
            size=(160, 160),
            align=lv.ALIGN.CENTER,
            primary_color=primary_color,
            arc_width=6,
            arc_length=90,
            arc_rotation=270,
            rotation_step=2,  # 顺时针旋转
        )
        
        arc_2 = ArcLoader(
            parent=self.loader_container,
            size=(160, 160),
            align=lv.ALIGN.CENTER,
            primary_color=primary_color,
            arc_width=6,
            arc_length=90,
            arc_rotation=90,
            rotation_step=2,  # 顺时针旋转
        )
        
        arc_3 = ArcLoader(
            parent=self.loader_container,
            size=(190, 190),
            align=lv.ALIGN.CENTER,
            primary_color=primary_color,
            arc_width=6,
            arc_length=270,
            arc_rotation=180,
            rotation_step=-2,  # 逆时针旋转
        )

        arc_4 = ArcLoader(
            parent=self.loader_container,
            size=(220, 220),
            align=lv.ALIGN.CENTER,
            primary_color=primary_color,
            arc_width=6,
            arc_length=120,
            arc_rotation=180,
            rotation_step=3,  # 逆时针旋转
        )

        arc_5 = ArcLoader(
            parent=self.loader_container,
            size=(250, 250),
            align=lv.ALIGN.CENTER,
            primary_color=primary_color,
            arc_width=6,
            arc_length=120,
            arc_rotation=0,
            rotation_step=-3,  # 逆时针旋转
        )
        arc_6 = ArcLoader(
            parent=self.loader_container,
            size=(250, 250),
            align=lv.ALIGN.CENTER,
            primary_color=primary_color,
            arc_width=6,
            arc_length=60,
            arc_rotation=180,
            rotation_step=-3,  # 逆时针旋转
        )
        # arc_7 = ArcLoader(
        #     parent=self.loader_container,
        #     size=(280, 280),
        #     align=lv.ALIGN.CENTER,
        #     primary_color=primary_color,
        #     arc_width=8,
        #     arc_length=60,
        #     arc_rotation=240,
        #     rotation_step=-3,  # 逆时针旋转
        # )
        # 将所有加载器添加到管理器
        for arc in [arc_1, arc_2, arc_3, arc_4, arc_5, arc_6]:
            self.loader_manager.add_loader(arc)

        
        self.btn_continue = NormalButton(self.loader_container, _(i18n_keys.BUTTON__CONTINUE))
        self.btn_continue.set_size(120, 120)
        self.btn_continue.add_style(
            StyleWrapper()
            .text_font(font_GeistRegular26)
            # .text_color(lv_colors.ONEKEY_WHITE_4)
            # .bg_color(lv_colors.ONEKEY_GRAY_3)
            .radius(60)
            , 0)
        self.btn_continue.align(lv.ALIGN.CENTER, 0, 0)
        self.btn_continue.move_foreground()
        self.btn_continue.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

        import gc
        gc.collect()

    def on_click(self, event):
        code = event.code
        target = event.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.btn_continue:
                print("click")
                motor.vibrate()
        
    def destroy(self, delay=0):
        """销毁窗口时清理加载器管理器"""
        if hasattr(self, 'loader_manager'):
            self.loader_manager.delete()
        super().destroy(delay)

class ShowBar(FullSizeWindow):
    def __init__(
        self, 
        title="Loading", 
        primary_color=lv_colors.ONEKEY_GREEN,
        bar_count=5,  # 进度条数量
        bar_width=20,  # 进度条宽度
        bar_height=200,  # 进度条高度
        bar_spacing=10  # 进度条间距
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )

        # 创建容器
        self.container = lv.obj(self.content_area)
        total_width = bar_count * bar_width + (bar_count - 1) * bar_spacing
        self.container.set_size(total_width, bar_height + 40)
        self.container.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 80)
        self.container.set_style_bg_opa(0, 0)  # 透明背景
        self.container.set_style_border_width(0, 0)  # 无边框
        self.container.set_style_pad_all(0, 0)  # 无内边距

        # 创建进度条样式
        self.style_indic = lv.style_t()
        self.style_indic.init()
        self.style_indic.set_bg_opa(lv.OPA.COVER)
        self.style_indic.set_bg_color(lv_colors.WHITE)
        self.style_indic.set_bg_grad_color(primary_color)
        self.style_indic.set_bg_grad_dir(lv.GRAD_DIR.VER)
        
        # 创建背景样式
        self.style_bg = lv.style_t()
        self.style_bg.init()
        self.style_bg.set_bg_opa(lv.OPA.COVER)
        self.style_bg.set_bg_color(lv_colors.ONEKEY_GRAY_3)
        self.style_bg.set_radius(4)  # 圆角


        line_points = [ {"x":5, "y":5},
                        # {"x":70, "y":70},
                        # {"x":120, "y":10},
                        # {"x":180, "y":60},
                        {"x":240, "y":10}]

        # Create style
        style_line = lv.style_t()
        style_line.init()
        style_line.set_line_width(8)
        style_line.set_line_color(lv.palette_main(lv.PALETTE.BLUE))
        style_line.set_line_rounded(True)

        # Create a line and apply the new style
        line1 = lv.line(self.content_area)
        line1.set_points(line_points, 2)     # Set the points
        line1.add_style(style_line, 0)
        line1.center()


        # 创建多个进度条
        self.bars = []
        self.anims = []
        
        for i in range(bar_count):
            # 创建进度条并添加到容器
            bar = lv.bar(self.container)
            bar.add_style(self.style_bg, lv.PART.MAIN)
            bar.add_style(self.style_indic, lv.PART.INDICATOR)
            bar.set_size(bar_width, bar_height)
            bar.set_pos(i * (bar_width + bar_spacing), 0)
            bar.set_range(0, 100)
            
            # 创建动画
            a = lv.anim_t()
            a.init()
            a.set_var(bar)
            a.set_values(0, 100)
            
            # 设置不同的动画时间和延迟，使动画错开
            base_time = 500
            a.set_time(base_time + i * 100)
            a.set_playback_time(base_time + i * 100)
            a.set_delay(i * 200)
            a.set_playback_delay(i * 100)
            
            a.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
            
            # 使用闭包捕获当前的 bar 值
            def create_callback(target_bar):
                return lambda a, val: self.set_bar_value(target_bar, val)
            
            a.set_custom_exec_cb(create_callback(bar))
            
            lv.anim_t.start(a)
            
            self.bars.append(bar)
            self.anims.append(a)

    def set_bar_value(self, bar, value):
        """更新进度条值的统一回调函数"""
        bar.set_value(value, lv.ANIM.ON)
        
    def destroy(self, delay_ms=400):
        """清理资源"""
        # 停止所有动画
        for anim in self.anims:
            if anim:
                anim._del()
        self.anims = []
        return super().destroy(delay_ms)
    
class ShowLine(FullSizeWindow):
    def __init__(
        self, 
        title="Turbo Mode", 
        primary_color=lv_colors.ONEKEY_GREEN,
        line_count=16,  # 线条数量，建议使用8或12等能均匀分布的数字
        line_width=6,  # 线条宽度
        line_length=50,  # 固定线条长度
        max_distance=200,  # 最大移动距离
    ):
        super().__init__(
            title,
            None,
            _(i18n_keys.BUTTON__CONTINUE),
            _(i18n_keys.BUTTON__REJECT),
            primary_color=primary_color,
        )
                
        # 添加背景图片
        self.content_area.set_size(lv.pct(100), lv.pct(100))
        self.content_area.set_style_max_height(800, 0)
        self.content_area.align(lv.ALIGN.TOP_MID, 0, 0)  # 将y轴偏移改为0
        self.bg_img = lv.img(self.content_area)
        self.bg_img.set_src("A:/res/test-bg.png")
        # self.bg_img.set_src("A:/assets/linebg.jpg")
        self.bg_img.align(lv.ALIGN.CENTER, 0, 0)
        self.bg_img.add_flag(lv.obj.FLAG.FLOATING)  # 让背景浮动，不影响其他元素布局
        self.bg_img.move_background()
        # self.bg_img.move_foreground()

        # 导入math模块
        import math
        self.math = math
        
        # 创建容器
        self.container = lv.obj(self.content_area)
        container_size = (max_distance + line_length) * 2 + 20  # 确保容器足够大
        self.container.set_size(container_size, container_size)
        self.container.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 100)
        self.container.set_style_bg_opa(0, 0)  # 透明背景
        self.container.set_style_border_width(0, 0)  # 无边框
        self.container.set_style_pad_all(0, 0)  # 无内边距
        
        # 创建线条样式
        self.style_line = lv.style_t()
        self.style_line.init()
        self.style_line.set_line_width(line_width)
        self.style_line.set_line_color(lv_colors.PURPLE)
        self.style_line.set_line_rounded(True)
        
        # 存储线条和动画
        self.lines = []
        self.anims = []
        self.line_points_list = []
        self.is_destroyed = False
        self.line_length = line_length
        
        # 计算中心点
        self.center_x = container_size // 2
        self.center_y = container_size // 2
        
        # 创建放射状线条
        for i in range(line_count):
            # 计算角度 (均匀分布在360度)
            angle = i * (360 / line_count)
            angle_rad = math.radians(angle)
            
            # 初始化线条点 (初始位置在中心)
            line_points = [
                {"x": self.center_x, "y": self.center_y},  # 起点
                {"x": self.center_x, "y": self.center_y}   # 终点 (初始与起点相同)
            ]
            
            self.line_points_list.append({
                "points": line_points,
                "angle": angle_rad
            })
            
            # 创建线条对象
            line = lv.line(self.container)
            line.set_points(line_points, 2)
            line.add_style(self.style_line, 0)
            
            # 创建动画
            anim = lv.anim_t()
            anim.init()
            anim.set_var(line)
            anim.set_values(0, max_distance)  # 从0到最大距离
            
            # 设置不同的动画时间和延迟，使动画错开
            base_time = 400
            anim.set_time(base_time)
            # anim.set_playback_time(base_time)
            anim.set_delay(i * 747 % 1001)  # 错开延迟
            
            anim.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
            
            # 使用闭包捕获当前线条索引
            def create_callback(idx):
                return lambda a, val: self.update_line_position(idx, val)
            
            anim.set_custom_exec_cb(create_callback(i))
            
            lv.anim_t.start(anim)
            
            self.lines.append(line)
            self.anims.append(anim)

        self.btn_continue = NormalButton(self.container, _(i18n_keys.BUTTON__CONTINUE))
        self.btn_continue.set_size(120, 120)
        self.btn_continue.add_style(
            StyleWrapper()
            .text_font(font_GeistRegular26)
            # .text_color(lv_colors.ONEKEY_WHITE_4)
            # .bg_color(lv_colors.ONEKEY_GRAY_3)
            .radius(60)
            , 0)
        self.btn_continue.align(lv.ALIGN.CENTER, 0, 0)
        self.btn_continue.move_foreground()
        self.btn_continue.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

        import gc
        gc.collect()

    def on_click(self, event):
        code = event.code
        target = event.get_target()
        if code == lv.EVENT.CLICKED:
            if target == self.btn_continue:
                print("click")
                motor.vibrate()

    def update_line_position(self, line_idx, distance):
        """更新指定线条位置的回调函数"""
        # 检查窗口是否已销毁或索引是否有效
        if self.is_destroyed or line_idx >= len(self.line_points_list):
            return
            
        try:
            line_data = self.line_points_list[line_idx]
            angle = line_data["angle"]
            
            # 计算线条起点和终点
            start_x = self.center_x + int(distance * self.math.cos(angle))
            start_y = self.center_y + int(distance * self.math.sin(angle))
            
            # 计算线条终点 (起点 + 固定长度)
            end_x = start_x + int(self.line_length * self.math.cos(angle))
            end_y = start_y + int(self.line_length * self.math.sin(angle))
            
            # 更新线条点
            line_data["points"][0]["x"] = start_x
            line_data["points"][0]["y"] = start_y
            line_data["points"][1]["x"] = end_x
            line_data["points"][1]["y"] = end_y
            
            # 更新线条对象的点
            if line_idx < len(self.lines):
                self.lines[line_idx].set_points(line_data["points"], 2)
        except (IndexError, AttributeError):
            # 捕获任何可能的索引错误或属性错误
            pass
    
    def destroy(self, delay_ms=400):
        """清理资源"""
        # 标记窗口为已销毁状态
        self.is_destroyed = True
        
        # 停止所有动画
        for anim in self.anims:
            if anim:
                anim._del()
        self.anims = []
        
        # 清空引用
        self.lines = []
        self.line_points_list = []
        
        return super().destroy(delay_ms)
    
class ShowRipple(FullSizeWindow):
    def __init__(self):
        super().__init__(
            "Turbo Mode",
            None,
            # _(i18n_keys.BUTTON__CONTINUE),
            # _(i18n_keys.BUTTON__REJECT),
            primary_color=lv_colors.ONEKEY_GREEN,
        )

        # 添加背景图片
        self.content_area.set_size(lv.pct(100), lv.pct(100))
        self.content_area.set_style_max_height(800, 0)
        self.content_area.align(lv.ALIGN.TOP_MID, 0, 40)  # 将y轴偏移改为0
        self.bg_img = lv.img(self.content_area)
        self.bg_img.set_src("A:/res/test-point.png")
        self.bg_img.align(lv.ALIGN.CENTER, 0, 0)
        self.bg_img.add_flag(lv.obj.FLAG.FLOATING)  # 让背景浮动，不影响其他元素布局
        self.bg_img.move_background()
        # self.bg_img.move_foreground()

        ### static mask #####################################################
        # circle
        self.circle = lv.obj(self.content_area)
        self.circle.set_size(110, 110)  # 直径为300
        self.circle.align_to(self.bg_img, lv.ALIGN.CENTER, 0, 0)
        self.circle.set_style_radius(60, 0)  # 设置半径为150
        self.circle.set_style_bg_color(lv_colors.BLACK, 0)  # 设置背景颜色为黑色
        self.circle.set_style_border_width(0, 0)  # 无边框

        # mask 1
        self.mask1 = lv.arc(self.content_area)

        self.mask1.set_size(230, 230)
        self.mask1.align_to(self.bg_img, lv.ALIGN.CENTER, 0, 0)
        
        self.mask1.set_bg_angles(0, 360)
        self.mask1.set_range(0, 360)
        self.mask1.set_value(360)
        self.mask1.remove_style(None, lv.PART.KNOB)

        # mask 2
        self.mask2 = lv.arc(self.content_area)
        self.mask2.set_size(340, 340)
        self.mask2.align_to(self.bg_img, lv.ALIGN.CENTER, 0, 0)
        
        self.mask2.set_bg_angles(0, 360)
        self.mask2.set_range(0, 360)
        self.mask2.set_value(360)
        self.mask2.remove_style(None, lv.PART.KNOB)

        # 设置主弧形样式
        style_mask = lv.style_t()
        style_mask.init()
        style_mask.set_arc_color(lv_colors.BLACK)
        style_mask.set_arc_width(35)
        self.mask1.add_style(style_mask, lv.PART.INDICATOR)
        self.mask2.add_style(style_mask, lv.PART.INDICATOR)
        
        # 设置背景弧形样式（透明）
        style_bg = lv.style_t()
        style_bg.init()
        style_bg.set_arc_opa(lv.OPA.TRANSP)
        self.mask1.add_style(style_bg, lv.PART.MAIN)
        self.mask2.add_style(style_bg, lv.PART.MAIN)
        ### static mask #####################################################


        ### anime mask #####################################################
        # inner
        self.anime_mask2 = lv.obj(self.content_area)
        self.anime_mask2.set_size(120, 120)
        self.anime_mask2.set_style_radius(180, 0)
        self.anime_mask2.align_to(self.bg_img, lv.ALIGN.CENTER, 0, 0)
        self.anime_mask2.set_style_bg_color(lv_colors.BLACK, 0)
        self.anime_mask2.set_style_border_width(0, 0)

        # outer
        self.anime_mask1 = lv.arc(self.content_area)
        self.anime_mask1.set_size(370, 370)
        self.anime_mask1.align_to(self.bg_img, lv.ALIGN.CENTER, 0, 0)
        self.anime_mask1.set_bg_angles(0, 360)
        self.anime_mask1.set_range(0, 360)
        self.anime_mask1.set_value(360)
        self.anime_mask1.remove_style(None, lv.PART.KNOB)

        # set style
        self.style_anime_mask_1 = lv.style_t()
        self.style_anime_mask_1.init()
        self.style_anime_mask_1.set_arc_color(lv_colors.BLACK)
        self.style_anime_mask_1.set_arc_width(170)
        self.anime_mask1.add_style(self.style_anime_mask_1, lv.PART.INDICATOR)

        self.style_anime_mask_bg_1 = lv.style_t()
        self.style_anime_mask_bg_1.init()
        self.style_anime_mask_bg_1.set_arc_opa(lv.OPA.TRANSP)
        self.anime_mask1.add_style(self.style_anime_mask_bg_1, lv.PART.MAIN)

        ### anime mask #####################################################


        ### anime  #####################################################
        anime = lv.anim_t()
        anime.init()
        anime.set_var(self.anime_mask1)
        anime.set_values(180, 0)
        anime.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
        
        base_time = 1500
        anime.set_time(base_time)
        # anime.set_playback_time(base_time)
        anime.set_delay(500)
        # anime.set_playback_delay(300)
        
        anime.set_repeat_count(lv.ANIM_REPEAT.INFINITE)

        anime.set_custom_exec_cb(lambda a, val: self.update_arc_width(val))
        lv.anim_t.start(anime)

        ### btn #####################################################
        self.btn_continue = NormalButton(self.content_area, "SIGN")
        self.btn_continue.set_size(120, 120)
        self.btn_continue.add_style(
            StyleWrapper()
            # .text_font(font_GeistRegular26)
            # .text_color(lv_colors.ONEKEY_WHITE_4)
            .bg_color(lv_colors.ONEKEY_GRAY_4)
            .radius(75)
            , 0)
        self.btn_continue.align(lv.ALIGN.CENTER, 0, 0)
        self.btn_continue.move_foreground()
        
        # 创建按钮大小变化的动画
        btn_anim = lv.anim_t()
        btn_anim.init()
        btn_anim.set_var(self.btn_continue)
        btn_anim.set_time(200)  # 动画持续时间(ms)
        btn_anim.set_values(120, 150)  # 从120px到140px
        btn_anim.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
        btn_anim.set_playback_time(200)  # 回放动画时间(ms)
        btn_anim.set_repeat_delay(1450)
        # btn_anim.set_playback_delay(50)  # 回放前的短暂停留(ms)
        btn_anim.set_path_cb(lv.anim_t.path_overshoot)  # 使用overshoot路径效果
        
        # 设置大小变化的回调函数

        btn_anim.set_custom_exec_cb(lambda a, val: self.size_cb(self.btn_continue, val))
        lv.anim_t.start(btn_anim)

    def size_cb(self, btn, value):
        btn.set_size(value, value)
        btn.align(lv.ALIGN.CENTER, 0, 0)  # 保持居中
        

    def update_arc_width(self, val):
        self.anime_mask2.set_size(360-2*val - 20, 360-2*val - 20)
        self.anime_mask2.set_style_radius(180-val-10, 0)
        self.anime_mask2.align_to(self.bg_img, lv.ALIGN.CENTER, 0, 0)
        self.anime_mask2.invalidate()

        self.style_anime_mask_1.set_arc_width(val)
        self.anime_mask1.invalidate()
        ### anime  #####################################################

class Turbo(FullSizeWindow):
    def __init__(self):
        super().__init__(
            None,
            None,
            primary_color=lv_colors.ONEKEY_GREEN,
        )

        self.add_style(
            StyleWrapper()
            # .bg_opa(lv.OPA.TRANSP)
            .bg_img_src("A:/res/rgb565.jpg"),
            0,
        )
        
        self.content_area.add_style(
            StyleWrapper()
            .bg_opa(lv.OPA.TRANSP),
            0,
        )
        self.content_area.clear_flag(lv.obj.FLAG.SCROLLABLE)

        # 标题
        self.title = lv.img(self.content_area)
        self.title.set_src("A:/res/Turbomode.png")
        self.title.align(lv.ALIGN.TOP_MID, 0, 60)

        from .components.listitem import ShortInfoItem
        self.info_item = ShortInfoItem(
                        parent=self.content_area, 
                        img_src="A:/res/sol-69.png", 
                        title_text="Send 5 SOL to Trump", 
                        subtitle_text="Solana",
                        bg_color=lv_colors.ONEKEY_GRAY_3,
                        )
        self.info_item.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 50)
        # self.info_item.add_flag(lv.obj.FLAG.HIDDEN)

######################################################################################
        # 确认按钮
        click_style = (
            StyleWrapper()
            .bg_img_recolor_opa(lv.OPA._30)
            .bg_img_recolor(lv_colors.BLACK)
        )
        self.confirm_btn = lv.imgbtn(self.content_area)
        self.confirm_btn.set_size(280, 280)
        self.confirm_btn.align_to(self.info_item, lv.ALIGN.OUT_BOTTOM_MID, 0, 70)
        self.confirm_btn.set_style_bg_img_src("A:/res/Turn.png", 0)
        self.confirm_btn.add_style(click_style, lv.PART.MAIN | lv.STATE.PRESSED)
        self.confirm_btn.add_flag(lv.obj.FLAG.EVENT_BUBBLE)
        self.confirm_btn.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

        # self.confirm_btn.set_style_transform_angle(1800, lv.STATE.PRESSED)
        # self.confirm_btn.set_style_transform_pivot_x(140, lv.STATE.PRESSED)
        # self.confirm_btn.set_style_transform_pivot_y(140, lv.STATE.PRESSED)
        # self.confirm_btn.set_style_opa(lv.OPA._30, lv.STATE.PRESSED)
        # self.confirm_btn.align_to(self.info_item, lv.ALIGN.OUT_BOTTOM_MID, 0, 70)
        # self.confirm_btn.set_style_bg_img_src("A:/res/Turn.png", 0)
        
        # # 创建按钮对象
        # self.confirm_btn = lv.btn(self.content_area)
        # self.confirm_btn.set_size(250, 250)
        # self.confirm_btn.align_to(self.info_item, lv.ALIGN.OUT_BOTTOM_MID, 0, 70)

        # # 使用StyleWrapper设置按钮为透明
        # self.confirm_btn.add_style(
        #     StyleWrapper()
        #     .radius(130)
        #     .bg_opa(lv.OPA.TRANSP), 
        #     0)
        
        # self.confirm_btn.add_style(
        #     StyleWrapper()
        #     .bg_opa(lv.OPA._30)
        #     .bg_color(lv_colors.BLACK), 
        #     lv.PART.MAIN | lv.STATE.PRESSED)

        # # 添加图像到按钮
        # self.confirm_img = lv.img(self.content_area)
        # self.confirm_img.set_src("A:/res/Turn.png")
        # self.confirm_img.align_to(self.confirm_btn, lv.ALIGN.CENTER, 0, 0)

        # # 添加事件回调
        # self.confirm_btn.move_foreground()
        # self.confirm_btn.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)

        
        # 等待动画 - 水波扩散效果
        # 创建多个同心圆实现水波扩散效果
        self.ripple_container = lv.obj(self.content_area)
        self.ripple_container.set_size(440, 440)  # 足够大以容纳扩散效果
        self.ripple_container.align_to(self.confirm_btn, lv.ALIGN.CENTER, 0, 0)
        self.ripple_container.set_style_bg_opa(lv.OPA.TRANSP, 0)  # 透明背景
        self.ripple_container.set_style_border_width(0, 0)  # 无边框
        self.ripple_container.set_style_pad_all(0, 0)  # 无内边距
        self.ripple_container.clear_flag(lv.obj.FLAG.CLICKABLE)  # 不可点击
        
        # 创建2个水波圆环
        self.ripples = []
        for i in range(2):  # 只创建1个水波
            ripple_data = self.create_ripple(i)
            self.ripples.append(ripple_data)
        
        # 取消交易
        self.btn_no = NormalButton(self, "Reject")

        self.btn_no.add_style(
            StyleWrapper()
            .bg_color(lv_colors.BLACK)
            .bg_opa(lv.OPA.TRANSP),
            lv.PART.MAIN | lv.STATE.DEFAULT,
        )

        self.btn_no.add_style(
            StyleWrapper()
            .bg_color(lv_colors.ONEKEY_BLACK)
            .bg_opa(lv.OPA._30),
            lv.PART.MAIN | lv.STATE.PRESSED,
        )

        self.btn_no.clear_flag(lv.obj.FLAG.CLICKABLE)
        self.btn_no.click_mask.add_flag(lv.obj.FLAG.CLICKABLE)
        self.btn_no.align(lv.ALIGN.BOTTOM_LEFT, 12, -8)
        self.btn_no.add_event_cb(self.on_click, lv.EVENT.CLICKED, None)
######################################################################################

    def create_ripple(self, index):
        """创建单个水波圆环及其动画"""
        ripple = lv.arc(self.ripple_container)
        ripple.set_size(280, 280)  # 初始大小与按钮相同
        ripple.align(lv.ALIGN.CENTER, 0, 0)
        
        # 设置为完整圆环
        ripple.set_bg_angles(0, 360)
        ripple.set_range(0, 360)
        ripple.set_value(360)
        ripple.remove_style(None, lv.PART.KNOB)  # 移除旋钮
        
        # 设置圆环样式
        style_ripple = lv.style_t()
        style_ripple.init()
        style_ripple.set_arc_color(lv_colors.WHITE)
        style_ripple.set_arc_width(8)  # 线条宽度8px
        style_ripple.set_arc_opa(lv.OPA.TRANSP)  # 初始透明度
        ripple.add_style(style_ripple, lv.PART.INDICATOR)
        
        # 设置为不可点击
        ripple.clear_flag(lv.obj.FLAG.CLICKABLE)

        # 保存样式引用以便后续更新
        ripple_data = {"arc": ripple, "style": style_ripple}
        
        # 设置背景透明
        style_bg = lv.style_t()
        style_bg.init()
        style_bg.set_arc_opa(lv.OPA.TRANSP)
        ripple.add_style(style_bg, lv.PART.MAIN)
        
        # 创建动画
        anim = lv.anim_t()
        anim.init()
        anim.set_var(ripple)
        anim.set_time(700)  # 1秒完成一次扩散
        anim.set_values(280, 440)  # 从按钮半径扩散到屏幕边缘
        anim.set_delay(1000 + index * 400)  # 错开开始时间
        anim.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
        anim.set_repeat_delay(1000)
        
        # 自定义动画回调函数
        def create_ripple_cb(r_data):
            return lambda a, val: self.update_ripple(r_data, val)
        
        anim.set_custom_exec_cb(create_ripple_cb(ripple_data))
        anim_obj = lv.anim_t.start(anim)
        
        ripple_data["anim"] = anim_obj
        return ripple_data
    
    def update_ripple(self, ripple_data, size):
        """更新水波圆环的大小和透明度"""
        ripple = ripple_data["arc"]
        style = ripple_data["style"]
        
        # 更新大小
        ripple.set_size(size, size)
        ripple.align(lv.ALIGN.CENTER, 0, 0)
        
        # 计算透明度 - 随着扩散逐渐变透明
        # 将size从280-480映射到100-0的透明度
        min_size, max_size = 280, 440
        min_opa, max_opa = 100, 0
        opa = max_opa + (min_opa - max_opa) * (max_size - size) / (max_size - min_size)
        if opa == 100:
            opa = 0
            print("# fix opa to 0")
        # progress = (size - min_size) / (max_size - min_size)
        # exponent = -2  # 可以调整这个值来控制曲线的形状
        # opa = min_opa + (max_opa - min_opa) * ((math.exp(progress * exponent) - 1) / (math.exp(exponent) - 1))
        style.set_arc_opa(int(opa))
        
        # 计算弧形宽度 - 从2到10
        min_width, max_width = 4, 12
        width = min_width + (max_width - min_width) * (size - min_size) / (max_size - min_size)
        style.set_arc_width(int(width))

        # 强制重绘
        ripple.invalidate()
        

    def destroy(self, delay_ms=1100):
        print("# destroy")
        for ripple_data in self.ripples:
            lv.anim_del(ripple_data["anim"].var, None)
        self.del_delayed(delay_ms)

    def on_click(self, event_obj):
        code = event_obj.code
        target = event_obj.get_target()
        print(f"# Event code: {code}, Target: {target}")
        if code == lv.EVENT.CLICKED:
            print(f"# target: {target}")
            if target == self.btn_no.click_mask:
                print("# Reject")
                self.confirm_btn_done.set_style_img_opa(lv.OPA.COVER, 0)

                self.destroy()
                self.channel.publish(0)
            elif hasattr(self, "confirm_btn") and target == self.confirm_btn:
                print("# Starting confirm animation")
                for ripple_data in self.ripples:
                    lv.anim_del(ripple_data["anim"].var, None)
                    ripple_data["arc"].delete()
                    del ripple_data["arc"]
                self.start_confirm_animation()

                if hasattr(self, "confirm_btn"):
                    self.confirm_btn.delete()
                    del self.confirm_btn
                self.destroy(5000)
                # self.channel.publish(1)


    def start_confirm_animation(self):
        """启动确认按钮的旋转动画"""
        
        self.confirm_btn_bg = lv.img(self.content_area)
        self.confirm_btn_bg.set_src("A:/res/turn-bg.png")
        self.confirm_btn_bg.align_to(self.confirm_btn, lv.ALIGN.CENTER, 0, 0)

        self.confirm_btn_done = lv.img(self.content_area)
        self.confirm_btn_done.set_src("A:/res/turn-done.png")
        self.confirm_btn_done.align_to(self.confirm_btn, lv.ALIGN.CENTER, 0, 0)
        # self.confirm_btn_done.set_style_img_opa(lv.OPA.COVER, 0)
        self.confirm_btn_done.move_foreground()
        # 创建旋转动画
        anim = lv.anim_t()
        anim.init()
        anim.set_var(self.confirm_btn_done)
        anim.set_time(300)  # 动画持续时间(ms)
        anim.set_values(0, lv.OPA.COVER)  # 从0度旋转到360度
        # anim.set_repeat_count(lv.ANIM_REPEAT.INFINITE)
        
        anim.set_custom_exec_cb(lambda a, val: self.set_btn(val))
        
        # anim.set_ready_cb(lambda a: self.animation_completed())
        
        # 启动动画
        lv.anim_t.start(anim)

    def set_btn(self, opa):
        self.confirm_btn_done.set_style_img_opa(int(opa), 0)
        angle = opa / lv.OPA.COVER * 3600
        self.confirm_btn_done.set_angle(int(angle))

    # def animation_completed(self):
    #     # self.confirm_btn_done.set_style_img_opa(lv.OPA.COVER, 0)
    #     print("# Animation completed")
