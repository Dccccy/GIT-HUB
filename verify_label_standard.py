#!/usr/bin/env python3
# =============================================================================
# GitHub Label Color Standardization Verification Script
# 标签颜色标准化验证脚本：简化版本，专注于核心验证功能
# =============================================================================

import sys
import os
import requests
import base64
from typing import Dict, List, Optional, Tuple, Set
from dotenv import load_dotenv


class LabelStandardizationVerifier:
    """GitHub标签颜色标准化验证器"""

    def __init__(self):
        self.config = None
        self.headers = None
        self.org = None
        self.repo = None
        self.verification_results = []
        self.has_critical_error = False

    def load_configuration(self):
        """加载验证配置"""
        self.config = {
            "target_repo": "GIT-HUB",
            "feature_branch": {
                "name": "main",
                "doc_file": "docs/label-color-standardization.md"
            },
            "label_document": {
                "min_label_count": 12,
            },
            "expected_labels": [
                "bug", "enhancement", "documentation", "feature", "question",
                "priority-high", "priority-medium", "priority-low",
                "status-in-progress", "status-review", "status-done", "status-blocked"
            ]
        }

    def setup_environment(self):
        """环境准备验证"""
        load_dotenv(".env")

        github_token = os.environ.get("GITHUB_TOKEN")
        self.org = os.environ.get("GITHUB_ORG")
        self.repo = self.config["target_repo"]

        if not github_token or not self.org:
            return False

        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # 测试API连接
        test_success, _ = self.github_api_request("")
        if not test_success:
            return False

        self.record_result("环境验证", "环境配置正确，API连接成功", "success")
        return True

    def github_api_request(self, endpoint: str) -> Tuple[bool, Optional[Dict]]:
        """通用GitHub API请求"""
        if endpoint == "":
            url = f"https://api.github.com/repos/{self.org}/{self.repo}"
        else:
            url = f"https://api.github.com/repos/{self.org}/{self.repo}/{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            return response.status_code == 200, response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return False, None

    def record_result(self, task: str, message: str, status: str = "info"):
        """记录验证结果"""
        result = {
            "task": task,
            "message": message,
            "status": status,
        }
        self.verification_results.append(result)

        if status == "critical":
            self.has_critical_error = True

        status_symbol = "✅" if status == "success" else "❌" if status == "critical" else "⚠️"
        print(f"{status_symbol} {task}: {message}")

    def verify_branch_existence(self):
        """功能分支存在性验证"""
        branch_name = self.config["feature_branch"]["name"]
        success, _ = self.github_api_request(f"branches/{branch_name}")

        if success:
            self.record_result("分支验证", f"功能分支 {branch_name} 存在", "success")
            return True
        else:
            self.record_result("分支验证", f"功能分支 {branch_name} 不存在", "critical")
            return False

    def verify_label_document(self):
        """标签文档完整性验证"""
        branch_name = self.config["feature_branch"]["name"]
        doc_file = self.config["feature_branch"]["doc_file"]

        success, response = self.github_api_request(f"contents/{doc_file}?ref={branch_name}")
        if not success:
            self.record_result("文档验证", f"标签文档 {doc_file} 不存在", "critical")
            return False

        try:
            content = base64.b64decode(response["content"]).decode("utf-8")
        except (KeyError, ValueError):
            self.record_result("文档验证", "文档内容解码失败", "critical")
            return False

        # 解析标签数量
        labels = self.parse_label_table(content)
        if len(labels) < self.config["label_document"]["min_label_count"]:
            self.record_result("文档验证",
                              f"标签数量不足: 需要至少 {self.config['label_document']['min_label_count']} 个, 实际 {len(labels)} 个",
                              "warning")
        else:
            self.record_result("文档验证", f"标签文档完整, 包含 {len(labels)} 个标签", "success")
        return True
    
    def parse_label_table(self, content: str) -> List[Dict]:
        """解析标签表格"""
        labels = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('|') and '#' in line and '---' not in line:
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                if len(cells) >= 2 and cells[0] and cells[1].startswith('#'):
                    labels.append({"name": cells[0], "color": cells[1]})
        return labels

    def verify_standardization_issue(self):
        """标准化Issue合规性验证"""
        success, issues = self.github_api_request("issues?state=all&per_page=100")
        if not success:
            self.record_result("Issue验证", "无法获取Issue列表", "critical")
            return None

        # 查找标准化相关的Issue
        target_issue = None
        for issue in issues:
            if "pull_request" in issue:
                continue
                
            title = issue.get("title", "").lower()
            body = issue.get("body", "").lower() if issue.get("body") else ""
            
            if any(keyword in title for keyword in ['标签', 'label', '标准化']) or \
               any(keyword in body for keyword in ['标签体系', '颜色规范']):
                target_issue = issue
                break

        if not target_issue:
            self.record_result("Issue验证", "未找到标准化需求Issue", "warning")
            return None

        self.record_result("Issue验证", f"标准化Issue #{target_issue['number']} 验证完成: {target_issue['title']}", "success")
        return target_issue

    def generate_report(self):
        """生成验证报告"""
        print("\n" + "="*60)
        print("GitHub标签颜色标准化验证报告")
        print("="*60)

        success_count = sum(1 for r in self.verification_results if r["status"] == "success")
        warning_count = sum(1 for r in self.verification_results if r["status"] == "warning")
        error_count = sum(1 for r in self.verification_results if r["status"] == "critical")

        print(f"验证任务总数: {len(self.verification_results)}")
        print(f"成功: {success_count} | 警告: {warning_count} | 错误: {error_count}")
        print("-"*60)

        for result in self.verification_results:
            status_symbol = "✅" if result["status"] == "success" else "❌" if result["status"] == "critical" else "⚠️"
            print(f"{status_symbol} {result['task']}: {result['message']}")

        print("="*60)

        if self.has_critical_error:
            print("❌ 验证失败: 存在关键错误")
            return False
        else:
            print("✅ 所有验证通过!")
            return True

    def run_verification(self):
        """执行完整验证流程"""
        print("开始GitHub标签颜色标准化验证...")
        print(f"目标仓库: {self.org}/{self.repo}")
        print("-"*40)

        # 任务1: 环境准备验证
        if not self.setup_environment():
            return False

        # 任务2: 功能分支存在性验证
        if not self.verify_branch_existence():
            return False

        # 任务3: 标签文档完整性验证
        if not self.verify_label_document():
            return False

        # 任务4: 标准化Issue合规性验证
        self.verify_standardization_issue()

        # 生成报告
        return self.generate_report()


def main():
    """主函数"""
    verifier = LabelStandardizationVerifier()
    verifier.load_configuration()

    success = verifier.run_verification()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
