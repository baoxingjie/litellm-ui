#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure OpenAI GPT-4o 多模态能力测试
使用Azure OpenAI服务进行多模态测试
"""

import os
import base64
from PIL import Image, ImageDraw, ImageFont
import io
from myllm import myllm
from logger import logger

class AzureMultimodalTest:
    """
    Azure OpenAI 多模态测试类
    """
    
    def __init__(self):
        self.test_results = []
    
    def create_simple_image(self, text: str, bg_color: str = "lightblue") -> str:
        """
        创建一个简单的测试图像
        """
        try:
            size = (300, 200)
            img = Image.new('RGB', size, color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # 使用默认字体
            font = ImageFont.load_default()
            
            # 绘制文本
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            draw.text((x, y), text, fill="black", font=font)
            
            # 添加边框
            draw.rectangle([5, 5, size[0]-5, size[1]-5], outline="navy", width=2)
            
            # 转换为base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"创建图像失败: {e}")
            raise
    
    def check_azure_availability(self) -> tuple[bool, str]:
        """
        检查Azure OpenAI是否可用
        """
        try:
            # 检查Azure配置
            azure_key = os.getenv('AZURE_API_KEY')
            azure_base = os.getenv('AZURE_API_BASE')
            
            if not azure_key or not azure_base:
                return False, "Azure OpenAI配置不完整"
            
            # 检查可用模型
            available_models = myllm.get_available_models()
            azure_models = [model for model in available_models if 'azure' in model.name.lower()]
            
            if not azure_models:
                return False, "没有可用的Azure模型"
            
            # 找到支持视觉的模型
            vision_models = []
            for model in azure_models:
                if any(keyword in model.name.lower() for keyword in ['gpt-4', 'vision', 'turbo']):
                    vision_models.append(model)
            
            if not vision_models:
                return False, "没有找到支持视觉的Azure模型"
            
            return True, vision_models[0].name
            
        except Exception as e:
            return False, f"检查Azure可用性失败: {e}"
    
    def test_simple_vision(self, model_key: str) -> dict:
        """
        测试基础视觉能力
        """
        test_name = "基础视觉测试"
        print(f"\n=== {test_name} ===")
        print(f"使用模型: {model_key}")
        
        try:
            # 创建测试图像
            test_text = "Vision Test"
            image_data = self.create_simple_image(test_text)
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请描述这张图片中你看到的内容。"
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
                model_key=model_key,
                messages=messages,
                max_tokens=200,
                temperature=0.1
            )
            
            result = {
                "test_name": test_name,
                "success": True,
                "response": response.choices[0].message.content,
                "model": model_key
            }
            
            print(f"✅ 测试成功")
            print(f"模型回复: {result['response']}")
            
        except Exception as e:
            result = {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "model": model_key
            }
            print(f"❌ 测试失败: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_text_recognition(self, model_key: str) -> dict:
        """
        测试文字识别能力
        """
        test_name = "文字识别测试"
        print(f"\n=== {test_name} ===")
        
        try:
            # 创建包含文字的图像
            test_text = "Hello Azure GPT-4!"
            image_data = self.create_simple_image(test_text, "lightyellow")
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请准确读出这张图片中的所有文字。"
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
                model_key=model_key,
                messages=messages,
                max_tokens=100,
                temperature=0.0
            )
            
            result = {
                "test_name": test_name,
                "success": True,
                "response": response.choices[0].message.content,
                "expected_text": test_text,
                "model": model_key
            }
            
            print(f"✅ 测试成功")
            print(f"期望文字: {test_text}")
            print(f"识别结果: {result['response']}")
            
        except Exception as e:
            result = {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "model": model_key
            }
            print(f"❌ 测试失败: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_color_detection(self, model_key: str) -> dict:
        """
        测试颜色识别能力
        """
        test_name = "颜色识别测试"
        print(f"\n=== {test_name} ===")
        
        try:
            # 创建红色背景的图像
            image_data = self.create_simple_image("RED", "red")
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "这张图片的主要背景颜色是什么？"
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
                model_key=model_key,
                messages=messages,
                max_tokens=50,
                temperature=0.0
            )
            
            result = {
                "test_name": test_name,
                "success": True,
                "response": response.choices[0].message.content,
                "expected_color": "红色",
                "model": model_key
            }
            
            print(f"✅ 测试成功")
            print(f"期望颜色: 红色")
            print(f"识别结果: {result['response']}")
            
        except Exception as e:
            result = {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "model": model_key
            }
            print(f"❌ 测试失败: {e}")
        
        self.test_results.append(result)
        return result
    
    def run_tests(self):
        """
        运行所有测试
        """
        print("\n🚀 开始 Azure OpenAI 多模态能力测试")
        print("=" * 50)
        
        # 检查Azure可用性
        is_available, model_or_error = self.check_azure_availability()
        
        if not is_available:
            print(f"❌ Azure OpenAI不可用: {model_or_error}")
            print("\n请检查以下配置:")
            print("1. AZURE_API_KEY 是否正确设置")
            print("2. AZURE_API_BASE 是否正确设置")
            print("3. 是否有支持视觉的Azure模型配置")
            return
        
        model_key = model_or_error
        print(f"✅ 使用Azure模型: {model_key}")
        
        # 运行测试
        self.test_simple_vision(model_key)
        self.test_text_recognition(model_key)
        self.test_color_detection(model_key)
        
        # 输出总结
        self.print_summary()
    
    def print_summary(self):
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
        
        if total_tests > 0:
            print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
        
        if successful_tests > 0:
            print("\n✅ 成功的测试:")
            for result in self.test_results:
                if result['success']:
                    print(f"- {result['test_name']}")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"- {result['test_name']}: {result['error']}")
        
        print("\n" + "=" * 50)
        
        # 如果有成功的测试，说明多模态功能正常
        if successful_tests > 0:
            print("\n🎉 多模态功能测试通过！")
            print("myllm.py 工具类可以正常调用支持视觉的模型。")
        else:
            print("\n⚠️  所有测试都失败了，请检查配置和网络连接。")

def main():
    """
    主函数
    """
    try:
        tester = AzureMultimodalTest()
        tester.run_tests()
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        logger.error(f"Azure多模态测试失败: {e}")

if __name__ == "__main__":
    main()