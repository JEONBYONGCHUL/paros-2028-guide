import os
import glob
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="2028 대입 과목 이수 가이드",
    page_icon="🎓",
    layout="wide"
)

# 1. 엑셀 파일 로드 함수
@st.cache_data
def load_data():
    # 저장소 내 xlsx 파일 자동 탐색 (없을 시 파일 업로더 지원)
    xlsx_files = glob.glob("*.xlsx")
    if xlsx_files:
        filepath = xlsx_files[0]
        df = pd.read_excel(filepath)
    else:
        uploaded_file = st.sidebar.file_uploader("엑셀 파일(.xlsx)을 업로드하세요", type=["xlsx"])
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
        else:
            return None

    # 유연한 열 이름 매핑 로직
    def get_col(candidates, exclude=None):
        for col in df.columns:
            clean = str(col).replace(" ", "").replace("\n", "").strip()
            if exclude and any(ex in clean for ex in exclude):
                continue
            for cand in candidates:
                if cand in clean:
                    return col
        return None

    col_univ = get_col(["대학명", "대학교", "대학", "학교명"])
    col_dept = get_col(["모집단위", "학과", "학부", "전공", "계열"])
    col_core = get_col(["핵심권장", "핵심과목", "핵심"])
    col_recom = get_col(["권장과목", "권장"], exclude=["핵심"])
    col_note = get_col(["비고", "참조", "특이사항", "참고사항", "안내"])
    col_region = get_col(["권역", "시도", "지역"])

    # 필수 열 매핑 및 이름 정규화
    mapping = {}
    if col_region:
        mapping[col_region] = "지역"
    if col_univ:
        mapping[col_univ] = "대학명"
    if col_dept:
        mapping[col_dept] = "모집단위(학과)"
    if col_core:
        mapping[col_core] = "핵심권장과목"
    if col_recom:
        mapping[col_recom] = "권장과목"
    if col_note:
        mapping[col_note] = "참조"

    df = df.rename(columns=mapping)

    # 기본 열이 없을 경우 빈 열 생성
    target_cols = ["대학명", "모집단위(학과)", "핵심권장과목", "권장과목", "참조"]
    if "지역" in df.columns:
        target_cols.insert(0, "지역")

    for col in target_cols:
        if col not in df.columns:
            df[col] = "-"

    # 결측치 정돈
    df[target_cols] = df[target_cols].fillna("-").astype(str)
    return df[target_cols]


# 메인 화면 구성
st.title("🎓 대입 권장과목 & 전공 연계 가이드")
st.caption("대학별 모집단위의 핵심권장과목, 권장과목 및 참조(비고) 사항을 검색합니다.")

data = load_data()

if data is None:
    st.info("💡 GitHub 저장소에 엑셀 파일(.xlsx)을 업로드하거나, 좌측 사이드바에서 파일을 직접 등록해 주세요.")
else:
    # 검색 및 필터 영역
    with st.container():
        col1, col2, col3 = st.columns([1.5, 2, 2])

        with col1:
            univ_list = ["전체"] + sorted([u for u in data["대학명"].unique() if u != "-"])
            selected_univ = st.selectbox("🏫 대학 선택", univ_list)

        with col2:
            search_dept = st.text_input("🔍 모집단위(학과) 검색", placeholder="예: 컴퓨터, 경영, 의예")

        with col3:
            search_subject = st.text_input("📚 권장과목 검색", placeholder="예: 미적분, 물리학, 화학")

    # 필터링 적용
    filtered_df = data.copy()

    if selected_univ != "전체":
        filtered_df = filtered_df[filtered_df["대학명"] == selected_univ]

    if search_dept.strip():
        filtered_df = filtered_df[filtered_df["모집단위(학과)"].str.contains(search_dept.strip(), case=False, na=False)]

    if search_subject.strip():
        sub_query = search_subject.strip()
        filtered_df = filtered_df[
            filtered_df["핵심권장과목"].str.contains(sub_query, case=False, na=False) |
            filtered_df["권장과목"].str.contains(sub_query, case=False, na=False)
        ]

    st.markdown("---")
    st.markdown(f"**검색 결과: 총 `{len(filtered_df):,}`건**")

    # 테이블 뷰
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "지역": st.column_config.TextColumn("지역", width="small"),
            "대학명": st.column_config.TextColumn("대학명", width="medium"),
            "모집단위(학과)": st.column_config.TextColumn("모집단위(학과)", width="large"),
            "핵심권장과목": st.column_config.TextColumn("핵심권장과목", width="large"),
            "권장과목": st.column_config.TextColumn("권장과목", width="large"),
            "참조": st.column_config.TextColumn("참조 (비고)", width="large"),
        }
    )

    # 주요 참조사항 강조 상세 카드 (선택 시 열람)
    if not filtered_df.empty:
        with st.expander("📌 상세 카드 뷰로 보기 (참조사항 포함)"):
            for idx, row in filtered_df.head(20).iterrows():
                with st.container():
                    st.markdown(f"#### **{row['대학명']}** - {row['모집단위(학과)']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**• 핵심권장:** {row['핵심권장과목']}")
                    with c2:
                        st.markdown(f"**• 일반권장:** {row['권장과목']}")
                    
                    if row["참조"] != "-":
                        st.info(f"**💡 참조:** {row['참조']}")
                    st.divider()
            
            if len(filtered_df) > 20:
                st.caption("상세 카드 뷰는 상위 20건까지만 표시됩니다. 전체 내역은 상단 표에서 확인하세요.")
