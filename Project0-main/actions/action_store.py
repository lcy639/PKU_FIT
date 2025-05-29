import json
import os

# 数据存储文件
DATA_FILE = "fitness_library.json"

# 动作库数据结构
exercise_library = []

def load_data():
    """加载已有数据"""
    global exercise_library
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r',encoding='utf-8') as f:
            exercise_library = json.load(f)

def save_data():
    """保存数据到文件"""
    with open(DATA_FILE, 'w',encoding='utf-8') as f:
        json.dump(exercise_library, f, indent=2)

def add_exercise():
    """添加新动作"""
    print("\n--- 添加新动作 ---")
    exercise = {
        "name": input("动作名称："),
        "target_muscles": input("目标肌肉群（用逗号分隔）：").split(','),
        "equipment": input("所需器材："),
        "difficulty": input("难度等级（1-5）："),
        "description": input("动作描述：")
    }
    exercise_library.append(exercise)
    save_data()
    print("✅ 动作添加成功！")

def view_exercises():
    """查看所有动作"""
    print("\n--- 动作列表 ---")
    for idx, exercise in enumerate(exercise_library, 1):
        print(f"{idx}. {exercise['name']}")
        print(f"   目标肌肉：{', '.join(exercise['target_muscles'])}")
        print(f"   难度：{exercise['difficulty']}/5")
        print(f"   器材：{exercise['equipment']}")
        print("-" * 40)

def search_exercises():
    """搜索动作"""
    keyword = input("\n请输入搜索关键词（名称/肌肉群/器材）：").lower()
    results = []
    
    for exercise in exercise_library:
        if (keyword in exercise['name'].lower() or
            any(keyword in m.lower() for m in exercise['target_muscles']) or
            keyword in exercise['equipment'].lower()):
            results.append(exercise)
    
    if results:
        print(f"\n找到 {len(results)} 个匹配结果：")
        for ex in results:
            print(f"· {ex['name']} ({ex['equipment']})")
    else:
        print("没有找到匹配的动作")

def delete_exercise():
    """删除动作"""
    view_exercises()
    try:
        choice = int(input("\n请输入要删除的动作编号：")) - 1
        if 0 <= choice < len(exercise_library):
            removed = exercise_library.pop(choice)
            save_data()
            print(f"已删除：{removed['name']}")
        else:
            print("无效的编号")
    except ValueError:
        print("请输入有效数字")

def show_menu():
    """显示主菜单"""
    print("\n🏋️ 健身动作库管理系统")
    print("1. 查看所有动作")
    print("2. 添加新动作")
    print("3. 搜索动作")
    print("4. 删除动作")
    print("5. 退出系统")

def main():
    load_data()
    while True:
        show_menu()
        try:
            choice = int(input("\n请选择操作（1-5）："))
            if choice == 1:
                view_exercises()
            elif choice == 2:
                add_exercise()
            elif choice == 3:
                search_exercises()
            elif choice == 4:
                delete_exercise()
            elif choice == 5:
                print("感谢使用，再见！")
                break
            else:
                print("请输入1-5之间的数字")
        except ValueError:
            print("请输入有效数字")

if __name__ == "__main__":
    main()