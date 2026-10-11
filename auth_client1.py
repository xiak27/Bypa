import re
import time
from DrissionPage import ChromiumPage, ChromiumOptions

class AutoBypassClient:
    def __init__(self):
        self.base_url = "https://baconbypass.xyz"

    def execute_full_auto(self, target_url):
        """
        全自动形态：驱动系统浏览器过盾 -> 自动提取 Token -> 浏览器内安全发起 API 请求
        """
        # 配置 DrissionPage 适配 Termux/Android 沙盒环境
        co = ChromiumOptions()
        co.headless(True)  # 设置为无头模式（后台默默运行，不弹窗）
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-gpu')
        
        page = ChromiumPage(co)
        try:
            print("[AutoAgent] 正在启动系统浏览器过 Cloudflare 盾...")
            # 1. 访问主站，触发并自动通过 Cloudflare JS 挑战
            page.get(self.base_url)
            time.sleep(3.5) # 等待盾完全加载并放行

            # 2. 访问目标 Platoboost 页面以自动获取初始 Token
            print(f"[AutoAgent] 正在访问目标页面: {target_url}")
            page.get(target_url)
            time.sleep(2.0)

            # 3. 从网页源码中正则匹配提取初始 Token
            html_content = page.html
            match = re.search(r'(1\.[A-Za-z0-9_\-\.]+)', html_content)
            if not match:
                return {"status": "error", "message": "未能从页面源码中自动匹配到初始化 token"}
            
            initial_token = match.group(1)
            print(f"[AutoAgent] 成功自动提取 Token: {initial_token[:15]}...")

            # 4. 直接在浏览器上下文中通过 fetch 发送请求
            # 这样可以完美继承浏览器刚刚过盾拿到的所有 Cookie（cf_clearance），绝不出现 403
            print(f"[AutoAgent] 正在通过浏览器上下文请求 Challenge...")
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

            # 5. 请求最终绕过接口
            bypass_res = page.run_js(f"""
                return fetch('{self.base_url}/api/bypass', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ url: '{target_url}', token2: '{token2}' }})
                }}).then(res => res.json());
            """)

            if not bypass_res or 'result' not in bypass_res:
                return {"status": "error", "message": f"Bypass 阶段失败: {str(bypass_res)}"}

            print(f"[AutoAgent] 绕过大功告成！")
            return {
                "status": "success",
                "result": bypass_res['result']
            }

        except Exception as e:
            return {"status": "error", "message": f"浏览器自动化执行异常: {str(e)}"}
        finally:
            # 确保每次跑完安全关闭浏览器进程，防止内存泄露
            page.quit()
