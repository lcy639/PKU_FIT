import json
import math

# 加载数据
with open("fitness_library.json", "r", encoding="utf-8") as f:
    exercise_library = json.load(f)


def generate_workout_plan(duration_minutes, target_muscle, difficulty_level):
    """
    根据时间、目标肌肉和难度，生成动作计划（重复使用动作填满时间）
    """
    estimated_minutes_per_exercise = 5
    total_needed = max(1, math.floor(duration_minutes / estimated_minutes_per_exercise))

    # 找出符合条件的动作
    matched = [
        ex for ex in exercise_library
        if target_muscle in ex["target_muscles"] and int(ex["difficulty"]) <= difficulty_level
    ]

    # 如果匹配为空，尝试只匹配肌肉（不考虑难度）
    if not matched:
        matched = [ex for ex in exercise_library if target_muscle in ex["target_muscles"]]

    # 还是找不到就终止
    if not matched:
        return []

    # 重复选择动作填满训练时间
    workout_plan = []
    while len(workout_plan) < total_needed:
        for ex in matched:
            if len(workout_plan) >= total_needed:
                break
            workout_plan.append(ex)

    return workout_plan


# 示例用法
if __name__ == "__main__":
    duration = int(input("请输入训练时间（分钟）："))
    target = input("请输入目标肌肉（如：腹直肌、臀大肌）：").strip()
    difficulty = int(input("请输入最大训练难度（1~5）："))

    plan = generate_workout_plan(duration, target, difficulty)

    if plan:
        print(f"\n💪 为你生成的训练计划（共{len(plan)}个动作，每个约5分钟）：")
        for idx, ex in enumerate(plan, 1):
            print(
                f"{idx}. {ex['name']} （难度：{ex['difficulty']}） - {ex['description']}")
    else:
        print("⚠️ 没有找到匹配的动作，请尝试降低难度或更换目标肌肉。")
