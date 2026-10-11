import re
import time
import subprocess
from DrissionPage import ChromiumPage, ChromiumOptions

class AutoBypassClient:
    def __init__(self):
        self.base_url = "https://baconbypass.xyz"
        self.port = 9222
        # Termux 中 Chromium 的绝对路径
        self.browser_path = '/data/data/com.termux/files/usr/bin/chromium'

    def _start_browser_process(self):
        """
        使用绝对路径在后台拉起 Chromium 并开启调试端口
        """
        try:
            subprocess.run(['pkill', '-f', 'chromium'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.5)

            cmd = [
                self.browser_path,
                f'--remote-debugging-port={self.port}',
                '--no-sandbox',
                '--headless',
                '--disable-gpu',
                '--disable-software-rasterizer'
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[AutoAgent] 正在后台自主拉起浏览器内核...")
            time.sleep(3.0)
        except Exception as e:
            print(f"[AutoAgent] 拉起浏览器进程异常: {str(e)}")

    def execute_full_auto(self, target_url):
        # 1. 后台自主启动浏览器
        self._start_browser_process()

        try:
            co = ChromiumOptions()
            co.set_local_port(self.port)
            co.set_browser_path(self.browser_path)
            page = ChromiumPage(addr_or_opts=co)
        except Exception as e:
            return {"status": "error", "message": f"连接浏览器调试端口失败: {str(e)}"}

        try:
            print(f"[AutoAgent] 正在访问主站过 Cloudflare 盾...")
            page.get(self.base_url)
            time.sleep(4.0)

            print(f"[AutoAgent] 正在访问目标页面: {target_url}")
            page.get(target_url)
            time.sleep(2.0)

            html_content = page.html
            match = re.search(r'(1\.[A-Za-z0-9_\-\.]+)', html_content)
            if not match:
                return {"status": "error", "message": "未能从页面源码中自动匹配到初始化 token"}
            
            initial_token = match.group(1)
            print(f"[AutoAgent] 成功自动提取 Token: {initial_token[:15]}...")

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
