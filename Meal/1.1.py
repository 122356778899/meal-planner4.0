
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
import random
from typing import List, Dict
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'  # 用于会话管理

@app.route('/')
def page1():
    return render_template('html_page1.html')

@app.route('/page2')
def page2():
    return render_template('html_page2.html')

@app.route('/page3')
def page3():
    return render_template('html_page3.html')

@app.route('/page4')
def page4():
    meal_plan = session.get('meal_plan')
    if meal_plan:
        return render_template('html_page4.html', meal_plan=meal_plan)
    else:
        return redirect(url_for('page1'))


@app.route('/submit_meal_info', methods=['POST'])
def submit_meal_info():
    data = request.get_json()

    if 'meal-type' not in data:  # 从 page2 提交的数据
        session['page2_data'] = data
        return jsonify({"redirect": url_for('page3')})  # 返回重定向信息
    else:  # 从 page3 提交的数据
        page2_data = session.get('page2_data', {})
        combined_data = {**page2_data, **data}

        gender = combined_data.get('gender')
        height = float(combined_data.get('height'))
        weight = float(combined_data.get('weight'))
        activity = combined_data.get('activity')
        age = int(combined_data.get('age'))
        meal_type = combined_data.get('meal-type')
        goal = combined_data.get('weight-goal')
        print('接收到的数据:', combined_data)

        user_data = {
            'gender': gender,
            'height': height,
            'weight': weight,
            'age': age,
            'activity_level': activity,
            'goal': goal
        }

        # 计算热量需求
        bmr = calculate_bmr(user_data)
        total_calories = calculate_total_calories(bmr, user_data['activity_level'], user_data['goal'])

        # 生成营养目标
        macro_targets = calculate_macro_targets(total_calories)

        # 生成三餐食谱
        meal_plan = generate_intelligent_meal_plan(total_calories, macro_targets)

        session['meal_plan'] = meal_plan  # 将处理结果存储在会话中
        print(meal_plan)

        return jsonify({"redirect": url_for('page4')})  # 返回重定向信息
# 以下代码保持不变
food_db = [
    # 早餐类
    {"name": "燕麦", "type": "breakfast", "calories": 100, "protein": 4, "fat": 2, "carbs": 17, "fiber": 2},
    {"name": "全麦面包", "type": "breakfast", "calories": 80, "protein": 3, "fat": 1, "carbs": 15, "fiber": 3},
    {"name": "希腊酸奶", "type": "breakfast", "calories": 60, "protein": 10, "fat": 0.4, "carbs": 4, "fiber": 0},
    {"name": "牛奶(全脂)", "type": "breakfast", "calories": 64, "protein": 3.3, "fat": 3.7, "carbs": 4.8, "fiber": 0},
    {"name": "燕麦片", "type": "breakfast", "calories": 389, "protein": 16.9, "fat": 6.9, "carbs": 66, "fiber": 10},
    {"name": "水煮蛋", "type": "breakfast", "calories": 155, "protein": 13, "fat": 11, "carbs": 1.1, "fiber": 0},

    # 蛋白质类（午/晚餐）
    {"name": "鸡胸肉", "type": "protein", "calories": 165, "protein": 31, "fat": 3.6, "carbs": 0, "fiber": 0},
    {"name": "三文鱼", "type": "protein", "calories": 206, "protein": 22, "fat": 13, "carbs": 0, "fiber": 0},
    {"name": "牛肉(瘦)", "type": "protein", "calories": 143, "protein": 26, "fat": 3.5, "carbs": 1.9, "fiber": 0},
    {"name": "鸡蛋", "type": "protein", "calories": 147, "protein": 12.6, "fat": 9.9, "carbs": 1.1, "fiber": 0},
    {"name": "虾仁", "type": "protein", "calories": 99, "protein": 24, "fat": 0.3, "carbs": 0.2, "fiber": 0},
    {"name": "豆腐", "type": "protein", "calories": 76, "protein": 8.1, "fat": 4.2, "carbs": 1.9, "fiber": 0.4},

    # 碳水类（午/晚餐）
    {"name": "糙米", "type": "carb", "calories": 123, "protein": 2.7, "fat": 0.9, "carbs": 26, "fiber": 1},
    {"name": "红薯", "type": "carb", "calories": 90, "protein": 2, "fat": 0.2, "carbs": 21, "fiber": 3},
    {"name": "大米(生)", "type": "carb", "calories": 365, "protein": 7.1, "fat": 0.7, "carbs": 79, "fiber": 1.3},
    {"name": "面条(干)", "type": "carb", "calories": 138, "protein": 4.5, "fat": 0.6, "carbs": 29, "fiber": 1.2},
    {"name": "土豆", "type": "carb", "calories": 77, "protein": 2, "fat": 0.1, "carbs": 17, "fiber": 2.2},

    # 蔬菜类（通用）
    {"name": "西兰花", "type": "vegetable", "calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 6.6, "fiber": 2.6},
    {"name": "胡萝卜", "type": "vegetable", "calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 9.6, "fiber": 2.8},
    {"name": "菠菜", "type": "vegetable", "calories": 23, "protein": 2.9, "fat": 0.4, "carbs": 3.6, "fiber": 2.2},
    {"name": "番茄", "type": "vegetable", "calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9, "fiber": 1.2},
    {"name": "黄瓜", "type": "vegetable", "calories": 15, "protein": 0.6, "fat": 0.1, "carbs": 3.6, "fiber": 0.5},

    # 水果/加餐类
    {"name": "苹果", "type": "snack", "calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14, "fiber": 2.4},
    {"name": "香蕉", "type": "snack", "calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23, "fiber": 2.6},
    {"name": "酸奶(低脂)", "type": "snack", "calories": 63, "protein": 5.3, "fat": 1.6, "carbs": 7, "fiber": 0},
    {"name": "杏仁", "type": "snack", "calories": 578, "protein": 21, "fat": 49, "carbs": 22, "fiber": 12},
]

@app.route('/api/recommend', methods=['POST'])
def recommend_meal_plan():
    try:
        user_data = request.json

        # 参数验证
        required_fields = ['gender', 'height', 'weight', 'age', 'activity_level', 'goal']
        if not all(field in user_data for field in required_fields):
            return jsonify({"code": 400, "message": "Missing required fields"}), 400

        # 计算热量需求
        bmr = calculate_bmr(user_data)
        total_calories = calculate_total_calories(bmr, user_data['activity_level'], user_data['goal'])

        # 生成营养目标
        macro_targets = calculate_macro_targets(total_calories)

        # 生成三餐食谱
        meal_plan = generate_intelligent_meal_plan(total_calories, macro_targets)

        return jsonify({
            "code": 200,
            "data": {
                "total_calories": total_calories,
                "macros": macro_targets,
                "meals": meal_plan
            }
        })

    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@app.route('/get_meal_dishes', methods=['GET'])
def get_meal_dishes():
    """获取分类食物列表
    参数说明：
    - type: 筛选类型（breakfast/protein/carb/vegetable/snack）
    - search: 模糊搜索关键词
    """
    try:
        category = request.args.get('type', '').lower()
        search_key = request.args.get('search', '').lower()

        filtered = food_db

        # 类型筛选
        if category:
            filtered = [f for f in filtered if f['type'] == category]

        # 模糊搜索
        if search_key:
            filtered = [f for f in filtered if search_key in f['name'].lower()]

        return jsonify({
            "code": 200,
            "count": len(filtered),
            "data": filtered
        })
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


def calculate_bmr(user_data: Dict) -> float:
    """计算基础代谢率"""
    weight = user_data['weight']
    height = user_data['height'] * 100  # 转换为cm
    age = user_data['age']

    if user_data['gender'] == 'male':
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161


def calculate_total_calories(bmr: float, activity_level: str, goal: str) -> float:
    """计算每日总热量需求"""
    activity_factors = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'super_active': 1.9
    }

    # 基础热量计算
    tdee = bmr * activity_factors.get(activity_level, 1.2)

    # 根据目标调整
    if goal == 'lose':
        return tdee - 500
    elif goal == 'gain':
        return tdee + 500
    else:  # maintain
        return tdee


def calculate_macro_targets(total_calories: float) -> Dict:
    """计算宏量营养素目标"""
    return {
        'protein': (total_calories * 0.3) / 4,  # 30%热量来自蛋白质
        'fat': (total_calories * 0.25) / 9,  # 25%脂肪
        'carbs': (total_calories * 0.45) / 4,  # 45%碳水
        'fiber': 25  # 膳食纤维推荐量
    }


def generate_intelligent_meal_plan(total_calories: float, macro_targets: Dict) -> Dict:
    """智能生成三餐食谱"""
    meals = {
        "breakfast": select_meal('breakfast', total_calories * 0.3, macro_targets),
        "lunch": select_meal('lunch', total_calories * 0.4, macro_targets),
        "dinner": select_meal('dinner', total_calories * 0.3, macro_targets)
    }

    # 营养统计
    totals = {
        'calories': sum(m['total_calories'] for m in meals.values()),
        'protein': sum(m['total_protein'] for m in meals.values()),
        'fat': sum(m['total_fat'] for m in meals.values()),
        'carbs': sum(m['total_carbs'] for m in meals.values()),
        'fiber': sum(m['total_fiber'] for m in meals.values())
    }

    return {
        "meals": meals,
        "totals": totals
    }


def select_meal(meal_type: str, calorie_target: float, macro_targets: Dict) -> Dict:
    """为单餐选择食物组合"""
    candidates = {
        'breakfast': ['breakfast', 'protein', 'vegetable'],
        'lunch': ['protein', 'carb', 'vegetable'],
        'dinner': ['protein', 'carb', 'vegetable']
    }

    selected = []
    current_cals = 0
    macros = {'protein': 0, 'fat': 0, 'carbs': 0, 'fiber': 0}
    available_types = candidates[meal_type]

    # 智能选择算法
    while current_cals < calorie_target * 0.9:  # 允许90%的热量填充
        # 按优先级选择食物类型
        remaining_protein = macro_targets['protein'] - macros['protein']
        remaining_carbs = macro_targets['carbs'] - macros['carbs']

        # 动态调整选择策略
        if remaining_protein > remaining_carbs:
            food_type_priority = ['protein', 'vegetable', 'carb']
        else:
            food_type_priority = ['carb', 'vegetable', 'protein']

        # 筛选候选食物
        available = [
            f for f in food_db
            if f['type'] in available_types
               and f['calories'] <= (calorie_target - current_cals)
               and f not in selected
        ]

        if not available:
            break

        # 根据优先级选择最佳食物
        for ft in food_type_priority:
            candidates = [f for f in available if f['type'] == ft]
            if candidates:
                food = max(candidates, key=lambda x: x['protein'] if ft == 'protein' else x['carbs'])
                selected.append(food)
                current_cals += food['calories']
                macros['protein'] += food['protein']
                macros['fat'] += food['fat']
                macros['carbs'] += food['carbs']
                macros['fiber'] += food['fiber']
                break

    return {
        "items": [f['name'] for f in selected],
        "total_calories": round(current_cals, 1),
        "total_protein": round(macros['protein'], 1),
        "total_fat": round(macros['fat'], 1),
        "total_carbs": round(macros['carbs'], 1),
        "total_fiber": round(macros['fiber'], 1)
    }


@app.route('/get_nutrient_data', methods=['GET'])
def get_nutrient_data():
    # 这里简单模拟营养成分数据，实际应用中应根据三餐数据计算
    meal_plan = session.get('meal_plan')
    if not meal_plan:
        return jsonify({"error": "No meal plan found"}), 400

    return jsonify({
        'labels': ['蛋白质', '脂肪', '碳水化合物'],
        'datasets': [{
            'data': [
                meal_plan['totals']['protein'],
                meal_plan['totals']['fat'],
                meal_plan['totals']['carbs']
            ],
            'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56']
        }],

})

if __name__ == '__main__':
    app.run(debug=True, port=8888)