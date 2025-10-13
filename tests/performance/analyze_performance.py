"""
Django网站性能测试 - 性能数据分析
项目：shenyiqing.xin
功能：分析性能测试结果并生成报告
"""

import csv
import json
import os
import time
from datetime import datetime
from statistics import mean, median, stdev


class PerformanceAnalyzer:
    """性能数据分析器"""
    
    def __init__(self, results_dir="tests/reports"):
        self.results_dir = results_dir
        self.performance_data = []
        self.analysis_results = {}
    
    def load_performance_data(self, csv_file):
        """加载性能测试数据"""
        if not os.path.exists(csv_file):
            print(f"性能数据文件不存在: {csv_file}")
            return
        
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.performance_data.append(row)
        
        print(f"已加载 {len(self.performance_data)} 条性能数据")
    
    def analyze_response_times(self):
        """分析响应时间"""
        if not self.performance_data:
            return
        
        response_times = []
        for data in self.performance_data:
            try:
                response_time = float(data.get('Response Time', 0))
                if response_time > 0:
                    response_times.append(response_time)
            except (ValueError, TypeError):
                continue
        
        if response_times:
            self.analysis_results['response_times'] = {
                'count': len(response_times),
                'mean': round(mean(response_times), 3),
                'median': round(median(response_times), 3),
                'min': round(min(response_times), 3),
                'max': round(max(response_times), 3),
                'std_dev': round(stdev(response_times), 3) if len(response_times) > 1 else 0
            }
    
    def analyze_throughput(self):
        """分析吞吐量"""
        if not self.performance_data:
            return
        
        # 按时间窗口分析吞吐量
        time_windows = {}
        for data in self.performance_data:
            try:
                timestamp = data.get('Timestamp', '')
                if timestamp:
                    # 简化时间戳处理
                    time_key = timestamp[:16]  # 精确到分钟
                    if time_key not in time_windows:
                        time_windows[time_key] = 0
                    time_windows[time_key] += 1
            except (ValueError, TypeError):
                continue
        
        if time_windows:
            throughput_values = list(time_windows.values())
            self.analysis_results['throughput'] = {
                'avg_requests_per_minute': round(mean(throughput_values), 2),
                'max_requests_per_minute': max(throughput_values),
                'min_requests_per_minute': min(throughput_values)
            }
    
    def analyze_error_rates(self):
        """分析错误率"""
        if not self.performance_data:
            return
        
        total_requests = len(self.performance_data)
        error_requests = 0
        
        for data in self.performance_data:
            status_code = data.get('Status Code', '')
            if status_code and status_code.startswith('4') or status_code.startswith('5'):
                error_requests += 1
        
        error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
        
        self.analysis_results['error_rates'] = {
            'total_requests': total_requests,
            'error_requests': error_requests,
            'error_rate_percent': round(error_rate, 2)
        }
    
    def analyze_percentiles(self):
        """分析百分位数"""
        if not self.performance_data:
            return
        
        response_times = []
        for data in self.performance_data:
            try:
                response_time = float(data.get('Response Time', 0))
                if response_time > 0:
                    response_times.append(response_time)
            except (ValueError, TypeError):
                continue
        
        if response_times:
            sorted_times = sorted(response_times)
            n = len(sorted_times)
            
            self.analysis_results['percentiles'] = {
                'p50': round(sorted_times[int(n * 0.5)], 3),
                'p90': round(sorted_times[int(n * 0.9)], 3),
                'p95': round(sorted_times[int(n * 0.95)], 3),
                'p99': round(sorted_times[int(n * 0.99)], 3)
            }
    
    def analyze_by_endpoint(self):
        """按端点分析性能"""
        if not self.performance_data:
            return
        
        endpoint_stats = {}
        
        for data in self.performance_data:
            endpoint = data.get('Name', 'Unknown')
            try:
                response_time = float(data.get('Response Time', 0))
                status_code = data.get('Status Code', '')
                
                if endpoint not in endpoint_stats:
                    endpoint_stats[endpoint] = {
                        'count': 0,
                        'response_times': [],
                        'error_count': 0
                    }
                
                endpoint_stats[endpoint]['count'] += 1
                if response_time > 0:
                    endpoint_stats[endpoint]['response_times'].append(response_time)
                
                if status_code.startswith('4') or status_code.startswith('5'):
                    endpoint_stats[endpoint]['error_count'] += 1
                    
            except (ValueError, TypeError):
                continue
        
        # 计算每个端点的统计信息
        for endpoint, stats in endpoint_stats.items():
            if stats['response_times']:
                stats['avg_response_time'] = round(mean(stats['response_times']), 3)
                stats['max_response_time'] = round(max(stats['response_times']), 3)
                stats['min_response_time'] = round(min(stats['response_times']), 3)
                stats['error_rate'] = round((stats['error_count'] / stats['count']) * 100, 2)
            else:
                stats['avg_response_time'] = 0
                stats['max_response_time'] = 0
                stats['min_response_time'] = 0
                stats['error_rate'] = 0
        
        self.analysis_results['endpoint_analysis'] = endpoint_stats
    
    def generate_performance_report(self):
        """生成性能测试报告"""
        report = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'total_requests': len(self.performance_data),
                'test_duration': '30 seconds'  # 默认测试时长
            },
            'analysis_results': self.analysis_results
        }
        
        # 保存JSON报告
        json_file = os.path.join(self.results_dir, 'performance_analysis.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 生成CSV报告
        csv_file = os.path.join(self.results_dir, 'performance_summary.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value', 'Unit'])
            
            if 'response_times' in self.analysis_results:
                rt = self.analysis_results['response_times']
                writer.writerow(['Average Response Time', rt['mean'], 'seconds'])
                writer.writerow(['Median Response Time', rt['median'], 'seconds'])
                writer.writerow(['Min Response Time', rt['min'], 'seconds'])
                writer.writerow(['Max Response Time', rt['max'], 'seconds'])
                writer.writerow(['Response Time Std Dev', rt['std_dev'], 'seconds'])
            
            if 'throughput' in self.analysis_results:
                tp = self.analysis_results['throughput']
                writer.writerow(['Average Throughput', tp['avg_requests_per_minute'], 'requests/min'])
                writer.writerow(['Max Throughput', tp['max_requests_per_minute'], 'requests/min'])
            
            if 'error_rates' in self.analysis_results:
                er = self.analysis_results['error_rates']
                writer.writerow(['Error Rate', er['error_rate_percent'], '%'])
                writer.writerow(['Total Requests', er['total_requests'], 'count'])
                writer.writerow(['Error Requests', er['error_requests'], 'count'])
            
            if 'percentiles' in self.analysis_results:
                p = self.analysis_results['percentiles']
                writer.writerow(['P50 Response Time', p['p50'], 'seconds'])
                writer.writerow(['P90 Response Time', p['p90'], 'seconds'])
                writer.writerow(['P95 Response Time', p['p95'], 'seconds'])
                writer.writerow(['P99 Response Time', p['p99'], 'seconds'])
        
        print(f"性能分析报告已生成:")
        print(f"  JSON报告: {json_file}")
        print(f"  CSV报告: {csv_file}")
        
        return report
    
    def print_summary(self):
        """打印性能分析摘要"""
        print("\n" + "="*50)
        print("性能测试分析摘要")
        print("="*50)
        
        if 'response_times' in self.analysis_results:
            rt = self.analysis_results['response_times']
            print(f"响应时间统计:")
            print(f"  平均响应时间: {rt['mean']} 秒")
            print(f"  中位数响应时间: {rt['median']} 秒")
            print(f"  最小响应时间: {rt['min']} 秒")
            print(f"  最大响应时间: {rt['max']} 秒")
            print(f"  标准差: {rt['std_dev']} 秒")
        
        if 'throughput' in self.analysis_results:
            tp = self.analysis_results['throughput']
            print(f"\n吞吐量统计:")
            print(f"  平均吞吐量: {tp['avg_requests_per_minute']} 请求/分钟")
            print(f"  最大吞吐量: {tp['max_requests_per_minute']} 请求/分钟")
        
        if 'error_rates' in self.analysis_results:
            er = self.analysis_results['error_rates']
            print(f"\n错误率统计:")
            print(f"  总请求数: {er['total_requests']}")
            print(f"  错误请求数: {er['error_requests']}")
            print(f"  错误率: {er['error_rate_percent']}%")
        
        if 'percentiles' in self.analysis_results:
            p = self.analysis_results['percentiles']
            print(f"\n百分位数统计:")
            print(f"  P50: {p['p50']} 秒")
            print(f"  P90: {p['p90']} 秒")
            print(f"  P95: {p['p95']} 秒")
            print(f"  P99: {p['p99']} 秒")
        
        if 'endpoint_analysis' in self.analysis_results:
            print(f"\n端点性能分析:")
            for endpoint, stats in self.analysis_results['endpoint_analysis'].items():
                print(f"  {endpoint}:")
                print(f"    请求数: {stats['count']}")
                print(f"    平均响应时间: {stats['avg_response_time']} 秒")
                print(f"    错误率: {stats['error_rate']}%")
        
        print("="*50)
    
    def run_analysis(self, csv_file=None):
        """运行完整的性能分析"""
        if csv_file:
            self.load_performance_data(csv_file)
        
        print("开始性能数据分析...")
        
        self.analyze_response_times()
        self.analyze_throughput()
        self.analyze_error_rates()
        self.analyze_percentiles()
        self.analyze_by_endpoint()
        
        report = self.generate_performance_report()
        self.print_summary()
        
        return report


def main():
    """主函数"""
    analyzer = PerformanceAnalyzer()
    
    # 查找性能数据文件
    csv_files = [
        'tests/reports/performance_data.csv',
        'tests/reports/performance_data_stats.csv',
        'tests/reports/performance_data_failures.csv'
    ]
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            print(f"找到性能数据文件: {csv_file}")
            analyzer.run_analysis(csv_file)
            break
    else:
        print("未找到性能数据文件，生成示例分析...")
        # 生成示例数据进行分析
        analyzer.run_analysis()


if __name__ == "__main__":
    main()
