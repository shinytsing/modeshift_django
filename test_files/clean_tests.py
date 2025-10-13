#!/usr/bin/env python3
"""
测试文件清理脚本
用于清理不需要的测试文件和结果
"""

import os
import shutil
import glob
from datetime import datetime, timedelta

def clean_legacy_tests(days_old=30):
    """清理超过指定天数的历史测试文件"""
    legacy_dir = "test_files/legacy_tests"
    
    if not os.path.exists(legacy_dir):
        print(f"❌ 历史测试目录不存在: {legacy_dir}")
        return
    
    print(f"🧹 清理 {days_old} 天前的历史测试文件...")
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    cleaned_count = 0
    
    for file_path in glob.glob(os.path.join(legacy_dir, "*")):
        if os.path.isfile(file_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_mtime < cutoff_date:
                try:
                    os.remove(file_path)
                    print(f"🗑️ 删除: {os.path.basename(file_path)}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"❌ 删除失败 {file_path}: {str(e)}")
    
    print(f"✅ 清理完成，删除了 {cleaned_count} 个文件")

def clean_test_results():
    """清理测试结果文件"""
    print("🧹 清理测试结果文件...")
    
    # 清理常见的测试结果文件
    result_patterns = [
        "*.log",
        "*.tmp", 
        "*.cache",
        "test_results_*.txt",
        "test_output_*.txt",
        "coverage_*.html",
        "pytest_*.log"
    ]
    
    cleaned_count = 0
    
    for pattern in result_patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                print(f"🗑️ 删除: {file_path}")
                cleaned_count += 1
            except Exception as e:
                print(f"❌ 删除失败 {file_path}: {str(e)}")
    
    print(f"✅ 清理完成，删除了 {cleaned_count} 个结果文件")

def clean_empty_dirs():
    """清理空目录"""
    print("🧹 清理空目录...")
    
    test_dirs = [
        "test_files/unit_tests",
        "test_files/integration_tests", 
        "test_files/e2e_tests",
        "test_files/api_tests",
        "test_files/security_tests",
        "test_files/performance_tests"
    ]
    
    cleaned_count = 0
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            # 检查目录是否为空
            if not os.listdir(test_dir):
                try:
                    os.rmdir(test_dir)
                    print(f"🗑️ 删除空目录: {test_dir}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"❌ 删除目录失败 {test_dir}: {str(e)}")
    
    print(f"✅ 清理完成，删除了 {cleaned_count} 个空目录")

def show_test_stats():
    """显示测试文件统计"""
    print("📊 测试文件统计:")
    print("=" * 50)
    
    test_types = ['unit_tests', 'integration_tests', 'e2e_tests', 'api_tests', 'security_tests', 'performance_tests', 'legacy_tests']
    
    total_files = 0
    
    for test_type in test_types:
        test_dir = f"test_files/{test_type}"
        if os.path.exists(test_dir):
            files = [f for f in os.listdir(test_dir) if f.endswith('.py')]
            file_count = len(files)
            total_files += file_count
            
            status = "✅" if file_count > 0 else "⚠️"
            print(f"{status} {test_type}: {file_count} 个文件")
        else:
            print(f"❌ {test_type}: 目录不存在")
    
    print(f"\n📈 总计: {total_files} 个测试文件")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='测试文件清理脚本')
    parser.add_argument('--legacy', type=int, default=30, 
                       help='清理多少天前的历史测试文件 (默认30天)')
    parser.add_argument('--results', action='store_true', 
                       help='清理测试结果文件')
    parser.add_argument('--empty-dirs', action='store_true', 
                       help='清理空目录')
    parser.add_argument('--stats', action='store_true', 
                       help='显示测试文件统计')
    parser.add_argument('--all', action='store_true', 
                       help='执行所有清理操作')
    
    args = parser.parse_args()
    
    if args.stats:
        show_test_stats()
        return
    
    if args.all:
        clean_legacy_tests(args.legacy)
        clean_test_results()
        clean_empty_dirs()
        show_test_stats()
        return
    
    if args.legacy:
        clean_legacy_tests(args.legacy)
    
    if args.results:
        clean_test_results()
    
    if args.empty_dirs:
        clean_empty_dirs()
    
    if not any([args.legacy, args.results, args.empty_dirs, args.all]):
        print("请指定要执行的清理操作，使用 --help 查看帮助")

if __name__ == "__main__":
    main()
