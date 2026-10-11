import re
import time
import subprocess
from DrissionPage import ChromiumPage, ChromiumOptions

class AutoBypassClient:
    def __init__(self):
        self.base_url = "https://baconbypass.xyz"
        self.port = 9222

    def _start_browser_process(self):
        """
        在 Termux 后台自主拉起 Chromium 浏览器并开启远程调试端口，彻底规避路径报错
        """
        try:
            # 杀掉可能残存的旧进程
            subprocess.run(['pkill', '-f', 'chromium'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.5)

            # 在后台无头启动系统 Chromium
            cmd = [
                'chromium',
                f'--remote-debugging-port={self.port}',
                '--no-sandbox',
                '--headless',
                '--disable-gpu',
                '--disable-software-rasterizer'
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[AutoAgent] 正在后台自主拉起浏览器内核...")
            time.sleep(3.0)  # 等待浏览器服务完全启动
        except Exception as e:
            print(f"[AutoAgent] 拉起浏览器进程异常: {str(e)}")

    def execute_full_auto(self, target_url):
        # 1. 脚本自主启动浏览器
        self._start_browser_process()

        # 2. 通过 CDP 端口连接浏览器
        try:
            co = ChromiumOptions()
            co.set_local_port(self.port)
            page = ChromiumPage(addr_or_opts=co)
        except Exception as e:
            return {"status": "error", "message": f"连接浏览器调试端口失败: {str(e)}"}

        try:
            print(f"[AutoAgent] 正在访问主站过 Cloudflare 盾...")
            page.get(self.base_url)
            time.sleep(4.0)  # 等待 JS 挑战自动跑完

            # 3. 访问目标 Platoboost 页面获取初始化 Token
            print(f"[AutoAgent] 正在访问目标页面: {target_url}")
            page.get(target_url)
            time.sleep(2.0)

            # 4. 自动正则提取 Token
            html_content = page.html
            match = re.search(r'(1\.[A-Za-z0-9_\-\.]+)', html_content)
            if not match:
                return {"status": "error", "message": "未能从页面源码中自动匹配到初始化 token"}
            
            initial_token = match.group(1)
            print(f"[AutoAgent] 成功自动提取 Token: {initial_token[:15]}...")

            # 5. 在浏览器上下文中通过 fetch 发送 Challenge 请求（继承 cf_clearance）
            print(f"[AutoAgent] 正在请求 Challenge 接口...")
            challenge_res = page.run_js(f"""
                return fetch('{self.base_url}/api/token2/challenge', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ token: '{initial_token}' }})
                }}).then(res => res.json());
            """)

            if not challenge_res or 'data' not in challenge_res:
                return {"status": "error", "message": f"Challenge 阶段失败: {str(challenge_res)}"}

            token2 = challenge_res['data']
            print(f"[AutoAgent] 成功获取 token2，正在提交最终 Bypass...")

            # 6. 请求最终绕过接口
            bypass_res = page.run_js(f"""
                return fetch('{self.base_url}/api/bypass', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ url: '{target_url}', token2: '{token2}' }})
                }}).then(res => res.json());
            """)

            if not bypass_res or 'result' not in bypass_res:
                return {"status": "error", "message": f"Bypass 阶段失败: {str(bypass_res)}"}

            print(f"[AutoAgent] 全自动绕过成功！")
            return {
                "status": "success",
                "result": bypass_res['result']
            }

        except Exception as e:
            return {"status": "error", "message": f"自动化执行异常: {str(e)}"}
        finally:
            try:
                page.quit()
            except:
                pass
