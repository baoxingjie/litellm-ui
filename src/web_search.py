#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联网查询模块
实现意图分析、Bing搜索、阿里云IQS搜索和结果整合功能
"""

import os
import json
import requests
from typing import List, Dict, Any
from logger import logger
from myllm import myllm

# 阿里云IQS相关导入
try:
    from Tea.exceptions import TeaException
    from alibabacloud_iqs20241111 import models
    from alibabacloud_iqs20241111.client import Client
    from alibabacloud_tea_openapi import models as open_api_models
    KUAKE_AVAILABLE = True
except ImportError:
    KUAKE_AVAILABLE = False
    logger.warning("阿里云IQS SDK未安装，将仅支持Bing搜索")

class WebSearchTool:
    def __init__(self):
        # Bing搜索配置
        self.bing_api_key = os.getenv('BING_SEARCH_API_KEY')
        self.bing_search_url = "https://api.bing.microsoft.com/v7.0/search"
        
        # 阿里云IQS配置
        self.aliyun_access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
        self.aliyun_access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
        
        # 搜索引擎选择配置
        self.default_search_engine = os.getenv('DEFAULT_SEARCH_ENGINE', 'bing').lower()
        
        # 验证配置
        self._validate_config()
        
    def _validate_config(self):
        """验证搜索引擎配置"""
        if self.default_search_engine == 'bing':
            if not self.bing_api_key:
                logger.warning("Bing API密钥未配置，将尝试使用阿里云IQS")
                if KUAKE_AVAILABLE and self.aliyun_access_key_id and self.aliyun_access_key_secret:
                    self.default_search_engine = 'kuake'
                else:
                    logger.error("没有可用的搜索引擎配置")
        elif self.default_search_engine == 'kuake':
            if not KUAKE_AVAILABLE:
                logger.warning("阿里云IQS SDK未安装，切换到Bing搜索")
                self.default_search_engine = 'bing'
            elif not (self.aliyun_access_key_id and self.aliyun_access_key_secret):
                logger.warning("阿里云IQS密钥未配置，切换到Bing搜索")
                self.default_search_engine = 'bing'
                
        logger.info(f"当前搜索引擎: {self.default_search_engine}")
    
    def _create_kuake_client(self) -> Client:
        """创建阿里云IQS客户端"""
        config = open_api_models.Config(
            access_key_id=self.aliyun_access_key_id,
            access_key_secret=self.aliyun_access_key_secret
        )
        config.endpoint = 'iqs.cn-zhangjiakou.aliyuncs.com'
        return Client(config)
        
    def extract_search_keywords(self, user_query: str) -> List[str]:
        """
        使用LLM分析用户意图并提取搜索关键词
        """
        intent_analysis_prompt = f"""
你是一个专业的搜索意图分析助手。请分析用户的查询意图，并提取出最适合进行网络搜索的关键词。

用户查询：{user_query}

请按照以下要求：
1. 识别查询的核心主题和关键信息
2. 提取2-4个最相关的搜索关键词
3. 关键词应该简洁、准确，适合搜索引擎
4. 如果涉及时间敏感信息，请包含时间相关词汇
5. 只返回关键词，用逗号分隔，不要其他解释

示例：
用户查询："2024年人工智能发展趋势如何？"
输出：人工智能,2024年,发展趋势,AI技术

用户查询："苹果公司最新财报数据"
输出：苹果公司,最新财报,季度业绩,Apple earnings

现在请分析上述用户查询并输出关键词：
        """
        
        try:
            keywords_text = myllm.simple_completion(
                prompt=intent_analysis_prompt,
                max_tokens=100,
                temperature=0.3
            )
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
            
            logger.info(f"提取的搜索关键词: {keywords}")
            return keywords[:4]  # 最多返回4个关键词
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            # 回退方案：简单分词
            return [user_query]
    
    def search_bing(self, keywords: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """
        使用Bing搜索API获取搜索结果
        """
        search_results = []
        
        for keyword in keywords:
            try:
                headers = {
                    'Ocp-Apim-Subscription-Key': self.bing_api_key,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                params = {
                    'q': keyword,
                    'count': max_results,
                    'offset': 0,
                    'mkt': 'zh-CN',
                    'safesearch': 'Moderate'
                }
                
                response = requests.get(
                    self.bing_search_url,
                    headers=headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'webPages' in data and 'value' in data['webPages']:
                        for item in data['webPages']['value'][:max_results]:
                            search_results.append({
                                'title': item.get('name', ''),
                                'url': item.get('url', ''),
                                'snippet': item.get('snippet', ''),
                                'keyword': keyword
                            })
                else:
                    logger.warning(f"Bing搜索失败，状态码: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"搜索关键词 '{keyword}' 时出错: {e}")
                continue
        
        # 去重并限制结果数量
        unique_results = []
        seen_urls = set()
        
        for result in search_results:
            if result['url'] not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result['url'])
                
                if len(unique_results) >= max_results:
                    break
        
        logger.info(f"获取到 {len(unique_results)} 条搜索结果")
        return unique_results
    
    def search_kuake(self, keywords: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """使用阿里云IQS搜索API获取搜索结果"""
        search_results = []
        
        try:
            client = self._create_kuake_client()
            
            for keyword in keywords:
                try:
                    request = models.UnifiedSearchRequest(
                        body=models.UnifiedSearchInput(
                            query=keyword,
                            time_range='NoLimit',
                            contents=models.RequestContents(
                                summary=True,
                                main_text=True,
                            )
                        )
                    )
                    
                    response = client.unified_search(request)
                    
                    if response.body and response.body.page_items:
                        for item in response.body.page_items[:max_results]:
                            search_results.append({
                                'title': item.title or '',
                                'url': item.link or '',
                                'snippet': item.snippet or item.summary or '',
                                'keyword': keyword,
                                'published_time': item.published_time or '',
                                'rerank_score': getattr(item, 'rerank_score', None)
                            })
                            
                except TeaException as e:
                    logger.error(f"阿里云IQS搜索关键词 '{keyword}' 失败: {e.code} - {e.data.get('message', '')}")
                    continue
                except Exception as e:
                    logger.error(f"搜索关键词 '{keyword}' 时出错: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"创建阿里云IQS客户端失败: {e}")
            return []
        
        # 去重并限制结果数量
        unique_results = []
        seen_urls = set()
        
        for result in search_results:
            if result['url'] and result['url'] not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result['url'])
                
                if len(unique_results) >= max_results:
                    break
        
        logger.info(f"阿里云IQS获取到 {len(unique_results)} 条搜索结果")
        return unique_results
    
    def search(self, keywords: List[str], max_results: int = 5, engine: str = None) -> List[Dict[str, Any]]:
        """统一搜索接口，根据配置选择搜索引擎"""
        search_engine = engine or self.default_search_engine
        
        if search_engine == 'kuake' and KUAKE_AVAILABLE:
            return self.search_kuake(keywords, max_results)
        elif search_engine == 'bing':
            return self.search_bing(keywords, max_results)
        else:
            # 回退到可用的搜索引擎
            if self.bing_api_key:
                logger.info("回退到Bing搜索")
                return self.search_bing(keywords, max_results)
            elif KUAKE_AVAILABLE and self.aliyun_access_key_id:
                logger.info("回退到阿里云IQS搜索")
                return self.search_kuake(keywords, max_results)
            else:
                logger.error("没有可用的搜索引擎")
                return []
     
    def format_search_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        格式化搜索结果为上下文信息
        """
        if not search_results:
            return "未找到相关的网络搜索结果。"
        
        context = "以下是相关的网络搜索结果：\n\n"
        
        for i, result in enumerate(search_results, 1):
            context += f"【搜索结果 {i}】\n"
            context += f"标题：{result['title']}\n"
            context += f"摘要：{result['snippet']}\n"
            context += f"来源：{result['url']}\n\n"
        
        return context
    

    
    def create_enhanced_prompt(self, user_query: str, search_context: str) -> str:
        """
        创建增强的提示词，结合用户查询和搜索结果
        """
        enhanced_prompt = f"""
你是一个专业的AI助手，能够基于最新的网络信息为用户提供准确、全面的回答。

用户问题：{user_query}

{search_context}

请基于以上搜索结果，为用户提供详细、准确的回答。要求：

1. **信息整合**：综合多个搜索结果中的信息，提供全面的回答
2. **时效性**：优先使用最新的信息，如果涉及时间敏感话题请特别注意
3. **准确性**：确保信息的准确性，如有不确定的地方请明确说明
4. **结构化**：使用清晰的结构组织回答，包括要点、详细说明等
5. **引用来源**：在回答中适当引用搜索结果的来源，增加可信度
6. **客观性**：保持客观中立的态度，避免主观臆断

如果搜索结果与用户问题不够匹配，请基于你的知识库提供回答，并说明信息来源的局限性。

请开始回答：
        """
        
        return enhanced_prompt
    
    def perform_web_search(self, user_query: str) -> tuple[str, List[Dict[str, Any]]]:
        """
        执行完整的联网查询流程
        返回增强的提示词和搜索结果
        """
        try:
            # 1. 提取搜索关键词
            keywords = self.extract_search_keywords(user_query)
            
            # 2. 执行搜索
            search_results = self.search(keywords)
            
            # 3. 格式化搜索上下文
            search_context = self.format_search_context(search_results)
            
            # 4. 创建增强提示词
            enhanced_prompt = self.create_enhanced_prompt(user_query, search_context)
            
            return enhanced_prompt, search_results
            
        except Exception as e:
            logger.error(f"联网查询失败: {e}")
            # 返回原始查询作为回退
            return user_query, []

# 全局实例
web_search_tool = WebSearchTool()