# main.py - 同步加载修复版
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
import os
import sys
from datetime import datetime
import json
import requests
import threading

# 设置窗口大小
Window.size = (360, 640)
Window.clearcolor = (0.95, 0.97, 0.99, 1)


def get_base_dir():
    """获取程序所在目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def register_chinese_font():
    """注册中文字体，优先使用同目录下的msyh.ttf"""
    base_dir = get_base_dir()

    # 优先检查同目录下的msyh.ttf
    local_font = os.path.join(base_dir, 'msyh.ttf')
    if os.path.exists(local_font):
        try:
            LabelBase.register(name='ChineseFont', fn_regular=local_font)
            print(f"✓ 成功加载本地字体: {local_font}")
            return 'ChineseFont'
        except Exception as e:
            print(f"✗ 加载本地字体失败: {e}")

    # 如果本地字体不存在或加载失败，尝试系统字体
    font_paths = []

    if os.name == 'nt':  # Windows
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/msyhbd.ttc',
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/simhei.ttf'
        ]
    elif sys.platform == 'darwin':  # macOS
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',
            '/Library/Fonts/Arial Unicode.ttf'
        ]
    else:  # Linux
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'
        ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='ChineseFont', fn_regular=font_path)
                print(f"✓ 使用系统字体: {font_path}")
                return 'ChineseFont'
            except Exception as e:
                print(f"✗ 加载系统字体失败 {font_path}: {e}")
                continue

    # 所有字体加载失败，使用默认字体
    print("⚠ 警告：未找到任何中文字体，使用系统默认字体")
    return 'Arial'


# 注册字体
DEFAULT_FONT = register_chinese_font()

# ==================== 自定义美化组件 ====================
class GradientButton(Button):
    """渐变背景按钮 - 修复版"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.color = (1, 1, 1, 1)
        self.font_name = DEFAULT_FONT
        self.border = (0, 0, 0, 0)
        self.main_color = (0.2, 0.5, 0.8, 1)
        self._canvas_initialized = False
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        Clock.schedule_once(self._init_canvas, 0.1)
        # 设置文字自动缩小以适应按钮
        self.text_size = self.size
        self.halign = 'center'
        self.valign = 'middle'

    def _init_canvas(self, dt):
        if not self._canvas_initialized:
            self._update_canvas()
            self._canvas_initialized = True

    def _update_canvas(self, *args):
        if not self.parent:
            return
        if self.size[0] <= 0 or self.size[1] <= 0:
            return

        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.main_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )


class PrimaryButton(GradientButton):
    """主按钮 - 蓝色"""

    def __init__(self, **kwargs):
        self.main_color = (0.2, 0.55, 0.85, 1)
        super().__init__(**kwargs)
        self.font_size = '16sp'


class SuccessButton(GradientButton):
    """成功按钮 - 绿色"""

    def __init__(self, **kwargs):
        self.main_color = (0.2, 0.7, 0.35, 1)
        super().__init__(**kwargs)
        self.font_size = '15sp'


class DangerButton(GradientButton):
    """危险按钮 - 红色"""

    def __init__(self, **kwargs):
        self.main_color = (0.8, 0.25, 0.25, 1)
        super().__init__(**kwargs)
        self.font_size = '14sp'


class WarningButton(GradientButton):
    """警告按钮 - 橙色"""

    def __init__(self, **kwargs):
        self.main_color = (0.95, 0.6, 0.1, 1)
        super().__init__(**kwargs)
        self.font_size = '18sp'


class OutlinedButton(Button):
    """描边按钮 - 修复版"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.color = (0.2, 0.55, 0.85, 1)
        self.font_name = DEFAULT_FONT
        self.border = (0, 0, 0, 0)
        self._canvas_initialized = False
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        Clock.schedule_once(self._init_canvas, 0.1)
        # 设置文字自动缩小
        self.text_size = self.size
        self.halign = 'center'
        self.valign = 'middle'

    def _init_canvas(self, dt):
        if not self._canvas_initialized:
            self._update_canvas()
            self._canvas_initialized = True

    def _update_canvas(self, *args):
        if not self.parent:
            return
        if self.size[0] <= 0 or self.size[1] <= 0:
            return

        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.2, 0.55, 0.85, 1)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
            Color(0.95, 0.97, 0.99, 1)
            RoundedRectangle(
                pos=(self.x + 2, self.y + 2),
                size=(self.width - 4, self.height - 4),
                radius=[dp(7)]
            )


class RoundLabel(Label):
    """圆角背景标签 - 修复版"""

    def __init__(self, bg_color=(0.2, 0.5, 0.8, 0.15), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.font_name = DEFAULT_FONT
        self.padding = [dp(8), dp(4)]
        self._canvas_initialized = False
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        Clock.schedule_once(self._init_canvas, 0.1)
        self.text_size = self.size
        self.halign = 'center'
        self.valign = 'middle'

    def _init_canvas(self, dt):
        if not self._canvas_initialized:
            self._update_canvas()
            self._canvas_initialized = True

    def _update_canvas(self, *args):
        if not self.parent:
            return
        if self.size[0] <= 0 or self.size[1] <= 0:
            return

        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(
                pos=(self.x - dp(8), self.y - dp(4)),
                size=(self.width + dp(16), self.height + dp(8)),
                radius=[dp(10)]
            )


class CardBox(BoxLayout):
    """卡片容器 - 修复版"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = dp(15)
        self.spacing = dp(10)
        self.orientation = 'vertical'
        self._canvas_initialized = False
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        Clock.schedule_once(self._init_canvas, 0.1)

    def _init_canvas(self, dt):
        if not self._canvas_initialized:
            self._update_canvas()
            self._canvas_initialized = True

    def _update_canvas(self, *args):
        if not self.parent:
            return
        if self.size[0] <= 0 or self.size[1] <= 0:
            return

        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
            Color(0.9, 0.92, 0.95, 1)
            RoundedRectangle(
                pos=(self.x + 1, self.y + 1),
                size=(self.width - 2, self.height - 2),
                radius=[dp(11)]
            )


class ModernTextInput(TextInput):
    """现代化文本输入框 - 最简版"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = DEFAULT_FONT
        self.padding = [dp(12), dp(10)]
        self.cursor_color = (0.2, 0.55, 0.85, 1)
        self.background_color = (1, 1, 1, 1)
        self.hint_text_color = (0.7, 0.7, 0.7, 1)


class CustomCheckBox(BoxLayout):
    """自定义复选框"""

    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(30)
        self.spacing = dp(8)

        self.checkbox = CheckBox(size_hint_x=None, width=dp(24))
        self.checkbox.color = (0.2, 0.55, 0.85, 1)
        self.add_widget(self.checkbox)

        self.label = Label(
            text=text,
            font_name=DEFAULT_FONT,
            font_size='14sp',
            color=(0.3, 0.3, 0.3, 1),
            halign='left'
        )
        self.add_widget(self.label)
        self.add_widget(Widget())

    @property
    def active(self):
        return self.checkbox.active

    @active.setter
    def active(self, value):
        self.checkbox.active = value


# ==================== 工具函数 ====================
# 注意：get_base_dir 已在前面定义，这里不再重复

# ==================== 用户数据管理模块 ====================
class UserManager:
    """用户数据管理器 - 单例模式"""
    _instance = None
    _users = None
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_users(self):
        if self._loaded and self._users is not None:
            return True

        try:
            base_dir = get_base_dir()
            paths = [
                os.path.join(base_dir, 'users.json'),
                os.path.join(base_dir, 'data', 'users.json'),
                'users.json',
                'data/users.json'
            ]

            for path in paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        self._users = json.load(f)
                    print(f"从文件加载了 {len(self._users)} 个用户: {path}")
                    self._loaded = True
                    return True

            print("用户文件 users.json 不存在！")
            self._users = []
            self._loaded = True
            return False

        except Exception as e:
            print(f"加载用户数据失败: {e}")
            self._users = []
            self._loaded = True
            return False

    def get_user_by_code(self, code):
        if not self._loaded:
            self.load_users()

        for user in self._users:
            if user.get('code') == code:
                return user
        return None

    def get_user_name(self, code):
        user = self.get_user_by_code(code)
        if user:
            return user.get('name', code)
        return code


# ==================== 数据管理模块 ====================
class DataManager:
    """数据管理器 - 单例模式"""
    _instance = None
    _data = None
    _index = None
    _loading = False
    _error = None
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_data(self, callback=None):
        """异步加载数据（保留兼容）"""
        if self._loaded and self._data is not None:
            if callback:
                callback(self._data, self._index)
            return True

        if self._loading:
            return False

        self._loading = True
        self._error = None

        def load_thread():
            try:
                data_file = self._find_data_file()

                if data_file:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        self._data = json.load(f)
                    print(f"从文件加载了 {len(self._data)} 条数据: {data_file}")
                else:
                    self._error = "数据文件 hazard_data.json 不存在！"
                    self._data = []

                self._index = {}
                for hazard in self._data:
                    point_name = hazard.get('riskPointName', '')
                    if point_name not in self._index:
                        self._index[point_name] = []
                    self._index[point_name].append(hazard)

                print(f"建立了 {len(self._index)} 个风险点索引")
                self._loading = False
                self._loaded = True

                if callback:
                    Clock.schedule_once(lambda dt: callback(self._data, self._index), 0)

            except Exception as e:
                self._error = f"加载数据失败: {e}"
                self._data = []
                self._index = {}
                self._loading = False
                self._loaded = True
                if callback:
                    Clock.schedule_once(lambda dt: callback(self._data, self._index), 0)

        threading.Thread(target=load_thread, daemon=True).start()
        return True

    def load_data_sync(self):
        """同步加载数据，用于启动时确保数据加载完成"""
        try:
            data_file = self._find_data_file()
            
            print(f"正在查找数据文件...")
            
            if data_file:
                with open(data_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                print(f"✓ 从文件加载了 {len(self._data)} 条数据: {data_file}")
            else:
                self._error = "数据文件 hazard_data.json 不存在！"
                self._data = []
                print("✗ 未找到数据文件 hazard_data.json")
            
            self._index = {}
            for hazard in self._data:
                point_name = hazard.get('riskPointName', '')
                if point_name not in self._index:
                    self._index[point_name] = []
                self._index[point_name].append(hazard)
            
            print(f"✓ 建立了 {len(self._index)} 个风险点索引")
            self._loaded = True
            self._loading = False
            return True
            
        except Exception as e:
            self._error = f"加载数据失败: {e}"
            self._data = []
            self._index = {}
            self._loaded = True
            self._loading = False
            print(f"✗ 加载数据失败: {e}")
            return False

    def _find_data_file(self):
        base_dir = get_base_dir()
        paths = [
            os.path.join(base_dir, 'hazard_data.json'),
            os.path.join(os.getcwd(), 'hazard_data.json'),
            os.path.join(base_dir, 'data', 'hazard_data.json'),
            os.path.join(os.getcwd(), 'data', 'hazard_data.json'),
            'hazard_data.json',
        ]

        # 去重
        seen = set()
        unique_paths = []
        for path in paths:
            if path not in seen:
                seen.add(path)
                unique_paths.append(path)

        print(f"当前程序目录: {base_dir}")
        for path in unique_paths:
            exists = os.path.exists(path)
            print(f"  检查: {path} -> {'存在' if exists else '不存在'}")
            if exists:
                return path
        
        # 尝试列出当前目录所有json文件
        try:
            files = os.listdir(base_dir)
            json_files = [f for f in files if f.endswith('.json')]
            if json_files:
                print(f"当前目录下的JSON文件: {json_files}")
        except Exception as e:
            print(f"无法列出目录文件: {e}")
        
        return None

    def has_error(self):
        return self._error is not None

    def get_error(self):
        return self._error

    def get_all_data_by_point(self, point_name):
        if self._index is None:
            return []
        return self._index.get(point_name, [])

    def get_data_by_point(self, point_name, limit=30, offset=0):
        if self._index is None:
            return [], 0

        data_list = self._index.get(point_name, [])
        total = len(data_list)
        start = offset
        end = min(start + limit, total)

        return data_list[start:end], total

    def get_point_list(self):
        if self._index is None:
            return []
        return sorted(list(self._index.keys()))

    def get_total_count(self):
        if self._data is None:
            return 0
        return len(self._data)


# ==================== API客户端 ====================
class SafetyCheckClient:
    """安全检查API客户端"""

    def __init__(self):
        self.base_url = "http://it.xinxing-pipes.com:8011"
        self.session = requests.Session()
        self.token = None
        self.is_logged_in = False
        self.login_name = ''
        self.login_code = ''

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; 2201122C Build/TKQ1.220807.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/134.0.6998.135 Mobile Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "X-Requested-With": "com.baosight.anbaoxxzgandroid",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        })

    def login(self, username, password):
        if self.is_logged_in:
            return True, "已登录"

        login_url = f"{self.base_url}/sf-xxzg/mobileapi/login"
        login_data = {
            "loginName": username,
            "password": password
        }

        try:
            response = self.session.post(login_url, json=login_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('isSuccess'):
                    self.token = result.get('jwt')
                    self.session.headers.update({"token": self.token})
                    self.is_logged_in = True
                    self.login_code = username

                    user_manager = UserManager()
                    user = user_manager.get_user_by_code(username)
                    if user:
                        self.login_name = user.get('name', username)
                    else:
                        self.login_name = username

                    return True, result.get('message', '登录成功')
                else:
                    return False, result.get('message', '登录失败')
            else:
                return False, f"登录请求失败，状态码: {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "连接超时，请检查网络"
        except requests.exceptions.ConnectionError:
            return False, "网络连接失败"
        except Exception as e:
            return False, f"登录异常: {str(e)}"

    def get_hazard_check_id(self):
        if not self.is_logged_in:
            return None, "未登录，请先登录"

        url = f"{self.base_url}/sf-xxzg/mobileapi/wx/getHazardCheckId"

        try:
            response = self.session.post(url, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('isSuccess'):
                    hazard_check_id = result.get('data', {}).get('hazardCheckId')
                    return hazard_check_id, None
                else:
                    return None, result.get('message', '获取检查任务ID失败')
            else:
                return None, f"请求失败，状态码: {response.status_code}"
        except requests.exceptions.Timeout:
            return None, "获取检查任务ID超时"
        except requests.exceptions.ConnectionError:
            return None, "网络连接失败"
        except Exception as e:
            return None, f"获取检查任务ID异常: {str(e)}"

    def save_check_detail(self, check_data):
        if not self.is_logged_in:
            return None, "未登录，请先登录"

        url = f"{self.base_url}/sf-xxzg/mobileapi/wx/saveCheckDetail"

        try:
            response = self.session.post(url, json=check_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('isSuccess'):
                    return result, None
                else:
                    return None, result.get('message', '提交失败')
            else:
                return None, f"提交请求失败，状态码: {response.status_code}"
        except requests.exceptions.Timeout:
            return None, "提交超时，请检查网络"
        except requests.exceptions.ConnectionError:
            return None, "网络连接失败"
        except Exception as e:
            return None, f"提交异常: {str(e)}"


# ==================== 登录页面 ====================
class LoginScreen(Screen):
    """登录页面 - 美化版"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = SafetyCheckClient()
        self.config_file = os.path.join(get_base_dir(), 'config.json')
        self.user_manager = UserManager()
        self.user_manager.load_users()

        # 主布局
        main_layout = FloatLayout()

        # 背景装饰
        with main_layout.canvas.before:
            Color(0.95, 0.97, 0.99, 1)
            Rectangle(pos=main_layout.pos, size=main_layout.size)

            # 顶部装饰圆
            Color(0.2, 0.55, 0.85, 0.08)
            RoundedRectangle(
                pos=(0, Window.height * 0.6),
                size=(Window.width, Window.height * 0.5),
                radius=[(0, 0), (0, 0), (Window.width / 2, Window.width / 2), (Window.width / 2, Window.width / 2)]
            )

        # 登录卡片
        card = CardBox(
            size_hint=(0.85, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # 标题
        title_label = Label(
            text='安全风险管控',
            font_size='26sp',
            font_name=DEFAULT_FONT,
            color=(0.15, 0.3, 0.5, 1),
            size_hint_y=0.15,
            bold=True
        )
        card.add_widget(title_label)

        # 副标题
        subtitle = Label(
            text='请输入账号密码登录',
            font_size='13sp',
            font_name=DEFAULT_FONT,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.05
        )
        card.add_widget(subtitle)

        # 账号输入
        card.add_widget(Label(
            text='账号',
            font_size='14sp',
            font_name=DEFAULT_FONT,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=0.06,
            halign='left'
        ))
        self.username_input = ModernTextInput(
            text='',
            size_hint_y=0.08,
            multiline=False,
            hint_text='请输入账号'
        )
        card.add_widget(self.username_input)

        # 密码输入
        card.add_widget(Label(
            text='密码',
            font_size='14sp',
            font_name=DEFAULT_FONT,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=0.06,
            halign='left'
        ))
        self.password_input = ModernTextInput(
            text='',
            size_hint_y=0.08,
            multiline=False,
            password=True,
            hint_text='请输入密码'
        )
        card.add_widget(self.password_input)

        # 记住密码
        remember_layout = BoxLayout(orientation='horizontal', size_hint_y=0.06, spacing=dp(5))
        self.remember_check = CustomCheckBox(text='记住密码')
        remember_layout.add_widget(self.remember_check)
        card.add_widget(remember_layout)

        # 登录按钮
        login_btn = PrimaryButton(
            text='登 录',
            size_hint_y=0.12
        )
        login_btn.bind(on_press=self.do_login)
        card.add_widget(login_btn)

        # 版本信息
        version_label = Label(
            text='v1.0.0',
            font_size='11sp',
            font_name=DEFAULT_FONT,
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.04
        )
        card.add_widget(version_label)

        main_layout.add_widget(card)
        self.add_widget(main_layout)

        # 加载上次保存的账号密码
        self.load_saved_login()

    def load_saved_login(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    username = config.get('saved_username', '')
                    password = config.get('saved_password', '')
                    remember = config.get('remember_password', False)

                    if username:
                        self.username_input.text = username
                    if password and remember:
                        self.password_input.text = password
                    self.remember_check.active = remember
        except Exception as e:
            print(f"加载登录信息失败: {e}")

    def save_login_info(self, username, password, remember):
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

            config['saved_username'] = username
            config['remember_password'] = remember
            if remember:
                config['saved_password'] = password
            else:
                config['saved_password'] = ''

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存登录信息失败: {e}")

    def do_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self.show_message('请输入账号和密码')
            return

        self.show_loading_popup('正在登录，请稍候...')
        threading.Thread(target=self._do_login_thread, args=(username, password), daemon=True).start()

    def _do_login_thread(self, username, password):
        success, message = self.client.login(username, password)
        Clock.schedule_once(lambda dt: self._login_result(success, message, username, password), 0)

    def _login_result(self, success, message, username, password):
        self.close_loading_popup()

        if success:
            self.save_login_info(username, password, self.remember_check.active)
            self.show_auto_close_popup('登录成功！', 1)
            Clock.schedule_once(lambda dt: self.go_to_main(), 0.5)
        else:
            self.show_message(f'登录失败：{message}')

    def go_to_main(self):
        main_screen = self.manager.get_screen('main')
        main_screen.set_client(self.client)
        self.manager.current = 'main'

    def show_auto_close_popup(self, message, auto_close_time=1):
        popup = AutoClosePopup(message, auto_close_time)
        popup.open()

    def show_loading_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text=message, font_name=DEFAULT_FONT, color=(0.3, 0.3, 0.3, 1)))

        self.loading_popup = Popup(
            title='请稍候',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False,
            background_color=(1, 1, 1, 0.95)
        )
        self.loading_popup.open()

    def close_loading_popup(self):
        if hasattr(self, 'loading_popup') and self.loading_popup:
            self.loading_popup.dismiss()
            self.loading_popup = None

    def show_message(self, message):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        content.add_widget(Label(
            text=message,
            font_name=DEFAULT_FONT,
            text_size=(dp(250), None),
            halign='center',
            color=(0.3, 0.3, 0.3, 1)
        ))

        btn = PrimaryButton(text='确 定', size_hint_y=0.3)
        content.add_widget(btn)

        popup = Popup(
            title='提示',
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=True,
            background_color=(1, 1, 1, 0.95)
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()


# ==================== UI组件 ====================
class AutoClosePopup(Popup):
    """自动关闭的弹出窗口"""

    def __init__(self, message, auto_close_time=1, **kwargs):
        super().__init__(**kwargs)
        self.auto_close_time = auto_close_time
        self.title = '提示'
        self.size_hint = (0.8, 0.3)
        self.auto_dismiss = True
        self.background_color = (1, 1, 1, 0.95)

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(Label(
            text=message,
            font_name=DEFAULT_FONT,
            text_size=(dp(250), None),
            halign='center',
            color=(0.3, 0.3, 0.3, 1)
        ))
        self.content = content

        Clock.schedule_once(self.auto_dismiss_popup, auto_close_time)

    def auto_dismiss_popup(self, dt):
        self.dismiss()


class ModernHazardItem(BoxLayout):
    """现代化危险源项组件 - 修复版"""

    def __init__(self, hazard_data, **kwargs):
        super().__init__(**kwargs)
        self.hazard_data = hazard_data
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(48)
        self.spacing = dp(6)
        self.padding = [dp(8), dp(4)]
        self._canvas_initialized = False
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        Clock.schedule_once(self._init_canvas, 0.1)

        # 复选框
        self.checkbox = CheckBox(size_hint_x=0.12, size_hint_y=0.7)
        self.checkbox.color = (0.2, 0.55, 0.85, 1)
        self.add_widget(self.checkbox)

        # 文本标签
        self.label = Label(
            text=hazard_data['hazardFirst'],
            font_size='12sp',
            halign='left',
            valign='middle',
            font_name=DEFAULT_FONT,
            size_hint_x=0.7,
            text_size=(dp(180), None),
            color=(0.25, 0.25, 0.25, 1),
            shorten=True,
            shorten_from='right'
        )
        self.add_widget(self.label)

        # 状态标签
        status_label = RoundLabel(
            text='待检',
            font_size='10sp',
            bg_color=(0.95, 0.6, 0.1, 0.15),
            color=(0.95, 0.6, 0.1, 1),
            size_hint_x=0.15
        )
        self.add_widget(status_label)

    def _init_canvas(self, dt):
        if not self._canvas_initialized:
            self._update_canvas()
            self._canvas_initialized = True

    def _update_canvas(self, *args):
        if not self.parent:
            return
        if self.size[0] <= 0 or self.size[1] <= 0:
            return

        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(6)]
            )
            Color(0.95, 0.96, 0.97, 1)
            RoundedRectangle(
                pos=(self.x + 1, self.y + 1),
                size=(self.width - 2, self.height - 2),
                radius=[dp(5)]
            )

    @property
    def is_checked(self):
        return self.checkbox.active

    @is_checked.setter
    def is_checked(self, value):
        self.checkbox.active = value


class ModernLoadMoreButton(Button):
    """现代化加载更多按钮 - 修复版"""

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint_y = None
        self.height = dp(40)
        self.font_size = '13sp'
        self.font_name = DEFAULT_FONT
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.color = (0.2, 0.55, 0.85, 1)
        self._canvas_initialized = False
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        Clock.schedule_once(self._init_canvas, 0.1)
        self.text_size = self.size
        self.halign = 'center'
        self.valign = 'middle'

    def _init_canvas(self, dt):
        if not self._canvas_initialized:
            self._update_canvas()
            self._canvas_initialized = True

    def _update_canvas(self, *args):
        if not self.parent:
            return
        if self.size[0] <= 0 or self.size[1] <= 0:
            return

        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.2, 0.55, 0.85, 1)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
            Color(0.95, 0.97, 0.99, 1)
            RoundedRectangle(
                pos=(self.x + 1, self.y + 1),
                size=(self.width - 2, self.height - 2),
                radius=[dp(7)]
            )


# ==================== 页面 ====================
class HazardDetailScreen(Screen):
    """风险详情页面 - 美化版"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', spacing=dp(3))

        # 顶部导航
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=0.06, spacing=dp(5), padding=dp(5))
        back_btn = DangerButton(
            text='返回',
            size_hint_x=0.2,
            font_size='13sp'
        )
        back_btn.bind(on_press=self.go_back)
        nav_layout.add_widget(back_btn)

        nav_layout.add_widget(Widget())

        # 用户信息显示
        self.user_info_label = Label(
            text='',
            font_size='11sp',
            color=(0.2, 0.5, 0.8, 1),
            font_name=DEFAULT_FONT,
            size_hint_x=0.5,
            halign='right'
        )
        nav_layout.add_widget(self.user_info_label)
        self.main_layout.add_widget(nav_layout)

        # 标题区域
        header_layout = BoxLayout(orientation='vertical', size_hint_y=0.07, padding=[dp(15), dp(3)])
        self.title_label = Label(
            text='',
            font_size='17sp',
            font_name=DEFAULT_FONT,
            color=(0.15, 0.3, 0.5, 1),
            bold=True,
            halign='center'
        )
        header_layout.add_widget(self.title_label)

        self.info_label = Label(
            text='',
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            font_name=DEFAULT_FONT,
            halign='center'
        )
        header_layout.add_widget(self.info_label)
        self.main_layout.add_widget(header_layout)

        # 滚动区域
        scroll = ScrollView()
        self.hazard_grid = GridLayout(
            cols=1,
            spacing=dp(4),
            padding=dp(8),
            size_hint_y=None
        )
        self.hazard_grid.bind(minimum_height=self.hazard_grid.setter('height'))
        scroll.add_widget(self.hazard_grid)
        self.main_layout.add_widget(scroll)

        # 底部操作栏
        bottom_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.07,
            spacing=dp(6),
            padding=dp(8)
        )

        self.select_all_btn = OutlinedButton(
            text='全选',
            font_size='13sp',
            size_hint_x=0.25
        )
        self.select_all_btn.bind(on_press=self.select_all)
        bottom_layout.add_widget(self.select_all_btn)

        bottom_layout.add_widget(Widget())

        # 统计信息
        self.count_label = Label(
            text='已选 0 项',
            font_size='12sp',
            font_name=DEFAULT_FONT,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_x=0.3
        )
        bottom_layout.add_widget(self.count_label)

        self.check_btn = SuccessButton(
            text='提交',
            font_size='14sp',
            size_hint_x=0.3
        )
        self.check_btn.bind(on_press=self.perform_check)
        bottom_layout.add_widget(self.check_btn)

        self.main_layout.add_widget(bottom_layout)
        self.add_widget(self.main_layout)

        # 状态变量
        self.current_risk_point = ''
        self.hazard_items = []
        self.all_hazard_items = []
        self.loading_popup = None
        self.client = None
        self.is_logged_in = False
        self.login_name = ''
        self.login_code = ''
        self.data_manager = DataManager()
        self.current_page = 0
        self.page_size = 25
        self.total_count = 0
        self.all_hazards = []
        self.is_loading = False
        self.update_queue = []
        self.is_select_all = False
        self.all_data_loaded = False
        self.is_loading_all_data = False

    def set_client(self, client):
        self.client = client
        if client:
            self.is_logged_in = client.is_logged_in
            self.login_name = client.login_name
            self.login_code = client.login_code
            self.user_info_label.text = f'用户：{self.login_name}'

    def update_hazards(self, risk_point):
        if self.is_loading:
            self.update_queue.append(risk_point)
            return

        self.current_risk_point = risk_point
        self.current_page = 0
        self.hazard_items = []
        self.all_hazard_items = []
        self.is_select_all = False
        self.select_all_btn.text = '全选'
        self.all_data_loaded = False
        self.is_loading_all_data = False

        self.hazard_grid.clear_widgets()

        loading_label = Label(
            text='加载中...',
            font_name=DEFAULT_FONT,
            size_hint_y=None,
            height=dp(50),
            color=(0.5, 0.5, 0.5, 1)
        )
        self.hazard_grid.add_widget(loading_label)

        self.is_loading = True
        self.data_manager.load_data(self._on_data_loaded)

    def _on_data_loaded(self, data, index):
        if self.data_manager.has_error():
            Clock.schedule_once(lambda dt: self._show_error(), 0)
            return

        self.all_hazards = self.data_manager.get_all_data_by_point(self.current_risk_point)
        self.total_count = len(self.all_hazards)

        data_list, _ = self.data_manager.get_data_by_point(
            self.current_risk_point,
            limit=self.page_size,
            offset=0
        )

        self.current_page_data = data_list
        Clock.schedule_once(lambda dt: self._render_page(), 0)

    def _show_error(self):
        self.hazard_grid.clear_widgets()
        error_label = Label(
            text=self.data_manager.get_error(),
            font_name=DEFAULT_FONT,
            color=(0.8, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(50)
        )
        self.hazard_grid.add_widget(error_label)
        self.is_loading = False

    def _render_page(self):
        self.hazard_grid.clear_widgets()

        if self.total_count == 0:
            no_data = Label(
                text='该风险点暂无数据',
                font_name=DEFAULT_FONT,
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(50)
            )
            self.hazard_grid.add_widget(no_data)
            self.title_label.text = self.current_risk_point
            self.info_label.text = '暂无数据'
            self.is_loading = False
            return

        self.title_label.text = self.current_risk_point
        self.info_label.text = f'共 {self.total_count} 项'

        for hazard in self.current_page_data:
            item = ModernHazardItem(hazard)
            self.hazard_grid.add_widget(item)
            self.hazard_items.append(item)
            self.all_hazard_items.append(item)

        if len(self.all_hazard_items) < self.total_count:
            load_btn = ModernLoadMoreButton(
                text=f'加载更多 ({self.total_count - len(self.all_hazard_items)}项)'
            )
            load_btn.bind(on_press=self.load_more)
            self.hazard_grid.add_widget(load_btn)
        else:
            self.all_data_loaded = True

        self.hazard_grid.height = len(self.hazard_grid.children) * dp(52)
        self.is_loading = False
        self.update_count_label()

        if self.update_queue:
            next_point = self.update_queue.pop(0)
            self.update_hazards(next_point)

    def load_more(self, instance):
        self.current_page += 1

        data_list, _ = self.data_manager.get_data_by_point(
            self.current_risk_point,
            limit=self.page_size,
            offset=self.current_page * self.page_size
        )

        if len(self.hazard_grid.children) > 0:
            last_child = self.hazard_grid.children[0]
            if isinstance(last_child, ModernLoadMoreButton):
                self.hazard_grid.remove_widget(last_child)

        for hazard in data_list:
            item = ModernHazardItem(hazard)
            self.hazard_grid.add_widget(item)
            self.hazard_items.append(item)
            self.all_hazard_items.append(item)

        if len(self.all_hazard_items) < self.total_count:
            load_btn = ModernLoadMoreButton(
                text=f'加载更多 ({self.total_count - len(self.all_hazard_items)}项)'
            )
            load_btn.bind(on_press=self.load_more)
            self.hazard_grid.add_widget(load_btn)
        else:
            self.all_data_loaded = True

        self.info_label.text = f'共 {self.total_count} 项'
        self.hazard_grid.height = len(self.hazard_grid.children) * dp(52)
        self.update_count_label()

    def update_count_label(self):
        selected = len([item for item in self.all_hazard_items if item.is_checked])
        self.count_label.text = f'已选 {selected} 项'

    def select_all(self, instance):
        if self.select_all_btn.text == '全选':
            if not self.all_data_loaded:
                if self.is_loading_all_data:
                    return
                self.is_loading_all_data = True
                self._load_all_data_for_select_all()
                return

            for item in self.all_hazard_items:
                item.is_checked = True
            self.select_all_btn.text = '取消'
            self.is_select_all = True
        else:
            for item in self.all_hazard_items:
                item.is_checked = False
            self.select_all_btn.text = '全选'
            self.is_select_all = False
        self.update_count_label()

    def _load_all_data_for_select_all(self):
        if self.is_loading:
            return

        self.is_loading = True

        def load_all():
            all_data = self.data_manager.get_all_data_by_point(self.current_risk_point)
            Clock.schedule_once(lambda dt: self._render_all_data(all_data), 0)

        threading.Thread(target=load_all, daemon=True).start()

    def _render_all_data(self, all_data):
        self.hazard_grid.clear_widgets()
        self.hazard_items = []
        self.all_hazard_items = []

        for hazard in all_data:
            item = ModernHazardItem(hazard)
            self.hazard_grid.add_widget(item)
            self.hazard_items.append(item)
            self.all_hazard_items.append(item)

        self.total_count = len(all_data)
        self.all_data_loaded = True
        self.is_loading_all_data = False
        self.info_label.text = f'共 {self.total_count} 项'
        self.hazard_grid.height = len(self.hazard_grid.children) * dp(52)
        self.is_loading = False

        for item in self.all_hazard_items:
            item.is_checked = True
        self.select_all_btn.text = '取消'
        self.is_select_all = True
        self.update_count_label()

        self.show_auto_close_popup(f'已加载全部 {self.total_count} 项数据')

    def perform_check(self, instance):
        selected = [item for item in self.all_hazard_items if item.is_checked]

        if not selected:
            self.show_message('请至少选择一个危险源')
            return

        if not self.login_name or not self.login_code:
            self.show_message('未获取到用户信息，请重新登录')
            return

        self.show_check_confirm(selected)

    def show_check_confirm(self, selected):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

        info_label = Label(
            text=f'即将提交 {len(selected)} 个危险源\n\n检查人员：{self.login_name}',
            font_name=DEFAULT_FONT,
            text_size=(dp(250), None),
            halign='center',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=0.6
        )
        content.add_widget(info_label)

        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=0.4)

        cancel_btn = DangerButton(text='取消', font_size='14sp')
        confirm_btn = SuccessButton(text='确认', font_size='14sp')

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title='确认提交',
            content=content,
            size_hint=(0.85, 0.4),
            auto_dismiss=True,
            background_color=(1, 1, 1, 0.95)
        )

        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self._do_perform_check(selected, popup))

        popup.open()

    def _do_perform_check(self, selected, popup):
        popup.dismiss()

        if not self.is_logged_in or not self.client:
            self.show_message('未登录，请重新登录')
            return

        self.check_btn.disabled = True
        self.check_btn.text = '提交中...'
        threading.Thread(target=self.submit_check, args=(selected,), daemon=True).start()

    def submit_check(self, selected):
        try:
            hazard_check_id, error = self.client.get_hazard_check_id()

            if not hazard_check_id:
                Clock.schedule_once(lambda dt: self.show_message(f'获取任务ID失败：{error}'), 0)
                return

            str_today = datetime.now().strftime('%Y-%m-%d')
            check_detail_ids = ','.join([item.hazard_data.get('hazardId', '') for item in selected])

            check_data = {
                "checkDate": str_today,
                "checkDetailIds": check_detail_ids,
                "checkEmpCode": self.login_code,
                "checkEmpName": self.login_name,
                "checkResult": "本次检查正常",
                "hazardCheckId": hazard_check_id
            }

            result, error = self.client.save_check_detail(check_data)

            if result:
                message = f'提交成功！已提交 {len(selected)} 个危险源'
                Clock.schedule_once(lambda dt: self.show_auto_close_popup(message, 1.5), 0)
                Clock.schedule_once(lambda dt: self.clear_selections(), 0.5)
            else:
                Clock.schedule_once(lambda dt: self.show_message(f'提交失败：{error}'), 0)

        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_message(f'提交异常：{str(e)}'), 0)
        finally:
            Clock.schedule_once(lambda dt: self.restore_button(), 0.5)

    def clear_selections(self):
        for item in self.all_hazard_items:
            item.is_checked = False
        self.select_all_btn.text = '全选'
        self.is_select_all = False
        self.update_count_label()

    def restore_button(self):
        self.check_btn.disabled = False
        self.check_btn.text = '提交'

    def show_auto_close_popup(self, message, auto_close_time=1):
        popup = AutoClosePopup(message, auto_close_time)
        popup.open()

    def show_loading_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text=message, font_name=DEFAULT_FONT, color=(0.3, 0.3, 0.3, 1)))

        self.loading_popup = Popup(
            title='请稍候',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False,
            background_color=(1, 1, 1, 0.95)
        )
        self.loading_popup.open()

    def close_loading_popup(self):
        if self.loading_popup:
            self.loading_popup.dismiss()
            self.loading_popup = None

    def show_message(self, message):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        content.add_widget(Label(
            text=message,
            font_name=DEFAULT_FONT,
            text_size=(dp(250), None),
            halign='center',
            color=(0.3, 0.3, 0.3, 1)
        ))

        btn = PrimaryButton(text='确 定', size_hint_y=0.3)
        content.add_widget(btn)

        popup = Popup(
            title='提示',
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=True,
            background_color=(1, 1, 1, 0.95)
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def go_back(self, instance):
        self.manager.current = 'hazard_list'


class MainScreen(Screen):
    """主界面 - 美化版"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = None

        main_layout = FloatLayout()

        # 背景
        with main_layout.canvas.before:
            Color(0.95, 0.97, 0.99, 1)
            Rectangle(pos=main_layout.pos, size=main_layout.size)

        # 顶部欢迎区域
        header = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.2),
            pos_hint={'top': 1},
            padding=[dp(20), dp(20)]
        )
        header.add_widget(Label(
            text='安全风险管控',
            font_size='28sp',
            font_name=DEFAULT_FONT,
            color=(0.15, 0.3, 0.5, 1),
            bold=True,
            size_hint_y=0.6,
            halign='center'
        ))
        self.user_label = Label(
            text='',
            font_size='14sp',
            font_name=DEFAULT_FONT,
            color=(0.3, 0.6, 0.9, 1),
            size_hint_y=0.4,
            halign='center'
        )
        header.add_widget(self.user_label)
        main_layout.add_widget(header)

        # 功能卡片
        card_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint=(0.9, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # 功能按钮
        hazard_btn = GradientButton(
            text='危险源录入',
            font_size='18sp',
            size_hint_y=0.3
        )
        hazard_btn.main_color = (0.2, 0.55, 0.85, 1)
        hazard_btn.bind(on_press=self.go_to_hazard_list)
        card_layout.add_widget(hazard_btn)

        info_btn = GradientButton(
            text='个人信息',
            font_size='18sp',
            size_hint_y=0.3
        )
        info_btn.main_color = (0.2, 0.7, 0.35, 1)
        info_btn.bind(on_press=self.go_to_personal_info)
        card_layout.add_widget(info_btn)

        logout_btn = GradientButton(
            text='退出登录',
            font_size='16sp',
            size_hint_y=0.3
        )
        logout_btn.main_color = (0.8, 0.25, 0.25, 0.8)
        logout_btn.bind(on_press=self.do_logout)
        card_layout.add_widget(logout_btn)

        main_layout.add_widget(card_layout)

        # 底部版本信息
        version_label = Label(
            text='v1.0.0  |  安全检查系统',
            font_size='11sp',
            font_name=DEFAULT_FONT,
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.05),
            pos_hint={'y': 0.02}
        )
        main_layout.add_widget(version_label)

        self.add_widget(main_layout)

        # 数据已在App启动时同步加载，无需再次预加载
        # 只是显示数据加载状态
        Clock.schedule_once(lambda dt: self.check_data_status(), 0.5)

    def check_data_status(self):
        data_manager = DataManager()
        if data_manager._loaded:
            count = data_manager.get_total_count()
            print(f"主界面：数据已加载，共 {count} 条")
            # 可以更新界面显示数据状态
        else:
            print("主界面：数据未加载")

    def set_client(self, client):
        self.client = client
        if client and client.is_logged_in:
            self.user_label.text = f'欢迎回来，{client.login_name}'

    def go_to_hazard_list(self, instance):
        detail_screen = self.manager.get_screen('hazard_detail')
        if self.client:
            detail_screen.set_client(self.client)
        self.manager.current = 'hazard_list'

    def go_to_personal_info(self, instance):
        info_screen = self.manager.get_screen('personal_info')
        if self.client:
            info_screen.set_user_info(self.client.login_name, self.client.login_code)
        self.manager.current = 'personal_info'

    def do_logout(self, instance):
        if self.client:
            self.client.is_logged_in = False
            self.client.token = None
            self.client.login_name = ''
            self.client.login_code = ''
        self.manager.current = 'login'


class HazardListScreen(Screen):
    """风险点列表 - 美化版"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=dp(5))

        # 导航栏
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=0.06, padding=dp(5), spacing=dp(5))
        back_btn = DangerButton(
            text='返回',
            size_hint_x=0.2,
            font_size='13sp'
        )
        back_btn.bind(on_press=self.go_back)
        nav_layout.add_widget(back_btn)

        nav_layout.add_widget(Label(
            text='风险点列表',
            font_name=DEFAULT_FONT,
            font_size='18sp',
            color=(0.15, 0.3, 0.5, 1),
            bold=True
        ))
        nav_layout.add_widget(Widget())
        self.layout.add_widget(nav_layout)

        # 加载提示
        self.loading_label = Label(
            text='加载风险点列表...',
            font_size='14sp',
            font_name=DEFAULT_FONT,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.05
        )
        self.layout.add_widget(self.loading_label)

        # 滚动网格
        scroll = ScrollView()
        self.grid = GridLayout(
            cols=2,
            spacing=dp(10),
            padding=dp(12),
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        self.layout.add_widget(scroll)

        self.add_widget(self.layout)

        # 直接检查数据是否已加载
        Clock.schedule_once(lambda dt: self.load_risk_points(), 0.1)

    def load_risk_points(self):
        data_manager = DataManager()
        
        # 如果数据已经加载完成，直接渲染
        if data_manager._loaded and data_manager._data is not None:
            self._render_buttons()
            return
        
        # 如果数据正在加载，显示等待
        self.loading_label.text = '数据加载中，请稍候...'
        self.grid.clear_widgets()
        
        # 尝试重新加载
        def on_data_loaded(data, index):
            Clock.schedule_once(lambda dt: self._render_buttons(), 0.1)
        
        data_manager.load_data(on_data_loaded)
        
        # 设置超时检查
        Clock.schedule_once(self._check_load_status, 0.5)
        Clock.schedule_once(self._check_load_status, 2.0)
        Clock.schedule_once(self._check_load_status, 5.0)

    def _check_load_status(self, dt):
        data_manager = DataManager()
        if data_manager._loaded and data_manager._data is not None:
            self._render_buttons()
            return True
        elif data_manager.has_error():
            self.loading_label.text = f'加载失败: {data_manager.get_error()}'
            return True
        else:
            # 还在加载中
            if self.loading_label.text == '加载风险点列表...':
                self.loading_label.text = '数据加载中，请稍候...'
            return False

    def _render_buttons(self):
        self.grid.clear_widgets()
        self.layout.remove_widget(self.loading_label)

        data_manager = DataManager()

        if data_manager.has_error():
            error_label = Label(
                text=f'数据文件不存在\n请创建 hazard_data.json',
                font_name=DEFAULT_FONT,
                color=(0.8, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(60)
            )
            self.grid.add_widget(error_label)
            self.grid.height = dp(70)
            return

        risk_points = data_manager.get_point_list()

        if not risk_points:
            no_data = Label(
                text='暂无数据',
                font_name=DEFAULT_FONT,
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(50)
            )
            self.grid.add_widget(no_data)
            self.grid.height = dp(60)
            return

        for point in risk_points:
            btn = GradientButton(
                text=point,
                font_size='13sp',
                size_hint_y=None,
                height=dp(50)
            )
            btn.main_color = (0.35, 0.45, 0.6, 1)
            btn.bind(on_press=lambda instance, p=point: self.go_to_hazard_detail(p))
            self.grid.add_widget(btn)

        self.grid.height = len(risk_points) * dp(60)

    def go_back(self, instance):
        self.manager.current = 'main'

    def go_to_hazard_detail(self, risk_point):
        detail_screen = self.manager.get_screen('hazard_detail')
        detail_screen.update_hazards(risk_point)
        self.manager.current = 'hazard_detail'


class PersonalInfoScreen(Screen):
    """个人信息页面 - 美化版"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.login_name = ''
        self.login_code = ''

        main_layout = FloatLayout()

        # 背景
        with main_layout.canvas.before:
            Color(0.95, 0.97, 0.99, 1)
            Rectangle(pos=main_layout.pos, size=main_layout.size)

        # 返回按钮
        back_btn = DangerButton(
            text='返回',
            size_hint=(0.2, 0.05),
            pos_hint={'x': 0.02, 'top': 0.97},
            font_size='13sp'
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)

        # 个人信息卡片
        card = CardBox(
            size_hint=(0.85, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # 头像图标
        avatar = Label(
            text='用户',
            font_size='40sp',
            size_hint_y=0.3,
            halign='center',
            color=(0.2, 0.55, 0.85, 1),
            bold=True
        )
        card.add_widget(avatar)

        # 姓名
        self.name_label = Label(
            text='姓名：',
            font_size='18sp',
            font_name=DEFAULT_FONT,
            color=(0.15, 0.3, 0.5, 1),
            size_hint_y=0.15,
            bold=True,
            halign='center'
        )
        card.add_widget(self.name_label)

        # 编码
        self.code_label = Label(
            text='编码：',
            font_size='16sp',
            font_name=DEFAULT_FONT,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.15,
            halign='center'
        )
        card.add_widget(self.code_label)

        # 分割线
        divider = Label(
            text='-' * 20,
            font_size='12sp',
            color=(0.85, 0.85, 0.85, 1),
            size_hint_y=0.05
        )
        card.add_widget(divider)

        # 状态
        status_label = RoundLabel(
            text='已登录',
            font_size='14sp',
            bg_color=(0.2, 0.7, 0.35, 0.15),
            color=(0.2, 0.7, 0.35, 1),
            size_hint_y=0.1,
            halign='center'
        )
        card.add_widget(status_label)

        main_layout.add_widget(card)

        # 版本信息
        version_label = Label(
            text='安全风险管控系统 v1.0.0',
            font_size='11sp',
            font_name=DEFAULT_FONT,
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.04),
            pos_hint={'y': 0.02}
        )
        main_layout.add_widget(version_label)

        self.add_widget(main_layout)

    def set_user_info(self, name, code):
        self.login_name = name
        self.login_code = code
        self.name_label.text = f'姓名：{name}'
        self.code_label.text = f'编码：{code}'

    def go_back(self, instance):
        self.manager.current = 'main'


# ==================== 主程序 ====================
class MyApp(App):
    def build(self):
        sm = ScreenManager()

        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(HazardListScreen(name='hazard_list'))
        sm.add_widget(HazardDetailScreen(name='hazard_detail'))
        sm.add_widget(PersonalInfoScreen(name='personal_info'))

        sm.current = 'login'

        return sm

    def on_start(self):
        # 【关键修改】使用同步加载确保数据在启动时加载完成
        print("=" * 50)
        print("应用启动，开始加载数据...")
        data_manager = DataManager()
        success = data_manager.load_data_sync()
        
        if success:
            count = data_manager.get_total_count()
            print(f"✓ 数据加载成功！共 {count} 条数据")
        else:
            print(f"✗ 数据加载失败: {data_manager.get_error()}")
        
        # 加载用户数据
        user_manager = UserManager()
        user_manager.load_users()
        
        print(f"程序目录: {get_base_dir()}")
        print("应用启动完成")
        print("=" * 50)


if __name__ == '__main__':
    MyApp().run()
