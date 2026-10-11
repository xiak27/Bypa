import re
import time
from curl_cffi import requests as c_requests

class AutoBypassClient:
    def __init__(self):
        # 初始化带 Chrome TLS 指纹伪装的 Session，自动维护 Cookie
        self.session = c_requests.Session(impersonate="chrome")
        self.base_url = "https://baconbypass.xyz"
        self.headers = {
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Mobile Safari/537.36 EdgA/153.0.0.0"
        }

    def extract_token_from_target(self, target_url):
        """
        全自动核心：访问目标 Platoboost 链接，从网页源码中自动提取初始 token
        """
        try:
            print(f"[AutoAgent] 正在访问目标页面以提取 Token: {target_url}")
            res = self.session.get(target_url, headers={"User-Agent": self.headers["User-Agent"]}, timeout=15)
            if res.status_code != 200:
                return None, f"访问目标页面失败 (HTTP {res.status_code})"
            
            html_content = res.text
            
            # 使用正则匹配 Platoboost 页面中常见的以 "1." 开头的初始化令牌
            match = re.search(r'(1\.[A-Za-z0-9_\-\.]+)', html_content)
            if match:
                initial_token = match.group(1)
                return initial_token, None
            
            return None, "未能在目标页面源码中自动匹配到初始化 token"
        except Exception as e:
            return None, f"提取 Token 异常: {str(e)}"

    def execute_full_auto(self, target_url):
        """
        一键全自动执行流：
        URL -> 自动解析 Token -> Challenge 获取 token2 -> 最终 Bypass 结果
        """
        # 步骤 1：自动提取 Token
        initial_token, err = self.extract_token_from_target(target_url)
        if not initial_token:
            return {"status": "error", "message": err}

        print(f"[AutoAgent] 成功自动提取 Token，开始进行底层挑战...")
        time.sleep(1.0)

        try:
            # 步骤 2：请求 challenge 接口获取 token2
            challenge_res = self.session.post(
                f"{self.base_url}/api/token2/challenge",
                json={"token": initial_token},
                headers=self.headers,
                timeout=15
            )

            if challenge_res.status_code != 200:
                return {"status": "error", "message": f"Challenge 阶段失败 (HTTP {challenge_res.status_code})"}

            token2 = challenge_res.json().get("data")
            if not token2:
                return {"status": "error", "message": "未能从 Challenge 响应中解析到 token2"}

            print(f"[AutoAgent] 成功获取 token2，正在向绕过接口提交...")
            time.sleep(1.0)

            # 步骤 3：正式请求 bypass 接口
            bypass_res = self.session.post(
                f"{self.base_url}/api/bypass",
                json={"url": target_url, "token2": token2},
                headers=self.headers,
                timeout=15
            )

            if bypass_res.status_code != 200:
                return {"status": "error", "message": f"Bypass 阶段失败 (HTTP {bypass_res.status_code})"}

            bypass_data = bypass_res.json()
            result_url = bypass_data.get("result")

            if not result_url:
                return {"status": "error", "message": "Bypass 成功但未返回结果链接"}

            print(f"[AutoAgent] 绕过大功告成！")
            return {
                "status": "success",
                "result": result_url
            }

        except Exception as e:
            return {"status": "error", "message": f"全自动执行异常: {str(e)}"}
