#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-4o 多模态能力测试类
测试 myllm.py 中的图像理解和分析功能
"""

import os
import base64
import requests
from typing import List, Dict, Any
from myllm import myllm
from logger import logger

class MultimodalTest:
    """
    多模态测试类
    用于测试 GPT-4o 的图像理解能力
    """
    
    def __init__(self):
        self.test_results = []
    
    def encode_image_from_url(self, image_url: str) -> str:
        """
        从URL获取图像并转换为base64编码
        """
        try:
            # 设置合适的User-Agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 将图像内容转换为base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            
            # 获取图像格式
            content_type = response.headers.get('content-type', 'image/jpeg')
            image_format = content_type.split('/')[-1]
            
            return f"data:{content_type};base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"获取图像失败: {e}")
            raise
    
    def encode_image_from_file(self, image_path: str) -> str:
        """
        从本地文件读取图像并转换为base64编码
        """
        try:
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 根据文件扩展名确定MIME类型
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            
            mime_type = mime_types.get(ext, 'image/jpeg')
            return f"data:{mime_type};base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"读取本地图像失败: {e}")
            raise
    
    def test_image_description(self, image_source: str, is_url: bool = True) -> Dict[str, Any]:
        """
        测试图像描述功能
        """
        test_name = "图像描述测试"
        print(f"\n=== {test_name} ===")
        
        try:
            # 编码图像
            if is_url:
                image_data = self.encode_image_from_url(image_source)
                print(f"测试图像URL: {image_source}")
            else:
                image_data = self.encode_image_from_file(image_source)
                print(f"测试图像文件: {image_source}")
            
            # 构建多模态消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请详细描述这张图片的内容，包括主要对象、场景、颜色、构图等细节。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data
                            }
                        }
                    ]
                }
            ]
            
            # 调用模型
            response = myllm.completion(
                model_key="azure-gpt-4o",
                messages=messages,
                max_tokens=500,
                temperature=0.3
            )
            
            result = {
                "test_name": test_name,
                "success": True,
                "response": response.choices[0].message.content,
                "image_source": image_source
            }
            
            print(f"✅ 测试成功")
            print(f"模型回复: {result['response']}")
            
        except Exception as e:
            result = {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "image_source": image_source
            }
            print(f"❌ 测试失败: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_image_analysis(self, image_source: str, question: str, is_url: bool = True) -> Dict[str, Any]:
        """
        测试图像分析功能
        """
        test_name = "图像分析测试"
        print(f"\n=== {test_name} ===")
        
        try:
            # 编码图像
            if is_url:
                image_data = self.encode_image_from_url(image_source)
                print(f"测试图像URL: {image_source}")
            else:
                image_data = self.encode_image_from_file(image_source)
                print(f"测试图像文件: {image_source}")
            
            print(f"分析问题: {question}")
            
            # 构建多模态消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data
                            }
                        }
                    ]
                }
            ]
            
            # 调用模型
            response = myllm.completion(
                model_key="azure-gpt-4o",
                messages=messages,
                max_tokens=300,
                temperature=0.2
            )
            
            result = {
                "test_name": test_name,
                "success": True,
                "response": response.choices[0].message.content,
                "question": question,
                "image_source": image_source
            }
            
            print(f"✅ 测试成功")
            print(f"模型回复: {result['response']}")
            
        except Exception as e:
            result = {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "question": question,
                "image_source": image_source
            }
            print(f"❌ 测试失败: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_multiple_images(self, image_sources: List[str], question: str, are_urls: bool = True) -> Dict[str, Any]:
        """
        测试多图像对比分析功能
        """
        test_name = "多图像对比测试"
        print(f"\n=== {test_name} ===")
        
        try:
            print(f"对比问题: {question}")
            print(f"图像数量: {len(image_sources)}")
            
            # 构建消息内容
            content = [
                {
                    "type": "text",
                    "text": question
                }
            ]
            
            # 添加多个图像
            for i, image_source in enumerate(image_sources):
                if are_urls:
                    image_data = self.encode_image_from_url(image_source)
                    print(f"图像 {i+1}: {image_source}")
                else:
                    image_data = self.encode_image_from_file(image_source)
                    print(f"图像 {i+1}: {image_source}")
                
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_data
                    }
                })
            
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]
            
            # 调用模型
            response = myllm.completion(
                model_key="azure-gpt-4o",
                messages=messages,
                max_tokens=600,
                temperature=0.3
            )
            
            result = {
                "test_name": test_name,
                "success": True,
                "response": response.choices[0].message.content,
                "question": question,
                "image_count": len(image_sources),
                "image_sources": image_sources
            }
            
            print(f"✅ 测试成功")
            print(f"模型回复: {result['response']}")
            
        except Exception as e:
            result = {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "question": question,
                "image_sources": image_sources
            }
            print(f"❌ 测试失败: {e}")
        
        self.test_results.append(result)
        return result
    
    def run_comprehensive_tests(self):
        """
        运行综合测试套件
        """
        print("\n🚀 开始 GPT-4o 多模态能力综合测试")
        print("=" * 50)
        
        # 测试1: 基础图像描述
        self.test_image_description(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            is_url=True
        )
        
        # 测试2: 图像内容分析
        self.test_image_analysis(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/No_Image_Available.jpg/300px-No_Image_Available.jpg",
            "这张图片传达了什么信息？有什么特殊含义吗？",
            is_url=True
        )
        
        # 测试3: 技术图表分析
        self.test_image_analysis(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Matplotlib_icon.svg/240px-Matplotlib_icon.svg.png",
            "请识别这个图标代表什么软件或技术，并说明其用途。",
            is_url=True
        )
        
        # 测试4: 多图像对比（如果需要的话）
        # self.test_multiple_images(
        #     [
        #         "https://example.com/image1.jpg",
        #         "https://example.com/image2.jpg"
        #     ],
        #     "请对比这两张图片的异同点。",
        #     are_urls=True
        # )
        
        # 输出测试总结
        self.print_test_summary()
    
    def print_test_summary(self):
        """
        打印测试总结
        """
        print("\n" + "=" * 50)
        print("📊 测试总结")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"- {result['test_name']}: {result['error']}")
        
        print("\n" + "=" * 50)

def main():
    """
    主函数 - 运行多模态测试
    """
    # 检查是否有 GPT-4o 模型可用
    try:
        available_models = myllm.get_available_models()
        azure_gpt4o_available = any('azure-gpt-4o' in model.name.lower() for model in available_models)
        
        if not azure_gpt4o_available:
            print("❌ Azure GPT-4o 模型不可用，请检查配置")
            print("可用模型:")
            for model in available_models:
                print(f"  - {model.name}: {model.display_name}")
            return
        
        print("✅ Azure GPT-4o 模型可用，开始测试")
        
        # 创建测试实例并运行测试
        tester = MultimodalTest()
        tester.run_comprehensive_tests()
        
    except Exception as e:
        print(f"❌ 测试初始化失败: {e}")
        logger.error(f"多模态测试失败: {e}")

if __name__ == "__main__":
    main()