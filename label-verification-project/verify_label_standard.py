#!/usr/bin/env python3
# =============================================================================
# GitHub Label Color Standardization Verification Script
# 标签颜色标准化验证脚本：完整实现9大验证任务，支持配置化适配不同项目
# 依赖：requests, python-dotenv（安装：pip install requests python-dotenv）
# =============================================================================

import sys
import os
import re
import requests
from typing import Dict, List, Optional, Tuple, Set
from dotenv import load_dotenv
from datetime import datetime


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
            # 目标仓库信息
            "target_repo": "GIT-HUB",
            
            # 功能分支配置
            "feature_branch": {
                "name": "feat/label-standardization",
                "doc_file": "docs/labels-standard.md"
            },
            
            # 标签文档配置
            "label_document": {
                "table_header": "| 标签名称 | 颜色值 | 描述 |",
                "min_label_count": 15,
                "required_columns": ["标签名称", "颜色值", "描述"]
            },
            
            # Issue验证配置
            "issue_validation": {
                "title_keywords": ["标签标准化", "Label Standardization"],
                "body_keywords": ["标签体系", "颜色规范", "标准化需求"],
                "required_labels": ["enhancement", "documentation"],
                "required_sections": ["## 问题描述", "## 预期标准", "## 标签清单"]
            },
            
            # PR验证配置
            "pr_validation": {
                "title_keywords": ["实施标签标准化", "Label Standardization Implementation"],
                "body_keywords": ["关联Issue", "标签变更", "测试结果"],
                "required_labels": ["documentation", "enhancement"],
                "required_sections": ["## 修改摘要", "## 标签变更", "## 测试结果"],
                "min_labels_count": 3
            },
            
            # 预期标签列表（根据实际项目调整）
            "expected_labels": [
                "bug", "enhancement", "documentation", "feature", "question",
                "help-wanted", "good-first-issue", "priority-high", 
                "priority-medium", "priority-low", "status-in-progress",
                "status-review", "status-done", "status-blocked", "wontfix"
            ],
            
            # 核心标签（必须存在的标签）
            "core_labels": [
                "bug", "enhancement", "documentation", "priority-high", 
                "priority-medium", "priority-low"
            ]
        }
        
    def setup_environment(self):
        """环境准备验证 - 任务1"""
        load_dotenv(".env")
        
        github_token = os.environ.get("GITHUB_TOKEN")
        self.org = os.environ.get("GITHUB_ORG")
        self.repo = self.config["target_repo"]
        
        if not github_token:
            self.record_result("环境错误", "未配置 GITHUB_TOKEN", "critical")
            return False
            
        if not self.org:
            self.record_result("环境错误", "未配置 GITHUB_ORG", "critical")
            return False
            
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # 测试API连接
        test_success, _ = self.github_api_request("")
        if not test_success:
            self.record_result("API连接失败", "无法访问GitHub API", "critical")
            return False
            
        self.record_result("环境验证", "环境配置正确，API连接成功", "success")
        return True
    
    def github_api_request(self, endpoint: str) -> Tuple[bool, Optional[Dict]]:
        """通用GitHub API请求"""
        url = f"https://api.github.com/repos/{self.org}/{self.repo}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, None
        except requests.exceptions.RequestException as e:
            print(f"[API错误] {endpoint}: {str(e)}", file=sys.stderr)
            return False, None
    
    def record_result(self, task: str, message: str, status: str = "info"):
        """记录验证结果"""
        result = {
            "task": task,
            "message": message,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        self.verification_results.append(result)
        
        if status == "critical":
            self.has_critical_error = True
            
        status_symbol = "✅" if status == "success" else "❌" if status == "critical" else "⚠️" if status == "warning" else "ℹ️"
        print(f"{status_symbol} {task}: {message}")
    
    def verify_branch_existence(self):
        """功能分支存在性验证 - 任务2"""
        branch_name = self.config["feature_branch"]["name"]
        success, _ = self.github_api_request(f"branches/{branch_name}")
        
        if success:
            self.record_result("分支验证", f"功能分支 {branch_name} 存在", "success")
            return True
        else:
            self.record_result("分支验证", f"功能分支 {branch_name} 不存在", "critical")
            return False
    
    def verify_label_document(self):
        """标签文档完整性验证 - 任务3"""
        branch_name = self.config["feature_branch"]["name"]
        doc_file = self.config["feature_branch"]["doc_file"]
        
        success, response = self.github_api_request(f"contents/{doc_file}?ref={branch_name}")
        if not success:
            self.record_result("文档验证", f"标签文档 {doc_file} 不存在", "critical")
            return False
        
        # 获取文件内容
        import base64
        content = base64.b64decode(response["content"]).decode("utf-8")
        
        # 检查表格格式
        table_header = self.config["label_document"]["table_header"]
        if table_header not in content:
            self.record_result("文档验证", "标签文档缺少标准表格格式", "critical")
            return False
        
        # 解析标签数量
        labels = self.parse_label_table(content, table_header)
        if len(labels) < self.config["label_document"]["min_label_count"]:
            self.record_result("文档验证", 
                              f"标签数量不足: 需要至少 {self.config['label_document']['min_label_count']} 个, 实际 {len(labels)} 个", 
                              "critical")
            return False
        
        self.record_result("文档验证", 
                          f"标签文档完整, 包含 {len(labels)} 个标签", 
                          "success")
        return True
    
    def parse_label_table(self, content: str, table_header: str) -> List[Dict]:
        """解析标签表格"""
        labels = []
        lines = content.split('\n')
        in_table = False
        headers = []
        
        for line in lines:
            if table_header in line:
                in_table = True
                # 解析表头
                headers = [h.strip() for h in line.strip('|').split('|')]
                continue
            
            if in_table and line.startswith('|') and '---' not in line:
                values = [v.strip() for v in line.strip('|').split('|')]
                if len(values) >= 3:  # 至少包含名称、颜色、描述
                    label_data = dict(zip(headers, values))
                    labels.append(label_data)
            
            if in_table and line.strip() == '':
                break
        
        return labels
    
    def verify_standardization_issue(self):
        """标准化Issue合规性验证 - 任务4"""
        title_keywords = self.config["issue_validation"]["title_keywords"]
        
        # 搜索相关Issue
        success, issues = self.github_api_request("issues?state=all&per_page=50")
        if not success:
            self.record_result("Issue验证", "无法获取Issue列表", "critical")
            return False
        
        target_issue = None
        for issue in issues:
            if "pull_request" in issue:
                continue  # 跳过PR
                
            title = issue.get("title", "")
            if any(keyword in title for keyword in title_keywords):
                target_issue = issue
                break
        
        if not target_issue:
            self.record_result("Issue验证", "未找到标准化需求Issue", "critical")
            return False
        
        # 验证Issue内容
        issue_body = target_issue.get("body", "")
        issue_labels = [label["name"] for label in target_issue.get("labels", [])]
        
        # 检查必需关键词
        missing_keywords = []
        for keyword in self.config["issue_validation"]["body_keywords"]:
            if keyword not in issue_body:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            self.record_result("Issue验证", 
                              f"Issue缺少关键词: {', '.join(missing_keywords)}", 
                              "warning")
        
        # 检查必需章节
        missing_sections = []
        for section in self.config["issue_validation"]["required_sections"]:
            if section not in issue_body:
                missing_sections.append(section)
        
        if missing_sections:
            self.record_result("Issue验证", 
                              f"Issue缺少章节: {', '.join(missing_sections)}", 
                              "warning")
        
        # 检查标签
        missing_labels = []
        for label in self.config["issue_validation"]["required_labels"]:
            if label not in issue_labels:
                missing_labels.append(label)
        
        if missing_labels:
            self.record_result("Issue验证", 
                              f"Issue缺少标签: {', '.join(missing_labels)}", 
                              "warning")
        
        self.record_result("Issue验证", 
                          f"标准化Issue #{target_issue['number']} 验证完成", 
                          "success")
        return target_issue
    
    def verify_standardization_pr(self, issue):
        """标准化PR合规性验证 - 任务5"""
        title_keywords = self.config["pr_validation"]["title_keywords"]
        
        # 搜索相关PR
        success, prs = self.github_api_request("pulls?state=all&per_page=50")
        if not success:
            self.record_result("PR验证", "无法获取PR列表", "critical")
            return None
        
        target_pr = None
        for pr in prs:
            title = pr.get("title", "")
            if any(keyword in title for keyword in title_keywords):
                target_pr = pr
                break
        
        if not target_pr:
            self.record_result("PR验证", "未找到标准化实施PR", "critical")
            return None
        
        # 验证PR内容
        pr_body = target_pr.get("body", "")
        pr_labels = [label["name"] for label in target_pr.get("labels", [])]
        
        # 检查关联Issue
        if f"#{issue['number']}" not in pr_body:
            self.record_result("PR验证", "PR未关联标准化Issue", "warning")
        
        # 检查必需章节
        missing_sections = []
        for section in self.config["pr_validation"]["required_sections"]:
            if section not in pr_body:
                missing_sections.append(section)
        
        if missing_sections:
            self.record_result("PR验证", 
                              f"PR缺少章节: {', '.join(missing_sections)}", 
                              "warning")
        
        # 检查标签数量
        if len(pr_labels) < self.config["pr_validation"]["min_labels_count"]:
            self.record_result("PR验证", 
                              f"PR标签数量不足: 需要至少 {self.config['pr_validation']['min_labels_count']} 个", 
                              "warning")
        
        self.record_result("PR验证", 
                          f"标准化PR #{target_pr['number']} 验证完成", 
                          "success")
        return target_pr
    
    def verify_issue_label_completeness(self, issue):
        """Issue标签完整性验证 - 任务6"""
        issue_labels = [label["name"] for label in issue.get("labels", [])]
        expected_labels = set(self.config["expected_labels"])
        actual_labels = set(issue_labels)
        
        missing_labels = expected_labels - actual_labels
        
        if missing_labels:
            self.record_result("标签完整性", 
                              f"Issue缺少 {len(missing_labels)} 个预期标签", 
                              "warning")
            return False
        
        self.record_result("标签完整性", 
                          "Issue包含所有预期标签", 
                          "success")
        return True
    
    def verify_issue_comments(self, issue, pr):
        """Issue评论追溯验证 - 任务7"""
        issue_number = issue["number"]
        pr_number = pr["number"]
        
        success, comments = self.github_api_request(f"issues/{issue_number}/comments")
        if not success:
            self.record_result("评论验证", "无法获取Issue评论", "warning")
            return False
        
        pr_reference_found = False
        completion_keyword_found = False
        
        for comment in comments:
            body = comment.get("body", "")
            
            if f"#{pr_number}" in body or f"pull/{pr_number}" in body:
                pr_reference_found = True
            
            if any(keyword in body.lower() for keyword in ["完成", "完成验证", "已验证", "标准化完成"]):
                completion_keyword_found = True
        
        if not pr_reference_found:
            self.record_result("评论验证", "Issue评论中未找到PR引用", "warning")
        
        if not completion_keyword_found:
            self.record_result("评论验证", "Issue评论中未找到完成验证关键词", "warning")
        
        if pr_reference_found and completion_keyword_found:
            self.record_result("评论验证", "Issue评论追溯验证通过", "success")
            return True
        
        return False
    
    def verify_document_label_consistency(self):
        """文档与标签一致性验证 - 任务8"""
        branch_name = self.config["feature_branch"]["name"]
        doc_file = self.config["feature_branch"]["doc_file"]
        
        success, response = self.github_api_request(f"contents/{doc_file}?ref={branch_name}")
        if not success:
            self.record_result("一致性验证", "无法获取标签文档", "critical")
            return False
        
        import base64
        content = base64.b64decode(response["content"]).decode("utf-8")
        
        # 解析文档中的标签
        table_header = self.config["label_document"]["table_header"]
        documented_labels = self.parse_label_table(content, table_header)
        doc_label_names = {label["标签名称"] for label in documented_labels if "标签名称" in label}
        
        # 获取实际仓库标签
        success, repo_labels = self.github_api_request("labels?per_page=100")
        if not success:
            self.record_result("一致性验证", "无法获取仓库标签", "critical")
            return False
        
        repo_label_names = {label["name"] for label in repo_labels}
        
        # 比较差异
        missing_in_doc = repo_label_names - doc_label_names
        extra_in_doc = doc_label_names - repo_label_names
        
        if missing_in_doc:
            self.record_result("一致性验证", 
                              f"文档缺少 {len(missing_in_doc)} 个实际标签", 
                              "warning")
        
        if extra_in_doc:
            self.record_result("一致性验证", 
                              f"文档包含 {len(extra_in_doc)} 个多余标签", 
                              "warning")
        
        if not missing_in_doc and not extra_in_doc:
            self.record_result("一致性验证", 
                              "文档与实际标签完全一致", 
                              "success")
            return True
        
        return len(missing_in_doc) == 0  # 只关心文档是否缺少实际标签
    
    def verify_pr_core_labels(self, pr):
        """PR核心标签合规性验证 - 任务9"""
        pr_labels = [label["name"] for label in pr.get("labels", [])]
        core_labels = set(self.config["core_labels"])
        pr_label_set = set(pr_labels)
        
        missing_core_labels = core_labels - pr_label_set
        
        if missing_core_labels:
            self.record_result("核心标签验证", 
                              f"PR缺少 {len(missing_core_labels)} 个核心标签", 
                              "warning")
            return False
        
        self.record_result("核心标签验证", 
                          "PR包含所有核心标签", 
                          "success")
        return True
    
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
        elif error_count > 0:
            print("⚠️ 验证完成但存在警告")
            return True
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
        issue = self.verify_standardization_issue()
        if not issue:
            return False
        
        # 任务5: 标准化PR合规性验证
        pr = self.verify_standardization_pr(issue)
        if not pr:
            return False
        
        # 任务6: Issue标签完整性验证
        self.verify_issue_label_completeness(issue)
        
        # 任务7: Issue评论追溯验证
        self.verify_issue_comments(issue, pr)
        
        # 任务8: 文档与标签一致性验证
        self.verify_document_label_consistency()
        
        # 任务9: PR核心标签合规性验证
        self.verify_pr_core_labels(pr)
        
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