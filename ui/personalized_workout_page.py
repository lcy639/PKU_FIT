import json
import math
import os
import random
from openai import OpenAI
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QMessageBox, QComboBox
)
from .base import BasePage


action_file_path = './actions/fitness_library.json'

# 统一难度映射（动作库使用"低/中/高"，程序内部使用数字1-3）
DIFFICULTY_MAPPING = {
    "低": 1,
    "中": 2,
    "高": 3
}

# 统一肌肉名称映射（程序显示名称 -> 动作库存储名称）
MUSCLE_MAPPING = {
    "三角肌": "肩部",
    "三角肌中束": "肩部",
    "三角肌后束": "肩部",
    "肱二头肌": "二头肌",
    "肱三头肌": "三头肌",
    "肩胛稳定肌群": "肩部",
    "腹直肌": "腹肌",
    "腹外斜肌": "腹肌",
    "腹内斜肌": "腹肌",
    "核心": "腹肌",
    "胸大肌": "胸肌",
    "斜方肌": "斜方肌",
    "下背部": "腰部",
    "臀大肌": "臀部",
    "股四头肌": "大腿",
    "腿后侧肌群": "大腿",
    "小腿三头肌": "小腿",
    "全身": "全身",
    "心肺": "心肺"
}


class PersonalizedWorkoutPage(BasePage):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.exercise_library = []
        self.client = OpenAI(
            api_key="sk-37cacfbdfb6b43908eafbb46ec984362",
            base_url="https://api.deepseek.com"
        )
        self.model_name = "deepseek-chat"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 训练时长
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("训练时长（分钟）："))
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("如 30")
        time_layout.addWidget(self.time_input)
        layout.addLayout(time_layout)

        # 目标肌肉（使用统一映射后的选项）
        muscle_layout = QHBoxLayout()
        muscle_layout.addWidget(QLabel("目标肌肉："))
        self.muscle_input = QComboBox()
        # 提取映射后的显示名称并排序
        muscle_options = sorted(MUSCLE_MAPPING.keys())
        self.muscle_input.addItems(muscle_options)
        muscle_layout.addWidget(self.muscle_input)
        layout.addLayout(muscle_layout)

        # 难度等级（统一为1-3，对应低/中/高）
        difficulty_layout = QHBoxLayout()
        difficulty_layout.addWidget(QLabel("最大难度（高、中、低）："))
        self.difficulty_input = QComboBox()
        self.difficulty_input.addItems([ "3 (高)","2 (中)","1 (低)", ])
        difficulty_layout.addWidget(self.difficulty_input)
        layout.addLayout(difficulty_layout)

        # 按钮布局
        btn_layout = QHBoxLayout()
        ai_btn = QPushButton("AI生成计划")
        ai_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        ai_btn.clicked.connect(self.generate_ai_plan)
        btn_layout.addWidget(ai_btn)

        regular_btn = QPushButton("普通生成计划")
        regular_btn.setStyleSheet("background-color: #008CBA; color: white;")
        regular_btn.clicked.connect(self.generate_regular_plan)
        btn_layout.addWidget(regular_btn)
        layout.addLayout(btn_layout)

        # 结果显示
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        # 返回按钮
        back_btn = QPushButton("返回主界面")
        back_btn.clicked.connect(lambda: self.controller.show_page("MainPage"))
        layout.addWidget(back_btn)

        # 添加至主界面按钮
        self.add_to_main_btn = QPushButton("添加至主界面清单")
        self.add_to_main_btn.clicked.connect(self.add_plan_to_mainpage)
        layout.addWidget(self.add_to_main_btn)

        self.setLayout(layout)
        self.load_library()

    def load_library(self):
        """加载动作库并处理数据类型"""
        try:
            with open(action_file_path, "r", encoding="utf-8") as f:
                self.exercise_library = json.load(f)
            # 转换难度为数字，方便后续比较
            for ex in self.exercise_library:
                ex["difficulty_num"] = DIFFICULTY_MAPPING[ex["difficulty"]]
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载动作库：{e}")
            self.exercise_library = []

    def generate_ai_plan(self):
        """使用AI生成训练计划"""
        try:
            duration = int(self.time_input.text())
            target_display = self.muscle_input.currentText()
            difficulty_display = self.difficulty_input.currentText()
            
            # 转换为内部存储的名称和数值
            target_muscle = MUSCLE_MAPPING[target_display]
            difficulty = int(difficulty_display.split()[0])  # 提取数字部分

        except (ValueError, KeyError):
            QMessageBox.warning(self, "输入错误", "请输入有效的训练时长和选择目标肌肉")
            return

        if not target_muscle:
            QMessageBox.warning(self, "输入错误", "目标肌肉不能为空")
            return

        # 筛选动作
        filtered = self._filter_actions(target_muscle, difficulty)
        if not filtered:
            self.result_box.setText("⚠️ 没有找到匹配的动作，请尝试降低难度或更换目标肌肉。")
            return

        # 构建提示词
        prompt = self._build_prompt(duration, target_display, difficulty, filtered)
        
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
            QMessageBox.critical(self, "生成失败", f"API调用失败：{str(e)}")

    def generate_regular_plan(self):
        """普通方式生成训练计划"""
        try:
            duration = int(self.time_input.text())
            target_display = self.muscle_input.currentText()
            difficulty = int(self.difficulty_input.currentText().split()[0])
            target_muscle = MUSCLE_MAPPING[target_display]
        except (ValueError, KeyError):
            QMessageBox.warning(self, "输入错误", "请输入有效的训练时长和选择目标肌肉")
            return

        matched = self._filter_actions(target_muscle, difficulty)
        if not matched:
            self.result_box.setText("⚠️ 没有找到匹配的动作，请尝试降低难度或更换目标肌肉。")
            self.generated_plan = []
            return

        # 计算所需动作数量（每个动作5分钟）
        total_needed = max(1, math.ceil(duration / 5))  # 向上取整确保时间足够
    
        # 生成训练计划：如果动作数量不足，则重复使用已有动作
        workout_plan = []
        while len(workout_plan) < total_needed:
            # 随机打乱匹配的动作顺序
            random.shuffle(matched)
            # 添加到计划中，直到满足时间需求
            workout_plan.extend(matched[:total_needed - len(workout_plan)])
    
        # 保存生成的计划
        self.generated_plan = workout_plan

        # 显示结果
        self.result_box.clear()
        self.result_box.append(f"💪 为你生成的训练计划（共 {len(workout_plan)} 个动作，预计 {len(workout_plan)*5} 分钟）：\n")
    
        # 记录每个动作的重复次数
        action_counts = {}
        for i, ex in enumerate(workout_plan, 1):
            action_name = ex['name']
            if action_name not in action_counts:
                action_counts[action_name] = 1
            else:
                action_counts[action_name] += 1
        
            # 如果是重复动作，添加序号标识
            display_name = f"{action_name} ({action_counts[action_name]})" if action_counts[action_name] > 1 else action_name
        
            self.result_box.append(f"{i}. {display_name} （难度：{ex['difficulty']}）\n - {ex['description']}\n")

    def _filter_actions(self, target, difficulty):
        """根据目标肌肉和难度筛选动作"""
        if target == "心肺":
            # 特殊处理心肺训练（匹配有氧动作）
            return [ex for ex in self.exercise_library if "有氧" in ex['name'].lower()]
        elif target == "全身":
            return self.exercise_library
        else:
            return [
                ex for ex in self.exercise_library
                if target in ex["target_muscles"] and ex["difficulty_num"] <= difficulty
            ]

    def _build_prompt(self, duration, target_display, difficulty, filtered):
        """构建AI提示词"""
        # 处理目标肌肉显示名称（多个肌群用中文逗号分隔）
        target_for_prompt = target_display if target_display in ["全身", "心肺"] else ", ".join(
            [k for k, v in MUSCLE_MAPPING.items() if v == MUSCLE_MAPPING[target_display]]
        )

        return f"""请根据以下要求生成专业健身计划：

## 用户需求
- 总时长：{duration}分钟 (±5分钟)
- 目标肌肉：{target_for_prompt}
- 难度限制：{difficulty}/3（1=低，2=中，3=高）

## 可用动作（必须使用以下动作）：
{json.dumps(filtered, indent=2, ensure_ascii=False, default=str)}

## 计划要求
1. 结构包含：动态热身（10%）、正式训练（80%）、静态拉伸（10%）
2. 正式训练包含3-5个不同动作
3. 每个动作注明：
   - 组数×次数（如：4×8-12）
   - 组间休息时间（秒）
   - 重量选择建议（根据难度：低=自重/轻重量，中=中等重量，高=大重量）
4. 使用Markdown格式
5. 动作名称必须严格匹配提供的列表
"""

    def show_plan(self, plan):
        """显示生成的计划"""
        self.result_box.clear()
        self.result_box.setMarkdown(f"# 🏋️ 智能训练计划\n\n{plan}")
        self.result_box.append("\n\n⚠️ 温馨提示：本计划仅供参考，请根据自身情况调整")

    def add_plan_to_mainpage(self):
        """添加计划到主界面"""
        if not hasattr(self, "generated_plan") or not self.generated_plan:
            QMessageBox.information(self, "提示", "请先生成训练计划")
            return

        main_page = self.controller.pages.get("MainPage")
        if main_page:
            for ex in self.generated_plan:
                # 从字典中提取动作名称（假设名称键为 "name"）
                action_name = ex.get("name", "未知动作")
                main_page.add_to_training_list(action_name)  # 传递字符串而非整个字典
            QMessageBox.information(self, "添加成功", "已添加至主界面训练清单")
        else:
            QMessageBox.warning(self, "错误", "无法访问主界面")