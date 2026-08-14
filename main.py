from pathlib import Path
from urllib.parse import urlparse
import webbrowser

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

try:
    from android.runnable import run_on_ui_thread
    from jnius import PythonJavaClass, autoclass, java_method

    ANDROID = True
except ImportError:
    ANDROID = False

    def run_on_ui_thread(function):
        return function


DEFAULT_URL = (
    "https://20-2026-isaacplamedi-2026-mainzip-mainzip-mainzip--empresawta.replit.app"
)

NAVY = get_color_from_hex("#102A43")
TEAL = get_color_from_hex("#087F8C")
MINT = get_color_from_hex("#DFF3F3")
BACKGROUND = get_color_from_hex("#F5FBFB")
TEXT_MUTED = get_color_from_hex("#627D98")
WHITE = get_color_from_hex("#FFFFFF")
ERROR = get_color_from_hex("#D64545")


def valid_url(value):
    parsed = urlparse(value.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


if ANDROID:

    class ClickListener(PythonJavaClass):
        __javainterfaces__ = ["android/view/View$OnClickListener"]

        def __init__(self, callback):
            super().__init__()
            self.callback = callback

        @java_method("(Landroid/view/View;)V")
        def onClick(self, _view):
            self.callback()


class AndroidWebView:
    """Native Android WebView overlay with a small navigation toolbar."""

    def __init__(self, app):
        self.app = app
        self.root = None
        self.overlay = None
        self.webview = None
        self.listeners = []

    def open(self):
        if ANDROID:
            self._open_native()
        else:
            webbrowser.open(self.app.url)

    @run_on_ui_thread
    def _open_native(self):
        if self.overlay is not None:
            self.webview.loadUrl(self.app.url)
            return

        activity_class = autoclass("org.kivy.android.PythonActivity")
        frame_layout = autoclass("android.widget.FrameLayout")
        linear_layout = autoclass("android.widget.LinearLayout")
        button_class = autoclass("android.widget.Button")
        webview_class = autoclass("android.webkit.WebView")
        webview_client = autoclass("android.webkit.WebViewClient")
        cookie_manager = autoclass("android.webkit.CookieManager")
        android_r_id = autoclass("android.R$id")
        gravity = autoclass("android.view.Gravity")

        activity = activity_class.mActivity
        self.root = activity.findViewById(android_r_id.content)
        self.overlay = frame_layout(activity)
        self.webview = webview_class(activity)

        settings = self.webview.getSettings()
        settings.setJavaScriptEnabled(True)
        settings.setDomStorageEnabled(True)
        settings.setDatabaseEnabled(True)
        settings.setSupportZoom(False)
        settings.setBuiltInZoomControls(False)
        settings.setDisplayZoomControls(False)
        settings.setJavaScriptCanOpenWindowsAutomatically(True)
        settings.setSupportMultipleWindows(False)
        self.webview.setWebViewClient(webview_client())
        self.webview.setBackgroundColor(0xFFF5FBFB)

        cookies = cookie_manager.getInstance()
        cookies.setAcceptCookie(True)
        cookies.setAcceptThirdPartyCookies(self.webview, True)

        self.overlay.addView(
            self.webview,
            frame_layout.LayoutParams(-1, -1),
        )

        toolbar = linear_layout(activity)
        toolbar.setOrientation(linear_layout.HORIZONTAL)
        toolbar.setGravity(gravity.CENTER)
        toolbar.setBackgroundColor(0xFF102A43)

        actions = [
            ("Menu", self.open_site_menu),
            ("Voltar", self.go_back),
            ("Avançar", self.go_forward),
            ("Atualizar", self.reload),
            ("Config.", self.close),
        ]
        for label, callback in actions:
            button = button_class(activity)
            button.setText(label)
            button.setTextColor(0xFFFFFFFF)
            button.setTextSize(12)
            button.setAllCaps(False)
            button.setBackgroundColor(0xFF102A43)
            listener = ClickListener(callback)
            self.listeners.append(listener)
            button.setOnClickListener(listener)
            toolbar.addView(
                button,
                linear_layout.LayoutParams(0, -1, 1.0),
            )

        toolbar_params = frame_layout.LayoutParams(-1, int(dp(58)))
        toolbar_params.gravity = gravity.BOTTOM
        self.overlay.addView(toolbar, toolbar_params)
        self.root.addView(self.overlay, frame_layout.LayoutParams(-1, -1))
        self.webview.loadUrl(self.app.url)

    @run_on_ui_thread
    def open_site_menu(self):
        if self.webview is None:
            return
        script = """
            (() => {
              const selectors = [
                '#sidebarToggle',
                '#menuToggle',
                '#hamburger',
                '.sidebar-toggle',
                '.menu-toggle',
                '.hamburger',
                '.hamburger-menu',
                '[data-menu-toggle]',
                '[data-sidebar-toggle]',
                '[aria-label*="menu" i]',
                '[title*="menu" i]',
                '[data-bs-toggle="offcanvas"]',
                '[data-bs-toggle="collapse"]'
              ];
              const button = selectors
                .flatMap((selector) => Array.from(document.querySelectorAll(selector)))
                .find((element) => {
                  const rect = element.getBoundingClientRect();
                  return rect.width > 0 && rect.height > 0;
                });
              if (button) {
                button.dispatchEvent(new MouseEvent('click', {
                  bubbles: true,
                  cancelable: true,
                  view: window
                }));
              }
              true;
            })();
        """
        self.webview.evaluateJavascript(script, None)

    @run_on_ui_thread
    def go_back(self):
        if self.webview is not None and self.webview.canGoBack():
            self.webview.goBack()

    @run_on_ui_thread
    def go_forward(self):
        if self.webview is not None and self.webview.canGoForward():
            self.webview.goForward()

    @run_on_ui_thread
    def reload(self):
        if self.webview is not None:
            self.webview.reload()

    @run_on_ui_thread
    def close(self):
        if self.overlay is not None and self.root is not None:
            self.root.removeView(self.overlay)
        self.overlay = None
        self.webview = None
        self.listeners = []
        Clock.schedule_once(lambda _dt: self.app.show_settings(), 0)

    @run_on_ui_thread
    def handle_back(self):
        if self.webview is not None and self.webview.canGoBack():
            self.webview.goBack()
        else:
            self.close()


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(36), dp(24), dp(24)],
            spacing=dp(16),
        )
        layout.add_widget(Image(source="icon.png", size_hint_y=None, height=dp(92)))
        layout.add_widget(
            Label(
                text="jmbelem Gestão",
                color=NAVY,
                font_size="25sp",
                bold=True,
                size_hint_y=None,
                height=dp(42),
            )
        )
        layout.add_widget(
            Label(
                text="Sistema de faturação",
                color=TEXT_MUTED,
                font_size="15sp",
                size_hint_y=None,
                height=dp(28),
            )
        )
        layout.add_widget(
            Label(
                text="O sistema será aberto dentro do aplicativo.",
                color=TEXT_MUTED,
                font_size="14sp",
                halign="center",
                text_size=(dp(300), None),
            )
        )

        open_button = Button(
            text="Abrir sistema",
            background_normal="",
            background_color=TEAL,
            color=WHITE,
            font_size="16sp",
            size_hint_y=None,
            height=dp(52),
        )
        open_button.bind(on_release=lambda _button: app.open_webview())
        layout.add_widget(open_button)

        settings_button = Button(
            text="Configurar link",
            background_normal="",
            background_color=MINT,
            color=TEAL,
            font_size="15sp",
            size_hint_y=None,
            height=dp(48),
        )
        settings_button.bind(on_release=lambda _button: app.show_settings())
        layout.add_widget(settings_button)
        layout.add_widget(Label())
        self.add_widget(layout)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(34), dp(24), dp(24)],
            spacing=dp(12),
        )
        layout.add_widget(
            Label(
                text="Configurações",
                color=NAVY,
                font_size="24sp",
                bold=True,
                size_hint_y=None,
                height=dp(44),
            )
        )
        layout.add_widget(
            Label(
                text="Defina o endereço do seu sistema de faturação.",
                color=TEXT_MUTED,
                font_size="14sp",
                halign="left",
                text_size=(dp(330), None),
                size_hint_y=None,
                height=dp(44),
            )
        )
        self.url_input = TextInput(
            text=self.app.url,
            hint_text="https://o-seu-sistema.com",
            multiline=False,
            write_tab=False,
            font_size="14sp",
            size_hint_y=None,
            height=dp(54),
            padding=[dp(14), dp(16)],
        )
        layout.add_widget(self.url_input)
        self.error_label = Label(
            text="",
            color=ERROR,
            font_size="12sp",
            halign="left",
            text_size=(dp(330), None),
            size_hint_y=None,
            height=dp(28),
        )
        layout.add_widget(self.error_label)

        save_button = Button(
            text="Guardar link",
            background_normal="",
            background_color=TEAL,
            color=WHITE,
            font_size="15sp",
            size_hint_y=None,
            height=dp(52),
        )
        save_button.bind(on_release=self.save)
        layout.add_widget(save_button)

        back_button = Button(
            text="Voltar",
            background_normal="",
            background_color=MINT,
            color=TEAL,
            font_size="15sp",
            size_hint_y=None,
            height=dp(48),
        )
        back_button.bind(on_release=lambda _button: self.app.show_webview())
        layout.add_widget(back_button)
        layout.add_widget(Label())
        self.add_widget(layout)

    def on_pre_enter(self, *_args):
        self.url_input.text = self.app.url
        self.error_label.text = ""

    def save(self, *_args):
        value = self.url_input.text.strip().rstrip("/")
        if not valid_url(value):
            self.error_label.text = "Digite um link válido começando por https://"
            return
        self.app.save_url(value)
        self.app.show_webview()


class JmbelemGestaoApp(App):
    title = "jmbelem Gestão"

    def build(self):
        self.url = DEFAULT_URL
        store_path = Path(self.user_data_dir) / "settings.json"
        self.store = JsonStore(str(store_path))
        if self.store.exists("system"):
            stored_url = self.store.get("system").get("url", "")
            if valid_url(stored_url):
                self.url = stored_url.rstrip("/")

        self.web_controller = AndroidWebView(self)
        manager = ScreenManager()
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(SettingsScreen(name="settings"))
        self.manager = manager
        Window.clearcolor = BACKGROUND
        return manager

    def on_start(self):
        Clock.schedule_once(lambda _dt: self.open_webview(), 0.5)

    def save_url(self, value):
        self.url = value
        self.store.put("system", url=value)

    def open_webview(self):
        self.manager.current = "home"
        self.web_controller.open()

    def show_settings(self):
        self.manager.current = "settings"

    def show_webview(self):
        self.manager.current = "home"
        Clock.schedule_once(lambda _dt: self.web_controller.open(), 0.1)

    def on_request_close(self, *_args):
        if ANDROID and self.web_controller.overlay is not None:
            self.web_controller.handle_back()
            return True
        return False


if __name__ == "__main__":
    JmbelemGestaoApp().run()