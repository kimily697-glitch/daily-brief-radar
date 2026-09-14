"""
一键运行：依次执行抓取 → AI摘要 → 发送简报邮件

每天运行一次早间简报。

用法：python run_all.py
"""
import subprocess
import sys
import time

# 每一步最多重试几次、每次重试前等多久（秒）
MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 60

FETCH_STEPS = [
    ("抓取 GitHub Trending", "fetchers/fetch_github_trending.py"),
    ("抓取教务网通知", "fetchers/fetch_jwc_news.py"),
    ("抓取 Hacker News", "fetchers/fetch_hacker_news.py"),
    ("抓取科技/AI媒体RSS", "fetchers/fetch_rss_sources.py"),
    ("抓取经济/政治/科学突破新闻", "fetchers/fetch_category_news.py"),
]

steps = FETCH_STEPS + [
    ("生成AI摘要", "core/summarize.py"),
    ("发送简报邮件", "core/send_email.py"),
]

def run_step_with_retry(step_name, script, extra_args):
    """执行一步，失败就等一会儿重试，重试次数用完才算真正失败"""
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n{'='*40}")
        print(f"▶ 正在执行：{step_name}（第{attempt}次尝试）")
        print('='*40)
        result = subprocess.run([sys.executable, script] + extra_args)
        if result.returncode == 0:
            return True
        print(f"⚠️ {step_name} 第{attempt}次失败（退出码 {result.returncode}）")
        if attempt < MAX_RETRIES:
            print(f"   等待 {RETRY_WAIT_SECONDS} 秒后重试...")
            time.sleep(RETRY_WAIT_SECONDS)
    print(f"❌ {step_name} 重试{MAX_RETRIES}次仍然失败，停止后续步骤")
    return False


all_ok = True
for step in steps:
    step_name, script = step[0], step[1]
    extra_args = list(step[2:])
    if not run_step_with_retry(step_name, script, extra_args):
        all_ok = False
        break

if all_ok:
    print("\n✅ 全部完成！早间简报已生成并发送")
else:
      sys.exit(1)
  
