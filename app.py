import glob
import os
import pandas as pd
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="2028 대학별 권장과목 조회 | 파로스대입랩",
    page_icon="🎓",
    layout="wide",
)

# 2. 디자인 스타일 적용 (Streamlit 모든 마크/뱃지/헤더 완전 제거 & 모바일 최적화)
st.markdown(
    """
    <style>
    /* ===================================================
       [Streamlit 상단 바, 햄버거 메뉴, 로고 뱃지 완전 제거]
       =================================================== */
    #MainMenu {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    header[data-testid="stHeader"] {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    div[data-testid="stAppDeployButton"] {display: none !important;}
    footer {visibility: hidden; display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
    a[href*="streamlit.io"] {display: none !important;}
    
    /* 상단 헤더 숨김 시 글자가 화면 맨 위에 붙지 않도록 안전 여백 확보 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif; }
    
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.3rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #374151;
        margin-bottom: 1.2rem;
    }
    .sub-title a {
        color: #2563EB;
        text-decoration: none;
        font-weight: 600;
    }
    .sub-title a:hover {
        color: #1D4ED8;
        text-decoration: none;
    }
    .guide-box {
        background-color: #F8FAFC;
        border-left: 5px solid #2563EB;
        padding: 1.1rem 1.3rem;
        border-radius: 8px;
        margin-bottom: 1.6rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        line-height: 1.8;
        font-size: 0.96rem;
        color: #1F2937;
    }
    .result-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .badge-core {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 6px;
    }
    .badge-recommend {
        background-color: #DBEAFE;
        color: #1D4ED8;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 6px;
    }
    .badge-ref {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 6px;
    }
    .univ-tag {
        font-size: 1.2rem;
        font-weight: 700;
        color: #111827;
    }
    .major-tag {
        font-size: 1.05rem;
        font-weight: 600;
        color: #2563EB;
        margin-left: 6px;
    }
    .custom-table tr:hover {
        background-color: #F8FAFC;
    }
    .footer-text {
        text-align: center;
        color: #9CA3AF;
        font-size: 0.88rem;
        margin-top: 3rem;
        border-top: 1px solid #E5E7EB;
        padding-top: 1.5rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 3. 엑셀 데이터 정밀 로드 함수
@st.cache_data
def load_data():
    xlsx_files = glob.glob("*.xlsx")
    if not xlsx_files:
        return None

    filepath = xlsx_files[0]
    df_raw = pd.read_excel(filepath, header=None)

    # 실제 데이터 시작 행 탐색 (5번째 행)
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

    # 대학명 줄바꿈 정리
    df_data["대학명"] = (
        df_data["대학명"]
        .str.replace("\n", " ")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # 학과 및 계열 표기 결합
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


# 4. 상단 타이틀 및 안내문
st.markdown(
    '<div class="main-title">🎓 2028 대학별 권장과목 조회</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">파로스대입랩 네이버블로그 <a href="http://blog.naver.com/pharoslab" target="_blank">http://blog.naver.com/pharoslab</a></div>',
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

data = load_data()

if data is None:
    st.error(
        "❌ 엑셀 파일(.xlsx)을 찾을 수 없습니다. 저장소에 파일이 등록되어 있는지 확인해 주세요."
    )
else:
    # 5. 검색 및 필터 컨트롤
    col1, col2, col3 = st.columns([1.5, 2, 2])

    with col1:
        univ_list = ["전체"] + sorted(
            [u for u in data["대학명"].unique() if u != "-"]
        )
        selected_univ = st.selectbox("🏫 대학 선택", univ_list)

    with col2:
        search_dept = st.text_input(
            "🔍 모집단위(학과) 검색", placeholder="예: 컴퓨터, 경영, 의예, 간호, 데이터"
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

    st.markdown(f"**검색 결과: 총 `{len(filtered_df):,}`건**")

    # 6. 표 출력 (헤더 가운데 정렬 및 모바일 최적화 유지)
    if filtered_df.empty:
        st.warning("선택하신 조건에 일치하는 데이터가 없습니다.")
    else:
        rows_html = []
        for _, row in filtered_df.iterrows():
            core_cell = str(row["핵심권장과목"]).replace("\n", "<br>")
            recom_cell = str(row["권장과목"]).replace("\n", "<br>")
            ref_cell = str(row["참조"]).replace("\n", "<br>")

            rows_html.append(
                f'<tr style="border-bottom: 1px solid #E2E8F0;">'
                f'<td style="padding: 10px 8px; font-weight: 700; vertical-align: top; color: #111827; word-break: keep-all;">{row["대학명"]}</td>'
                f'<td style="padding: 10px 8px; font-weight: 600; color: #2563EB; vertical-align: top; line-height: 1.5; word-break: keep-all;">{row["모집단위(학과)"]}</td>'
                f'<td style="padding: 10px 8px; vertical-align: top; line-height: 1.6; color: #1F2937; word-break: keep-all;">{core_cell}</td>'
                f'<td style="padding: 10px 8px; vertical-align: top; line-height: 1.6; color: #1F2937; word-break: keep-all;">{recom_cell}</td>'
                f'<td style="padding: 10px 8px; vertical-align: top; line-height: 1.6; color: #374151; font-size: 0.9rem; word-break: keep-all;">{ref_cell}</td>'
                f"</tr>"
            )

        table_html = (
            f'<div style="max-height: 650px; overflow-x: auto; overflow-y: auto; border: 1px solid #CBD5E1; border-radius: 8px; margin-bottom: 1.6rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); -webkit-overflow-scrolling: touch;">'
            f'<table class="custom-table" style="width: 100%; min-width: 580px; border-collapse: collapse; table-layout: fixed; text-align: left; font-size: 0.91rem; background-color: #FFFFFF;">'
            f"<colgroup>"
            f'<col style="width: 14%;">'  # 대학명
            f'<col style="width: 22%;">'  # 모집단위
            f'<col style="width: 25%;">'  # 핵심권장
            f'<col style="width: 16%;">'  # 권장
            f'<col style="width: 23%;">'  # 참조
            f"</colgroup>"
            f'<thead style="background-color: #F8FAFC; position: sticky; top: 0; z-index: 10; border-bottom: 2px solid #CBD5E1;">'
            f"<tr>"
            f'<th style="padding: 11px 8px; color: #1E293B; font-weight: 700; white-space: nowrap; text-align: center;">대학명</th>'
            f'<th style="padding: 11px 8px; color: #1E293B; font-weight: 700; white-space: nowrap; text-align: center;">모집단위</th>'
            f'<th style="padding: 11px 8px; color: #1E293B; font-weight: 700; white-space: nowrap; text-align: center;">핵심권장</th>'
            f'<th style="padding: 11px 8px; color: #1E293B; font-weight: 700; white-space: nowrap; text-align: center;">권장</th>'
            f'<th style="padding: 11px 8px; color: #1E293B; font-weight: 700; white-space: nowrap; text-align: center;">참조</th>'
            f"</tr>"
            f"</thead>"
            f"<tbody>"
            f'{"".join(rows_html)}'
            f"</tbody>"
            f"</table>"
            f"</div>"
        )
        st.markdown(table_html, unsafe_allow_html=True)

    # 7. 상세 카드 뷰
    if not filtered_df.empty:
        with st.expander("📌 대학별 상세 카드 뷰로 확인하기 (참조 내용 강조)"):
            for idx, row in filtered_df.head(25).iterrows():
                ref_text = row["참조"]

                if ref_text != "-":
                    ref_clean = ref_text.replace("\n", "<br>")
                    ref_part = f'<div style="margin-top: 10px; line-height: 1.6; color: #374151; background-color: #FFFBEB; padding: 10px 14px; border-radius: 6px; border: 1px solid #FDE68A;"><span class="badge-ref">참조</span> {ref_clean}</div>'
                else:
                    ref_part = ""

                card_html = (
                    f'<div class="result-card">'
                    f'<div style="margin-bottom: 8px;">'
                    f'<span class="univ-tag">{row["대학명"]}</span>'
                    f'<span class="major-tag">| {row["모집단위(학과)"]}</span>'
                    f'<span style="color: #6B7280; font-size: 0.85rem; margin-left: 8px;">({row["지역"]})</span>'
                    f"</div>"
                    f'<div style="line-height: 1.8; margin-top: 6px;">'
                    f'<span class="badge-core">핵심 권장</span> <span style="font-weight: 500;">{row["핵심권장과목"]}</span><br>'
                    f'<span class="badge-recommend">일반 권장</span> <span style="font-weight: 500;">{row["권장과목"]}</span>'
                    f"</div>"
                    f"{ref_part}"
                    f"</div>"
                )

                st.markdown(card_html, unsafe_allow_html=True)

            if len(filtered_df) > 25:
                st.caption(
                    "상세 카드 뷰는 상위 25건까지만 표시됩니다. 전체 목록은 상단 표에서 확인하실 수 있습니다."
                )

    # 8. 하단 브랜딩 푸터
    st.markdown(
        """
        <div class="footer-text">
            © 파로스대입랩 | 2028 대입 전공 연계 권장과목 연구 자료
        </div>
    """,
        unsafe_allow_html=True,
    )
