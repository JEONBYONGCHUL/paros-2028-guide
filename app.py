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

# 2. 안전하고 강력한 CSS 숨김 처리
st.markdown(
    """
    <style>
    /* Streamlit 기본 UI 완벽 숨김 */
    #MainMenu {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* 우측/좌측 하단 뱃지 기본 차단 */
    [data-testid="manage-app-button"],
    [data-testid="stAppDeployButton"],
    .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_,
    [class*="viewerBadge"],
    [class*="stDeployButton"] {
        display: none !important; 
        visibility: hidden !important; 
        opacity: 0 !important;
        pointer-events: none !important;
        z-index: -9999 !important;
    }

    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1200px;
    }

    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }

    /* 메인 타이틀 */
    .main-title-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1.2rem;
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

    /* 서브타이틀 */
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
    .mini-logo-img { height: 24px; width: auto; vertical-align: middle; display: inline-block; margin-right: 2px; }
    .sub-title a { color: #2563EB; text-decoration: none; font-weight: 600; background: #EFF6FF; padding: 3px 10px; border-radius: 6px; border: 1px solid #DBEAFE; transition: all 0.2s ease; }
    
    /* 모바일 환경 최적화 */
    @media (max-width: 640px) {
        .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; padding-top: 1.2rem !important; }
        .main-title-wrap { margin-bottom: 0.9rem; }
        .main-title { font-size: 1.4rem !important; white-space: nowrap !important; }
        .sub-title { font-size: 0.88rem !important; gap: 6px !important; }
        .guide-box { padding: 0.9rem 1rem !important; font-size: 0.88rem !important; line-height: 1.7 !important; }
    }

    .guide-box { background: linear-gradient(135deg, #F8FAFC 0%, #F0F7FF 100%); border: 1px solid #DBEAFE; border-left: 4px solid #2563EB; padding: 1.15rem 1.4rem; border-radius: 12px; margin-bottom: 1.8rem; box-shadow: 0 4px 16px -2px rgba(37, 99, 235, 0.06); line-height: 1.8; font-size: 0.95rem; color: #1E293B; }
    .live-status { display: flex; align-items: center; gap: 6px; font-size: 0.9rem; font-weight: 600; color: #059669; background: #ECFDF5; border: 1px solid #A7F3D0; padding: 2px 8px; border-radius: 20px; width: fit-content; }
    .live-dot { width: 7px; height: 7px; background-color: #10B981; border-radius: 50%; box-shadow: 0 0 6px #10B981; }
    
    .custom-table-container { max-height: 650px; overflow-x: auto; overflow-y: auto; border: 1px solid #CBD5E1; border-radius: 12px; margin-bottom: 1.8rem; box-shadow: 0 4px 20px -3px rgba(15, 23, 42, 0.08); background-color: #FFFFFF; -webkit-overflow-scrolling: touch; }
    .custom-table { width: 100%; min-width: 600px; border-collapse: separate; border-spacing: 0; table-layout: fixed; text-align: left; font-size: 0.91rem; }
    .custom-table thead { position: sticky; top: 0; z-index: 10; }
    .custom-table th { background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%); color: #F8FAFC; font-weight: 700; white-space: nowrap; text-align: center; padding: 13px 10px; font-size: 0.88rem; border-bottom: 1px solid #334155; }
    .custom-table td { padding: 12px 10px; vertical-align: top; border-bottom: 1px solid #F1F5F9; word-break: keep-all; }
    
    .result-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.3rem; margin-bottom: 1.1rem; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04); }
    .badge-core { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.82rem; margin-right: 6px; }
    .badge-recommend { background: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.82rem; margin-right: 6px; }
    .badge-ref { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.82rem; margin-right: 6px; }
    .univ-tag { font-size: 1.22rem; font-weight: 800; color: #0F172A; }
    .major-tag { font-size: 1.05rem; font-weight: 700; color: #2563EB; margin-left: 6px; }
    .footer-text { text-align: center; color: #94A3B8; font-size: 0.86rem; margin-top: 3.5rem; border-top: 1px solid #F1F5F9; padding-top: 1.8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. 백지화 오류 없는 정밀 타격 뱃지 차단 자바스크립트
components.html(
    """
    <script>
    function stealthKillBadges() {
        try {
            const docs = [document];
            if (window.parent) docs.push(window.parent.document);
            if (window.top) docs.push(window.top.document);
            
            docs.forEach(doc => {
                // Streamlit 특유의 뱃지 클래스 및 속성만 핀포인트로 찾아 투명화
                const targets = doc.querySelectorAll('[class*="viewerBadge"], [class*="ViewerBadge"], [data-testid="stAppDeployButton"], [data-testid="manage-app-button"], a[href*="streamlit.io"]');
                targets.forEach(el => {
                    el.style.setProperty("display", "none", "important");
                    el.style.setProperty("opacity", "0", "important");
                    el.style.setProperty("pointer-events", "none", "important");
                    
                    // 'Hosted with Streamlit' 뱃지가 a 태그 안에 감싸져 있는 경우 부모 배경까지 날림
                    if(el.tagName === 'A' && el.parentElement) {
                        el.parentElement.style.setProperty("display", "none", "important");
                        el.parentElement.style.setProperty("opacity", "0", "important");
                        el.parentElement.style.setProperty("background", "transparent", "important");
                    }
                });
            });
        } catch (e) {}
    }
    // 부하가 발생하지 않는 선에서 0.1초마다 백그라운드 스캔 (Render 환경에서는 타겟이 없으므로 자동 패스됨)
    stealthKillBadges();
    document.addEventListener("DOMContentLoaded", stealthKillBadges);
    setInterval(stealthKillBadges, 100);
    </script>
    """,
    height=0,
    width=0,
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

# 5. 엑셀 데이터 로드 함수
@st.cache_data
def load_data(filepath, file_mtime):
    df_raw = pd.read_excel(filepath, header=None, engine='openpyxl')

    start_row = 4
    for idx, row in df_raw.iloc[:10].iterrows():
        row_vals = [str(x).strip() for x in row.values]
        if "수도권" in row_vals or "가톨릭대" in row_vals:
            start_row = idx
            break

    df_data = df_raw.iloc[start_row:].copy().reset_index(drop=True)
    df_data = df_data.iloc[:, :8]
    df_data.columns = ["권역", "지역", "대학명", "계열_단과대", "세부학과", "핵심과목", "권장과목", "비고"]

    for col in df_data.columns:
        df_data[col] = df_data[col].fillna("").astype(str).str.strip().replace({"nan": "", "None": ""})

    df_data["대학명"] = df_data["대학명"].str.replace("\n", " ").str.replace(r"\s+", " ", regex=True).str.strip()

    def format_dept(r):
        c_sub = r["세부학과"]
        c_main = r["계열_단과대"]
        if c_sub and c_sub not in ["-", ""]:
            if c_main and c_main not in ["-", "", c_sub]:
                return f"{c_sub} ({c_main})"
            return c_sub
        return c_main

    df_data["모집단위(학과)"] = df_data.apply(format_dept, axis=1)
    df_data["핵심권장과목"] = df_data["핵심과목"].replace({"": "-", "nan": "-"})
    df_data["권장과목"] = df_data["권장과목"].replace({"": "-", "nan": "-"})
    df_data["참조"] = df_data["비고"].replace({"": "-", "nan": "-"})

    df_data = df_data[df_data["대학명"] != ""]
    return df_data[["지역", "대학명", "모집단위(학과)", "핵심권장과목", "권장과목", "참조"]]

# 6. 상단 헤더 영역
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

# 엑셀 파일 로드
xlsx_files = glob.glob("*.xlsx")
if not xlsx_files:
    st.error("❌ 엑셀 파일(.xlsx)을 찾을 수 없습니다.")
    data = None
else:
    target_file = xlsx_files[0]
    file_mtime = os.path.getmtime(target_file)
    data = load_data(target_file, file_mtime)

if data is not None:
    # 검색 및 필터
    col1, col2, col3 = st.columns([1.5, 2, 2])
    with col1:
        univ_list = ["전체"] + sorted([u for u in data["대학명"].unique() if u != "-"])
        selected_univ = st.selectbox("🏫 대학 선택", univ_list)
    with col2:
        search_dept = st.text_input("🔍 모집단위(학과) 검색", placeholder="예: 컴퓨터, 경영, 의예, 전모집단위")
    with col3:
        search_subject = st.text_input("📚 권장과목 검색", placeholder="예: 미적분, 물리학, 화학")

    filtered_df = data.copy()
    if selected_univ != "전체":
        filtered_df = filtered_df[filtered_df["대학명"] == selected_univ]
    if search_dept.strip():
        filtered_df = filtered_df[filtered_df["모집단위(학과)"].str.contains(search_dept.strip(), case=False, na=False)]
    if search_subject.strip():
        sub_q = search_subject.strip()
        filtered_df = filtered_df[
            filtered_df["핵심권장과목"].str.contains(sub_q, case=False, na=False) | 
            filtered_df["권장과목"].str.contains(sub_q, case=False, na=False)
        ]

    st.markdown(
        f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.6rem;">
        <span style="font-size: 0.95rem; color: #334155; font-weight: 500;">
            검색 결과: 총 <strong style="color: #2563EB; font-size: 1.05rem;">{len(filtered_df):,}</strong> 건
        </span>
        <div class="live-status"><span class="live-dot"></span> LIVE DATA</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

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
                f'<td style="padding: 12px 10px; font-weight: 700; color: #0F172A;">{row["대학명"]}</td>'
                f'<td style="padding: 12px 10px; font-weight: 600; color: #2563EB;">{row["모집단위(학과)"]}</td>'
                f'<td style="padding: 12px 10px; color: #1E293B;">{core_cell}</td>'
                f'<td style="padding: 12px 10px; color: #1E293B;">{recom_cell}</td>'
                f'<td style="padding: 12px 10px; color: #475569; font-size: 0.9rem;">{ref_cell}</td>'
                f"</tr>"
            )

        table_html = (
            f'<div class="custom-table-container"><table class="custom-table">'
            f"<colgroup><col style='width: 14%;'><col style='width: 22%;'><col style='width: 25%;'><col style='width: 16%;'><col style='width: 23%;'></colgroup>"
            f"<thead><tr><th>대학명</th><th>모집단위</th><th>핵심권장</th><th>권장</th><th>참조</th></tr></thead>"
            f"<tbody>{''.join(rows_html)}</tbody>"
            f"</table></div>"
        )
        st.markdown(table_html, unsafe_allow_html=True)

    if not filtered_df.empty:
        with st.expander("📌 대학별 상세 카드 뷰로 확인하기 (참조 내용 강조)"):
            for idx, row in filtered_df.head(25).iterrows():
                ref_text = row["참조"]
                ref_part = f'<div style="margin-top: 10px; line-height: 1.6; color: #374151; background-color: #FFFBEB; padding: 10px 14px; border-radius: 8px; border: 1px solid #FDE68A;"><span class="badge-ref">참조</span> {ref_text.replace(chr(10), "<br>")}</div>' if ref_text != "-" else ""

                card_html = (
                    f'<div class="result-card">'
                    f'<div style="margin-bottom: 8px;"><span class="univ-tag">{row["대학명"]}</span><span class="major-tag">| {row["모집단위(학과)"]}</span><span style="color: #64748B; font-size: 0.85rem; margin-left: 8px;">({row["지역"]})</span></div>'
                    f'<div style="line-height: 1.8; margin-top: 6px;"><span class="badge-core">핵심 권장</span> <span style="font-weight: 500; color: #1E293B;">{row["핵심권장과목"]}</span><br><span class="badge-recommend">일반 권장</span> <span style="font-weight: 500; color: #1E293B;">{row["권장과목"]}</span></div>'
                    f"{ref_part}</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)

            if len(filtered_df) > 25:
                st.caption("상세 카드 뷰는 상위 25건까지만 표시됩니다. 전체 목록은 상단 표에서 확인하실 수 있습니다.")

    st.markdown(
        """
        <div class="footer-text">
            © 파로스대입랩 (PHAROS LAB) | 2028 대입 전공 연계 권장과목 연구 자료
        </div>
    """,
        unsafe_allow_html=True,
    )
