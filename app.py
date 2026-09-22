import pandas as pd
import streamlit as st

# 1. 웹 브라우저 탭 및 레이아웃 설정
st.set_page_config(
    page_title="2028 대학별 권장과목 조회기 | 파로스대입랩",
    page_icon="🎓",
    layout="wide",
)

# 2. 파로스랩디자인 스타일 적용 (CSS)
st.markdown(
    """
    <style>
    /* 상단 메뉴, 깃허브 링크, 하단 배너 숨기기 */
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
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .guide-box {
        background-color: #F8FAFC;
        border-left: 5px solid #2563EB;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .result-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.3rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        transition: transform 0.15s ease-in-out;
    }
    .result-card:hover {
        border-color: #93C5FD;
        transform: translateY(-2px);
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
    .univ-tag {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
    }
    .major-tag {
        font-size: 1rem;
        font-weight: 600;
        color: #4B5563;
        margin-left: 8px;
    }
    .footer-text {
        text-align: center;
        color: #9CA3AF;
        font-size: 0.9rem;
        margin-top: 3rem;
        border-top: 1px solid #E5E7EB;
        padding-top: 1.5rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 3. 엑셀 파일 불러오기 (캐싱으로 로딩 속도 최적화)
@st.cache_data
def load_excel_data():
    file_name = "2028_권장과목.xlsx"
    data = pd.read_excel(file_name)
    data.columns = data.columns.astype(str).str.strip()
    return data


try:
    df = load_excel_data()

    # 상단 타이틀 영역
    st.markdown(
        '<div class="main-title">🎓 2028 대학별 모집단위 권장과목 조회기</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-title">파로스대입랩 | 2028 대입 개편안 및 고교학점제 선택과목 가이드</div>',
        unsafe_allow_html=True,
    )

    # 이수 안내 가이드 박스
    st.markdown(
        """
    <div class="guide-box">
        <strong>📌 권장과목 확인 시 유의사항</strong><br>
        • <strong>핵심 권장과목:</strong> 해당 학과 전공 이수를 위해 고교 재학 중 <em>반드시 이수할 것을 강력 권장</em>하는 과목입니다.<br>
        • <strong>권장과목:</strong> 전공 학업 수행에 실질적 도움이 되므로 <em>이수를 권장</em>하는 과목입니다.<br>
        • 학생부종합전형 서류평가 및 학생부교과전형(정성평가 반영 대학)의 전공 연계 교과 이수 노력에 직접 활용됩니다.
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 엑셀 헤더명 자동 매핑 (헤더명이 조금 달라도 자동 인식)
    col_univ = next(
        (c for c in df.columns if c in ["대학", "대학명", "대학교"]),
        df.columns[0],
    )
    col_major = next(
        (
            c
            for c in df.columns
            if c in ["학과", "모집단위", "학과명", "모집단위명"]
        ),
        df.columns[1],
    )
    col_core = next(
        (
            c
            for c in df.columns
            if "핵심" in c or c in ["핵심권장과목", "핵심 권장과목"]
        ),
        None,
    )
    col_rec = next(
        (
            c
            for c in df.columns
            if ("권장" in c and "핵심" not in c)
            or c in ["권장과목", "일반권장과목"]
        ),
        None,
    )
    col_note = next(
        (c for c in df.columns if c in ["비고", "참고", "비고사항"]), None
    )

    # 4. 검색 필터 드롭다운 구성
    major_list = sorted(df[col_major].dropna().unique().tolist())
    univ_list = sorted(df[col_univ].dropna().unique().tolist())

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_major = st.selectbox(
            "🔍 희망 모집단위(학과)를 선택하세요",
            options=["-- 학과를 선택해 주세요 --"] + major_list,
            index=0,
        )

    with col2:
        selected_univ = st.selectbox(
            "🏫 대학별 필터 (선택 사항)",
            options=["전체 대학 보기"] + univ_list,
            index=0,
        )

    # 5. 결과 화면 출력
    if selected_major != "-- 학과를 선택해 주세요 --":
        result_df = df[df[col_major] == selected_major]

        if selected_univ != "전체 대학 보기":
            result_df = result_df[result_df[col_univ] == selected_univ]

        st.markdown(
            f"#### 📋 **'{selected_major}'** 조회 결과 (총 {len(result_df)}개 대학)"
        )

        if result_df.empty:
            st.warning("선택하신 조건에 일치하는 데이터가 없습니다.")
        else:
            for _, row in result_df.iterrows():
                univ_val = row.get(col_univ, "-")
                core_val = row.get(col_core, "-") if col_core else "-"
                rec_val = row.get(col_rec, "-") if col_rec else "-"
                note_val = row.get(col_note, "") if col_note else ""

                core_str = (
                    str(core_val).strip()
                    if pd.notna(core_val) and str(core_val).strip()
                    else "지정 과목 없음"
                )
                rec_str = (
                    str(rec_val).strip()
                    if pd.notna(rec_val) and str(rec_val).strip()
                    else "지정 과목 없음"
                )
                note_str = (
                    f"<div style='margin-top: 8px; font-size: 0.88rem; color: #64748B;'>📝 <strong>비고:</strong> {note_val}</div>"
                    if pd.notna(note_val) and str(note_val).strip()
                    else ""
                )

                card_html = f"""
                <div class="result-card">
                    <div style="margin-bottom: 8px;">
                        <span class="univ-tag">{univ_val}</span>
                        <span class="major-tag">| {selected_major}</span>
                    </div>
                    <div style="line-height: 1.8; margin-top: 6px;">
                        <span class="badge-core">핵심 권장</span> <span style="font-weight: 500;">{core_str}</span><br>
                        <span class="badge-recommend">일반 권장</span> <span style="font-weight: 500;">{rec_str}</span>
                    </div>
                    {note_str}
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info(
            "💡 위 드롭다운 검색창을 클릭하여 관심 있는 학과를 선택해 보세요."
        )

    # 하단 출처 표기
    st.markdown(
        """
        <div class="footer-text">
            © 파로스대입랩 (PHAROS LAB) | 2028 대입 지원 연구 자료
        </div>
    """,
        unsafe_allow_html=True,
    )

except FileNotFoundError:
    st.error(
        "❌ '2028_권장과목.xlsx' 파일을 찾을 수 없습니다. GitHub 저장소에 엑셀 파일이 정확한 이름으로 업로드되어 있는지 확인해 주세요."
    )
except Exception as err:
    st.error(f"❌ 데이터를 불러오는 도중 오류가 발생했습니다: {err}")
