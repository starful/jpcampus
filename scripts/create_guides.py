import os
import datetime

# 저장될 디렉토리
OUTPUT_DIR = "app/templates/guides"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 현재 날짜 (업데이트 날짜용)
today = datetime.date.today().strftime("%Y년 %m月 %d日")

# HTML 템플릿 (가독성 강화 디자인)
TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - JP Campus 일본 유학 가이드</title>
    <meta name="description" content="{desc}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        /* 읽기 좋은 긴 글 스타일 */
        .article-container {{ max-width: 860px; margin: 40px auto; padding: 0 20px; background: #fff; }}
        
        .article-header {{ text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); border-radius: 16px; margin-bottom: 40px; }}
        .article-category {{ color: #3498db; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem; }}
        .article-title {{ font-size: 2.2rem; color: #2c3e50; margin: 15px 0; line-height: 1.3; word-break: keep-all; }}
        .article-meta {{ color: #7f8c8d; font-size: 0.9rem; }}
        
        .article-body {{ font-size: 1.1rem; line-height: 1.9; color: #333; }}
        .article-body h2 {{ font-size: 1.6rem; color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-top: 60px; margin-bottom: 25px; }}
        .article-body h3 {{ font-size: 1.3rem; color: #2980b9; margin-top: 40px; margin-bottom: 15px; border-left: 5px solid #2980b9; padding-left: 15px; }}
        .article-body p {{ margin-bottom: 20px; text-align: justify; }}
        
        /* 리스트 스타일 */
        .article-body ul, .article-body ol {{ margin-bottom: 30px; padding-left: 20px; background: #f9f9f9; padding: 20px 20px 20px 40px; border-radius: 8px; }}
        .article-body li {{ margin-bottom: 10px; }}
        
        /* 테이블 스타일 */
        .data-table {{ width: 100%; border-collapse: collapse; margin: 30px 0; font-size: 0.95rem; }}
        .data-table th {{ background: #2c3e50; color: #fff; padding: 12px; text-align: left; }}
        .data-table td {{ border: 1px solid #ddd; padding: 12px; }}
        .data-table tr:nth-child(even) {{ background-color: #f2f2f2; }}

        /* 강조 박스 */
        .highlight-box {{ background-color: #e8f4f8; border: 2px solid #3498db; border-radius: 10px; padding: 25px; margin: 30px 0; }}
        .highlight-title {{ font-weight: bold; color: #2980b9; font-size: 1.1rem; margin-bottom: 10px; display: block; }}

        /* FAQ 섹션 */
        .faq-box {{ background: #fff8e1; border: 1px solid #ffe082; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .faq-q {{ font-weight: bold; color: #f57c00; margin-bottom: 10px; display: block; }}
        
        /* 버튼 */
        .btn-area {{ text-align: center; margin-top: 80px; padding: 40px 0; border-top: 1px solid #eee; }}
        .cta-button {{ display: inline-block; background: #3498db; color: white; padding: 15px 40px; border-radius: 50px; font-weight: bold; text-decoration: none; transition: 0.3s; box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3); }}
        .cta-button:hover {{ background: #2980b9; transform: translateY(-3px); }}
    </style>
</head>
<body>
    <header class="main-header" style="padding: 15px 0; background: #fff; border-bottom: 1px solid #eee;">
        <div style="text-align: center;">
            <a href="/" style="font-size: 1.5rem; font-weight: bold; color: #333; text-decoration: none;">JP Campus</a>
        </div>
    </header>

    <article class="article-container">
        <header class="article-header">
            <span class="article-category">{category}</span>
            <h1 class="article-title">{title}</h1>
            <div class="article-meta">최종 업데이트: {date} · JP Campus 편집부</div>
        </header>

        <div class="article-body">
            {content}
        </div>

        <div class="btn-area">
            <h3>나에게 딱 맞는 학교를 찾고 싶다면?</h3>
            <p>위치, 학비, 국적 비율 데이터를 기반으로 최적의 학교를 추천해드립니다.</p>
            <br>
            <a href="/" class="cta-button">🏫 학교 검색하러 가기</a>
            <br><br>
            <a href="/guide" style="color:#999; text-decoration:underline;">목록으로 돌아가기</a>
        </div>
    </article>

    <footer class="main-footer">
        <p class="copyright">© 2024 JP Campus. All rights reserved.</p>
    </footer>
</body>
</html>
"""

# ==========================================
# [콘텐츠 데이터] - 내용을 대폭 보강함
# ==========================================
articles = [
    {
        "filename": "cost",
        "title": "💰 일본 어학연수 1년 비용 완벽 분석 (학비, 생활비, 숨은 비용)",
        "category": "비용/예산",
        "desc": "일본 유학 1년 비용은 얼마일까요? 도쿄 기준 학비, 기숙사, 생활비부터 숨겨진 초기 비용까지 현실적인 예산을 엑셀처럼 꼼꼼하게 정리해드립니다.",
        "content": """
            <p>일본 유학을 준비하는 분들이 가장 먼저, 그리고 가장 심각하게 고민하는 부분이 바로 <strong>'비용'</strong>입니다. 인터넷에 검색해보면 "1,500만원이면 된다"부터 "3,000만원은 있어야 한다"까지 정보가 제각각이라 혼란스러우셨을 겁니다. 이는 개인의 소비 성향과 거주 지역(도쿄 vs 지방)에 따라 편차가 크기 때문입니다.</p>
            <p>JP Campus에서는 2024년 도쿄 물가를 기준으로, 숨겨진 비용 하나까지 놓치지 않고 <strong>가장 현실적인 1년 유학 비용</strong>을 분석해 드립니다. 이 글을 통해 구체적인 예산을 수립해 보세요.</p>

            <h2>1. 일본어학교 학비 (1년 기준)</h2>
            <p>학비는 학교마다, 코스마다 다르지만 도쿄 지역 학교들의 평균적인 비용은 다음과 같습니다. 최근 엔저 현상과 물가 상승으로 인해 학비가 조금씩 오르는 추세입니다.</p>
            
            <table class="data-table">
                <tr><th>항목</th><th>평균 비용 (엔)</th><th>비고</th></tr>
                <tr><td>선고료 (전형료)</td><td>20,000 ~ 30,000</td><td>원서 접수 시 1회 납부 (환불 불가)</td></tr>
                <tr><td>입학금</td><td>50,000 ~ 70,000</td><td>입학 첫 해만 납부</td></tr>
                <tr><td>수업료 (1년)</td><td>600,000 ~ 700,000</td><td>전기/후기 6개월 분납 가능한 학교 많음</td></tr>
                <tr><td>시설비/교재비</td><td>40,000 ~ 80,000</td><td>냉난방비, 프린트물 등 포함</td></tr>
                <tr><td><strong>총 합계</strong></td><td><strong>약 75만엔 ~ 85만엔</strong></td><td><strong>한화 약 700~800만원</strong></td></tr>
            </table>
            
            <div class="highlight-box">
                <span class="highlight-title">💡 학비를 아끼는 꿀팁</span>
                <ul>
                    <li><strong>준비교육과정 여부 확인:</strong> 대학 진학이 목표가 아니라면, 상대적으로 저렴한 일반 회화 중심 학교를 선택하세요.</li>
                    <li><strong>장학금 제도:</strong> 입학 전 JLPT N1/N2 소지자에게 입학금을 면제해주거나, 수업료를 10% 감면해주는 학교가 많습니다. JP Campus 검색 필터에서 '장학금'을 확인하세요.</li>
                    <li><strong>지역 변경:</strong> 도쿄보다 오사카나 후쿠오카, 지방 도시의 학교는 연간 학비가 10~15만엔 정도 저렴할 수 있습니다.</li>
                </ul>
            </div>

            <h2>2. 주거비 (가장 큰 변수)</h2>
            <p>어디에 사느냐에 따라 1년 예산이 500만원 이상 차이가 날 수 있습니다. 초기 정착 비용까지 고려해야 합니다.</p>

            <h3>(1) 학교 기숙사 (2인실 기준)</h3>
            <p>가장 일반적인 선택입니다. 학교에서 관리하므로 안전하고, 입주 심사가 없어 편리합니다. 보통 3개월 치를 선납합니다.</p>
            <ul>
                <li>입실료(예치금): 3~5만엔</li>
                <li>월세(광열비 포함): 4~5만엔</li>
                <li><strong>1년 예상 비용: 약 60만엔</strong></li>
            </ul>

            <h3>(2) 사설 쉐어하우스</h3>
            <p>외국인들과 교류하고 싶다면 추천합니다. 보증금이 없고 최소 계약 기간이 짧은 편입니다.</p>
            <ul>
                <li>월세+관리비: 5~7만엔</li>
                <li><strong>1년 예상 비용: 약 80만엔</strong></li>
            </ul>

            <h3>(3) 원룸 자취 (임대)</h3>
            <p>초기 비용(시키킹, 레이킹, 보증회사, 화재보험, 가구 구매 등)이 월세의 3~4배가 들어갑니다. 유학 초반에는 추천하지 않습니다.</p>
            <ul>
                <li>초기 비용: 20~30만엔</li>
                <li>월세: 6~8만엔 (도쿄 기준)</li>
                <li><strong>1년 예상 비용: 약 100~120만엔</strong></li>
            </ul>

            <h2>3. 생활비 (식비, 교통비, 통신비)</h2>
            <p>숨만 쉬어도 나가는 돈입니다. 개인차가 크지만, 평균적인 유학생의 지출 내역은 다음과 같습니다.</p>
            
            <ul>
                <li><strong>식비 (월 3~4만엔):</strong> 일본은 외식비가 비쌉니다(한 끼 800~1,200엔). 마트에서 장을 봐서 직접 해 먹는다면 월 3만엔으로도 충분하지만, 매끼 사 먹으면 6만엔도 부족합니다.</li>
                <li><strong>교통비 (월 5천~1만엔):</strong> 일본 전철비는 한국의 2배입니다. 집과 학교가 멀다면 교통비 부담이 큽니다. 다행히 유학생은 '통학 정기권'을 끊어 최대 50% 이상 할인을 받을 수 있습니다.</li>
                <li><strong>통신비 (월 3~5천엔):</strong> 메이저 통신사 대신 알뜰폰(격안심)이나 GTN모바일 등을 사용하면 데이터를 충분히 쓰면서도 비용을 아낄 수 있습니다.</li>
                <li><strong>국민건강보험료 (월 1~2천엔):</strong> 유학생은 소득이 없으므로 감면 신청 시 최저 요금만 냅니다.</li>
            </ul>

            <h2>4. 총정리: 1년 유학, 얼마가 필요할까?</h2>
            <p>가장 일반적인 <strong>[도쿄 사립 어학원 + 기숙사 2인실 + 적당한 자취]</strong> 패턴으로 계산해보겠습니다.</p>
            
            <table class="data-table">
                <tr><td>학비 (1년)</td><td>800,000엔</td></tr>
                <tr><td>주거비 (1년)</td><td>600,000엔</td></tr>
                <tr><td>생활비 (12개월)</td><td>600,000엔</td></tr>
                <tr><td>항공권 및 기타</td><td>100,000엔</td></tr>
                <tr><td><strong>총 합계</strong></td><td><strong>2,100,000엔 (약 1,900만원)</strong></td></tr>
            </table>

            <h2>5. 아르바이트로 충당 가능할까?</h2>
            <p>희소식은 일본은 유학생 아르바이트(주 28시간)가 합법이라는 점입니다. 도쿄 편의점 시급 1,113엔 기준으로 계산해보겠습니다.</p>
            <ul>
                <li><strong>월 수입:</strong> 1,113엔 × 28시간 × 4주 = <strong>약 124,000엔</strong></li>
                <li><strong>1년 수입:</strong> 약 148만엔</li>
            </ul>
            <p>즉, <strong>초기 6개월 정도의 자금(약 1,000만원)</strong>만 들고 가서 현지에서 아르바이트를 꾸준히 한다면, 나머지 생활비와 후반기 학비는 스스로 벌어서 충당하는 것이 충분히 가능합니다. 이것이 바로 일본 유학의 가장 큰 장점입니다.</p>

            <h3>자주 묻는 질문 (FAQ)</h3>
            <div class="faq-box">
                <span class="faq-q">Q. 초기 비용은 얼마나 환전해 가야 하나요?</span>
                <p>A. 기숙사비와 3개월 정도의 생활비를 포함해 최소 50~70만엔(약 500~700만원)은 현금이나 카드로 준비해 가시는 것이 안전합니다. 알바를 바로 구하지 못할 수도 있기 때문입니다.</p>
                
                <span class="faq-q">Q. 지방으로 가면 얼마나 저렴한가요?</span>
                <p>A. 학비는 큰 차이가 없으나, 월세가 도쿄의 절반 수준(3~4만엔에 1인실 가능)입니다. 전체 비용은 약 20~30% 절약됩니다.</p>
            </div>
        """
    },
    {
        "filename": "school-choice",
        "title": "🏫 실패 없는 일본어학교 선택 기준 5가지 (진학/취업/회화)",
        "category": "학교선택",
        "desc": "수백 개의 일본어학교 중 어디를 가야 할까요? 자신의 목적(진학, 취업, 회화)과 성향에 딱 맞는 학교를 고르는 5가지 핵심 기준을 제시합니다.",
        "content": """
            <p>일본 유학 준비의 시작이자 가장 중요한 단계는 바로 <strong>'학교 선택'</strong>입니다. 일본 법무성 고시교만 해도 800개가 넘습니다. "유학원이 추천해 주는 곳", "친구가 간 곳"을 무작정 따라갔다가는 1년 내내 후회할 수 있습니다.</p>
            <p>학교마다 커리큘럼, 분위기, 국적 비율이 천차만별이기 때문입니다. 나에게 맞는 학교를 고르는 5가지 절대 기준을 알려드립니다.</p>

            <h2>1. '목적'에 맞는 커리큘럼인가?</h2>
            <p>가장 먼저 스스로에게 물어보세요. "나는 왜 일본어를 배우러 가는가?"</p>
            
            <h3>(1) 대학/대학원 진학형</h3>
            <p>일본 명문대 진학이 목표라면, 단순히 일본어만 가르치는 곳은 피해야 합니다. <strong>'준비교육과정'</strong>이 설치되어 있거나, EJU(일본유학시험) 대책 수업, 소논문 지도, 면접 대비가 체계적인 '진학 특화 학교'를 골라야 합니다.</p>
            
            <h3>(2) 일본 취업형</h3>
            <p>IT 기업이나 호텔 등 일본 현지 취업을 원한다면 <strong>'비즈니스 일본어 클래스'</strong>가 있는지 확인하세요. 이력서 첨삭, 모의 면접, 기업 매칭 서비스를 제공하는 학교가 유리합니다.</p>
            
            <h3>(3) 회화 및 문화체험형</h3>
            <p>스펙보다는 경험과 회화 실력 향상이 목적이라면, 교실에 앉아 문법만 파는 스파르타식 학교는 맞지 않습니다. 회화 위주의 수업, 다양한 과외 활동(디즈니랜드, 기모노 체험 등)이 많은 학교를 선택하세요.</p>

            <h2>2. 국적 비율: 한자권 vs 비한자권</h2>
            <p>학교 분위기를 좌우하는 가장 큰 요소입니다. JP Campus 지도 데이터의 '국적 비율'을 꼭 확인하세요.</p>
            
            <table class="data-table">
                <tr><th>구분</th><th>특징</th><th>장점</th><th>단점</th></tr>
                <tr><td><strong>중국/한자권 위주</strong></td><td>진학 실적 중심, 스파르타</td><td>한자 학습 속도가 빠름, 상위권 대학 진학률 높음</td><td>한국인과 중국인은 한자를 알아서 진도가 빠르지만 회화 기회는 적을 수 있음</td></tr>
                <tr><td><strong>서양/다국적 위주</strong></td><td>회화 중심, 자유분방</td><td>다양한 문화 교류, 일본어로 대화할 기회가 많음</td><td>한자 수업 진도가 느림, 진학 분위기는 약할 수 있음</td></tr>
            </table>

            <h2>3. 위치와 주변 환경 (도심 vs 주택가)</h2>
            <p>매일 통학해야 하는 곳입니다. 자신이 어떤 환경을 선호하는지 파악하세요.</p>
            <ul>
                <li><strong>도심(신주쿠, 시부야 등):</strong> 교통이 편리하고 아르바이트 구하기가 매우 쉽습니다. 하지만 물가가 비싸고 유혹(?)이 많아 공부에 방해될 수 있습니다.</li>
                <li><strong>주택가(다카다노바바, 나카노 등):</strong> 조용하고 면학 분위기가 좋습니다. 월세가 상대적으로 저렴합니다.</li>
            </ul>

            <h2>4. 학교의 규모 (대형 vs 소형)</h2>
            <ul>
                <li><strong>대규모 학교 (500명 이상):</strong> 레벨이 10단계 이상으로 세분화되어 있어 내 실력에 딱 맞는 반에 들어갈 수 있습니다. 시스템이 체계적입니다.</li>
                <li><strong>소규모 학교 (200명 이하):</strong> 선생님이 학생 이름을 다 외울 정도로 가족 같은 분위기입니다. 결석이나 생활 문제 등을 꼼꼼하게 케어해 줍니다.</li>
            </ul>

            <h2>5. 한국인 스태프 상주 여부</h2>
            <p>일본어가 서툰 초기에는 비자 갱신, 병원 방문, 통장 개설 등에서 도움이 절실합니다. 한국인 직원이 상주하는 학교는 이런 행정 처리를 모국어로 도와주므로 심리적으로 매우 든든합니다.</p>

            <div class="highlight-box">
                <span class="highlight-title">JP Campus 활용 팁</span>
                <p>JP Campus의 지도 검색 필터에서 <strong>[국적: 서양권 많음]</strong>, <strong>[특화: 비즈니스]</strong>, <strong>[규모: 소수정예]</strong> 등을 조합하여 검색해보세요. 수백 개의 학교 중 내 조건에 맞는 곳만 쏙 골라낼 수 있습니다.</p>
            </div>
        """
    },
    {
        "filename": "visa",
        "title": "✈️ 일본 유학 비자(COE) 신청 절차 A to Z (서류 준비부터 발급까지)",
        "category": "비자/서류",
        "desc": "일본 유학 비자 준비, 너무 복잡하죠? 학교 원서 접수부터 재류자격인정증명서(COE) 발급, 영사관 사증 신청까지의 모든 과정을 알기 쉽게 정리했습니다.",
        "content": """
            <p>일본어학교 입학이 결정되었다면 이제 가장 중요한 관문, <strong>'비자(VISA)'</strong>가 남았습니다. 일본 유학 비자는 서류 심사가 꼼꼼하기로 유명하여, 사소한 실수로 불합격되는 경우도 종종 발생합니다.</p>
            <p>입학 시기별 준비 일정과 필수 서류, 그리고 주의사항을 단계별로 완벽하게 정리해 드립니다.</p>

            <h2>1. 비자 수속 타임라인 (4월 학기 기준)</h2>
            <p>일본 유학은 보통 입학 <strong>6개월 전</strong>부터 준비를 시작해야 여유롭습니다.</p>
            <ul>
                <li><strong>전년도 9월~11월:</strong> 학교 선정 및 원서 접수 (학교별 마감일 주의)</li>
                <li><strong>11월 말:</strong> 학교에서 일본 입국관리국(뉴칸)에 서류 일괄 제출</li>
                <li><strong>12월~2월:</strong> 입국관리국 심사 기간 (약 2~3개월 소요)</li>
                <li><strong>2월 말:</strong> <strong>재류자격인정증명서(COE)</strong> 결과 발표 및 발급</li>
                <li><strong>3월 초:</strong> 학비 납부 및 COE 수령</li>
                <li><strong>3월 중순:</strong> 주한 일본 대사관(영사관)에 비자 사증 신청</li>
                <li><strong>3월 말:</strong> 비자 발급 및 일본 출국!</li>
            </ul>

            <h2>2. 가장 중요한 서류: COE 신청 준비물</h2>
            <p>비자 심사의 핵심은 <strong>"이 학생이 공부할 의지가 있는가?"</strong>와 <strong>"학비를 낼 돈이 있는가?"</strong> 두 가지입니다. 이를 증명하기 위해 다음 서류들이 필요합니다.</p>

            <h3>(1) 본인 관련 서류</h3>
            <ul>
                <li>입학원서 및 이력서 (학교 양식)</li>
                <li>최종학교 졸업증명서 (또는 졸업예정증명서)</li>
                <li>최종학교 성적증명서</li>
                <li>일본어 학습 증명서 (JLPT 합격증 또는 150시간 이상 수강 증명서)</li>
                <li>여권 복사본 및 증명사진</li>
            </ul>

            <h3>(2) 보증인(경비지변자) 관련 서류 - 보통 부모님</h3>
            <ul>
                <li><strong>은행 잔고증명서:</strong> 가장 중요합니다. 보통 <strong>3,000만원~4,000만원</strong> 이상의 잔고가 예치되어 있어야 합니다. (유학 기간 동안의 학비와 생활비를 감당할 수 있음을 증명)</li>
                <li>재직증명서 또는 사업자등록증명원</li>
                <li>소득금액증명원 (최근 1년 또는 3년치)</li>
                <li>가족관계증명서 (학생과 보증인의 관계 입증)</li>
            </ul>

            <h2>3. 대사관 비자 신청 (마지막 단계)</h2>
            <p>입국관리국 심사를 통과하여 COE(재류자격인정증명서)를 받았다면, 사실상 비자는 99% 나온 셈입니다. 이제 한국에 있는 일본 영사관에 가서 여권에 비자 스티커를 붙이는 절차만 남았습니다.</p>
            <ul>
                <li><strong>준비물:</strong> 여권, 사증신청서, 사진 1매, COE 원본(또는 사본), 주민등록등본</li>
                <li><strong>신청 장소:</strong> 거주지 관할 일본 총영사관 (서울, 부산, 제주) 또는 지정 여행사 대행</li>
                <li><strong>소요 기간:</strong> 보통 접수 다음 날 또는 2~3일 내 발급</li>
            </ul>

            <h2>4. 비자 심사 탈락(불교부)의 주된 원인</h2>
            <div class="highlight-box">
                <span class="highlight-title">⚠️ 주의하세요!</span>
                <ul>
                    <li><strong>이력서의 공백:</strong> 고등학교/대학교 졸업 후 5년 이상 특별한 소속 없이 공백기가 길다면 '유학 이유서'를 아주 구체적으로 잘 써야 합니다.</li>
                    <li><strong>과거 불법체류 이력:</strong> 일본뿐만 아니라 다른 나라에서의 오버스테이 기록도 문제가 될 수 있습니다.</li>
                    <li><strong>자금 능력 부족:</strong> 통장 잔고가 부족하거나, 보증인의 소득이 너무 낮게 신고되어 있는 경우입니다.</li>
                </ul>
            </div>
        """
    },
    {
        "filename": "housing",
        "title": "🏠 일본 기숙사 vs 쉐어하우스 vs 원룸 (장단점 및 비용 비교)",
        "category": "숙소/생활",
        "desc": "일본 유학 숙소, 어디가 좋을까? 학교 기숙사의 편리함, 쉐어하우스의 교류, 원룸의 자유로움. 각 주거 형태별 장단점과 초기 비용을 비교해 드립니다.",
        "content": """
            <p>일본 유학 준비에서 학교 선택만큼이나 골치 아픈 것이 바로 <strong>'집 구하기'</strong>입니다. 일본은 한국과 주거 문화가 다르고, 외국인이 집을 구하는 절차가 까다로운 편입니다. </p>
            <p>유학생들이 주로 선택하는 3가지 주거 형태인 <strong>학교 기숙사, 사설 쉐어하우스, 일반 임대(원룸)</strong>의 특징과 비용을 비교해 드릴 테니, 본인의 성향에 맞는 곳을 골라보세요.</p>

            <h2>1. 학교 기숙사 (School Dormitory)</h2>
            <p>대부분의 유학생이 입국 후 첫 3~6개월 동안 지내는 곳입니다. 학교 건물이거나 학교가 제휴한 맨션입니다.</p>
            <ul>
                <li><strong>장점:</strong> 학교와 가깝거나 통학이 편리한 곳에 위치합니다. 냉장고, 세탁기, 침대 등 가전가구가 완비되어 있어 몸만 들어가면 됩니다. 입주 절차가 가장 간편합니다.</li>
                <li><strong>단점:</strong> 1인실은 드물고 비싸며, 대부분 2인실~4인실입니다. 룸메이트와 생활 패턴이 안 맞으면 힘들 수 있습니다. 통금 시간 등 규칙이 있을 수 있습니다.</li>
                <li><strong>비용 (도쿄 2인실 기준):</strong> 월 4~5만엔 (초기 비용 약 15~20만엔)</li>
            </ul>

            <h2>2. 쉐어하우스 (Share House)</h2>
            <p>개인 방은 따로 쓰고 거실, 주방, 화장실, 욕실을 공유하는 형태입니다. 일본인과 외국인이 섞여 사는 곳이 많습니다.</p>
            <ul>
                <li><strong>장점:</strong> 보증금/사례금 등 초기 비용이 저렴합니다. 다양한 국적의 친구를 사귈 수 있어 회화 실력이 빨리 늡니다. 단기 계약(1개월~)이 가능한 곳이 많습니다.</li>
                <li><strong>단점:</strong> 공용 공간 청소 문제나 소음으로 인한 트러블이 생길 수 있습니다. 방음이 약한 건물이 많습니다.</li>
                <li><strong>비용:</strong> 월 5~8만엔 (위치와 시설에 따라 천차만별)</li>
            </ul>

            <h2>3. 일반 원룸 임대 (Private Apartment)</h2>
            <p>부동산을 통해 일본의 일반 맨션이나 아파트를 계약하는 것입니다. 보통 유학 생활에 적응한 6개월~1년 차 이후에 많이 이사합니다.</p>
            <ul>
                <li><strong>장점:</strong> 완벽한 사생활이 보장됩니다. 내가 원하는 인테리어로 집을 꾸밀 수 있습니다. 친구를 초대하기 자유롭습니다.</li>
                <li><strong>단점:</strong> <strong>초기 비용이 매우 비쌉니다.</strong> (시키킹, 레이킹, 보증회사비, 중개수수료, 화재보험료, 열쇠교환비 등 월세의 3~5배). 가전제품과 가구를 모두 직접 사야 합니다. 외국인 입주를 거절하는 집주인이 많습니다.</li>
                <li><strong>비용:</strong> 월 6~9만엔 + 공과금 별도 (초기 비용 30~40만엔)</li>
            </ul>

            <h2>4. 한눈에 보는 비교표</h2>
            <table class="data-table">
                <tr><th>구분</th><th>기숙사</th><th>쉐어하우스</th><th>원룸 자취</th></tr>
                <tr><td><strong>초기비용</strong></td><td>보통</td><td>저렴함</td><td>매우 비쌈</td></tr>
                <tr><td><strong>사생활</strong></td><td>낮음 (2인실)</td><td>중간 (개인실)</td><td>높음</td></tr>
                <tr><td><strong>가구/가전</strong></td><td>완비</td><td>완비</td><td>없음 (구매 필요)</td></tr>
                <tr><td><strong>일본어 향상</strong></td><td>보통</td><td>좋음 (교류 많음)</td><td>낮음 (혼자 지냄)</td></tr>
                <tr><td><strong>입주 난이도</strong></td><td>쉬움</td><td>쉬움</td><td>어려움 (심사 필요)</td></tr>
            </table>

            <div class="highlight-box">
                <span class="highlight-title">JP Campus 에디터의 추천</span>
                <p>처음 일본에 갈 때는 짐도 많고 지리도 낯설기 때문에 <strong>'학교 기숙사'</strong>나 <strong>'관리형 쉐어하우스'</strong>에서 3개월 정도 살아보는 것을 추천합니다. 그동안 일본 생활에 적응하고, 직접 발품을 팔아 마음에 드는 동네의 원룸을 구해 이사하는 것이 실패 확률을 줄이는 방법입니다.</p>
            </div>
        """
    },
    {
        "filename": "part-time",
        "title": "🍔 일본 유학 아르바이트: 구하는 법, 시급, 추천 직종",
        "category": "생활/알바",
        "desc": "일본 유학의 꽃, 아르바이트! 자격외활동허가서 발급부터 면접 꿀팁, 일본어 레벨별 추천 알바와 평균 시급까지 현실적인 정보를 알려드립니다.",
        "content": """
            <p>일본 유학 생활의 큰 즐거움이자 경제적 버팀목이 되는 것이 바로 <strong>'아르바이트(バイト, 바이토)'</strong>입니다. 일본은 유학생의 아르바이트 활동을 법적으로 폭넓게 보장하는 나라입니다.</p>
            <p>생활비도 벌고, 일본어 실력도 획기적으로 늘릴 수 있는 알바 구하기의 모든 것을 정리했습니다.</p>

            <h2>1. 알바 전 필수 준비물: 자격외활동허가서</h2>
            <p>유학 비자는 공부를 위한 비자이므로, 원칙적으로 취업 활동이 금지되어 있습니다. 일을 하려면 반드시 <strong>'자격외활동허가'</strong>를 받아야 합니다.</p>
            <ul>
                <li><strong>신청 방법:</strong> 일본 공항 입국 심사대에서 '자격외활동허가신청서'를 제출하면, 재류카드 뒷면에 허가 도장을 찍어줍니다. (입국 후 나중에 뉴칸에 가서 신청하려면 매우 번거로우니 꼭 공항에서 하세요!)</li>
                <li><strong>허용 시간:</strong> 주 28시간 이내 (단, 학교 방학 기간에는 하루 8시간, 주 40시간까지 가능)</li>
                <li><strong>금지 업종:</strong> 풍속업(파칭코, 마작, 바, 캬바쿠라 등 유흥업소) 및 관련 업무(청소, 전단지 배포 포함)는 절대 금지입니다. 적발 시 강제 추방될 수 있습니다.</li>
            </ul>

            <h2>2. 일본어 레벨별 추천 아르바이트</h2>
            <p>자신의 일본어 실력에 따라 할 수 있는 일의 종류가 달라집니다.</p>

            <h3>(1) 초급 (N4~N5 수준)</h3>
            <p>아직 말이 잘 안 통할 때입니다. 손님을 직접 응대하지 않는 업무 위주입니다.</p>
            <ul>
                <li><strong>주방 보조(설거지, 재료 손질):</strong> 몸은 힘들지만 식사(마카나이)를 제공해주는 곳이 많아 식비를 아낄 수 있습니다.</li>
                <li><strong>호텔 객실 청소:</strong> 묵묵히 일만 하면 됩니다.</li>
                <li><strong>공장 라인 작업, 신문 배달, 택배 상하차:</strong> 체력이 필요합니다.</li>
            </ul>

            <h3>(2) 중급 (N3~N2 수준)</h3>
            <p>간단한 의사소통이 가능해지면 선택지가 넓어집니다.</p>
            <ul>
                <li><strong>편의점:</strong> 일본 유학 알바의 정석. 계산, 물건 진열, 택배 접수 등 업무가 다양해서 일본어가 많이 듭니다.</li>
                <li><strong>슈퍼마켓 캐셔:</strong> 정해진 멘트 위주로 사용하므로 익숙해지면 편합니다.</li>
                <li><strong>패밀리 레스토랑 홀 서빙:</strong> 메뉴 주문받기 등 접객 용어(경어)를 배울 수 있습니다.</li>
            </ul>

            <h3>(3) 고급 (N1 이상)</h3>
            <p>일본인과 대등하게 일할 수 있는 수준입니다.</p>
            <ul>
                <li><strong>카페 (스타벅스 등):</strong> 유학생들의 로망. 높은 회화 실력과 서비스 마인드가 필요합니다.</li>
                <li><strong>의류 매장, 드러그스토어 판매원:</strong> 적극적인 접객이 필요합니다.</li>
                <li><strong>호텔 프론트, 사무 보조, 통번역:</strong> 시급이 높고 취업 스펙으로도 활용 가능합니다.</li>
            </ul>

            <h2>3. 시급과 수입은 얼마나 될까?</h2>
            <p>2024년 기준, 도쿄의 최저시급은 <strong>1,113엔</strong>입니다. 오사카는 약 1,064엔입니다. 보통 도심 식당이나 편의점은 1,150엔~1,300엔 정도를 줍니다.</p>
            <p><strong>[수입 예시]</strong> 시급 1,200엔 × 주 28시간 × 4주 = <strong>월 134,400엔</strong><br>
            이 정도면 월세와 생활비를 내고도 약간의 용돈이 남는 금액입니다. 밤 10시 이후 야간 수당(25% 할증)을 챙기면 더 벌 수도 있습니다.</p>

            <h2>4. 알바 구하는 방법</h2>
            <ul>
                <li><strong>타운워크(Townwork), 바이토루 등 앱 활용:</strong> 가장 일반적인 방법입니다. '유학생 환영(留学生歓迎)' 필터를 걸고 검색하세요.</li>
                <li><strong>가게 앞 채용 포스터:</strong> 집 근처 가게에 붙은 모집 공고를 보고 직접 전화하거나 방문해서 문의하는 것도 합격률이 높습니다.</li>
                <li><strong>지인 소개:</strong> 이미 일하고 있는 친구의 소개로 들어가면 면접 통과가 쉽습니다.</li>
            </ul>
        """
    },
    {
        "filename": "eju-jlpt",
        "title": "📚 EJU vs JLPT: 나에게 필요한 일본어 시험은?",
        "category": "시험/진학",
        "desc": "일본 유학의 필수 스펙, EJU와 JLPT의 차이점을 명쾌하게 비교해 드립니다. 대학 진학이 목표라면 무엇부터 준비해야 할까요?",
        "content": """
            <p>일본 유학을 준비하는 학생이라면 누구나 한 번쯤 고민하는 문제입니다. "JLPT N1을 따야 할까, 아니면 EJU 점수를 올려야 할까?" 결론부터 말씀드리면, <strong>여러분의 유학 '목적'에 따라 준비해야 할 시험은 완전히 다릅니다.</strong></p>

            <h2>1. JLPT (일본어능력시험)</h2>
            <p>전 세계적으로 가장 널리 알려진 일본어 자격증 시험입니다.</p>
            <ul>
                <li><strong>성격:</strong> 일본어 어휘, 문법, 독해, 청해 능력을 종합적으로 측정하여 합격/불합격을 판정합니다. (N1~N5 등급)</li>
                <li><strong>시기:</strong> 매년 7월, 12월 (연 2회)</li>
                <li><strong>필요한 사람:</strong>
                    <ul>
                        <li>일본 기업 <strong>취업</strong>을 희망하는 사람 (보통 N2 이상 필수, N1 우대)</li>
                        <li><strong>전문학교</strong> 입학 희망자 (N2 이상 있으면 일본어 시험 면제되는 곳 많음)</li>
                        <li>대학원 진학 희망자 (일부 연구과는 JLPT 성적만 보기도 함)</li>
                        <li>아르바이트를 구하고 싶은 유학생 (이력서 스펙용)</li>
                    </ul>
                </li>
            </ul>

            <h2>2. EJU (일본유학시험)</h2>
            <p>일본의 대학(학부)에 외국인 유학생 전형으로 입학하기 위해 치르는 시험입니다. 한국의 '수능'과 비슷합니다.</p>
            <ul>
                <li><strong>성격:</strong> 일본 대학에서 학업을 수행할 수 있는 기초 학력을 평가합니다. 합격/불합격이 아니라 '점수'로 나옵니다.</li>
                <li><strong>시기:</strong> 매년 6월, 11월 (연 2회)</li>
                <li><strong>과목:</strong>
                    <ul>
                        <li><strong>일본어:</strong> 독해, 청독해, 청해, 기술(작문). JLPT보다 속독과 학술적 내용 이해가 중요합니다.</li>
                        <li><strong>종합과목(문과) / 이과(물,화,생):</strong> 한국의 사회탐구/과학탐구와 비슷합니다.</li>
                        <li><strong>수학:</strong> 코스1(문과), 코스2(이과)로 나뉩니다.</li>
                    </ul>
                </li>
                <li><strong>필요한 사람:</strong> 일본의 <strong>4년제 국공립 및 사립 대학</strong>에 진학하려는 학생</li>
            </ul>

            <h2>3. JLPT와 EJU의 결정적 차이</h2>
            <table class="data-table">
                <tr><th>구분</th><th>JLPT</th><th>EJU</th></tr>
                <tr><td><strong>평가 방식</strong></td><td>문법, 어휘 지식 중심</td><td>정보 처리 능력, 논리적 사고 중심</td></tr>
                <tr><td><strong>문제 유형</strong></td><td>4지 선다형</td><td>4지 선다 + 서술형(기술)</td></tr>
                <tr><td><strong>활용처</strong></td><td>취업, 알바, 전문학교</td><td>대학 입시 (필수)</td></tr>
                <tr><td><strong>유효 기간</strong></td><td>평생</td><td>2년 (입시 기준)</td></tr>
            </table>

            <h2>4. 전략적 준비 방법</h2>
            <div class="highlight-box">
                <span class="highlight-title">🎯 목표별 로드맵</span>
                <ul>
                    <li><strong>명문대 진학이 목표라면:</strong> JLPT 공부는 과감히 접어두고 <strong>EJU 고득점</strong>에 올인해야 합니다. 상위권 대학은 EJU 일본어 300점 후반대 + 영어(TOEFL) + 본고사/면접 싸움입니다. JLPT N1이 있어도 EJU 점수가 낮으면 대학에 못 갑니다.</li>
                    <li><strong>전문학교나 미대, 취업이 목표라면:</strong> EJU보다는 <strong>JLPT N2~N1</strong> 취득이 우선입니다. 특히 전문학교는 JLPT N2 합격증만 있으면 일본어 필기시험을 면제해주는 경우가 대부분입니다.</li>
                </ul>
            </div>
        """
    },
    {
        "filename": "preparation",
        "title": "🧳 일본 유학 출국 전 필수 체크리스트 (짐 싸기 꿀팁)",
        "category": "출국준비",
        "desc": "일본으로 떠나기 전 캐리어에 무엇을 넣어야 할까요? 도장, 돼지코, 상비약 등 한국에서 꼭 챙겨가야 할 필수품과 현지에서 사도 되는 물건들을 정리했습니다.",
        "content": """
            <p>비자도 나왔고 비행기 표도 예매했다면, 이제 남은 건 <strong>짐 싸기</strong>입니다. "일본도 사람 사는 곳인데 다 있겠지"라고 방심했다가는 도착 첫날부터 당황할 수 있습니다. 반대로, 너무 바리바리 싸 들고 가서 짐만 되는 경우도 있죠.</p>
            <p>일본 유학 선배들이 입을 모아 추천하는 '한국에서 꼭 챙겨가야 할 필수템' 리스트를 공개합니다.</p>

            <h2>1. 절대 없으면 안 되는 필수품</h2>
            <ul>
                <li><strong>도장 (인감/막도장):</strong> 일본은 여전히 '도장 문화'입니다. 서명(사인)으로 대체 안 되는 경우가 많습니다.
                    <ul>
                        <li><strong>한자 성(姓) 도장:</strong> 택배 수령, 출석 확인용 (막도장)</li>
                        <li><strong>한자 풀네임 도장:</strong> 통장 개설, 집 계약용 (인감도장 스타일)</li>
                    </ul>
                </li>
                <li><strong>돼지코 (110v 변환 어댑터):</strong> 일본 전압은 110v입니다. 다이소에서 파는 500원짜리 돼지코를 5~6개 넉넉히 챙기세요. 한국 멀티탭을 가져가서 돼지코 하나 끼워 쓰면 편리합니다.</li>
                <li><strong>증명사진 (다양한 사이즈):</strong> 일본의 즉석 증명사진기는 보정이 안 되어 사실적(?)으로 나옵니다. 알바 이력서나 서류 제출용으로 한국에서 예쁘게 찍은 사진을 넉넉히 인화해 가세요 (3x4cm, 4x3cm).</li>
                <li><strong>해외 결제 가능한 카드:</strong> 일본 통장을 만들기 전까지 쓸 생활비가 필요합니다. 수수료가 저렴한 트래블월렛, 트래블로그, 하나 비바 카드 등을 준비하세요. 현금도 5~10만엔 정도는 챙겨야 합니다.</li>
            </ul>

            <h2>2. 챙겨가면 삶의 질이 올라가는 물건</h2>
            <ul>
                <li><strong>상비약:</strong> 일본 약은 한국 약보다 성분이 순해서 잘 안 듣는다는 분들이 많습니다. 평소 먹는 두통약, 소화제, 감기약, 연고 등은 한국에서 사 가세요.</li>
                <li><strong>안경/렌즈 여분:</strong> 일본에서 안경을 맞추려면 비싸고 시력 검사 절차가 복잡할 수 있습니다.</li>
                <li><strong>양말/속옷/수건:</strong> 의외로 한국의 면 제품 퀄리티가 훨씬 좋습니다. 일본 수건은 얇고 잘 닳는 편입니다.</li>
                <li><strong>때수건:</strong> 일본에는 없습니다. 목욕을 좋아한다면 필수!</li>
            </ul>

            <h2>3. 굳이 안 가져가도 되는 것 (부피 줄이기)</h2>
            <ul>
                <li><strong>무거운 샴푸, 린스, 세제:</strong> 도착 당일 쓸 여행용 키트만 챙기세요. 나머지는 일본 드럭스토어에서 저렴하고 질 좋은 제품을 쉽게 살 수 있습니다.</li>
                <li><strong>너무 많은 옷:</strong> 유니클로, GU 등 저렴한 브랜드가 많습니다. 계절에 맞는 옷만 챙기고 나머지는 현지 조달하거나 나중에 택배로 받으세요.</li>
                <li><strong>한국 식품:</strong> 도쿄 신오쿠보나 오사카 츠루하시에 가면 한국 마트가 널려있습니다. 심지어 동네 슈퍼에서도 신라면과 김치는 팝니다. 무겁게 쌀이나 라면을 챙길 필요 없습니다.</li>
            </ul>

            <div class="highlight-box">
                <span class="highlight-title">🚨 기내 수하물(핸드캐리)로 챙길 서류</span>
                <p>다음 서류는 위탁 수하물(캐리어)에 넣지 말고, 반드시 가방에 넣어 기내에 들고 타세요. 일본 공항 입국 심사 때 제출해야 합니다.</p>
                <ul>
                    <li>여권 (비자 부착 확인)</li>
                    <li>COE (재류자격인정증명서) 원본</li>
                    <li>입학허가서</li>
                    <li>자격외활동허가신청서 (알바 하실 분 필수)</li>
                </ul>
            </div>
        """
    },
    {
        "filename": "mobile-bank",
        "title": "📱 일본 도착 후 행정 처리 3대장: 주소등록, 핸드폰, 통장",
        "category": "현지정착",
        "desc": "일본 공항 도착 후 14일 이내에 해야 할 필수 행정 절차! 구청 전입신고, 유심 개통, 유초은행 통장 개설 순서와 팁.",
        "content": """
            <p>일본 공항에 내려서 "와, 일본이다!"라고 감탄하는 것도 잠시. 유학생 앞에는 넘어야 할 행정 처리의 산이 기다리고 있습니다. 이 3가지를 해결하지 않으면 일본에서 정상적인 생활(알바, 월세 계약 등)을 할 수 없습니다.</p>
            <p>가장 효율적인 <strong>[주소 등록 -> 핸드폰 개통 -> 통장 개설]</strong> 순서대로 공략법을 알려드립니다.</p>

            <h2>STEP 1. 구청에서 주소 등록 (전입신고)</h2>
            <p>공항에서 재류카드를 받았다면, 14일 이내에 자신이 살 곳의 관할 구청(시청)에 가서 주소를 등록해야 합니다.</p>
            <ul>
                <li><strong>준비물:</strong> 재류카드, 여권</li>
                <li><strong>절차:</strong> 구청 '주민과'나 '이동신고' 창구에 가서 전입신고서(住民異動届)를 작성해 제출합니다. 처리가 완료되면 재류카드 뒷면에 주소를 인쇄해 줍니다.</li>
                <li><strong>주의:</strong> 이때 <strong>국민건강보험</strong> 가입도 함께 진행됩니다. 반드시 "학생이라 소득이 없다"고 말하고 보험료 감면 신청을 하세요.</li>
            </ul>

            <h2>STEP 2. 핸드폰 개통 (일본 번호 만들기)</h2>
            <p>주소가 적힌 재류카드가 있어야 핸드폰을 만들 수 있습니다. 그리고 핸드폰 번호가 있어야 통장을 만들 수 있습니다. 즉, 2번째 단계입니다.</p>
            <ul>
                <li><strong>메이저 통신사 (도코모, au, 소프트뱅크):</strong> 약정 기간(2년)이 길고 요금이 비쌉니다(월 7~8천엔). 신용카드가 없으면 가입이 까다로울 수 있습니다.</li>
                <li><strong>알뜰폰 (MVNO, 격안심):</strong> 유학생의 90%가 선택합니다. 라인모바일, Y모바일, UQ모바일, GTN모바일 등이 있습니다.</li>
                <li><strong>추천:</strong> 한국에서 미리 <strong>GTN 모바일</strong> 등을 신청해서 유심을 받아오거나, 빅카메라 같은 양판점에서 당일 개통 가능한 알뜰폰 유심을 계약하세요. (본인 명의 체크/신용카드 필요)</li>
            </ul>

            <h2>STEP 3. 통장 개설 (유초은행)</h2>
            <p>알바비를 받으려면 일본 은행 계좌가 필수입니다. 하지만 UFJ, 미쓰이스미토모 등 시중 은행은 "일본 체류 기간 6개월 미만"인 외국인에게 통장을 잘 만들어주지 않습니다.</p>
            <p>그래서 유학생들의 첫 통장은 99% <strong>'우체국 은행 (유초은행)'</strong>입니다.</p>
            <ul>
                <li><strong>준비물:</strong> 재류카드(주소 등록 완료), 도장(필수!), 학생증(또는 입학허가서), 일본 핸드폰 번호</li>
                <li><strong>특징:</strong> 입국 직후에도 개설 가능하며, 전국 어디에나 ATM이 있어 편리합니다.</li>
                <li><strong>팁:</strong> 창구에서 "알바비 수령용(Arubaito nokyuuryou uketori)"이라고 목적을 말하면 됩니다. 현금카드(캐시카드)는 즉시 발급되지 않고 1~2주 뒤 우편으로 집으로 날아옵니다.</li>
            </ul>

            <div class="highlight-box">
                <strong>💡 요약:</strong> 입국 다음 날 구청에 가서 [주소등록+건강보험] 해결 → 그 길로 빅카메라 가서 [핸드폰 개통] → 다음 날 우체국 가서 [통장 개설]. 이 순서대로 하면 이틀 만에 정착 완료입니다!
            </div>
        """
    },
    {
        "filename": "insurance",
        "title": "🏥 일본 국민건강보험료 폭탄 피하는 법 (감면 신청 필수)",
        "category": "의료/보험",
        "desc": "유학생도 건강보험료를 내야 할까? 신청 안 하면 손해 보는 보험료 감면 제도와 일본 병원 이용 시 주의사항.",
        "content": """
            <p>일본에 3개월 이상 체류하는 유학생은 의무적으로 <strong>'국민건강보험'</strong>에 가입해야 합니다. "난 튼튼해서 병원 안 갈 건데?"라고 해도 강제 가입입니다. 하지만 걱정하지 마세요. 유학생을 위한 강력한 혜택이 있습니다.</p>

            <h2>1. 보험료 감면 신청 (가장 중요!)</h2>
            <p>일본의 건강보험료는 전년도 소득을 기준으로 책정됩니다. 유학생은 일본에서의 소득이 '0원'이므로, 이를 신고하면 보험료를 대폭 깎아줍니다.</p>
            <ul>
                <li><strong>언제?</strong> 구청에서 주소 등록(전입신고)을 할 때 건강보험 창구로 안내받게 됩니다.</li>
                <li><strong>어떻게?</strong> 직원이 "작년 소득이 있습니까?"라고 물으면 "학생이고, 소득이 없습니다 (Gakusei desu. Shuunyuu ga arimasen)"라고 명확히 말하세요.</li>
                <li><strong>결과:</strong> 감면 신청서(간이신고서)를 작성하면, 지역에 따라 다르지만 보통 월 보험료가 <strong>약 1,000엔 ~ 2,000엔</strong> 수준으로 줄어듭니다. (원래는 월 5천엔 이상 나올 수 있음)</li>
            </ul>

            <h2>2. 병원 이용 혜택</h2>
            <p>매달 꼬박꼬박 보험료를 냈다면 혜택을 누려야죠. 일본 병원에 갈 때 <strong>건강보험증</strong>을 제시하면, 전체 의료비의 <strong>30%</strong>만 본인이 부담하면 됩니다. (70%는 국가 부담)</p>
            <ul>
                <li>감기로 내과 진료 + 약 처방: 약 1,500엔 ~ 2,000엔</li>
                <li>치과 스케일링, 충치 치료: 보험 적용 가능</li>
            </ul>
            <p>※ 단, 미용 목적의 피부과 시술이나 치아 교정 등은 보험이 안 됩니다.</p>

            <h2>3. 보험료 납부 방법</h2>
            <p>가입 후 1~2주 뒤에 집으로 보험료 고지서(납부서) 뭉치가 우편으로 옵니다. 이 종이를 들고 편의점 계산대에 가서 내면 됩니다. 귀찮다면 통장 자동이체를 신청할 수도 있습니다.</p>

            <h2>4. 귀국 시 주의사항</h2>
            <div class="highlight-box">
                <span class="highlight-title">🚨 꼭 탈퇴하고 가세요!</span>
                <p>유학을 마치고 한국으로 완전 귀국할 때는 반드시 구청에 가서 <strong>'국민건강보험 탈퇴'</strong> 신고를 하고, 출국일까지의 밀린 보험료를 정산해야 합니다.</p>
                <p>이걸 안 하고 그냥 귀국하면 보험료가 계속 연체되며, 나중에 일본에 여행이나 워홀로 재입국할 때 비자 발급이 거부되거나 입국 심사에서 문제가 될 수 있습니다.</p>
            </div>
        """
    },
    {
        "filename": "region",
        "title": "🌏 도쿄 vs 오사카 vs 지방, 나에게 맞는 유학 지역은?",
        "category": "지역정보",
        "desc": "표준어를 배우고 싶다면 도쿄, 저렴한 물가와 정을 원한다면 오사카. 일본어학교 지역별 특징과 장단점 완벽 비교.",
        "content": """
            <p>일본어학교를 고를 때 '학교' 자체보다 더 먼저 결정해야 하는 것이 바로 <strong>'지역'</strong>입니다. 지역에 따라 사용하는 일본어의 억양, 생활비, 아르바이트 환경, 그리고 주말에 즐길 수 있는 문화생활이 완전히 달라지기 때문입니다.</p>
            <p>유학생들이 가장 많이 선택하는 대표 지역 3곳의 특징을 비교해 드립니다.</p>

            <h2>1. 도쿄 (Tokyo) - 압도적 인프라</h2>
            <p>전체 유학생의 절반 이상이 도쿄로 갑니다. 일본의 수도이자 모든 것의 중심입니다.</p>
            <ul>
                <li><strong>장점:</strong> 완벽한 표준어를 배울 수 있습니다. 학교 선택지가 수백 개로 가장 많습니다. 아르바이트 시급이 일본에서 가장 높고 일자리도 넘쳐납니다.</li>
                <li><strong>단점:</strong> 월세와 물가가 비쌉니다. 출퇴근 시간 '지옥철'을 경험해야 합니다. 사람이 너무 많아 피로할 수 있습니다.</li>
                <li><strong>추천:</strong> 대학 진학이나 취업이 목표인 사람, 도시의 화려한 라이프스타일을 즐기고 싶은 사람.</li>
            </ul>

            <h2>2. 오사카 (Osaka) - 정과 가성비</h2>
            <p>'일본의 부엌'이자 제2의 도시. 한국인과 정서가 비슷해 적응하기 쉽습니다.</p>
            <ul>
                <li><strong>장점:</strong> 도쿄보다 월세가 30% 정도 저렴합니다. 사람들이 개방적이고 유머러스해서 친구 사귀기가 좋습니다. 교토, 고베, 나라 등 매력적인 주변 도시 여행이 쉽습니다.</li>
                <li><strong>단점:</strong> 사투리(관서벤)가 강합니다. 학교에서는 표준어를 가르치지만, 알바처나 길거리에서는 사투리를 듣게 되어 본인도 모르게 억양이 섞일 수 있습니다.</li>
                <li><strong>추천:</strong> 생활비를 아끼고 싶은 사람, 활기차고 친근한 분위기를 좋아하는 사람.</li>
            </ul>

            <h2>3. 후쿠오카 및 지방 도시</h2>
            <p>한국(부산)에서 가장 가까운 일본. 최근 뜨고 있는 유학지입니다.</p>
            <ul>
                <li><strong>장점:</strong> 물가와 집값이 정말 저렴합니다 (도쿄의 절반 수준). 공항과 시내가 가깝고 도시가 컴팩트해 자전거 생활이 가능합니다. 한국에 자주 왔다 갔다 하기 편합니다.</li>
                <li><strong>단점:</strong> 아르바이트 자리가 대도시만큼 많지 않고 시급이 낮습니다. 대형 콘서트나 전시회 등 문화 혜택이 적을 수 있습니다.</li>
                <li><strong>추천:</strong> 조용하고 여유로운 환경에서 힐링하며 공부하고 싶은 사람, 저예산 유학을 계획하는 사람.</li>
            </ul>

            <div class="highlight-box">
                <span class="highlight-title">JP Campus 에디터의 조언</span>
                <p><strong>진학/취업</strong>이 절실하다면 정보와 기회가 많은 <strong>도쿄</strong>를 추천합니다. 반면, <strong>워킹홀리데이</strong>나 <strong>단기 어학연수</strong>로 즐겁게 생활하며 일본어를 배우고 싶다면 <strong>오사카</strong>나 <strong>후쿠오카</strong>가 만족도가 훨씬 높을 수 있습니다.</p>
            </div>
        """
    }
]

# 파일 생성 루프
for article in articles:
    file_path = os.path.join(OUTPUT_DIR, f"{article['filename']}.html")
    
    # HTML 내용 조립
    html_content = TEMPLATE.format(
        title=article['title'],
        desc=article['desc'],
        category=article['category'],
        content=article['content'],
        date=today
    )
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Created: {file_path}")

print("\n🎉 고품질 가이드 페이지 10개 생성 완료!")