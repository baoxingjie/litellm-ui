#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试联网搜索功能
测试Bing和阿里云IQS搜索引擎的集成
"""

import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
from web_search import WebSearchTool

# 加载环境变量
load_dotenv()

def test_search_engines():
    """测试不同搜索引擎"""
    web_tool = WebSearchTool()
    
    test_query = "人工智能最新发展"
    print(f"测试查询: {test_query}")
    print(f"当前默认搜索引擎: {web_tool.default_search_engine}")
    print("-" * 50)
    
    # 提取关键词
    keywords = web_tool.extract_search_keywords(test_query)
    print(f"提取的关键词: {keywords}")
    print("-" * 50)
    
    # 测试Bing搜索
    if web_tool.bing_api_key:
        print("\n=== 测试Bing搜索 ===")
        bing_results = web_tool.search(keywords, engine='bing')
        print(f"Bing搜索结果数量: {len(bing_results)}")
        for i, result in enumerate(bing_results[:2]):
            print(f"\n{i+1}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   摘要: {result['snippet'][:100]}...")
    else:
        print("Bing API密钥未配置，跳过Bing搜索测试")
    
    # 测试阿里云IQS搜索
    if web_tool.aliyun_access_key_id and web_tool.aliyun_access_key_secret:
        print("\n=== 测试阿里云IQS搜索 ===")
        try:
            kuake_results = web_tool.search(keywords, engine='kuake')
            print(f"阿里云IQS搜索结果数量: {len(kuake_results)}")
            for i, result in enumerate(kuake_results[:2]):
                print(f"\n{i+1}. {result['title']}")
                print(f"   URL: {result['url']}")
                print(f"   摘要: {result['snippet'][:100]}...")
                if result.get('rerank_score'):
                    print(f"   重排序分数: {result['rerank_score']}")
        except Exception as e:
            print(f"阿里云IQS搜索测试失败: {e}")
    else:
        print("阿里云IQS密钥未配置，跳过阿里云IQS搜索测试")
    
    # 测试默认搜索
    print("\n=== 测试默认搜索引擎 ===")
    default_results = web_tool.search(keywords)
    print(f"默认搜索结果数量: {len(default_results)}")
    
    # 测试完整的联网查询流程
    print("\n=== 测试完整联网查询流程 ===")
    enhanced_prompt, search_results = web_tool.perform_web_search(test_query)
    print(f"生成的增强提示词长度: {len(enhanced_prompt)}")
    print(f"搜索结果数量: {len(search_results)}")
    print("\n增强提示词预览:")
    print(enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt)

def test_engine_switching():
    """测试搜索引擎切换功能"""
    print("\n" + "=" * 60)
    print("测试搜索引擎切换功能")
    print("=" * 60)
    
    # 临时修改环境变量测试
    original_engine = os.getenv('DEFAULT_SEARCH_ENGINE')
    
    # 测试设置为kuake
    os.environ['DEFAULT_SEARCH_ENGINE'] = 'kuake'
    web_tool_kuake = WebSearchTool()
    print(f"设置为kuake后的默认引擎: {web_tool_kuake.default_search_engine}")
    
    # 测试设置为bing
    os.environ['DEFAULT_SEARCH_ENGINE'] = 'bing'
    web_tool_bing = WebSearchTool()
    print(f"设置为bing后的默认引擎: {web_tool_bing.default_search_engine}")
    
    # 恢复原始设置
    if original_engine:
        os.environ['DEFAULT_SEARCH_ENGINE'] = original_engine
    else:
        os.environ.pop('DEFAULT_SEARCH_ENGINE', None)

if __name__ == "__main__":
    print("开始测试联网搜索功能")
    print("=" * 60)
    
    try:
        test_search_engines()
        test_engine_switching()
        print("\n测试完成!")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()