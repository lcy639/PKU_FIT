import json
import math
import requests
import os
import random
import numpy as np
from openai import OpenAI
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QMessageBox, QComboBox
)
from .base import BasePage


action_file_path = './actions/fitness_library.json'


class PersonalizedWorkoutPage(BasePage):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.exercise_library = []
        # 初始化API客户端
        self.client = OpenAI(
            api_key="sk-37cacfbdfb6b43908eafbb46ec984362",
            base_url="https://api.deepseek.com"
        )
        self.model_name = "deepseek-chat"  # 与示例一致的模型名称
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 输入：训练时长
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("训练时长（分钟）："))
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("如 30")
        time_layout.addWidget(self.time_input)
        layout.addLayout(time_layout)

        # 输入：目标肌肉
        muscle_layout = QHBoxLayout()
        muscle_layout.addWidget(QLabel("目标肌肉："))
        self.muscle_input = QLineEdit()
        self.muscle_input.setPlaceholderText("如 腹直肌、臀大肌")
        muscle_layout.addWidget(self.muscle_input)
        layout.addLayout(muscle_layout)

        # 输入：最大难度等级
        difficulty_layout = QHBoxLayout()
        difficulty_layout.addWidget(QLabel("最大难度（1~5）："))
        self.difficulty_input = QComboBox()
        self.difficulty_input.addItems([str(i) for i in range(1, 6)])
        difficulty_layout.addWidget(self.difficulty_input)
        layout.addLayout(difficulty_layout)

        # 生成计划按钮
        '''
        generate_btn = QPushButton("生成训练计划")
        generate_btn.clicked.connect(self.generate_plan)
        layout.addWidget(generate_btn)'''
        
        btn_layout = QHBoxLayout()

        # AI生成按钮
        ai_btn = QPushButton("AI生成计划")
        ai_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        ai_btn.clicked.connect(self.generate_ai_plan)
        btn_layout.addWidget(ai_btn)

        # 普通生成按钮
        regular_btn = QPushButton("普通生成计划")
        regular_btn.setStyleSheet("background-color: #008CBA; color: white;")
        regular_btn.clicked.connect(self.generate_regular_plan)
        btn_layout.addWidget(regular_btn)

        layout.addLayout(btn_layout)

        # 结果显示区
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        # 返回按钮
        back_btn = QPushButton("返回主界面")
        back_btn.clicked.connect(lambda: self.controller.show_page("MainPage"))
        layout.addWidget(back_btn)

        self.setLayout(layout)
        self.load_library()

    def load_library(self):
        """尝试加载 JSON 文件中的动作库"""
        # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # file_path = os.path.join(base_dir, "data", "actions.json")
        file_path = action_file_path

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.exercise_library = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载动作库：{e}")
            self.exercise_library = []
    
    def generate_ai_plan(self):
        """根据用户输入生成训练计划"""
        try:
            duration = int(self.time_input.text())
            target = self.muscle_input.text().strip()
            difficulty = int(self.difficulty_input.currentText())
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数字和肌肉名称")
            return

        if not target:
            QMessageBox.warning(self, "输入错误", "目标肌肉不能为空")
            return

        # 筛选可用动作
        filtered = [
            ex for ex in self.exercise_library
            if target in ex["target_muscles"] and int(ex["difficulty"]) <= difficulty
        ]
        
        if not filtered:
            filtered = [
                ex for ex in self.exercise_library
                if target in ex["target_muscles"]
            ]
        
        if not filtered:
            self.result_box.setText("⚠️ 没有找到匹配的动作，请尝试降低难度或更换目标肌肉。")
            return

        # 构建提示词
        prompt = f"""请根据以下要求生成专业健身计划：

## 用户需求
- 总时长：{duration}分钟 (±5分钟)
- 目标肌肉：{", ".join(target)}
- 难度限制：{difficulty}/5

## 可用动作（必须使用以下动作）请特别注意，只能使用以下动作来生成计划：
{json.dumps(filtered, indent=2, ensure_ascii=False)}

## 计划要求
1. 结构包含：动态热身（10%）、正式训练（80%）、静态拉伸（10%）
2. 正式训练包含3-5个不同动作
3. 每个动作注明：
   - 组数×次数（如：4×8-12）
   - 组间休息时间
   - 重量选择建议（根据难度）
4. 使用Markdown格式
5. 动作名称必须严格匹配提供的列表
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            plan = response.choices[0].message.content
            self.show_plan(plan)
            
        except Exception as e:
            QMessageBox.critical(self, "生成失败", 
                f"API调用失败：{str(e)}\n"
                "请检查：\n"
                "1. 网络连接\n"
                "2. API密钥有效性\n"
                "3. 账户余额")

    def show_plan(self, plan):
            self.result_box.clear()
            self.result_box.setMarkdown(f"# 🏋️ 智能训练计划\n\n{plan}")
            self.result_box.append("\n\n⚠️ 温馨提示：本计划仅供参考，请根据自身情况调整")
   
    
    def generate_regular_plan(self):
        """根据用户输入生成训练计划"""
        try:
            duration = int(self.time_input.text())
            target = self.muscle_input.text().strip()
            difficulty = int(self.difficulty_input.currentText())
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数字和肌肉名称")
            return

        if not target:
            QMessageBox.warning(self, "输入错误", "目标肌肉不能为空")
            return

        estimated_minutes_per_exercise = 5
        total_needed = max(1, math.floor(duration / estimated_minutes_per_exercise))

        # 先匹配肌肉 + 难度
        matched = [
            ex for ex in self.exercise_library
            if target in ex["target_muscles"] and int(ex["difficulty"]) <= difficulty
        ]
        if not matched:
            matched = [
                ex for ex in self.exercise_library
                if target in ex["target_muscles"]
            ]

        if not matched:
            self.result_box.setText("⚠️ 没有找到匹配的动作，请尝试降低难度或更换目标肌肉。")
            return

        workout_plan = []
        while len(workout_plan) < total_needed:
            for ex in matched:
                if len(workout_plan) >= total_needed:
                    break
                workout_plan.append(ex)

        # 显示结果
        self.result_box.clear()
        self.result_box.append(f"💪 为你生成的训练计划（共 {len(workout_plan)} 个动作，每个约 5 分钟）：\n")
        for i, ex in enumerate(workout_plan, 1):
            self.result_box.append(f"{i}. {ex['name']} （难度：{ex['difficulty']}）\n - {ex['description']}\n")
