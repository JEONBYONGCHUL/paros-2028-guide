import base64
import glob
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="2028 대학별 권장 과목 조회 | 파로스대입랩",
    page_icon="🎓",
    layout="wide",
)

# 2. 하단 광고 및 Streamlit 뱃지 원천 차단 스크립트 (부모 창/모바일 완벽 대응)
components.html(
    """
    <script>
    function removeStreamlitBranding() {
        const docs = [document];
        try {
            if (window.parent && window.parent.document) docs.push(window.parent.document);
        } catch(e) {}
        try {
            if (window.top && window.top.document) docs.push(window.top.document);
        } catch(e) {}

        docs.forEach(doc => {
            const selectors = [
                '[class*="viewerBadge"]',
                '[class*="ViewerBadge"]',
                '[class*="styles_viewerBadge"]',
                '[class*="viewer-badge"]',
                '[data-testid="manage-app-button"]',
                '#manage-app-button',
                '[data-testid="stStatusWidget"]',
                '[data-testid="stDecoration"]',
                '[data-testid="stToolbar"]',
                '[data-testid="stAppDeployButton"]',
                '[data-testid="stBottom"]',
                'footer',
                '#MainMenu',
                '[href*="streamlit.io"]',
                '[href*="share.streamlit.io"]',
                'div[class*="manage-app"]',
                'div[class*="ManageApp"]'
            ];
            selectors.forEach(sel => {
                try {
                    doc.querySelectorAll(sel).forEach(el => {
                        el.style.setProperty("display", "none", "important");
                        el.style.setProperty("visibility", "hidden", "important");
                        el.style.setProperty("opacity", "0", "important");
                        el.style.setProperty("pointer-events", "none", "important");
                        el.style.setProperty("height", "0", "important");
                        el.style.setProperty("width", "0", "important");
                    });
                } catch(err) {}
            });

            try {
                doc.querySelectorAll('a, button, div, span').forEach(el => {
                    const text = el.innerText || el.textContent || '';
                    if (text.includes('Hosted with Streamlit') || text.includes('Made with Streamlit')) {
                        el.style.setProperty("display", "none", "important");
                        el.style.setProperty("visibility", "hidden", "important");
                    }
                });
            } catch(err) {}
        });
    }

    removeStreamlitBranding();
    document.addEventListener("DOMContentLoaded", removeStreamlitBranding);
    setInterval(removeStreamlitBranding, 300);
    </script>
""",
    height=0,
    width=0,
)

# 3. 디자인 스타일 적용 (모바일 반응형 타이틀 자동 폰트 조절 & 단어 쪼개짐 방지)
st.markdown(
    """
    <style>
    /* Streamlit 순정 UI/로고/뱃지/광고 완전 숨김 */
    #MainMenu {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    header[data-testid="stHeader"] {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    div[data-testid="stAppDeployButton"] {display: none !important;}
    div[data-testid="stBottom"] {display: none !important;}
    footer, [data-testid="stFooter"] {visibility: hidden; display: none !important;}
    
    [class*="viewerBadge"], [class*="ViewerBadge"], [class*="styles_viewerBadge"] {display: none !important; visibility: hidden !important;}
    .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK {display: none !important;}
    
    a[href*="streamlit.io"], a[href*="share.streamlit.io"] {display: none !important;}
    #manage-app-button, [data-testid="manage-app-button"] {display: none !important;}
    div[class*="manage-app"], div[class*="ManageApp"] {display: none !important;}

    iframe[title="streamlit.components.v1.html"] {
        position: absolute !important;
        height: 0px !important;
        width: 0px !important;
        border: none !important;
        visibility: hidden !important;
    }

    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1200px;
    }

    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }

    /* 메인 타이틀: 반응형 폰트(clamp) 및 한국어 단어 쪼개짐 방지(word-break: keep-all) */
    .main-title-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 0.45rem;
        text-align: center;
        width: 100%;
    }
    .main-title {
        font-size: clamp(1.35rem, 4.8vw, 2.2rem);
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.3;
        word-break: keep-all;
        text-align: center;
        background: linear-gradient(135deg, #0F172A 0%, #1E40AF 50%, #0284C7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 서브타이틀 중앙 정렬 & 미니 로고 아이콘 */
    .sub-title {
        font-size: 0.98rem;
        color: #475569;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        text-align: center;
    }
    .mini-logo-img {
        height: 24px;
        width: auto;
        vertical-align: middle;
        display: inline-block;
        margin-right: 2px;
    }
    .sub-title a {
        color: #2563EB;
        text-decoration: none;
        font-weight: 600;
        background: #EFF6FF;
        padding: 3px 10px;
        border-radius: 6px;
        border: 1px solid #DBEAFE;
        transition: all 0.2s ease;
    }
    .sub-title a:hover {
        color: #1D4ED8;
        background: #DBEAFE;
        border-color: #93C5FD;
        text-decoration: none;
    }

    /* 모바일 전용 미세 최적화 */
    @media (max-width: 640px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 1.2rem !important;
        }
        .main-title {
            font-size: 1.4rem !important;
            white-space: nowrap !important;
        }
        .sub-title {
            font-size: 0.88rem !important;
            gap: 6px !important;
        }
        .guide-box {
            padding: 0.9rem 1rem !important;
            font-size: 0.88rem !important;
            line-height: 1.7 !important;
        }
    }

    /* 안내 가이드 박스 */
    .guide-box {
        background: linear-gradient(135deg, #F8FAFC 0%, #F0F7FF 100%);
        border: 1px solid #DBEAFE;
        border-left: 4px solid #2563EB;
        padding: 1.15rem 1.4rem;
        border-radius: 12px;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 16px -2px rgba(37, 99, 235, 0.06);
        line-height: 1.8;
        font-size: 0.95rem;
        color: #1E293B;
    }

    /* 실시간 상태 표시 */
    .live-status {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #059669;
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        padding: 2px 8px;
        border-radius: 20px;
        width: fit-content;
    }
    .live-dot {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 6px #10B981;
    }

    /* 첨단 커맨드 다크 헤더 테이블 */
    .custom-table-container {
        max-height: 650px;
        overflow-x: auto;
        overflow-y: auto;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 20px -3px rgba(15, 23, 42, 0.08);
        background-color: #FFFFFF;
        -webkit-overflow-scrolling: touch;
    }
    .custom-table {
        width: 100%;
        min-width: 600px;
        border-collapse: separate;
        border-spacing: 0;
        table-layout: fixed;
        text-align: left;
        font-size: 0.91rem;
    }
    .custom-table thead {
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .custom-table th {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        color: #F8FAFC;
        font-weight: 700;
        white-space: nowrap;
        text-align: center;
        padding: 13px 10px;
        font-size: 0.88rem;
        letter-spacing: 0.02em;
        border-bottom: 1px solid #334155;
    }
    .custom-table td {
        padding: 12px 10px;
        vertical-align: top;
        border-bottom: 1px solid #F1F5F9;
        word-break: keep-all;
        transition: background 0.15s ease;
    }
    .custom-table tr:hover td {
        background-color: #F8FAFC;
    }

    /* 플로팅 결과 카드 */
    .result-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px -4px rgba(37, 99, 235, 0.12);
        border-color: #93C5FD;
    }

    .badge-core {
        display: inline-block;
        background: #FEF2F2;
        color: #DC2626;
        border: 1px solid #FECACA;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        margin-right: 6px;
    }
    .badge-recommend {
        display: inline-block;
        background: #EFF6FF;
        color: #2563EB;
        border: 1px solid #BFDBFE;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        margin-right: 6px;
    }
    .badge-ref {
        display: inline-block;
        background: #FFFBEB;
        color: #B45309;
        border: 1px solid #FDE68A;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        margin-right: 6px;
    }

    .univ-tag {
        font-size: 1.22rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
    }
    .major-tag {
        font-size: 1.05rem;
        font-weight: 700;
        color: #2563EB;
        margin-left: 6px;
    }

    .footer-text {
        text-align: center;
        color: #94A3B8;
        font-size: 0.86rem;
        margin-top: 3.5rem;
        border-top: 1px solid #F1F5F9;
        padding-top: 1.8rem;
        letter-spacing: 0.02em;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 4. 미니 등대 로고 아이콘 탐색
def get_mini_logo_html():
    img_candidates = glob.glob("*logo*.png") + glob.glob("*.png")
    for img_path in img_candidates:
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return f'<img src="data:image/png;base64,{encoded}" class="mini-logo-img" alt="파로스대입랩" />'
    return ""


# 5. 엑셀 데이터 로드 함수 (수정 시간 감지로 자동 캐시 갱신)
@st.cache_data
def load_data(filepath, file_mtime):
    df_raw = pd.read_excel(filepath, header=None)

    start_row = 4
    for idx, row in df_raw.iloc[:10].iterrows():
        row_vals = [str(x).strip() for x in row.values]
        if "수도권" in row_vals or "가톨릭대" in row_vals:
            start_row = idx
            break

    df_data = df_raw.iloc[start_row:].copy().reset_index(drop=True)
    df_data = df_data.iloc[:, :8]
    df_data.columns = [
        "권역",
        "지역",
        "대학명",
        "계열_단과대",
        "세부학과",
        "핵심과목",
        "권장과목",
        "비고",
    ]

    for col in df_data.columns:
        df_data[col] = (
            df_data[col]
            .fillna("")
            .astype(str)
            .str.strip()
            .replace({"nan": "", "None": ""})
        )

    df_data["대학명"] = (
        df_data["대학명"]
        .str.replace("\n", " ")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    def format_dept(r):
        c_sub = r["세부학과"]
        c_main = r["계열_단과대"]
        if c_sub and c_sub not in ["-", ""]:
            if c_main and c_main not in ["-", "", c_sub]:
                return f"{c_sub} ({c_main})"
            return c_sub
        return c_main

    df_data["모집단위(학과)"] = df_data.apply(format_dept, axis=1)
    df_data["핵심권장과목"] = df_data["핵심과목"].replace(
        {"": "-", "nan": "-"}
    )
    df_data["권장과목"] = df_data["권장과목"].replace(
        {"": "-", "nan": "-"}
    )
    df_data["참조"] = df_data["비고"].replace({"": "-", "nan": "-"})

    df_data = df_data[df_data["대학명"] != ""]
    return df_data[
        ["지역", "대학명", "모집단위(학과)", "핵심권장과목", "권장과목", "참조"]
    ]


# 6. 상단 헤더 영역 (순수 타이틀 반응형 중앙 정렬)
mini_logo = get_mini_logo_html()

st.markdown(
    f"""
<div class="main-title-wrap">
    <span class="main-title">2028 대학별 권장 과목 조회</span>
</div>
<div class="sub-title">
    {mini_logo}
    <span>파로스대입랩 네이버블로그</span>
    <a href="http://blog.naver.com/pharoslab" target="_blank">http://blog.naver.com/pharoslab</a>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="guide-box">
    • <strong>핵심권장과목:</strong> 학과 수학을 위해 고교 재학 중 <em>반드시 이수할 것을 강력히 권장</em>하는 과목입니다.<br>
    • <strong>권장과목:</strong> 전공 학업에 실질적 도움이 되어 <em>가급적 이수를 권장</em>하는 과목입니다.
</div>
""",
    unsafe_allow_html=True,
)

# 엑셀 파일 로드 및 자동 갱신
xlsx_files = glob.glob("*.xlsx")
if not xlsx_files:
    st.error(
        "❌ 엑셀 파일(.xlsx)을 찾을 수 없습니다. 저장소에 파일이 등록되어 있는지 확인해 주세요."
    )
    data = None
else:
    target_file = xlsx_files[0]
    file_mtime = os.path.getmtime(target_file)
    data = load_data(target_file, file_mtime)

if data is not None:
    # 7. 검색 및 필터 컨트롤
    col1, col2, col3 = st.columns([1.5, 2, 2])

    with col1:
        univ_list = ["전체"] + sorted(
            [u for u in data["대학명"].unique() if u != "-"]
        )
        selected_univ = st.selectbox("🏫 대학 선택", univ_list)

    with col2:
        search_dept = st.text_input(
            "🔍 모집단위(학과) 검색", placeholder="예: 컴퓨터, 경영, 의예, 간호, 데이터, 전모집단위"
        )

    with col3:
        search_subject = st.text_input(
            "📚 권장과목 검색", placeholder="예: 미적분, 물리학, 화학, 기하"
        )

    # 필터링 로직
    filtered_df = data.copy()

    if selected_univ != "전체":
        filtered_df = filtered_df[filtered_df["대학명"] == selected_univ]

    if search_dept.strip():
        filtered_df = filtered_df[
            filtered_df["모집단위(학과)"].str.contains(
                search_dept.strip(), case=False, na=False
            )
        ]

    if search_subject.strip():
        sub_q = search_subject.strip()
        filtered_df = filtered_df[
            filtered_df["핵심권장과목"].str.contains(
                sub_q, case=False, na=False
            )
            | filtered_df["권장과목"].str.contains(sub_q, case=False, na=False)
        ]

    # 실시간 데이터 상태 표시바
    st.markdown(
        f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.6rem;">
        <span style="font-size: 0.95rem; color: #334155; font-weight: 500;">
            검색 결과: 총 <strong style="color: #2563EB; font-size: 1.05rem;">{len(filtered_df):,}</strong> 건
        </span>
        <div class="live-status">
            <span class="live-dot"></span> LIVE DATA
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 8. 다크 테크 헤더 표 출력
    if filtered_df.empty:
        st.warning("선택하신 조건에 일치하는 데이터가 없습니다.")
    else:
        rows_html = []
        for _, row in filtered_df.iterrows():
            core_cell = str(row["핵심권장과목"]).replace("\n", "<br>")
            recom_cell = str(row["권장과목"]).replace("\n", "<br>")
            ref_cell = str(row["참조"]).replace("\n", "<br>")

            rows_html.append(
                f"<tr>"
                f'<td style="padding: 12px 10px; font-weight: 700; vertical-align: top; color: #0F172A; word-break: keep-all;">{row["대학명"]}</td>'
                f'<td style="padding: 12px 10px; font-weight: 600; color: #2563EB; vertical-align: top; line-height: 1.5; word-break: keep-all;">{row["모집단위(학과)"]}</td>'
                f'<td style="padding: 12px 10px; vertical-align: top; line-height: 1.6; color: #1E293B; word-break: keep-all;">{core_cell}</td>'
                f'<td style="padding: 12px 10px; vertical-align: top; line-height: 1.6; color: #1E293B; word-break: keep-all;">{recom_cell}</td>'
                f'<td style="padding: 12px 10px; vertical-align: top; line-height: 1.6; color: #475569; font-size: 0.9rem; word-break: keep-all;">{ref_cell}</td>'
                f"</tr>"
            )

        table_html = (
            f'<div class="custom-table-container">'
            f'<table class="custom-table">'
            f"<colgroup>"
            f'<col style="width: 14%;">'  # 대학명
            f'<col style="width: 22%;">'  # 모집단위
            f'<col style="width: 25%;">'  # 핵심권장
            f'<col style="width: 16%;">'  # 권장
            f'<col style="width: 23%;">'  # 참조
            f"</colgroup>"
            f"<thead>"
            f"<tr>"
            f"<th>대학명</th>"
            f"<th>모집단위</th>"
            f"<th>핵심권장</th>"
            f"<th>권장</th>"
            f"<th>참조</th>"
            f"</tr>"
            f"</thead>"
            f"<tbody>"
            f'{"".join(rows_html)}'
            f"</tbody>"
            f"</table>"
            f"</div>"
        )
        st.markdown(table_html, unsafe_allow_html=True)

    # 9. 상세 카드 뷰
    if not filtered_df.empty:
        with st.expander("📌 대학별 상세 카드 뷰로 확인하기 (참조 내용 강조)"):
            for idx, row in filtered_df.head(25).iterrows():
                ref_text = row["참조"]

                if ref_text != "-":
                    ref_clean = ref_text.replace("\n", "<br>")
                    ref_part = f'<div style="margin-top: 10px; line-height: 1.6; color: #374151; background-color: #FFFBEB; padding: 10px 14px; border-radius: 8px; border: 1px solid #FDE68A;"><span class="badge-ref">참조</span> {ref_clean}</div>'
                else:
                    ref_part = ""

                card_html = (
                    f'<div class="result-card">'
                    f'<div style="margin-bottom: 8px;">'
                    f'<span class="univ-tag">{row["대학명"]}</span>'
                    f'<span class="major-tag">| {row["모집단위(학과)"]}</span>'
                    f'<span style="color: #64748B; font-size: 0.85rem; margin-left: 8px;">({row["지역"]})</span>'
                    f"</div>"
                    f'<div style="line-height: 1.8; margin-top: 6px;">'
                    f'<span class="badge-core">핵심 권장</span> <span style="font-weight: 500; color: #1E293B;">{row["핵심권장과목"]}</span><br>'
                    f'<span class="badge-recommend">일반 권장</span> <span style="font-weight: 500; color: #1E293B;">{row["권장과목"]}</span>'
                    f"</div>"
                    f"{ref_part}"
                    f"</div>"
                )

                st.markdown(card_html, unsafe_allow_html=True)

            if len(filtered_df) > 25:
                st.caption(
                    "상세 카드 뷰는 상위 25건까지만 표시됩니다. 전체 목록은 상단 표에서 확인하실 수 있습니다."
                )

    # 10. 하단 브랜딩 푸터
    st.markdown(
        """
        <div class="footer-text">
            © 파로스대입랩 (PHAROS LAB) | 2028 대입 전공 연계 권장과목 연구 자료
        </div>
    """,
        unsafe_allow_html=True,
    )
