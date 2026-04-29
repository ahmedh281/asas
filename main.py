import google.generativeai as genai
import json

# --- الإعدادات ---
API_KEY = "AIzaSyAUIjLcEdDGAemE76dxqusIx_rcO8mFadQ"

# إعداد المكتبة
genai.configure(api_key=API_KEY)

def analyze_strategy(description, vision, mission):
    # اخترنا أحد النماذج المتاحة في قائمتك (Gemini 3 Flash)
    # ملاحظة: يمكنك تغيير الاسم إلى 'gemini-2.0-flash' إذا أردت استقراراً أكثر
    model_name = 'gemini-3-flash-preview' 
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    أنت خبير استراتيجي متخصص في منهجية "فريد ديفيد".
    بناءً على المعطيات التالية:
    وصف الشركة: {description}
    الرؤية: {vision}
    الرسالة: {mission}

    قم بإجراء تحليل استراتيجي كامل وأعطني المخرجات بصيغة JSON حصراً بالهيكل التالي:
    {{
      "SWOT": {{ "Strengths": [], "Weaknesses": [], "Opportunities": [], "Threats": [] }},
      "IFE_Matrix": [ 
        {{"factor": "string", "weight": float, "rating": int, "rationale": "string"}} 
      ],
      "EFE_Matrix": [ 
        {{"factor": "string", "weight": float, "rating": int, "rationale": "string"}} 
      ]
    }}

    شروط: 
    - مجموع الأوزان (weights) لكل مصفوفة يجب أن يساوي 1.0.
    - التقييم (rating) من 1 إلى 4.
    - اللغة: العربية.
    """

    try:
        # استدعاء التوليد مع إجبار المخرجات على تنسيق JSON
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"حدث خطأ أثناء التوليد: {e}")
        return None

def main():
    # بيانات مدخلة للتحليل
    company_desc = "شركة تقنية رائدة في حلول التخزين السحابي بالسوق السعودي."
    vision = "أن نكون الخيار الأول للشركات في التحول الرقمي الآمن."
    mission = "توفير بنية تحتية سحابية موثوقة تدعم نمو الأعمال."

    print(f"جاري التحليل باستخدام نموذج: gemini-3-flash-preview...")
    
    result = analyze_strategy(company_desc, vision, mission)

    if result:
        print("\n✅ تم التحليل بنجاح!")
        
        # عرض ملخص سريع
        ife_score = sum(f['weight'] * f['rating'] for f in result['IFE_Matrix'])
        efe_score = sum(f['weight'] * f['rating'] for f in result['EFE_Matrix'])
        
        print(f"--- إجمالي نقاط IFE: {ife_score:.2f}")
        print(f"--- إجمالي نقاط EFE: {efe_score:.2f}")

        # حفظ النتيجة في ملف
        with open('final_strategy.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print("\nتم حفظ التحليل في الملف: final_strategy.json")
    else:
        print("فشل التحليل. تأكد من اتصال الإنترنت وصلاحية المفتاح.")

if __name__ == "__main__":
    main()