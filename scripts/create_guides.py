import os
import datetime

# 저장될 디렉토리
OUTPUT_DIR = "app/templates/guides"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 현재 날짜 (업데이트 날짜용)
today = datetime.date.today().strftime("%Y-%m-%d")

# HTML 템플릿 (다국어 지원 스크립트 포함)
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_en} - JP Campus Guide</title>
    <meta name="description" content="{desc_en}">
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        .article-container {{ max-width: 860px; margin: 40px auto; padding: 0 20px; background: #fff; }}
        .article-header {{ text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); border-radius: 16px; margin-bottom: 40px; }}
        .article-category {{ color: #3498db; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem; }}
        .article-title {{ font-size: 2.2rem; color: #2c3e50; margin: 15px 0; line-height: 1.3; word-break: keep-all; }}
        .article-meta {{ color: #7f8c8d; font-size: 0.9rem; }}
        .article-body {{ font-size: 1.1rem; line-height: 1.9; color: #333; }}
        .article-body h2 {{ font-size: 1.6rem; color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-top: 60px; margin-bottom: 25px; }}
        .article-body h3 {{ font-size: 1.3rem; color: #2980b9; margin-top: 40px; margin-bottom: 15px; border-left: 5px solid #2980b9; padding-left: 15px; }}
        .article-body p {{ margin-bottom: 20px; text-align: justify; }}
        .article-body ul, .article-body ol {{ margin-bottom: 30px; padding-left: 20px; background: #f9f9f9; padding: 20px 20px 20px 40px; border-radius: 8px; }}
        .article-body li {{ margin-bottom: 10px; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin: 30px 0; font-size: 0.95rem; }}
        .data-table th {{ background: #2c3e50; color: #fff; padding: 12px; text-align: left; }}
        .data-table td {{ border: 1px solid #ddd; padding: 12px; }}
        .data-table tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .highlight-box {{ background-color: #e8f4f8; border: 2px solid #3498db; border-radius: 10px; padding: 25px; margin: 30px 0; }}
        .highlight-title {{ font-weight: bold; color: #2980b9; font-size: 1.1rem; margin-bottom: 10px; display: block; }}
        .faq-box {{ background: #fff8e1; border: 1px solid #ffe082; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .faq-q {{ font-weight: bold; color: #f57c00; margin-bottom: 10px; display: block; }}
        .btn-area {{ text-align: center; margin-top: 80px; padding: 40px 0; border-top: 1px solid #eee; }}
        .cta-button {{ display: inline-block; background: #3498db; color: white; padding: 15px 40px; border-radius: 50px; font-weight: bold; text-decoration: none; transition: 0.3s; box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3); }}
        .cta-button:hover {{ background: #2980b9; transform: translateY(-3px); }}
        
        /* 언어별 표시 제어 */
        .lang-content {{ display: none; }}
        .lang-content.active {{ display: block; }}
    </style>
</head>
<body>
    <header class="main-header" style="padding: 15px 0; background: #fff; border-bottom: 1px solid #eee; display: flex; justify-content: center; align-items: center; gap: 20px;">
        <a href="/" style="font-size: 1.5rem; font-weight: bold; color: #333; text-decoration: none;">JP Campus</a>
        <div class="lang-switch" style="margin-top:0;">
            <button onclick="setGuideLang('en')">🇺🇸</button>
            <button onclick="setGuideLang('ko')">🇰🇷</button>
        </div>
    </header>

    <article class="article-container">
        <!-- English Content -->
        <div id="content-en" class="lang-content">
            <header class="article-header">
                <span class="article-category">{cat_en}</span>
                <h1 class="article-title">{title_en}</h1>
                <div class="article-meta">Last Updated: {date} · JP Campus Editor</div>
            </header>
            <div class="article-body">
                {body_en}
            </div>
            <div class="btn-area">
                <h3>Find the perfect school for you?</h3>
                <p>Compare schools based on location, tuition, and nationality.</p>
                <br>
                <a href="/" class="cta-button">🏫 Search Schools</a>
                <br><br>
                <a href="/guide" style="color:#999; text-decoration:underline;">Back to List</a>
            </div>
        </div>

        <!-- Korean Content -->
        <div id="content-ko" class="lang-content">
            <header class="article-header">
                <span class="article-category">{cat_ko}</span>
                <h1 class="article-title">{title_ko}</h1>
                <div class="article-meta">최종 업데이트: {date} · JP Campus 편집부</div>
            </header>
            <div class="article-body">
                {body_ko}
            </div>
            <div class="btn-area">
                <h3>나에게 딱 맞는 학교를 찾고 싶다면?</h3>
                <p>위치, 학비, 국적 비율 데이터를 기반으로 최적의 학교를 추천해드립니다.</p>
                <br>
                <a href="/" class="cta-button">🏫 학교 검색하러 가기</a>
                <br><br>
                <a href="/guide" style="color:#999; text-decoration:underline;">목록으로 돌아가기</a>
            </div>
        </div>
    </article>

    <footer class="main-footer">
        <p class="copyright">© 2024 JP Campus. All rights reserved.</p>
    </footer>

    <script>
        function setGuideLang(lang) {{
            // 저장 및 상태 업데이트
            localStorage.setItem('lang', lang);
            
            // 모든 콘텐츠 숨김
            document.querySelectorAll('.lang-content').forEach(el => el.classList.remove('active'));
            
            // 선택된 언어만 표시
            const target = document.getElementById('content-' + lang);
            if (target) {{
                target.classList.add('active');
            }} else {{
                // Fallback to English if target lang not found
                document.getElementById('content-en').classList.add('active');
            }}
        }}

        // 초기 로드 시 언어 설정 확인
        document.addEventListener("DOMContentLoaded", () => {{
            const savedLang = localStorage.getItem('lang') || 'en';
            setGuideLang(savedLang);
        }});
    </script>
</body>
</html>
"""

# ==========================================
# [데이터] 영/한 쌍으로 구성
# ==========================================
articles = [
    {
        "filename": "cost",
        "cat_en": "Cost/Budget", "cat_ko": "비용/예산",
        "title_en": "💰 1-Year Cost Breakdown for Studying in Japan",
        "title_ko": "💰 일본 어학연수 1년 비용 완벽 분석 (학비, 생활비, 숨은 비용)",
        "desc_en": "Realistic budget analysis for 1 year in Tokyo: Tuition, housing, and living costs.",
        "body_en": """
            <p>One of the biggest concerns for students planning to study in Japan is <strong>cost</strong>. Estimates vary widely depending on lifestyle and location (Tokyo vs. rural areas).</p>
            <p>Here is a realistic breakdown based on 2024 Tokyo prices.</p>

            <h2>1. Tuition (1 Year)</h2>
            <p>Average tuition for language schools in Tokyo:</p>
            <table class="data-table">
                <tr><th>Item</th><th>Average Cost (JPY)</th></tr>
                <tr><td>Selection Fee</td><td>20,000 ~ 30,000</td></tr>
                <tr><td>Admission Fee</td><td>50,000 ~ 70,000</td></tr>
                <tr><td>Tuition (1 yr)</td><td>600,000 ~ 700,000</td></tr>
                <tr><td>Facility/Others</td><td>40,000 ~ 80,000</td></tr>
                <tr><td><strong>Total</strong></td><td><strong>Approx. 750k ~ 850k JPY</strong></td></tr>
            </table>

            <h2>2. Housing (The Biggest Variable)</h2>
            <h3>(1) School Dormitory</h3>
            <ul>
                <li>Initial Cost: 30k~50k JPY</li>
                <li>Monthly Rent (2-person room): 40k~50k JPY</li>
                <li><strong>1 Year Total: Approx. 600k JPY</strong></li>
            </ul>

            <h3>(2) Share House</h3>
            <ul>
                <li>Monthly Rent + Utilities: 50k~70k JPY</li>
                <li><strong>1 Year Total: Approx. 800k JPY</strong></li>
            </ul>

            <h3>(3) Private Apartment</h3>
            <ul>
                <li>Initial Cost (Key money, etc.): 200k~300k JPY</li>
                <li>Monthly Rent: 60k~80k JPY</li>
                <li><strong>1 Year Total: Approx. 1M~1.2M JPY</strong></li>
            </ul>

            <h2>3. Living Expenses</h2>
            <ul>
                <li><strong>Food:</strong> 30k~40k JPY/month (Cooking at home is key!)</li>
                <li><strong>Transport:</strong> 5k~10k JPY/month (Student commuter pass available)</li>
                <li><strong>Phone/Internet:</strong> 3k~5k JPY/month</li>
            </ul>

            <h2>4. Summary: Total 1-Year Cost</h2>
            <p>Based on [Tokyo School + Dormitory + Moderate Lifestyle]:</p>
            <table class="data-table">
                <tr><td>Tuition</td><td>800,000 JPY</td></tr>
                <tr><td>Housing</td><td>600,000 JPY</td></tr>
                <tr><td>Living</td><td>600,000 JPY</td></tr>
                <tr><td><strong>Grand Total</strong></td><td><strong>2,000,000 JPY (Approx $13,500)</strong></td></tr>
            </table>
        """,
        "body_ko": """
            <p>일본 유학을 준비하는 분들이 가장 먼저, 그리고 가장 심각하게 고민하는 부분이 바로 <strong>'비용'</strong>입니다. 인터넷에 검색해보면 "1,500만원이면 된다"부터 "3,000만원은 있어야 한다"까지 정보가 제각각이라 혼란스러우셨을 겁니다.</p>
            <p>JP Campus에서는 2024년 도쿄 물가를 기준으로, 숨겨진 비용 하나까지 놓치지 않고 <strong>가장 현실적인 1년 유학 비용</strong>을 분석해 드립니다.</p>

            <h2>1. 일본어학교 학비 (1년 기준)</h2>
            <table class="data-table">
                <tr><th>항목</th><th>평균 비용 (엔)</th><th>비고</th></tr>
                <tr><td>선고료 (전형료)</td><td>20,000 ~ 30,000</td><td>원서 접수 시 1회 납부</td></tr>
                <tr><td>입학금</td><td>50,000 ~ 70,000</td><td>입학 첫 해만 납부</td></tr>
                <tr><td>수업료 (1년)</td><td>600,000 ~ 700,000</td><td>6개월 분납 가능 학교 많음</td></tr>
                <tr><td>시설비/교재비</td><td>40,000 ~ 80,000</td><td>냉난방비 등 포함</td></tr>
                <tr><td><strong>총 합계</strong></td><td><strong>약 75만엔 ~ 85만엔</strong></td><td><strong>한화 약 700~800만원</strong></td></tr>
            </table>

            <h2>2. 주거비 (가장 큰 변수)</h2>
            <h3>(1) 학교 기숙사 (2인실 기준)</h3>
            <p>가장 일반적인 선택입니다. 학교에서 관리하므로 안전하고, 입주 심사가 없어 편리합니다.</p>
            <ul>
                <li>입실료: 3~5만엔</li>
                <li>월세: 4~5만엔</li>
                <li><strong>1년 예상 비용: 약 60만엔</strong></li>
            </ul>

            <h3>(2) 사설 쉐어하우스</h3>
            <p>보증금이 없고 최소 계약 기간이 짧은 편입니다.</p>
            <ul>
                <li>월세+관리비: 5~7만엔</li>
                <li><strong>1년 예상 비용: 약 80만엔</strong></li>
            </ul>

            <h3>(3) 원룸 자취 (임대)</h3>
            <p>초기 비용이 월세의 3~4배가 들어갑니다. 유학 초반에는 추천하지 않습니다.</p>
            <ul>
                <li>초기 비용: 20~30만엔</li>
                <li>월세: 6~8만엔 (도쿄 기준)</li>
                <li><strong>1년 예상 비용: 약 100~120만엔</strong></li>
            </ul>

            <h2>3. 생활비 (식비, 교통비, 통신비)</h2>
            <ul>
                <li><strong>식비:</strong> 월 3~4만엔 (자취 요리 기준)</li>
                <li><strong>교통비:</strong> 월 5천~1만엔 (유학생 정기권 할인 가능)</li>
                <li><strong>통신비:</strong> 월 3~5천엔 (알뜰폰 사용 시)</li>
            </ul>

            <h2>4. 총정리: 1년 유학, 얼마가 필요할까?</h2>
            <p>가장 일반적인 [도쿄 사립 어학원 + 기숙사 2인실 + 적당한 자취] 패턴입니다.</p>
            <table class="data-table">
                <tr><td>학비 (1년)</td><td>800,000엔</td></tr>
                <tr><td>주거비 (1년)</td><td>600,000엔</td></tr>
                <tr><td>생활비 (12개월)</td><td>600,000엔</td></tr>
                <tr><td><strong>총 합계</strong></td><td><strong>2,000,000엔 (약 1,900만원)</strong></td></tr>
            </table>
        """
    },
    {
        "filename": "school-choice",
        "cat_en": "School Selection", "cat_ko": "학교선택",
        "title_en": "🏫 5 Criteria for Choosing a Language School",
        "title_ko": "🏫 실패 없는 일본어학교 선택 기준 5가지 (진학/취업/회화)",
        "desc_en": "How to choose the right school for university advancement, employment, or conversation.",
        "body_en": """
            <p>There are over 800 language schools in Japan. Choosing the right one is crucial for your success.</p>

            <h2>1. Purpose of Study</h2>
            <ul>
                <li><strong>University Advancement:</strong> Look for schools with "Preparatory Courses" (Junbi Kyoiku Katei) and EJU classes.</li>
                <li><strong>Employment:</strong> Choose schools offering "Business Japanese" and job hunting support.</li>
                <li><strong>Conversation/Culture:</strong> Look for schools with many Western students and cultural activities.</li>
            </ul>

            <h2>2. Nationality Ratio</h2>
            <p>This determines the atmosphere of the class.</p>
            <ul>
                <li><strong>High Kanji-background (Chinese/Korean):</strong> Fast-paced, focused on kanji and exams.</li>
                <li><strong>High Non-Kanji background (Western/SE Asian):</strong> Focuses more on speaking and basic kanji.</li>
            </ul>

            <h2>3. Location (Tokyo)</h2>
            <ul>
                <li><strong>Shinjuku/Shibuya:</strong> Convenient transport, many part-time jobs, but busy and expensive.</li>
                <li><strong>Takadanobaba:</strong> Known as a "student town", relatively cheaper food.</li>
                <li><strong>Nippori/Ikebukuro:</strong> Lower rent, good access to Narita airport.</li>
            </ul>

            <h2>4. School Size</h2>
            <ul>
                <li><strong>Large (500+ students):</strong> Systematic, many levels of classes.</li>
                <li><strong>Small (Under 200):</strong> Family-like atmosphere, close attention from teachers.</li>
            </ul>
        """,
        "body_ko": """
            <p>일본에는 800개가 넘는 일본어학교가 있습니다. 목적에 맞는 학교를 고르는 5가지 절대 기준을 알려드립니다.</p>

            <h2>1. '목적'에 맞는 커리큘럼인가?</h2>
            <ul>
                <li><strong>진학형:</strong> EJU 대책 수업, 소논문 지도, '준비교육과정' 설치 여부를 확인하세요.</li>
                <li><strong>취업형:</strong> '비즈니스 일본어 클래스'가 있는지, 이력서 첨삭 지원을 해주는지 확인하세요.</li>
                <li><strong>회화형:</strong> 스파르타식보다는 회화 위주 수업과 다양한 과외 활동이 많은 곳이 좋습니다.</li>
            </ul>

            <h2>2. 국적 비율: 한자권 vs 비한자권</h2>
            <ul>
                <li><strong>한자권(중국/한국) 위주:</strong> 진도가 빠르고 면학 분위기가 진지합니다. 상위권 대학 진학에 유리합니다.</li>
                <li><strong>비한자권(서양 등) 위주:</strong> 회화 중심으로 수업이 진행되며 분위기가 자유롭습니다.</li>
            </ul>

            <h2>3. 위치와 주변 환경</h2>
            <ul>
                <li><strong>신주쿠/시부야:</strong> 교통과 알바 자리가 많지만 물가가 비쌉니다.</li>
                <li><strong>다카다노바바:</strong> 학생 거리로 저렴한 식당이 많고 면학 분위기가 좋습니다.</li>
                <li><strong>닛포리/이케부쿠로:</strong> 월세가 상대적으로 저렴합니다.</li>
            </ul>

            <h2>4. 학교의 규모</h2>
            <ul>
                <li><strong>대규모:</strong> 레벨이 세분화되어 있어 내 실력에 딱 맞는 반에 들어갈 수 있습니다.</li>
                <li><strong>소규모:</strong> 선생님이 학생 이름을 다 외울 정도로 가족 같은 분위기입니다.</li>
            </ul>
        """
    },
    {
        "filename": "visa",
        "cat_en": "Visa/COE", "cat_ko": "비자/서류",
        "title_en": "✈️ Student Visa Application Guide (A to Z)",
        "title_ko": "✈️ 일본 유학 비자(COE) 신청 절차 A to Z",
        "desc_en": "Step-by-step guide from document preparation to COE issuance and visa application.",
        "body_en": """
            <p>Getting a student visa involves strict documentation. Here is the timeline for April admission.</p>

            <h2>1. Timeline (April Intake)</h2>
            <ul>
                <li><strong>Sep-Nov (Prev Year):</strong> Apply to school.</li>
                <li><strong>Late Nov:</strong> School submits docs to Immigration Bureau.</li>
                <li><strong>Late Feb:</strong> COE (Certificate of Eligibility) Issued.</li>
                <li><strong>Early Mar:</strong> Pay tuition & Receive COE.</li>
                <li><strong>Mid Mar:</strong> Apply for Visa at the Japanese Embassy in your country.</li>
            </ul>

            <h2>2. Key Documents</h2>
            <ul>
                <li><strong>Personal:</strong> Application form, Diploma, Transcript, Passport copy.</li>
                <li><strong>Financial Supporter (Parents):</strong> Bank Balance Certificate (approx. 3M~4M JPY), Proof of Employment/Income.</li>
            </ul>

            <div class="highlight-box">
                <span class="highlight-title">⚠️ Common Rejection Reasons</span>
                <ul>
                    <li>Unexplained gaps in education/career history.</li>
                    <li>Insufficient funds in bank statement.</li>
                    <li>Past history of illegal stay or visa rejection.</li>
                </ul>
            </div>
        """,
        "body_ko": """
            <p>일본 유학 비자는 서류 심사가 까다롭습니다. 4월 학기 입학을 기준으로 한 일정입니다.</p>

            <h2>1. 수속 타임라인 (4월 학기)</h2>
            <ul>
                <li><strong>전년도 9~11월:</strong> 학교 원서 접수</li>
                <li><strong>11월 말:</strong> 일본 입국관리국에 서류 제출 (학교 대행)</li>
                <li><strong>2월 말:</strong> 재류자격인정증명서(COE) 발급</li>
                <li><strong>3월 초:</strong> 학비 납부 및 COE 수령</li>
                <li><strong>3월 중순:</strong> 주한 일본 대사관에서 비자 신청</li>
            </ul>

            <h2>2. 필수 서류</h2>
            <ul>
                <li><strong>본인:</strong> 입학원서, 졸업/성적증명서, 여권 사본, 사진</li>
                <li><strong>보증인(부모님):</strong> 은행 잔고증명서 (3~4천만원 이상), 재직/소득증명서</li>
            </ul>

            <div class="highlight-box">
                <span class="highlight-title">⚠️ 불합격 주의사항</span>
                <ul>
                    <li>이력서상의 공백 기간(군대 등)을 명확히 소명해야 합니다.</li>
                    <li>보증인의 재정 능력이 부족하면 불허될 수 있습니다.</li>
                </ul>
            </div>
        """
    },
    {
        "filename": "housing",
        "cat_en": "Housing", "cat_ko": "숙소/생활",
        "title_en": "🏠 Dorm vs Share House vs Apartment",
        "title_ko": "🏠 일본 기숙사 vs 쉐어하우스 vs 원룸 (장단점 및 비용 비교)",
        "desc_en": "Pros and cons of each housing type and comparison of initial costs.",
        "body_en": """
            <p>Finding a place to live is as important as choosing a school. Here are the 3 most common options.</p>

            <h2>1. School Dormitory</h2>
            <ul>
                <li><strong>Pros:</strong> Easy procedure, furnished (fridge, washing machine), close to school.</li>
                <li><strong>Cons:</strong> Often shared rooms (2-4 people), curfew rules.</li>
                <li><strong>Cost:</strong> 40k~50k JPY/month.</li>
            </ul>

            <h2>2. Share House</h2>
            <ul>
                <li><strong>Pros:</strong> Low initial cost, opportunity to make friends, short-term contracts available.</li>
                <li><strong>Cons:</strong> Shared kitchen/bathroom, noise issues.</li>
                <li><strong>Cost:</strong> 50k~70k JPY/month.</li>
            </ul>

            <h2>3. Private Apartment</h2>
            <ul>
                <li><strong>Pros:</strong> Complete privacy, freedom.</li>
                <li><strong>Cons:</strong> Very high initial cost (Key money, agent fee, etc.), unfurnished.</li>
                <li><strong>Cost:</strong> 60k~90k JPY/month + Utilities.</li>
            </ul>

            <div class="highlight-box">
                <span class="highlight-title">Recommendation</span>
                <p>Start with a <strong>Dormitory</strong> or <strong>Share House</strong> for the first 3 months to adjust to life in Japan, then move to an apartment later.</p>
            </div>
        """,
        "body_ko": """
            <p>유학생들이 주로 선택하는 3가지 주거 형태의 특징과 비용을 비교해 드립니다.</p>

            <h2>1. 학교 기숙사</h2>
            <ul>
                <li><strong>장점:</strong> 학교와 가깝고 가전가구가 완비되어 있어 몸만 들어가면 됩니다. 입주 절차가 간편합니다.</li>
                <li><strong>단점:</strong> 1인실은 드물고 2~4인실이 많습니다. 통금 등 규칙이 있을 수 있습니다.</li>
                <li><strong>비용:</strong> 월 4~5만엔</li>
            </ul>

            <h2>2. 쉐어하우스</h2>
            <ul>
                <li><strong>장점:</strong> 보증금 등 초기 비용이 저렴합니다. 다양한 국적의 친구를 사귈 수 있습니다.</li>
                <li><strong>단점:</strong> 공용 공간 청소 문제나 소음 트러블이 있을 수 있습니다.</li>
                <li><strong>비용:</strong> 월 5~7만엔</li>
            </ul>

            <h2>3. 일반 원룸 임대</h2>
            <ul>
                <li><strong>장점:</strong> 완벽한 사생활이 보장됩니다.</li>
                <li><strong>단점:</strong> 초기 비용이 매우 비쌉니다(월세의 3~5배). 가구를 직접 사야 합니다.</li>
                <li><strong>비용:</strong> 월 6~9만엔 + 공과금</li>
            </ul>

            <div class="highlight-box">
                <span class="highlight-title">에디터 추천</span>
                <p>처음에는 <strong>학교 기숙사</strong>나 <strong>쉐어하우스</strong>에서 3개월 정도 살아보며 적응한 뒤, 직접 발품을 팔아 원룸으로 이사하는 것을 추천합니다.</p>
            </div>
        """
    },
    {
        "filename": "part-time",
        "cat_en": "Part-time Job", "cat_ko": "생활/알바",
        "title_en": "🍔 Part-time Jobs in Japan: Guide & Wages",
        "title_ko": "🍔 일본 유학 아르바이트: 구하는 법, 시급, 추천 직종",
        "desc_en": "How to get a work permit, recommended jobs by Japanese level, and average hourly wages.",
        "body_en": """
            <p>Part-time jobs (Baito) are a great way to cover living expenses and practice Japanese.</p>

            <h2>1. Permission to Engage in Activity other than that Permitted...</h2>
            <p>You MUST apply for this permission at the airport upon arrival. It allows you to work up to <strong>28 hours/week</strong>.</p>

            <h2>2. Jobs by Japanese Level</h2>
            <ul>
                <li><strong>Beginner (N4-N5):</strong> Kitchen staff, hotel cleaning, warehouse work.</li>
                <li><strong>Intermediate (N3-N2):</strong> Convenience store, supermarket cashier, restaurant server.</li>
                <li><strong>Advanced (N1):</strong> Cafe (Starbucks), clothing store, hotel front desk.</li>
            </ul>

            <h2>3. Hourly Wages (Tokyo)</h2>
            <p>Minimum wage is around 1,113 JPY (2024). Night shifts (after 10 PM) get a 25% bonus.</p>
            <p>Example: 1,200 JPY x 28 hours x 4 weeks = <strong>Approx. 134,400 JPY/month</strong>.</p>
        """,
        "body_ko": """
            <p>일본 유학 생활의 꽃, 아르바이트에 대한 모든 것을 알려드립니다.</p>

            <h2>1. 자격외활동허가서 (필수!)</h2>
            <p>공항 입국 심사대에서 반드시 신청하세요. 주 28시간까지 합법적으로 일할 수 있는 허가입니다.</p>

            <h2>2. 일본어 레벨별 추천 알바</h2>
            <ul>
                <li><strong>초급:</strong> 주방 보조(설거지), 호텔 청소, 택배 상하차 등 말이 필요 없는 일.</li>
                <li><strong>중급:</strong> 편의점, 슈퍼마켓 계산원, 식당 서빙.</li>
                <li><strong>고급:</strong> 카페, 의류 매장, 호텔 프론트 등 접객 업무.</li>
            </ul>

            <h2>3. 시급과 수입</h2>
            <p>도쿄 평균 시급은 1,150엔~1,300엔 정도입니다.</p>
            <p><strong>[월 수입 예시]</strong> 시급 1,200엔 × 주 28시간 × 4주 = <strong>약 13만 4천엔</strong> (생활비 충당 가능)</p>
        """
    },
    {
        "filename": "eju-jlpt",
        "cat_en": "Exam/Uni", "cat_ko": "시험/진학",
        "title_en": "📚 EJU vs JLPT: Which one do I need?",
        "title_ko": "📚 EJU vs JLPT: 나에게 필요한 일본어 시험은?",
        "desc_en": "Differences between EJU and JLPT for university admission.",
        "body_en": """
            <p>Depending on your goal, you need to prepare for different exams.</p>

            <h2>1. JLPT (Japanese Language Proficiency Test)</h2>
            <ul>
                <li><strong>Purpose:</strong> General language ability certification (N1~N5).</li>
                <li><strong>Needed for:</strong> Employment, Vocational schools, some Graduate schools.</li>
                <li><strong>Schedule:</strong> Twice a year (July, December).</li>
            </ul>

            <h2>2. EJU (Examination for Japanese University Admission)</h2>
            <ul>
                <li><strong>Purpose:</strong> Academic ability test for university entrance.</li>
                <li><strong>Subjects:</strong> Japanese, Japan & the World, Science, Mathematics.</li>
                <li><strong>Needed for:</strong> Entering Japanese Universities (Bachelor's degree).</li>
                <li><strong>Schedule:</strong> Twice a year (June, November).</li>
            </ul>

            <div class="highlight-box">
                <span class="highlight-title">Strategy</span>
                <ul>
                    <li><strong>Aiming for University?</strong> Focus on <strong>EJU</strong> scores. JLPT is less important.</li>
                    <li><strong>Aiming for Job/Vocational School?</strong> Get <strong>JLPT N2 or N1</strong>.</li>
                </ul>
            </div>
        """,
        "body_ko": """
            <p>유학 목적에 따라 준비해야 할 시험이 다릅니다.</p>

            <h2>1. JLPT (일본어능력시험)</h2>
            <ul>
                <li><strong>성격:</strong> 일본어 종합 능력 평가 (합격/불합격).</li>
                <li><strong>필요한 사람:</strong> 취업 희망자, 전문학교 진학자.</li>
                <li><strong>시기:</strong> 연 2회 (7월, 12월).</li>
            </ul>

            <h2>2. EJU (일본유학시험)</h2>
            <ul>
                <li><strong>성격:</strong> 대학 수학 능력 평가 (점수제).</li>
                <li><strong>과목:</strong> 일본어, 종합과목(문과)/이과, 수학.</li>
                <li><strong>필요한 사람:</strong> 4년제 대학 진학 희망자.</li>
                <li><strong>시기:</strong> 연 2회 (6월, 11월).</li>
            </ul>

            <div class="highlight-box">
                <span class="highlight-title">전략</span>
                <ul>
                    <li><strong>대학 진학이 목표라면:</strong> JLPT보다는 <strong>EJU 고득점</strong>에 집중하세요.</li>
                    <li><strong>전문학교/취업이 목표라면:</strong> <strong>JLPT N2~N1</strong> 취득이 우선입니다.</li>
                </ul>
            </div>
        """
    },
    {
        "filename": "preparation",
        "cat_en": "Preparation", "cat_ko": "출국준비",
        "title_en": "🧳 Pre-departure Checklist: What to Pack",
        "title_ko": "🧳 일본 유학 출국 전 필수 체크리스트 (짐 싸기)",
        "desc_en": "Must-bring items like Hanko (seal), adapter, and documents.",
        "body_en": """
            <p>What should you pack in your luggage? Here is the essential list.</p>

            <h2>1. Must-haves</h2>
            <ul>
                <li><strong>Hanko (Personal Seal):</strong> Required for bank accounts and contracts. Bring a round seal with your last name (Kanji or Katakana).</li>
                <li><strong>Adapter (Type A):</strong> Japan uses 100V, Type A plugs (flat two-pin).</li>
                <li><strong>ID Photos:</strong> Bring various sizes (3x4cm, 4x3cm) for documents and resumes.</li>
                <li><strong>Cash & Cards:</strong> Bring at least 100,000 JPY in cash and a credit card for overseas use.</li>
            </ul>

            <h2>2. Good to have</h2>
            <ul>
                <li><strong>Medicine:</strong> Bring your usual painkillers, cold medicine, etc.</li>
                <li><strong>Glasses/Contacts:</strong> Spare pairs are recommended.</li>
            </ul>

            <h2>3. Hand Carry Items (Don't put in checked luggage!)</h2>
            <ul>
                <li>Passport with Visa</li>
                <li>COE (Certificate of Eligibility)</li>
                <li>Admission Letter</li>
            </ul>
        """,
        "body_ko": """
            <p>일본으로 떠나기 전 꼭 챙겨야 할 물건들을 정리했습니다.</p>

            <h2>1. 필수품</h2>
            <ul>
                <li><strong>도장:</strong> 일본은 도장 문화입니다. 한자 성(姓)이 새겨진 도장을 꼭 챙기세요. (은행 개설용)</li>
                <li><strong>돼지코 (어댑터):</strong> 일본은 110v를 씁니다. 다이소에서 넉넉히 사 가세요.</li>
                <li><strong>증명사진:</strong> 알바 이력서 등에 많이 쓰입니다. 넉넉히 인화해 가세요.</li>
                <li><strong>해외 결제 카드 & 현금:</strong> 초기 정착금으로 현금 10만엔 이상은 준비하세요.</li>
            </ul>

            <h2>2. 챙겨가면 좋은 것</h2>
            <ul>
                <li><strong>상비약:</strong> 평소 먹는 약, 감기약, 소화제 등.</li>
                <li><strong>안경/렌즈 여분:</strong> 일본에서 맞추려면 비쌀 수 있습니다.</li>
            </ul>

            <div class="highlight-box">
                <span class="highlight-title">🚨 기내 수하물로 챙길 것</span>
                <p>여권, COE 원본, 입학허가서는 절대 캐리어에 넣지 말고 가방에 넣어 들고 타세요.</p>
            </div>
        """
    },
    {
        "filename": "mobile-bank",
        "cat_en": "Settlement", "cat_ko": "현지정착",
        "title_en": "📱 Immediate To-Dos: Resident Registration, Phone, Bank",
        "title_ko": "📱 일본 도착 후 행정 처리 3대장 (주소/폰/통장)",
        "desc_en": "Guide to City Hall procedures, getting a SIM card, and opening a JP Bank account.",
        "body_en": """
            <p>Do these 3 things within 14 days of arrival to start your life in Japan.</p>

            <h2>STEP 1. Resident Registration (City Hall)</h2>
            <p>Go to the Ward Office (Kuyakusho) of your area.</p>
            <ul>
                <li>Bring: Passport, Residence Card.</li>
                <li>Action: Fill out "Moving-in Notification". Your address will be printed on the card.</li>
                <li><strong>Tip:</strong> Join National Health Insurance here and apply for student reduction.</li>
            </ul>

            <h2>STEP 2. Mobile Phone</h2>
            <p>You need a Residence Card with an address to get a SIM.</p>
            <ul>
                <li><strong>MVNO (Budget SIM):</strong> GTN Mobile, UQ Mobile, Y!Mobile are popular for students.</li>
                <li>Bring: Residence Card, Credit Card (some accept bank transfer).</li>
            </ul>

            <h2>STEP 3. Bank Account (JP Bank)</h2>
            <p>Most major banks require 6 months of stay. <strong>Japan Post Bank (Yucho)</strong> is the easiest for new students.</p>
            <ul>
                <li>Bring: Residence Card, Passport, Student ID, Hanko (Seal).</li>
            </ul>
        """,
        "body_ko": """
            <p>입국 후 14일 이내에 해결해야 할 3가지 필수 과제입니다. 순서대로 하세요.</p>

            <h2>STEP 1. 주소 등록 (구청)</h2>
            <p>살게 된 지역의 구청(시청)에 가서 전입신고를 합니다.</p>
            <ul>
                <li><strong>준비물:</strong> 재류카드, 여권</li>
                <li><strong>팁:</strong> 이때 국민건강보험도 같이 가입하고, 반드시 '보험료 감면 신청'을 하세요.</li>
            </ul>

            <h2>STEP 2. 핸드폰 개통</h2>
            <p>주소가 적힌 재류카드가 있어야 개통 가능합니다.</p>
            <ul>
                <li>유학생들은 약정이 없고 저렴한 <strong>알뜰폰(MVNO)</strong>이나 GTN모바일 등을 주로 씁니다.</li>
            </ul>

            <h2>STEP 3. 통장 개설 (유초은행)</h2>
            <p>시중 은행은 체류 기간 6개월 미만이면 만들기 어렵습니다. 우체국 은행(유초은행)이 가장 만들기 쉽습니다.</p>
            <ul>
                <li><strong>준비물:</strong> 재류카드, 도장(필수), 학생증</li>
            </ul>
        """
    },
    {
        "filename": "insurance",
        "cat_en": "Insurance", "cat_ko": "의료/보험",
        "title_en": "🏥 National Health Insurance & Exemptions",
        "title_ko": "🏥 국민건강보험료 폭탄 피하는 법 (감면 신청)",
        "desc_en": "How to apply for insurance fee reduction and use hospitals in Japan.",
        "body_en": """
            <p>International students staying over 3 months MUST join the National Health Insurance (NHI).</p>

            <h2>1. Apply for Reduction!</h2>
            <p>Since you have no income in Japan yet, declare "Zero Income" at the City Hall.</p>
            <ul>
                <li><strong>Result:</strong> Monthly fee reduces to approx. <strong>1,000 ~ 2,000 JPY</strong>.</li>
                <li>If you don't apply, it can be over 5,000 JPY.</li>
            </ul>

            <h2>2. Medical Benefits</h2>
            <p>With insurance, you only pay <strong>30%</strong> of the medical costs.</p>
            <ul>
                <li>Clinic visit + Medicine: Approx. 1,500 ~ 2,000 JPY.</li>
            </ul>

            <h2>3. Moving Out</h2>
            <div class="highlight-box">
                <span class="highlight-title">Important</span>
                <p>When you leave Japan permanently, you MUST go to City Hall to withdraw from NHI and pay any remaining fees. Otherwise, you may face issues entering Japan later.</p>
            </div>
        """,
        "body_ko": """
            <p>유학생도 의무적으로 국민건강보험에 가입해야 합니다.</p>

            <h2>1. 보험료 감면 신청 (필수!)</h2>
            <p>소득이 없는 학생임을 신고하면 보험료를 대폭 할인받습니다.</p>
            <ul>
                <li><strong>결과:</strong> 월 보험료가 약 <strong>1,000엔 ~ 2,000엔</strong> 수준으로 줄어듭니다. (신청 안 하면 훨씬 비쌉니다)</li>
            </ul>

            <h2>2. 병원 이용 혜택</h2>
            <p>병원비의 <strong>30%</strong>만 내면 됩니다.</p>
            <ul>
                <li>감기로 병원 진료 + 약 처방 시: 약 1,500엔 ~ 2,000엔 정도 나옵니다.</li>
            </ul>

            <h2>3. 귀국 시 주의사항</h2>
            <div class="highlight-box">
                <span class="highlight-title">🚨 꼭 탈퇴하세요!</span>
                <p>완전 귀국할 때는 구청에 가서 보험 탈퇴 신고를 하고 밀린 보험료를 정산해야 합니다. 그냥 가면 나중에 재입국 시 불이익을 받을 수 있습니다.</p>
            </div>
        """
    },
    {
        "filename": "region",
        "cat_en": "Region Info", "cat_ko": "지역정보",
        "title_en": "🌏 Tokyo vs Osaka vs Rural Areas",
        "title_ko": "🌏 도쿄 vs 오사카 vs 지방, 어디로 갈까?",
        "desc_en": "Comparison of standard language usage, living costs, and atmosphere.",
        "body_en": """
            <p>Choosing a region is as important as choosing a school.</p>

            <h2>1. Tokyo (The Capital)</h2>
            <ul>
                <li><strong>Pros:</strong> Standard Japanese, most job opportunities, convenient lifestyle.</li>
                <li><strong>Cons:</strong> High rent, crowded trains, expensive.</li>
                <li><strong>Recommended for:</strong> University advancement, Career seekers.</li>
            </ul>

            <h2>2. Osaka (The Kitchen of Japan)</h2>
            <ul>
                <li><strong>Pros:</strong> Cheaper rent than Tokyo, friendly people, great food culture.</li>
                <li><strong>Cons:</strong> Strong dialect (Kansai-ben). You might pick up the accent.</li>
                <li><strong>Recommended for:</strong> Those who want a lively atmosphere and lower costs.</li>
            </ul>

            <h2>3. Fukuoka / Rural Areas</h2>
            <ul>
                <li><strong>Pros:</strong> Very low cost of living (rent is half of Tokyo), relaxed pace, close to Korea/China.</li>
                <li><strong>Cons:</strong> Fewer part-time jobs, lower hourly wages.</li>
                <li><strong>Recommended for:</strong> Budget students, those who prefer a quiet life.</li>
            </ul>
        """,
        "body_ko": """
            <p>지역에 따라 사투리, 생활비, 분위기가 완전히 다릅니다.</p>

            <h2>1. 도쿄 (수도)</h2>
            <ul>
                <li><strong>장점:</strong> 표준어 사용, 압도적인 일자리와 정보, 편리한 생활.</li>
                <li><strong>단점:</strong> 비싼 월세와 물가, 복잡한 전철.</li>
                <li><strong>추천:</strong> 대학 진학이나 취업이 목표인 분.</li>
            </ul>

            <h2>2. 오사카 (제2의 도시)</h2>
            <ul>
                <li><strong>장점:</strong> 도쿄보다 저렴한 물가, 정이 많고 활기찬 분위기.</li>
                <li><strong>단점:</strong> 사투리(관서벤)가 강해 억양이 섞일 수 있습니다.</li>
                <li><strong>추천:</strong> 생활비를 아끼면서 즐겁게 생활하고 싶은 분.</li>
            </ul>

            <h2>3. 후쿠오카 및 지방</h2>
            <ul>
                <li><strong>장점:</strong> 물가가 매우 저렴합니다(월세가 도쿄 절반). 여유로운 생활이 가능합니다.</li>
                <li><strong>단점:</strong> 알바 자리가 상대적으로 적고 시급이 낮습니다.</li>
                <li><strong>추천:</strong> 저예산 유학, 조용한 환경을 선호하는 분.</li>
            </ul>
        """
    }
]

# 파일 생성 루프
for article in articles:
    file_path = os.path.join(OUTPUT_DIR, f"{article['filename']}.html")
    
    # HTML 내용 조립
    html_content = TEMPLATE.format(
        cat_en=article['cat_en'], cat_ko=article['cat_ko'],
        title_en=article['title_en'], title_ko=article['title_ko'],
        desc_en=article.get('desc_en', ''),
        body_en=article['body_en'], body_ko=article['body_ko'],
        date=today
    )
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Created: {file_path}")

print("\n🎉 Multi-language Guide Pages Created!")