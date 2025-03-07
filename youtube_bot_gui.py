import sys
import json
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QLabel, QLineEdit,
                             QPushButton, QSpinBox, QTableWidget, QTableWidgetItem,
                             QMessageBox, QFileDialog, QComboBox, QGroupBox)
from PySide6.QtCore import Qt
from youtube_bot import YouTubeBot

class YouTubeBotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Bot 管理器")
        self.setMinimumSize(1000, 700)  # 增加窗口大小以适应新的控件
        
        # 初始化配置
        self.config = self.load_config()
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建主布局
        layout = QVBoxLayout(main_widget)
        
        # 创建标签页
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # 添加账号管理标签页
        self.account_tab = self.create_account_tab()
        tabs.addTab(self.account_tab, "账号管理")
        
        # 添加视频管理标签页
        self.video_tab = self.create_video_tab()
        tabs.addTab(self.video_tab, "视频管理")
        
        # 添加运行控制按钮
        control_layout = QHBoxLayout()
        start_button = QPushButton("开始运行")
        start_button.clicked.connect(self.start_bot)
        control_layout.addWidget(start_button)
        
        save_button = QPushButton("保存配置")
        save_button.clicked.connect(self.save_config)
        control_layout.addWidget(save_button)
        
        layout.addLayout(control_layout)

    def create_account_tab(self):
        """创建账号管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 账号表格
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(8)  # 增加列数以包含代理信息
        self.account_table.setHorizontalHeaderLabels([
            "邮箱", "密码", "配置目录", "User Agent",
            "代理类型", "代理地址", "代理端口", "代理认证"
        ])
        layout.addWidget(self.account_table)
        
        # 添加账号的输入区域
        input_layout = QVBoxLayout()
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QHBoxLayout()
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("邮箱")
        basic_layout.addWidget(self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        basic_layout.addWidget(self.password_input)
        
        self.profile_input = QLineEdit()
        self.profile_input.setPlaceholderText("配置目录")
        basic_layout.addWidget(self.profile_input)
        
        self.user_agent_input = QLineEdit()
        self.user_agent_input.setPlaceholderText("User Agent")
        basic_layout.addWidget(self.user_agent_input)
        
        basic_group.setLayout(basic_layout)
        input_layout.addWidget(basic_group)
        
        # 代理设置组
        proxy_group = QGroupBox("代理设置")
        proxy_layout = QHBoxLayout()
        
        self.proxy_type_input = QComboBox()
        self.proxy_type_input.addItems(["http", "https", "socks5"])
        proxy_layout.addWidget(QLabel("代理类型:"))
        proxy_layout.addWidget(self.proxy_type_input)
        
        self.proxy_host_input = QLineEdit()
        self.proxy_host_input.setPlaceholderText("代理地址")
        proxy_layout.addWidget(QLabel("地址:"))
        proxy_layout.addWidget(self.proxy_host_input)
        
        self.proxy_port_input = QLineEdit()
        self.proxy_port_input.setPlaceholderText("端口")
        proxy_layout.addWidget(QLabel("端口:"))
        proxy_layout.addWidget(self.proxy_port_input)
        
        self.proxy_username_input = QLineEdit()
        self.proxy_username_input.setPlaceholderText("用户名")
        proxy_layout.addWidget(QLabel("用户名:"))
        proxy_layout.addWidget(self.proxy_username_input)
        
        self.proxy_password_input = QLineEdit()
        self.proxy_password_input.setPlaceholderText("密码")
        self.proxy_password_input.setEchoMode(QLineEdit.Password)
        proxy_layout.addWidget(QLabel("密码:"))
        proxy_layout.addWidget(self.proxy_password_input)
        
        proxy_group.setLayout(proxy_layout)
        input_layout.addWidget(proxy_group)
        
        layout.addLayout(input_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        add_account_btn = QPushButton("添加账号")
        add_account_btn.clicked.connect(self.add_account)
        button_layout.addWidget(add_account_btn)
        
        remove_account_btn = QPushButton("删除选中账号")
        remove_account_btn.clicked.connect(self.remove_account)
        button_layout.addWidget(remove_account_btn)
        
        layout.addLayout(button_layout)
        
        # 加载现有账号
        self.load_accounts()
        
        return widget

    def create_video_tab(self):
        """创建视频管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 视频表格
        self.video_table = QTableWidget()
        self.video_table.setColumnCount(3)
        self.video_table.setHorizontalHeaderLabels(["视频链接", "最小观看时间(秒)", "最大观看时间(秒)"])
        layout.addWidget(self.video_table)
        
        # 添加视频的输入区域
        input_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("视频链接")
        input_layout.addWidget(self.url_input)
        
        self.min_time_input = QSpinBox()
        self.min_time_input.setRange(1, 3600)
        self.min_time_input.setValue(30)
        self.min_time_input.setPrefix("最小时间: ")
        self.min_time_input.setSuffix(" 秒")
        input_layout.addWidget(self.min_time_input)
        
        self.max_time_input = QSpinBox()
        self.max_time_input.setRange(1, 3600)
        self.max_time_input.setValue(60)
        self.max_time_input.setPrefix("最大时间: ")
        self.max_time_input.setSuffix(" 秒")
        input_layout.addWidget(self.max_time_input)
        
        layout.addLayout(input_layout)
        
        # API设置
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("评论API地址:"))
        self.api_input = QLineEdit()
        self.api_input.setText(self.config.get("comment_api_url", ""))
        api_layout.addWidget(self.api_input)
        layout.addLayout(api_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        add_video_btn = QPushButton("添加视频")
        add_video_btn.clicked.connect(self.add_video)
        button_layout.addWidget(add_video_btn)
        
        remove_video_btn = QPushButton("删除选中视频")
        remove_video_btn.clicked.connect(self.remove_video)
        button_layout.addWidget(remove_video_btn)
        
        layout.addLayout(button_layout)
        
        # 加载现有视频
        self.load_videos()
        
        return widget

    def load_config(self):
        """加载配置文件"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"accounts": [], "videos": [], "comment_api_url": ""}

    def save_config(self):
        """保存配置到文件"""
        # 更新配置对象
        self.config["accounts"] = []
        for row in range(self.account_table.rowCount()):
            account = {
                "email": self.account_table.item(row, 0).text(),
                "password": self.account_table.item(row, 1).text(),
                "profile_dir": self.account_table.item(row, 2).text(),
                "user_agent": self.account_table.item(row, 3).text()
            }
            
            # 添加代理配置
            proxy_type = self.account_table.item(row, 4).text() if self.account_table.item(row, 4) else None
            if proxy_type:
                proxy = {
                    "type": proxy_type,
                    "host": self.account_table.item(row, 5).text(),
                    "port": self.account_table.item(row, 6).text()
                }
                
                # 添加代理认证信息
                auth = self.account_table.item(row, 7).text()
                if auth:
                    username, password = auth.split(":", 1)
                    proxy["username"] = username
                    proxy["password"] = password
                
                account["proxy"] = proxy
            
            self.config["accounts"].append(account)
        
        self.config["videos"] = []
        for row in range(self.video_table.rowCount()):
            video = {
                "url": self.video_table.item(row, 0).text(),
                "min_watch_time": int(self.video_table.item(row, 1).text()),
                "max_watch_time": int(self.video_table.item(row, 2).text())
            }
            self.config["videos"].append(video)
        
        self.config["comment_api_url"] = self.api_input.text()
        
        # 保存到文件
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "成功", "配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置时出错: {str(e)}")

    def load_accounts(self):
        """加载账号到表格"""
        self.account_table.setRowCount(0)
        for account in self.config["accounts"]:
            row = self.account_table.rowCount()
            self.account_table.insertRow(row)
            self.account_table.setItem(row, 0, QTableWidgetItem(account["email"]))
            self.account_table.setItem(row, 1, QTableWidgetItem(account["password"]))
            self.account_table.setItem(row, 2, QTableWidgetItem(account["profile_dir"]))
            self.account_table.setItem(row, 3, QTableWidgetItem(account["user_agent"]))
            
            # 添加代理信息
            if "proxy" in account:
                proxy = account["proxy"]
                self.account_table.setItem(row, 4, QTableWidgetItem(proxy.get("type", "")))
                self.account_table.setItem(row, 5, QTableWidgetItem(proxy.get("host", "")))
                self.account_table.setItem(row, 6, QTableWidgetItem(proxy.get("port", "")))
                auth = f"{proxy.get('username', '')}:{proxy.get('password', '')}" if proxy.get('username') else ""
                self.account_table.setItem(row, 7, QTableWidgetItem(auth))

    def load_videos(self):
        """加载视频到表格"""
        self.video_table.setRowCount(0)
        for video in self.config["videos"]:
            row = self.video_table.rowCount()
            self.video_table.insertRow(row)
            self.video_table.setItem(row, 0, QTableWidgetItem(video["url"]))
            self.video_table.setItem(row, 1, QTableWidgetItem(str(video["min_watch_time"])))
            self.video_table.setItem(row, 2, QTableWidgetItem(str(video["max_watch_time"])))

    def add_account(self):
        """添加新账号"""
        email = self.email_input.text()
        password = self.password_input.text()
        profile = self.profile_input.text()
        user_agent = self.user_agent_input.text()
        
        # 获取代理信息
        proxy_type = self.proxy_type_input.currentText()
        proxy_host = self.proxy_host_input.text()
        proxy_port = self.proxy_port_input.text()
        proxy_username = self.proxy_username_input.text()
        proxy_password = self.proxy_password_input.text()
        
        if not all([email, password, profile, user_agent]):
            QMessageBox.warning(self, "警告", "请填写所有账号基本信息")
            return
        
        row = self.account_table.rowCount()
        self.account_table.insertRow(row)
        self.account_table.setItem(row, 0, QTableWidgetItem(email))
        self.account_table.setItem(row, 1, QTableWidgetItem(password))
        self.account_table.setItem(row, 2, QTableWidgetItem(profile))
        self.account_table.setItem(row, 3, QTableWidgetItem(user_agent))
        
        # 添加代理信息到表格
        if proxy_host and proxy_port:
            self.account_table.setItem(row, 4, QTableWidgetItem(proxy_type))
            self.account_table.setItem(row, 5, QTableWidgetItem(proxy_host))
            self.account_table.setItem(row, 6, QTableWidgetItem(proxy_port))
            auth = f"{proxy_username}:{proxy_password}" if proxy_username and proxy_password else ""
            self.account_table.setItem(row, 7, QTableWidgetItem(auth))
        
        # 清空输入框
        self.email_input.clear()
        self.password_input.clear()
        self.profile_input.clear()
        self.user_agent_input.clear()
        self.proxy_host_input.clear()
        self.proxy_port_input.clear()
        self.proxy_username_input.clear()
        self.proxy_password_input.clear()

    def remove_account(self):
        """删除选中的账号"""
        current_row = self.account_table.currentRow()
        if current_row >= 0:
            self.account_table.removeRow(current_row)

    def add_video(self):
        """添加新视频"""
        url = self.url_input.text()
        min_time = self.min_time_input.value()
        max_time = self.max_time_input.value()
        
        if not url:
            QMessageBox.warning(self, "警告", "请输入视频链接")
            return
        
        if min_time > max_time:
            QMessageBox.warning(self, "警告", "最小观看时间不能大于最大观看时间")
            return
        
        row = self.video_table.rowCount()
        self.video_table.insertRow(row)
        self.video_table.setItem(row, 0, QTableWidgetItem(url))
        self.video_table.setItem(row, 1, QTableWidgetItem(str(min_time)))
        self.video_table.setItem(row, 2, QTableWidgetItem(str(max_time)))
        
        # 清空输入框
        self.url_input.clear()
        self.min_time_input.setValue(30)
        self.max_time_input.setValue(60)

    def remove_video(self):
        """删除选中的视频"""
        current_row = self.video_table.currentRow()
        if current_row >= 0:
            self.video_table.removeRow(current_row)

    def start_bot(self):
        """启动机器人"""
        # 先保存当前配置
        self.save_config()
        
        reply = QMessageBox.question(
            self,
            "确认",
            "是否开始运行YouTube机器人？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 禁用所有控件
                self.setEnabled(False)
                QApplication.processEvents()
                
                import youtube_bot
                youtube_bot.main()
                QMessageBox.information(self, "成功", "机器人运行完成")
            except Exception as e:
                error_msg = str(e)
                print(f"运行出错: {error_msg}")
                QMessageBox.critical(self, "错误", f"运行机器人时出现错误:\n{error_msg}")
            finally:
                # 重新启用所有控件
                self.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeBotGUI()
    window.show()
    sys.exit(app.exec()) 