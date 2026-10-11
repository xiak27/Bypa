import time
from curl_cffi import requests as c_requests

class AutoBypassClient:
    def __init__(self):
        self.session = c_requests.Session(impersonate="chrome")
        self.base_url = "https://baconbypass.xyz"
        
        # 💡 在这里填入你通过浏览器获取一次的长效 cf_clearance（通常能用好几天）
        # 只要填了一次，接下来的几天内所有链接全自动跑通！
        self.cf_clearance = "_VN6rlq7MZVtskHEfwdF882x09evqc.9Ig7tmKQgmJQ-1791687304-1.2.1.1-bPb3rLvs5S6qiX289Azvsb9GKy86iL_889UlkZXivv_brow49JQ9cNrq9QhAcUb51iEa3vHYmZo6Ic5nqoXuljOGjS25yb7j1MdLfxP4XcSgkIK7Jvm_EHdZYtat9R7COh0h522t2GoBiEuaQSlOffMKUztwsRa9Ze2FsU9sG3_6HPPMPsKJx4kFZK8A99PvK_i_m6B3eosVOxvcKbu9fiQPt7w1Hd8WGbt2q.VdeQ.6U3yiZ9EiT28X1I3Bp8xek5bfD0HOyTbr01an2E1pfF_A9foDJ.NOkcqYAYOMaA8mQ9OX8pjFR9MT1vXsuvii5o8LOIAHXRzt_VzG9p7LL7NCTTgbCvgGyWop2kYoKexyjD7iuHCJM4z6U8BIviV7jGPFbvCJ8eHLJg.e0lPtfgSYEq9ZQprp6hMJDoS_ex9san1lATDT9qxWJo2nNpiE"
        
        self.headers = {
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Mobile Safari/537.36 EdgA/153.0.0.0",
            "Cookie": f"cf_clearance={self.cf_clearance}"
        }

    def execute_full_auto(self, target_url, initial_token):
        """
        使用长效 Cookie 自动完成 Challenge -> Bypass 全流程
        """
        try:
            print(f"[AutoAgent] 正在请求 Challenge 接口...")
            challenge_res = self.session.post(
                f"{self.base_url}/api/token2/challenge",
                json={"token": initial_token},
                headers=self.headers,
                timeout=15
            )

            if challenge_res.status_code != 200:
                return {
                    "status": "error", 
                    "message": f"Challenge 阶段失败 (HTTP {challenge_res.status_code})。提示：可能是长效 cf_clearance 已过期，需更新一次。",
                    "raw": challenge_res.text
                }

            token2 = challenge_res.json().get("data")
            if not token2:
                return {"status": "error", "message": "未能从 Challenge 响应中解析到 token2"}

            time.sleep(1.0)

            print(f"[AutoAgent] 正在请求最终 Bypass...")
            bypass_res = self.session.post(
                f"{self.base_url}/api/bypass",
                json={"url": target_url, "token2": token2},
                headers=self.headers,
                timeout=15
            )

            if bypass_res.status_code != 200:
                return {"status": "error", "message": f"Bypass 阶段失败 (HTTP {bypass_res.status_code})"}

            result_url = bypass_res.json().get("result")
            if not result_url:
                return {"status": "error", "message": "Bypass 成功但未返回结果链接"}

            return {
                "status": "success",
                "result": result_url
            }

        except Exception as e:
            return {"status": "error", "message": f"执行异常: {str(e)}"}
