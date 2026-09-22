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

# 2. 디자인 스타일 적용 (상단 메뉴/깃허브 링크 숨김 및 카드 스타일)
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
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
        margin-bottom: 1.5rem;
    }
    .sub-title a {
        color: #2563EB;
        text-decoration: underline;
        font-weight: 600;
    }
    .sub-title a:hover {
        color: #1D4ED8;
    }
    .guide-box {
        background-color: #F8FAFC;
        border-left: 5px solid #2563EB;
        padding: 1.1rem 1.3rem;
        border-radius: 8px;
        margin-bottom: 1.6rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        line-height: 1.65;
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

    # 대학명 줄바꿈 제거
    df_data["대학명"] = (
        df_data["대학명"]
        .str.replace("\n", " ")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # 학과 및 계열 융합 표기
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


# 4. 상단 타이틀 및 네이버 블로그 링크 (요청 사항 반영)
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
    <strong>💡 권장과목 및 참조 안내</strong><br>
    • <strong>핵심권장과목:</strong> 학과 수학을 위해 고교 재학 중 <em>반드시 이수할 것을 강력히 권장</em>하는 과목입니다.<br>
    • <strong>권장과목:</strong> 전공 학업에 실질적 도움이 되어 <em>가급적 이수를 권장</em>하는 과목입니다.<br>
    • <strong>참조:</strong> 이수 과목 수(예: 3과목 이상), 과목 선택 위계, 평가 반영 방식 등 <strong>대학별 필수 확인 조건</strong>이 안내됩니다.
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
            "🔍 모집단위(학과) 검색", placeholder="예: 컴퓨터, 경영, 의예, 간호"
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

    # 6. 테이블 뷰 (표)
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "지역": st.column_config.TextColumn("지역", width="small"),
            "대학명": st.column_config.TextColumn("대학명", width="medium"),
            "모집단위(학과)": st.column_config.TextColumn(
                "모집단위(학과)", width="large"
            ),
            "핵심권장과목": st.column_config.TextColumn(
                "핵심권장과목", width="large"
            ),
            "권장과목": st.column_config.TextColumn("권장과목", width="large"),
            "참조": st.column_config.TextColumn("참조 (비고)", width="large"),
        },
    )

    # 7. 상세 카드 뷰 (코드 노출 방지를 위해 들여쓰기 공백 원천 제거)
    if not filtered_df.empty:
        with st.expander("📌 대학별 상세 카드 뷰로 확인하기 (참조 내용 강조)"):
            for idx, row in filtered_df.head(25).iterrows():
                ref_text = row["참조"]

                # 참조 박스 HTML (들여쓰기 없는 단일 문자열로 구성하여 마크다운 코드블록 변환 방지)
                if ref_text != "-":
                    ref_clean = ref_text.replace("\n", "<br>")
                    ref_part = f'<div style="margin-top: 10px; line-height: 1.6; color: #374151; background-color: #FFFBEB; padding: 10px 14px; border-radius: 6px; border: 1px solid #FDE68A;"><span class="badge-ref">참조</span> {ref_clean}</div>'
                else:
                    ref_part = ""

                # 전체 카드 HTML (각 줄 맨 앞 공백 0으로 생성)
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
