import os
import time
import json
import random
import requests
import urllib3
import ssl
from pathlib import Path
from packaging import version  # 使用 packaging 替代 distutils
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# 禁用证书验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 创建默认SSL上下文
ssl._create_default_https_context = ssl._create_unverified_context

class YouTubeBot:
    def __init__(self, account_config):
        """
        初始化YouTube机器人
        :param account_config: 账号配置信息字典
        """
        self.email = account_config['email']
        self.password = account_config['password']
        self.profile_dir = account_config['profile_dir']
        self.user_agent = account_config['user_agent']
        self.proxy = account_config.get('proxy', None)
        self.driver = None
        self.wait = None
        
        try:
            self._init_driver()
        except Exception as e:
            print(f"初始化浏览器时出现错误: {str(e)}")
            self.close()
            raise

    def _init_driver(self):
        """初始化浏览器驱动"""
        # 确保配置文件目录存在
        profile_path = Path(self.profile_dir)
        profile_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化Chrome驱动
        options = uc.ChromeOptions()
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={self.user_agent}')
        options.add_argument(f'--user-data-dir={profile_path.absolute()}')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--allow-insecure-localhost')
        options.add_argument('--disable-web-security')
        
        # 设置代理
        if self.proxy:
            proxy_str = self._get_proxy_string()
            if proxy_str:
                print(f"使用代理: {proxy_str}")
                options.add_argument(f'--proxy-server={proxy_str}')
                
                # 如果代理需要认证
                if self.proxy.get('username') and self.proxy.get('password'):
                    plugin_path = self._setup_proxy_auth()
                    if plugin_path:
                        options.add_argument(f'--load-extension={plugin_path}')
        
        try:
            # 设置 ChromeDriver 下载和验证选项
            uc.TARGET_VERSION = 'latest'
            uc.install(
                ssl_verify=False,
                ignore_ssl_errors=True,
                suppress_welcome=True
            )
            
            # 创建 Chrome 实例
            self.driver = uc.Chrome(
                options=options,
                version_main=None,  # 自动检测 Chrome 版本
                suppress_welcome=True
            )
            
            # 设置等待和超时
            self.wait = WebDriverWait(self.driver, 20)
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            
            # 设置请求拦截器来忽略证书错误
            self.driver.execute_cdp_cmd('Security.setIgnoreCertificateErrors', {'ignore': True})
            
        except Exception as e:
            print(f"创建Chrome驱动时出现错误: {str(e)}")
            raise

    def _get_proxy_string(self):
        """
        根据代理配置生成代理字符串
        """
        if not self.proxy:
            return None
            
        proxy_type = self.proxy.get('type', 'http').lower()
        host = self.proxy.get('host')
        port = self.proxy.get('port')
        
        if not (host and port):
            return None
            
        if proxy_type in ['http', 'https']:
            return f"{proxy_type}://{host}:{port}"
        elif proxy_type == 'socks5':
            return f"socks5://{host}:{port}"
        else:
            print(f"不支持的代理类型: {proxy_type}")
            return None

    def _setup_proxy_auth(self):
        """
        设置代理认证
        """
        if not (self.proxy.get('username') and self.proxy.get('password')):
            return None
            
        try:
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """

            background_js = """
            var config = {
                mode: "fixed_servers",
                rules: {
                    singleProxy: {
                        scheme: "%s",
                        host: "%s",
                        port: parseInt(%s)
                    },
                    bypassList: ["localhost"]
                }
            };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
            );
            """ % (
                self.proxy['type'],
                self.proxy['host'],
                self.proxy['port'],
                self.proxy['username'],
                self.proxy['password']
            )

            plugin_dir = Path(self.profile_dir) / "proxy_auth_plugin"
            plugin_dir.mkdir(parents=True, exist_ok=True)

            with open(plugin_dir / "manifest.json", "w") as f:
                f.write(manifest_json)

            with open(plugin_dir / "background.js", "w") as f:
                f.write(background_js)

            return str(plugin_dir)
        except Exception as e:
            print(f"设置代理认证时出现错误: {str(e)}")
            return None

    def close(self):
        """关闭浏览器"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"关闭浏览器时出现错误: {str(e)}")

    def login(self):
        """登录YouTube账号"""
        if not self.driver:
            raise Exception("浏览器未初始化")
            
        try:
            print(f"正在使用账号 {self.email} 登录YouTube...")
            
            # 设置较长的超时时间
            self.driver.set_page_load_timeout(60)
            self.wait = WebDriverWait(self.driver, 60)
            
            self.driver.get('https://accounts.google.com')
            
            # 输入邮箱
            email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "identifier")))
            email_field.send_keys(self.email)
            self.driver.find_element(By.ID, "identifierNext").click()
            
            # 输入密码
            password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_field.send_keys(self.password)
            self.driver.find_element(By.ID, "passwordNext").click()
            
            time.sleep(5)
            print("登录成功！")
            
            # 恢复正常超时时间
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 20)
            
        except Exception as e:
            print(f"登录过程中出现错误: {str(e)}")
            raise

    def process_video(self, video_config):
        """
        处理单个视频
        :param video_config: 视频配置信息字典
        """
        if not self.driver:
            raise Exception("浏览器未初始化")
            
        try:
            print(f"正在打开视频: {video_config['url']}")
            self.driver.get(video_config['url'])
            time.sleep(5)

            # 播放视频
            self.play_video()
            
            # 随机观看时间
            watch_time = random.randint(video_config['min_watch_time'], video_config['max_watch_time'])
            print(f"将观看视频 {watch_time} 秒...")
            time.sleep(watch_time)
            
            # 点赞视频
            self.like_video()
            
            # 发表评论
            self.post_comment()
            
        except Exception as e:
            print(f"处理视频时出现错误: {str(e)}")
            raise

    def play_video(self):
        """开始播放视频"""
        try:
            print("开始播放视频...")
            play_button = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ytp-play-button")))
            if "播放" in play_button.get_attribute("aria-label") or "Play" in play_button.get_attribute("aria-label"):
                play_button.click()
            print("视频正在播放")
        except Exception as e:
            print(f"播放视频时出现错误: {str(e)}")
            raise

    def like_video(self):
        """点赞视频"""
        try:
            print("尝试点赞视频...")
            like_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Like' or @aria-label='点赞']")))
            like_button.click()
            print("视频点赞成功！")
        except ElementClickInterceptedException:
            print("点赞按钮被遮挡，尝试滚动到按钮位置...")
            self.driver.execute_script("arguments[0].scrollIntoView();", like_button)
            like_button.click()
        except Exception as e:
            print(f"点赞视频时出现错误: {str(e)}")
            raise

    def get_comment_from_api(self):
        """从API获取评论内容"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            # 禁用SSL验证
            response = requests.get(config['comment_api_url'], verify=False)
            response.raise_for_status()
            return response.json()['comment']
        except Exception as e:
            print(f"从API获取评论时出现错误: {str(e)}")
            return "非常棒的视频！感谢分享！"  # 默认评论

    def post_comment(self):
        """发表评论"""
        try:
            print("正在发表评论...")
            # 滚动到评论区
            self.driver.execute_script("window.scrollTo(0, window.scrollY + 500)")
            time.sleep(2)
            
            # 点击评论框
            comment_box = self.wait.until(EC.presence_of_element_located((By.ID, "simplebox-placeholder")))
            comment_box.click()
            
            # 输入评论内容
            comment_input = self.wait.until(EC.presence_of_element_located((By.ID, "contenteditable-root")))
            comment_text = self.get_comment_from_api()
            comment_input.send_keys(comment_text)
            
            # 提交评论
            submit_button = self.wait.until(EC.presence_of_element_located((By.ID, "submit-button")))
            submit_button.click()
            print("评论发表成功！")
            
        except Exception as e:
            print(f"发表评论时出现错误: {str(e)}")
            raise

def main():
    # 读取配置文件
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"读取配置文件时出现错误: {str(e)}")
        return

    # 处理每个账号
    for account in config['accounts']:
        bot = None
        try:
            print(f"\n开始处理账号: {account['email']}")
            # 为每个账号创建新的bot实例
            bot = YouTubeBot(account)
            
            # 登录
            bot.login()
            
            # 处理每个视频
            for video in config['videos']:
                try:
                    bot.process_video(video)
                    # 在处理视频之间添加随机延迟
                    time.sleep(random.randint(10, 30))
                except Exception as e:
                    print(f"处理视频 {video['url']} 时出现错误: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"处理账号 {account['email']} 时出现错误: {str(e)}")
        finally:
            # 确保浏览器被关闭
            if bot:
                bot.close()
            # 在切换账号之前添加随机延迟
            time.sleep(random.randint(30, 60))

if __name__ == "__main__":
    main() 